import { useState, useRef, useEffect, useCallback } from 'react';
import { Mic, MicOff, X, Check } from 'lucide-react';

const VoiceInputOverlay = ({
  isOpen,
  onClose,
  onConfirm,
  placeholder = 'Speak now...'
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState(null);
  const [audioLevel, setAudioLevel] = useState(0);
  const [hasAudioData, setHasAudioData] = useState(false);
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const streamRef = useRef(null);
  const audioChunksRef = useRef([]);
  const prevIsOpenRef = useRef(false);

  const drawWaveform = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !analyserRef.current) return;

    const ctx = canvas.getContext('2d');
    const analyser = analyserRef.current;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      if (!isRecording) return;

      animationRef.current = requestAnimationFrame(draw);
      analyser.getByteTimeDomainData(dataArray);

      const maxLevel = Math.max(...dataArray);
      const minLevel = Math.min(...dataArray);
      const level = (maxLevel - minLevel) / 255;
      setAudioLevel(level);

      ctx.fillStyle = 'rgba(0, 0, 128, 0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.lineWidth = 3;
      ctx.strokeStyle = '#FF9933';
      ctx.beginPath();

      const sliceWidth = canvas.width / bufferLength;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = (v * canvas.height) / 2;

        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }

        x += sliceWidth;
      }

      ctx.lineTo(canvas.width, canvas.height / 2);
      ctx.stroke();
    };

    draw();
  }, [isRecording]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }

      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }

      if (audioContextRef.current) {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }
    }
  }, [isRecording]);

  const startRecording = useCallback(async () => {
    setHasAudioData(false);
    audioChunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      analyserRef.current.fftSize = 2048;

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4'
      });

      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          setHasAudioData(true);
        }
      };

      mediaRecorder.start(100);
      setIsRecording(true);
    } catch (err) {
      console.error('Microphone access error:', err);
      setError(err.message || 'Microphone access denied');
    }
  }, []);

  useEffect(() => {
    const wasOpen = prevIsOpenRef.current;
    prevIsOpenRef.current = isOpen;

    if (isOpen && !wasOpen) {
      setTranscript('');
      setError(null);
      setAudioLevel(0);
      startRecording();
    } else if (!isOpen && wasOpen) {
      stopRecording();
    }
  }, [isOpen, startRecording, stopRecording]);

  useEffect(() => {
    if (isRecording) {
      drawWaveform();
    }
  }, [isRecording, drawWaveform]);

  useEffect(() => {
    return () => {
      stopRecording();
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [stopRecording]);

  const handleConfirm = () => {
    if (onConfirm && (transcript || audioChunksRef.current.length > 0)) {
      const audioBlob = audioChunksRef.current.length > 0
        ? new Blob(audioChunksRef.current, { type: 'audio/webm' })
        : null;

      onConfirm({
        transcript,
        audioBlob,
        language: 'English'
      });
    }
    onClose();
  };

  const handleCancel = () => {
    stopRecording();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={handleCancel}
      />

      <div className="relative bg-white rounded-3xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
        <div className="bg-gradient-to-r from-[#000080] to-[#00004d] text-white p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`p-3 rounded-full ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-white/20'}`}>
                {error ? <MicOff size={24} /> : <Mic size={24} />}
              </div>
              <div>
                <h2 className="text-lg font-bold">Voice Input</h2>
                <p className="text-sm text-blue-200">
                  {isRecording ? 'Listening...' : error ? 'Microphone error' : 'Preparing...'}
                </p>
              </div>
            </div>
            <button
              onClick={handleCancel}
              className="p-2 hover:bg-white/20 rounded-full transition-colors"
              aria-label="Close"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        <div className="p-6">
          <div className="relative mb-6">
            <canvas
              ref={canvasRef}
              width={400}
              height={150}
              className="w-full h-36 rounded-xl bg-slate-900"
            />

            {isRecording && (
              <div
                className="absolute inset-0 rounded-xl border-4 border-orange-400 pointer-events-none transition-all"
                style={{
                  opacity: 0.3 + audioLevel * 0.7,
                  transform: `scale(${1 + audioLevel * 0.05})`
                }}
              />
            )}
          </div>

          <div className="mb-6">
            <div className="bg-slate-50 rounded-xl p-4 min-h-[80px] border border-slate-200">
              {transcript ? (
                <p className="text-slate-800 text-lg">{transcript}</p>
              ) : (
                <p className="text-slate-400 text-lg italic">{placeholder}</p>
              )}
            </div>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          <div className="flex gap-3">
            <button
              onClick={handleCancel}
              className="flex-1 flex items-center justify-center gap-2 py-3 px-4 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-medium transition-colors"
            >
              <X size={20} />
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              disabled={!transcript && !hasAudioData}
              className="flex-1 flex items-center justify-center gap-2 py-3 px-4 bg-gradient-to-r from-[#138808] to-[#0e6e06] hover:from-[#0e6e06] hover:to-[#0a5205] text-white rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Check size={20} />
              Confirm
            </button>
          </div>

          <div className="mt-4 text-center">
            <span className="text-xs text-slate-400">
              Language: English
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceInputOverlay;
