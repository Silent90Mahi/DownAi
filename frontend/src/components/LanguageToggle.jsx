/* eslint-disable react-refresh/only-export-components */
import { Globe } from 'lucide-react';

const STORAGE_KEY = 'voice_ui_language';

const LanguageToggle = ({
  onChange,
  className = '',
  variant = 'dropdown'
}) => {
  const handleLanguageChange = () => {
    if (onChange) {
      onChange({ code: 'en', name: 'English', native: 'English', flag: '🇬🇧' });
    }
  };

  if (variant === 'toggle') {
    return (
      <div className={`flex items-center gap-1 ${className}`}>
        <button
          className="px-3 py-2 rounded-lg text-sm font-medium bg-[#000080] text-white"
          aria-label="Language: English"
        >
          <span className="mr-1">🇬🇧</span>
          <span className="hidden sm:inline">English</span>
        </button>
      </div>
    );
  }

  return (
    <div className={`relative inline-block ${className}`}>
      <button
        onClick={handleLanguageChange}
        className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 rounded-xl hover:border-slate-300 transition-all shadow-sm cursor-default"
        aria-label="Language: English"
      >
        <Globe size={18} className="text-slate-500" />
        <span className="text-sm font-medium text-slate-700">
          🇬🇧 English
        </span>
      </button>
    </div>
  );
};

export const useLanguage = () => {
  const language = { code: 'en', name: 'English', native: 'English', flag: '🇬🇧' };

  const changeLanguage = () => {
    localStorage.setItem(STORAGE_KEY, 'en');
  };

  return { language, changeLanguage, languages: [language] };
};

export default LanguageToggle;
