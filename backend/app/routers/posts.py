from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from pydantic import BaseModel
from ..database import get_db
from ..models import Post, Comment, PostLike, CommentLike, User
from ..routers.auth import get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])


class PostCreate(BaseModel):
    title: Optional[str] = None
    content: str
    post_type: str = "general"
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class PostResponse(BaseModel):
    id: int
    author_id: int
    author_name: str
    title: Optional[str]
    content: str
    post_type: str
    category: Optional[str]
    tags: Optional[List[str]]
    likes_count: int
    comments_count: int
    shares_count: int
    views_count: int
    is_pinned: bool
    is_featured: bool
    is_announcement: bool
    is_liked: bool = False
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[int] = None
    image_url: Optional[str] = None


class CommentResponse(BaseModel):
    id: int
    post_id: int
    author_id: int
    author_name: str
    author_image: Optional[str]
    parent_id: Optional[int]
    content: str
    image_url: Optional[str]
    likes_count: int
    replies_count: int
    is_liked: bool = False
    created_at: str
    updated_at: Optional[str]
    replies: List["CommentResponse"] = []

    class Config:
        from_attributes = True


@router.get("", response_model=dict)
def get_posts(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    post_type: Optional[str] = None,
    author_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Post).filter(Post.id > 0)
    
    if category:
        query = query.filter(Post.category == category)
    if post_type:
        query = query.filter(Post.post_type == post_type)
    if author_id:
        query = query.filter(Post.author_id == author_id)
    
    total = query.count()
    posts = query.order_by(desc(Post.is_pinned), desc(Post.is_featured), desc(Post.created_at)).offset(skip).limit(limit).all()
    
    user_liked_post_ids = set(
        like.post_id for like in db.query(PostLike).filter(PostLike.user_id == current_user.id).all()
    )
    
    result = []
    for post in posts:
        author = db.query(User).filter(User.id == post.author_id).first()
        result.append({
            "id": post.id,
            "author_id": post.author_id,
            "author_name": author.name if author else "Unknown",
            "author_image": author.profile_image if author else None,
            "title": post.title,
            "content": post.content,
            "post_type": post.post_type,
            "category": post.category,
            "tags": post.tags or [],
            "likes_count": post.likes_count or 0,
            "comments_count": post.comments_count or 0,
            "shares_count": post.shares_count or 0,
            "views_count": post.views_count or 0,
            "is_pinned": post.is_pinned,
            "is_featured": post.is_featured,
            "is_announcement": post.is_announcement,
            "is_liked": post.id in user_liked_post_ids,
            "created_at": post.created_at.isoformat() if post.created_at else None,
            "updated_at": post.updated_at.isoformat() if post.updated_at else None,
        })
    
    return {"items": result, "total": total, "skip": skip, "limit": limit}


@router.post("", response_model=PostResponse)
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = Post(
        author_id=current_user.id,
        title=post_data.title,
        content=post_data.content,
        post_type=post_data.post_type,
        category=post_data.category,
        tags=post_data.tags,
        images=post_data.images,
        video_url=post_data.video_url
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    
    return {
        "id": post.id,
        "author_id": post.author_id,
        "author_name": current_user.name,
        "author_image": current_user.profile_image,
        "title": post.title,
        "content": post.content,
        "post_type": post.post_type,
        "category": post.category,
        "tags": post.tags or [],
        "likes_count": 0,
        "comments_count": 0,
        "shares_count": 0,
        "views_count": 0,
        "is_pinned": False,
        "is_featured": False,
        "is_announcement": False,
        "is_liked": False,
        "created_at": post.created_at.isoformat(),
        "updated_at": None,
    }


@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post.views_count = (post.views_count or 0) + 1
    db.commit()
    
    author = db.query(User).filter(User.id == post.author_id).first()
    is_liked = db.query(PostLike).filter(
        PostLike.post_id == post_id,
        PostLike.user_id == current_user.id
    ).first() is not None
    
    return {
        "id": post.id,
        "author_id": post.author_id,
        "author_name": author.name if author else "Unknown",
        "author_image": author.profile_image if author else None,
        "title": post.title,
        "content": post.content,
        "post_type": post.post_type,
        "category": post.category,
        "tags": post.tags or [],
        "images": post.images or [],
        "video_url": post.video_url,
        "likes_count": post.likes_count or 0,
        "comments_count": post.comments_count or 0,
        "shares_count": post.shares_count or 0,
        "views_count": post.views_count or 0,
        "is_pinned": post.is_pinned,
        "is_featured": post.is_featured,
        "is_announcement": post.is_announcement,
        "is_liked": is_liked,
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "updated_at": post.updated_at.isoformat() if post.updated_at else None,
    }


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}


@router.post("/{post_id}/like")
def toggle_post_like(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    existing_like = db.query(PostLike).filter(
        PostLike.post_id == post_id,
        PostLike.user_id == current_user.id
    ).first()
    
    if existing_like:
        db.delete(existing_like)
        post.likes_count = max(0, (post.likes_count or 1) - 1)
        db.commit()
        return {"liked": False, "likes_count": post.likes_count}
    else:
        like = PostLike(post_id=post_id, user_id=current_user.id)
        db.add(like)
        post.likes_count = (post.likes_count or 0) + 1
        db.commit()
        return {"liked": True, "likes_count": post.likes_count}


@router.get("/{post_id}/comments", response_model=List[CommentResponse])
def get_comments(
    post_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comments = db.query(Comment).filter(
        Comment.post_id == post_id,
        Comment.parent_id == None
    ).order_by(desc(Comment.created_at)).offset(skip).limit(limit).all()
    
    user_liked_comment_ids = set(
        like.comment_id for like in db.query(CommentLike).filter(CommentLike.user_id == current_user.id).all()
    )
    
    def format_comment(comment):
        author = db.query(User).filter(User.id == comment.author_id).first()
        replies = db.query(Comment).filter(Comment.parent_id == comment.id).order_by(Comment.created_at).all()
        
        return {
            "id": comment.id,
            "post_id": comment.post_id,
            "author_id": comment.author_id,
            "author_name": author.name if author else "Unknown",
            "author_image": author.profile_image if author else None,
            "parent_id": comment.parent_id,
            "content": comment.content,
            "image_url": comment.image_url,
            "likes_count": comment.likes_count or 0,
            "replies_count": comment.replies_count or 0,
            "is_liked": comment.id in user_liked_comment_ids,
            "created_at": comment.created_at.isoformat() if comment.created_at else None,
            "updated_at": comment.updated_at.isoformat() if comment.updated_at else None,
            "replies": [format_comment(reply) for reply in replies]
        }
    
    return [format_comment(c) for c in comments]


@router.post("/{post_id}/comments", response_model=CommentResponse)
def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comment = Comment(
        post_id=post_id,
        author_id=current_user.id,
        parent_id=comment_data.parent_id,
        content=comment_data.content,
        image_url=comment_data.image_url
    )
    db.add(comment)
    
    post.comments_count = (post.comments_count or 0) + 1
    
    if comment_data.parent_id:
        parent_comment = db.query(Comment).filter(Comment.id == comment_data.parent_id).first()
        if parent_comment:
            parent_comment.replies_count = (parent_comment.replies_count or 0) + 1
    
    db.commit()
    db.refresh(comment)
    
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "author_id": comment.author_id,
        "author_name": current_user.name,
        "author_image": current_user.profile_image,
        "parent_id": comment.parent_id,
        "content": comment.content,
        "likes_count": 0,
        "replies_count": 0,
        "is_liked": False,
        "created_at": comment.created_at.isoformat(),
        "updated_at": None,
        "replies": []
    }


@router.delete("/{post_id}/comments/{comment_id}")
def delete_comment(
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.post_id == post_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        post.comments_count = max(0, (post.comments_count or 1) - 1)
    
    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted successfully"}


@router.post("/{post_id}/comments/{comment_id}/like")
def toggle_comment_like(
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.post_id == post_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    existing_like = db.query(CommentLike).filter(
        CommentLike.comment_id == comment_id,
        CommentLike.user_id == current_user.id
    ).first()
    
    if existing_like:
        db.delete(existing_like)
        comment.likes_count = max(0, (comment.likes_count or 1) - 1)
        db.commit()
        return {"liked": False, "likes_count": comment.likes_count}
    else:
        like = CommentLike(comment_id=comment_id, user_id=current_user.id)
        db.add(like)
        comment.likes_count = (comment.likes_count or 0) + 1
        db.commit()
        return {"liked": True, "likes_count": comment.likes_count}
