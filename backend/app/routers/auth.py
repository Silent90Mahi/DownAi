from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas
from ..services import trust_service, notification_service
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)

# Use settings from environment instead of hardcoded values
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token using configured settings"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Validate and get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        phone: str = payload.get("sub")
        if phone is None:
            logger.warning("Token missing subject (phone)")
            raise credentials_exception
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise credentials_exception

    user = db.query(models.User).filter(models.User.phone == phone).first()
    if user is None:
        logger.warning(f"User not found for phone: {phone}")
        raise credentials_exception

    logger.debug(f"User authenticated: {user.id}")
    return user

async def get_current_user_optional(token: Optional[str] = None, db: Session = Depends(get_db)):
    """Validate and get current user from JWT token (optional - returns None if invalid)"""
    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        phone: str = payload.get("sub")
        if phone is None:
            return None
    except JWTError:
        return None

    user = db.query(models.User).filter(models.User.phone == phone).first()
    if user is None:
        return None

    return user

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/register-and-send-otp")
async def register_and_send_otp(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user and send OTP in one call (for smoother signup flow)"""
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.phone == user.phone).first()

    if db_user:
        # User exists, just send OTP
        mock_otp = "123456"
        return {
            "success": True,
            "message": "Account already exists. OTP sent to login.",
            "otp": mock_otp,
            "expires_in": 300,
            "user_exists": True
        }

    # Create new user
    new_user = models.User(
        phone=user.phone,
        name=user.name,
        email=user.email,
        role=models.UserRole(user.role),
        hierarchy_level=models.HierarchyLevel.SHG if user.role == "SHG" else models.HierarchyLevel.NONE,
        district=user.district,
        language_preference=user.language_preference,
        trust_score=50.0,
        trust_coins=0,
        trust_badge="Bronze"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create audit log
    await trust_service.create_audit_log(
        new_user.id,
        "user_registered",
        "user",
        new_user.id,
        {"role": user.role},
        db=db
    )

    # Send OTP
    mock_otp = "123456"
    return {
        "success": True,
        "message": "Registration successful! OTP sent to verify your phone.",
        "otp": mock_otp,
        "expires_in": 300,
        "user_exists": False,
        "user": {
            "id": new_user.id,
            "phone": new_user.phone,
            "name": new_user.name
        }
    }

@router.post("/register", response_model=schemas.UserResponse)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    db_user = db.query(models.User).filter(models.User.phone == user.phone).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Phone already registered")

    # Create new user
    new_user = models.User(
        phone=user.phone,
        name=user.name,
        email=user.email,
        role=models.UserRole(user.role),
        hierarchy_level=models.HierarchyLevel.SHG if user.role == "SHG" else models.HierarchyLevel.NONE,
        district=user.district,
        language_preference=user.language_preference,
        trust_score=50.0,
        trust_coins=0,
        trust_badge="Bronze"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create audit log
    await trust_service.create_audit_log(
        new_user.id,
        "user_registered",
        "user",
        new_user.id,
        {"role": user.role},
        db=db
    )

    return new_user

@router.post("/login", response_model=schemas.Token)
async def login_json(request: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login with phone and password (JSON format for frontend)"""
    user = db.query(models.User).filter(models.User.phone == request.phone).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phone number not registered. Please click the 'Register' tab to create an account.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.phone, "role": user.role.value},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer", "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60}

@router.post("/token", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with phone (simulated OTP-based)"""
    # For MVP, accept phone as username and any password
    user = db.query(models.User).filter(models.User.phone == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phone number not registered",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.phone, "role": user.role.value},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer", "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60}

@router.post("/send-otp")
async def send_otp(request: schemas.OTPRequest, db: Session = Depends(get_db)):
    """Send OTP (simulated - returns mock OTP)"""
    user = db.query(models.User).filter(models.User.phone == request.phone).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Phone number not found. Please register first by clicking the 'Register' tab above."
        )

    # Mock OTP - in production, send via SMS
    mock_otp = "123456"

    return {
        "success": True,
        "message": "OTP sent successfully",
        "otp": mock_otp,  # Only for development
        "expires_in": 300  # 5 minutes
    }

@router.post("/verify-otp", response_model=schemas.Token)
async def verify_otp(request: schemas.OTPVerify, db: Session = Depends(get_db)):
    """Verify OTP and return token"""
    # For MVP, accept any 6-digit OTP
    if len(request.otp) != 6 or not request.otp.isdigit():
        raise HTTPException(status_code=400, detail="Invalid OTP format")

    user = db.query(models.User).filter(models.User.phone == request.phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update last login and verify phone
    user.last_login = datetime.utcnow()
    user.phone_verified = True
    db.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.phone, "role": user.role.value},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=schemas.UserResponse)
async def get_profile(current_user: models.User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.put("/profile", response_model=schemas.UserResponse)
async def update_profile(
    updates: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    # Update fields that are provided
    update_data = updates.dict(exclude_unset=True)

    for field, value in update_data.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)

    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)

    return current_user

@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """Get current user info (alias for /profile)"""
    return current_user

@router.post("/logout")
async def logout(current_user: models.User = Depends(get_current_user)):
    """Logout (client-side token removal)"""
    return {"message": "Logged out successfully"}
