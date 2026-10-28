import React, { useRef, useState, useEffect } from 'react';
import { Camera, X, RefreshCw, AlertCircle } from 'lucide-react';
import { Button } from '../ui/Button';

interface CameraCaptureProps {
  onCapture: (file: File) => void;
  onClose: () => void;
}

export const CameraCapture: React.FC<CameraCaptureProps> = ({ onCapture, onClose }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let activeStream: MediaStream | null = null;
    async function startCamera() {
      try {
        const s = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } },
        });
        activeStream = s;
        setStream(s);
        if (videoRef.current) {
          videoRef.current.srcObject = s;
        }
      } catch (err) {
        setError('Could not access camera. Please allow camera permissions in your browser.');
      }
    }
    startCamera();

    return () => {
      if (activeStream) {
        activeStream.getTracks().forEach((t) => t.stop());
      }
    };
  }, []);

  const takeSnapshot = () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (!blob) return;
      const file = new File([blob], `camera-${Date.now()}.jpg`, { type: 'image/jpeg' });
      onCapture(file);
      onClose();
    }, 'image/jpeg', 0.92);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="relative bg-gray-900 rounded-3xl overflow-hidden max-w-xl w-full border border-gray-800 shadow-2xl">
        <div className="p-4 flex items-center justify-between border-b border-gray-800 text-white">
          <div className="flex items-center gap-2">
            <Camera className="w-5 h-5 text-primary-400" />
            <span className="font-semibold text-sm">Capture Plant Photo</span>
          </div>
          <button onClick={onClose} className="p-1 rounded-full text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="relative aspect-4/3 bg-black flex items-center justify-center">
          {error ? (
            <div className="p-6 text-center text-red-400 max-w-sm">
              <AlertCircle className="w-8 h-8 mx-auto mb-2" />
              <p className="text-sm">{error}</p>
            </div>
          ) : (
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />
          )}
        </div>

        <div className="p-5 flex items-center justify-center gap-4 bg-gray-950">
          <Button variant="ghost" size="sm" onClick={onClose} className="text-gray-300">
            Cancel
          </Button>
          {!error && (
            <button
              onClick={takeSnapshot}
              className="w-14 h-14 rounded-full border-4 border-white flex items-center justify-center bg-primary-600 hover:bg-primary-500 transition-all shadow-lg active:scale-95"
              title="Take Photo"
            >
              <div className="w-10 h-10 rounded-full bg-white" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
