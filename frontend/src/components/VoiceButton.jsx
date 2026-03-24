import { useState, useRef, useCallback } from 'react';
import { Mic, MicOff } from 'lucide-react';

const VoiceButton = ({
  onResult,
  disabled = false,
  className = ''
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);

  const startRecording = useCallback(async () => {
    if (disabled) return;

    setError(null);
    audioChunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4'
      });

      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: mediaRecorder.mimeType
        });

        if (onResult) {
          onResult({
            blob: audioBlob,
            language: 'English',
            mimeType: mediaRecorder.mimeType
          });
        }

        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }
      };

      mediaRecorder.start(100);
      setIsRecording(true);
    } catch (err) {
      console.error('Microphone access error:', err);
      setError(err.message || 'Microphone access denied');
      setIsRecording(false);
    }
  }, [disabled, onResult]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, [isRecording]);

  const toggleRecording = useCallback(() => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [isRecording, startRecording, stopRecording]);

  const baseClasses = `
    relative w-16 h-16 rounded-full flex items-center justify-center
    transition-all duration-300 ease-out focus:outline-none focus:ring-4
    disabled:opacity-50 disabled:cursor-not-allowed
  `;

  const recordingClasses = isRecording
    ? 'bg-red-500 hover:bg-red-600 focus:ring-red-300'
    : 'bg-gradient-to-r from-[#000080] to-[#00004d] hover:from-[#000066] hover:to-[#000040] focus:ring-blue-300';

  return (
    <div className="relative inline-flex">
      <button
        onClick={toggleRecording}
        disabled={disabled}
        aria-label={isRecording ? 'Stop recording' : 'Start voice recording'}
        className={`${baseClasses} ${recordingClasses} ${className}`}
      >
        {isRecording && (
          <span className="absolute inset-0 rounded-full bg-red-400 animate-ping opacity-75" />
        )}

        <span className="relative z-10 text-white">
          {error ? (
            <MicOff size={28} />
          ) : isRecording ? (
            <Mic size={28} className="animate-pulse" />
          ) : (
            <Mic size={28} />
          )}
        </span>
      </button>

      {isRecording && (
        <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
          <span className="flex items-center gap-1.5 text-xs font-medium text-red-600">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            Recording...
          </span>
        </div>
      )}

      {error && !isRecording && (
        <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
          <span className="text-xs font-medium text-red-600">
            Mic access denied
          </span>
        </div>
      )}
    </div>
  );
};

export default VoiceButton;
