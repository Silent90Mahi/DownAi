import PropTypes from 'prop-types';
import { useState } from 'react';
import { Plus } from 'lucide-react';

const SimplifiedCard = ({
  image,
  title,
  price,
  onClick,
  onAddToCart,
  buttonText = 'Add',
  currency = '₹',
  className = ''
}) => {
  const [isPressed, setIsPressed] = useState(false);
  const [imageError, setImageError] = useState(false);

  const handlePointerDown = () => setIsPressed(true);
  const handlePointerUp = () => setIsPressed(false);
  const handlePointerLeave = () => setIsPressed(false);

  const handleImageError = () => {
    setImageError(true);
  };

  const handleCardClick = () => {
    if (onClick) onClick();
  };

  const handleAddToCart = (e) => {
    e.stopPropagation();
    if (onAddToCart) onAddToCart();
  };

  const formatPrice = (value) => {
    if (typeof value === 'number') {
      return value.toLocaleString('en-IN');
    }
    return value;
  };

  return (
    <article
      role="button"
      tabIndex={0}
      onClick={handleCardClick}
      onKeyPress={(e) => e.key === 'Enter' && handleCardClick()}
      onPointerDown={handlePointerDown}
      onPointerUp={handlePointerUp}
      onPointerLeave={handlePointerLeave}
      aria-label={`${title}, ${currency}${price}`}
      className={`
        relative
        flex flex-col
        bg-white
        rounded-2xl
        border border-gray-100
        overflow-hidden
        transition-all duration-200 ease-out
        focus:outline-none focus:ring-4 focus:ring-[#FF9933]/30 focus:ring-offset-2
        ${isPressed ? 'scale-[0.98] shadow-inner' : 'shadow-[0_4px_16px_rgba(0,0,0,0.06)] hover:shadow-[0_8px_24px_rgba(0,0,0,0.1)]'}
        ${className}
      `}
    >
      <div className="relative aspect-square w-full bg-gray-50 overflow-hidden">
        {!imageError && image ? (
          <img
            src={image}
            alt={title}
            onError={handleImageError}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200">
            <span className="text-4xl text-gray-300">📦</span>
          </div>
        )}
      </div>

      <div className="flex flex-col flex-1 p-3 gap-2">
        <h3 className="text-base font-semibold text-gray-800 leading-tight line-clamp-2">
          {title}
        </h3>

        <div className="flex items-baseline gap-1">
          <span className="text-xl font-bold text-[#138808]">{currency}</span>
          <span className="text-2xl font-bold text-[#138808]">
            {formatPrice(price)}
          </span>
        </div>

        <button
          type="button"
          onClick={handleAddToCart}
          aria-label={`Add ${title} to cart`}
          className={`
            mt-auto
            min-h-[52px]
            w-full
            flex items-center justify-center gap-2
            bg-[#FF9933] hover:bg-[#e68a2e]
            text-white
            text-lg font-bold
            rounded-xl
            transition-all duration-150
            focus:outline-none focus:ring-2 focus:ring-[#FF9933]/50 focus:ring-offset-2
            active:scale-[0.97] active:bg-[#cc7a29]
            shadow-md shadow-[#FF9933]/20
          `}
        >
          <Plus size={24} strokeWidth={3} />
          <span>{buttonText}</span>
        </button>
      </div>
    </article>
  );
};

SimplifiedCard.propTypes = {
  image: PropTypes.string,
  title: PropTypes.string.isRequired,
  price: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
  onClick: PropTypes.func,
  onAddToCart: PropTypes.func,
  buttonText: PropTypes.string,
  currency: PropTypes.string,
  className: PropTypes.string
};

export default SimplifiedCard;
