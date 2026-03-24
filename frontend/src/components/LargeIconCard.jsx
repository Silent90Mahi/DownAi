import { useState } from 'react';
import PropTypes from 'prop-types';

const colorThemes = {
  orange: {
    bg: 'bg-[#FF9933]/10',
    bgHover: 'hover:bg-[#FF9933]/20',
    bgActive: 'active:bg-[#FF9933]/30',
    icon: 'text-[#FF9933]',
    border: 'border-[#FF9933]/20',
    borderHover: 'hover:border-[#FF9933]/40'
  },
  green: {
    bg: 'bg-[#138808]/10',
    bgHover: 'hover:bg-[#138808]/20',
    bgActive: 'active:bg-[#138808]/30',
    icon: 'text-[#138808]',
    border: 'border-[#138808]/20',
    borderHover: 'hover:border-[#138808]/40'
  },
  blue: {
    bg: 'bg-[#3b82f6]/10',
    bgHover: 'hover:bg-[#3b82f6]/20',
    bgActive: 'active:bg-[#3b82f6]/30',
    icon: 'text-[#3b82f6]',
    border: 'border-[#3b82f6]/20',
    borderHover: 'hover:border-[#3b82f6]/40'
  },
  gray: {
    bg: 'bg-gray-100',
    bgHover: 'hover:bg-gray-200',
    bgActive: 'active:bg-gray-300',
    icon: 'text-gray-600',
    border: 'border-gray-200',
    borderHover: 'hover:border-gray-300'
  }
};

const LargeIconCard = ({
  icon: Icon,
  label,
  onClick,
  badge,
  color = 'orange',
  disabled = false,
  className = ''
}) => {
  const [isPressed, setIsPressed] = useState(false);
  const theme = colorThemes[color] || colorThemes.orange;

  const handlePointerDown = () => {
    if (!disabled) setIsPressed(true);
  };

  const handlePointerUp = () => {
    setIsPressed(false);
  };

  const handlePointerLeave = () => {
    setIsPressed(false);
  };

  return (
    <button
      type="button"
      onClick={onClick}
      onPointerDown={handlePointerDown}
      onPointerUp={handlePointerUp}
      onPointerLeave={handlePointerLeave}
      disabled={disabled}
      aria-label={label || 'Action button'}
      className={`
        relative
        min-w-[80px] min-h-[80px] w-20 h-20
        flex flex-col items-center justify-center
        rounded-2xl
        border-2
        transition-all duration-150 ease-out
        focus:outline-none focus:ring-4 focus:ring-offset-2
        ${theme.bg} ${theme.bgHover} ${theme.bgActive} ${theme.border} ${theme.borderHover}
        ${isPressed ? 'scale-95 shadow-inner' : 'shadow-[0_4px_12px_rgba(0,0,0,0.08)] hover:shadow-[0_8px_20px_rgba(0,0,0,0.12)]'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${color === 'orange' ? 'focus:ring-[#FF9933]/30' : color === 'green' ? 'focus:ring-[#138808]/30' : 'focus:ring-blue-300'}
        ${className}
      `}
    >
      <div className={`${theme.icon} ${isPressed ? 'scale-90' : ''} transition-transform`}>
        {Icon && <Icon size={32} strokeWidth={2} />}
      </div>
      
      {label && (
        <span className="mt-1 text-xs font-semibold text-gray-700 text-center leading-tight max-w-full px-1 truncate">
          {label}
        </span>
      )}
      
      {badge !== undefined && badge !== null && (
        <span
          aria-label={`${badge} notifications`}
          className="absolute -top-1 -right-1 min-w-[22px] h-[22px] flex items-center justify-center bg-red-500 text-white text-xs font-bold rounded-full px-1.5 shadow-md"
        >
          {badge > 99 ? '99+' : badge}
        </span>
      )}
    </button>
  );
};

LargeIconCard.propTypes = {
  icon: PropTypes.elementType.isRequired,
  label: PropTypes.string,
  onClick: PropTypes.func,
  badge: PropTypes.number,
  color: PropTypes.oneOf(['orange', 'green', 'blue', 'gray']),
  disabled: PropTypes.bool,
  className: PropTypes.string
};

export default LargeIconCard;
