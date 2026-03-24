import { useState, useEffect, useCallback, useRef } from 'react';
import PropTypes from 'prop-types';
import { Volume2, VolumeX, Pause, Play } from 'lucide-react';

const VoiceSummary = ({
  text,
  autoPlay = false,
  onEnd,
  onError
}) => {
  const language = 'en-US';
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isSupported, setIsSupported] = useState(true);
  const [isSpeaking, setIsSpeaking] = useState(false);
  
  const utteranceRef = useRef(null);
  const progressIntervalRef = useRef(null);

  const checkSupport = useCallback(() => {
    return typeof window !== 'undefined' && 'speechSynthesis' in window;
  }, []);

  const getEstimatedDuration = useCallback((textContent) => {
    const wordsPerMinute = language.startsWith('en') ? 150 : 120;
    const words = textContent.trim().split(/\s+/).length;
    return (words / wordsPerMinute) * 60 * 1000;
  }, [language]);

  const clearProgressInterval = useCallback(() => {
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
      progressIntervalRef.current = null;
    }
  }, []);

  const stop = useCallback(() => {
    if (checkSupport()) {
      window.speechSynthesis.cancel();
    }
    clearProgressInterval();
    setIsPlaying(false);
    setIsPaused(false);
    setIsSpeaking(false);
    setProgress(0);
  }, [checkSupport, clearProgressInterval]);

  const speak = useCallback(() => {
    if (!checkSupport() || !text) {
      setIsSupported(false);
      return;
    }

    stop();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language;
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;

    const estimatedDuration = getEstimatedDuration(text);
    let startTime = Date.now();

    utterance.onstart = () => {
      setIsSpeaking(true);
      setIsPlaying(true);
      setIsPaused(false);
      startTime = Date.now();

      progressIntervalRef.current = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const newProgress = Math.min((elapsed / estimatedDuration) * 100, 95);
        setProgress(newProgress);
      }, 100);
    };

    utterance.onend = () => {
      clearProgressInterval();
      setProgress(100);
      setIsPlaying(false);
      setIsPaused(false);
      setIsSpeaking(false);
      if (onEnd) onEnd();
    };

    utterance.onerror = (event) => {
      clearProgressInterval();
      setIsPlaying(false);
      setIsPaused(false);
      setIsSpeaking(false);
      if (onError) onError(event.error);
    };

    utterance.onpause = () => {
      setIsPaused(true);
    };

    utterance.onresume = () => {
      setIsPaused(false);
    };

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  }, [text, language, checkSupport, stop, clearProgressInterval, getEstimatedDuration, onEnd, onError]);

  const pause = useCallback(() => {
    if (checkSupport() && window.speechSynthesis.speaking) {
      window.speechSynthesis.pause();
      setIsPaused(true);
      clearProgressInterval();
    }
  }, [checkSupport, clearProgressInterval]);

  const resume = useCallback(() => {
    if (checkSupport() && window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
      setIsPaused(false);
    }
  }, [checkSupport]);

  const togglePlayPause = useCallback(() => {
    if (isSpeaking && !isPaused) {
      pause();
    } else if (isPaused) {
      resume();
    } else {
      speak();
    }
  }, [isSpeaking, isPaused, pause, resume, speak]);

  useEffect(() => {
    setIsSupported(checkSupport());
  }, [checkSupport]);

  useEffect(() => {
    if (autoPlay && text && isSupported) {
      const timer = setTimeout(() => {
        speak();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [autoPlay, text, isSupported, speak]);

  useEffect(() => {
    return () => {
      stop();
    };
  }, [stop]);

  useEffect(() => {
    const handleBeforeUnload = () => {
      if (checkSupport()) {
        window.speechSynthesis.cancel();
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [checkSupport]);

  if (!isSupported) {
    return (
      <div className="flex items-center gap-2 p-3 bg-gray-100 rounded-xl text-gray-500 text-sm">
        <VolumeX size={20} />
        <span>Voice not supported in this browser</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 p-4 bg-white rounded-2xl border border-gray-200 shadow-sm">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={togglePlayPause}
          aria-label={isSpeaking && !isPaused ? 'Pause' : 'Play'}
          className={`
            min-w-[56px] min-h-[56px] w-14 h-14
            flex items-center justify-center
            rounded-full
            transition-all duration-200
            focus:outline-none focus:ring-4 focus:ring-offset-2
            ${isSpeaking && !isPaused
              ? 'bg-[#138808] hover:bg-[#0e6e06] focus:ring-[#138808]/30 text-white shadow-lg shadow-[#138808]/30'
              : 'bg-[#FF9933] hover:bg-[#e68a2e] focus:ring-[#FF9933]/30 text-white shadow-lg shadow-[#FF9933]/30'
            }
            active:scale-95
          `}
        >
          {isSpeaking && !isPaused ? (
            <Pause size={28} strokeWidth={2.5} />
          ) : (
            <Play size={28} strokeWidth={2.5} className="ml-1" />
          )}
        </button>

        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1.5">
            <Volume2 size={16} className="text-gray-500" />
            <span className="text-xs font-medium text-gray-500">
              {isSpeaking && !isPaused ? 'Reading...' : isPaused ? 'Paused' : 'Tap to listen'}
            </span>
          </div>
          
          <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="absolute top-0 left-0 h-full bg-gradient-to-r from-[#FF9933] to-[#138808] rounded-full transition-all duration-100"
              style={{ width: `${progress}%` }}
              role="progressbar"
              aria-valuenow={Math.round(progress)}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label="Reading progress"
            />
          </div>
        </div>

        <button
          type="button"
          onClick={stop}
          aria-label="Stop"
          disabled={!isSpeaking && !isPaused}
          className={`
            min-w-[44px] min-h-[44px] w-11 h-11
            flex items-center justify-center
            rounded-full
            transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-gray-300
            ${isSpeaking || isPaused
              ? 'bg-gray-100 hover:bg-gray-200 text-gray-600'
              : 'bg-gray-50 text-gray-300 cursor-not-allowed'
            }
            active:scale-95
          `}
        >
          <VolumeX size={20} />
        </button>
      </div>
    </div>
  );
};

VoiceSummary.propTypes = {
  text: PropTypes.string.isRequired,
  autoPlay: PropTypes.bool,
  onEnd: PropTypes.func,
  onError: PropTypes.func
};

export default VoiceSummary;
