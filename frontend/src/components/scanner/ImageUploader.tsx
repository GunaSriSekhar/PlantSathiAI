import React, { useRef, useState } from 'react';
import { UploadCloud, Image as ImageIcon, Camera, X, AlertCircle } from 'lucide-react';
import { Button } from '../ui/Button';

interface ImageUploaderProps {
  onImageSelected: (file: File) => void;
  onClear: () => void;
  selectedFile: File | null;
  previewUrl: string | null;
  onOpenCamera?: () => void;
  disabled?: boolean;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  onImageSelected,
  onClear,
  selectedFile,
  previewUrl,
  onOpenCamera,
  disabled = false,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const validateAndHandleFile = (file: File) => {
    setErrorMsg(null);
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setErrorMsg('Invalid format. Please select a JPEG, PNG, or WebP photo.');
      return;
    }
    const maxMb = 10;
    if (file.size > maxMb * 1024 * 1024) {
      setErrorMsg(`Image exceeds ${maxMb}MB limit. Please choose a smaller photo.`);
      return;
    }
    onImageSelected(file);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndHandleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndHandleFile(e.target.files[0]);
    }
  };

  return (
    <div className="w-full">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleChange}
        className="hidden"
        disabled={disabled}
      />

      {errorMsg && (
        <div className="mb-4 flex items-center gap-2 p-3 text-sm text-red-700 bg-red-50 border border-red-200 rounded-xl">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {previewUrl ? (
        <div className="relative rounded-2xl overflow-hidden border border-gray-200 bg-gray-50 max-w-lg mx-auto shadow-sm">
          <img
            src={previewUrl}
            alt="Uploaded leaf or plant"
            className="w-full h-72 object-cover"
          />
          <div className="absolute top-3 right-3 flex items-center gap-2">
            <button
              onClick={onClear}
              disabled={disabled}
              className="p-1.5 rounded-full bg-black/60 text-white hover:bg-black/80 transition-colors shadow-sm"
              title="Remove image"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          {selectedFile && (
            <div className="p-3 bg-white border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
              <span className="truncate max-w-[240px] font-medium text-gray-700">{selectedFile.name}</span>
              <span>{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</span>
            </div>
          )}
        </div>
      ) : (
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center cursor-pointer transition-all ${
            dragActive
              ? 'border-primary-600 bg-primary-50/50 scale-[0.99]'
              : 'border-gray-200 hover:border-primary-400 hover:bg-gray-50/70 bg-white'
          }`}
        >
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-primary-100 text-primary-800 flex items-center justify-center">
            <UploadCloud className="w-8 h-8" />
          </div>

          <h4 className="text-base font-semibold text-gray-900 mb-1">
            Drag & drop your plant or leaf photo here
          </h4>
          <p className="text-sm text-gray-500 max-w-md mx-auto mb-6">
            Supports JPEG, PNG, and WebP up to 10MB. Clear close-ups of leaves or full plants yield the best accuracy.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-3" onClick={(e) => e.stopPropagation()}>
            <Button
              type="button"
              variant="primary"
              size="sm"
              icon={<ImageIcon className="w-4 h-4" />}
              onClick={() => fileInputRef.current?.click()}
            >
              Browse Files
            </Button>
            {onOpenCamera && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                icon={<Camera className="w-4 h-4" />}
                onClick={onOpenCamera}
              >
                Use Camera
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
