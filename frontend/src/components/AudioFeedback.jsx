/* eslint-disable react-refresh/only-export-components */
import { useCallback, useRef, useEffect } from 'react';

const SOUND_PATTERNS = {
  success: {
    frequencies: [523.25, 659.25, 783.99],
    durations: [0.1, 0.1, 0.15],
    gains: [0.3, 0.3, 0.2]
  },
  error: {
    frequencies: [200, 150],
    durations: [0.15, 0.2],
    gains: [0.3, 0.25]
  },
  notification: {
    frequencies: [440, 554.37],
    durations: [0.08, 0.12],
    gains: [0.2, 0.2]
  },
  click: {
    frequencies: [800],
    durations: [0.05],
    gains: [0.15]
  }
};

const AudioFeedback = ({
  type = 'click',
  enabled = true,
  volume = 0.5,
  onPlay
}) => {
  const audioContextRef = useRef(null);

  const getAudioContext = useCallback(() => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    }
    return audioContextRef.current;
  }, []);

  const playTone = useCallback((frequency, duration, gain) => {
    if (!enabled) return;

    try {
      const audioContext = getAudioContext();

      if (audioContext.state === 'suspended') {
        audioContext.resume();
      }

      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      oscillator.type = 'sine';
      oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);

      const adjustedGain = gain * volume;
      gainNode.gain.setValueAtTime(adjustedGain, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(
        0.001,
        audioContext.currentTime + duration
      );

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + duration);
    } catch (error) {
      console.error('Audio playback error:', error);
    }
  }, [enabled, volume, getAudioContext]);

  const play = useCallback(() => {
    if (!enabled) return;

    const pattern = SOUND_PATTERNS[type];
    if (!pattern) return;

    let delay = 0;
    pattern.frequencies.forEach((freq, index) => {
      setTimeout(() => {
        playTone(freq, pattern.durations[index], pattern.gains[index]);
      }, delay * 1000);
      delay += pattern.durations[index];
    });

    if (onPlay) {
      onPlay(type);
    }
  }, [enabled, type, playTone, onPlay]);

  useEffect(() => {
    play();
  }, [type, play]);

  useEffect(() => {
    return () => {
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  return null;
};

export const useAudioFeedback = (enabled = true, volume = 0.5) => {
  const audioContextRef = useRef(null);

  const getAudioContext = useCallback(() => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    }
    return audioContextRef.current;
  }, []);

  const playSound = useCallback((type) => {
    if (!enabled) return;

    const pattern = SOUND_PATTERNS[type];
    if (!pattern) return;

    try {
      const audioContext = getAudioContext();

      if (audioContext.state === 'suspended') {
        audioContext.resume();
      }

      let delay = 0;
      pattern.frequencies.forEach((freq, index) => {
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(freq, audioContext.currentTime + delay);

        const adjustedGain = pattern.gains[index] * volume;
        gainNode.gain.setValueAtTime(adjustedGain, audioContext.currentTime + delay);
        gainNode.gain.exponentialRampToValueAtTime(
          0.001,
          audioContext.currentTime + delay + pattern.durations[index]
        );

        oscillator.start(audioContext.currentTime + delay);
        oscillator.stop(audioContext.currentTime + delay + pattern.durations[index]);

        delay += pattern.durations[index];
      });
    } catch (error) {
      console.error('Audio playback error:', error);
    }
  }, [enabled, volume, getAudioContext]);

  useEffect(() => {
    return () => {
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  return { playSound };
};

export default AudioFeedback;
