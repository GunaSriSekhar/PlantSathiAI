import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Camera,
  AlertCircle,
  HelpCircle,
  Leaf,
  Stethoscope,
  Layers,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { ImageUploader } from '../components/scanner/ImageUploader';
import { CameraCapture } from '../components/scanner/CameraCapture';
import { AnalysisProgress } from '../components/scanner/AnalysisProgress';
import { useImageUpload } from '../hooks/useImageUpload';
import { useAnalysis } from '../hooks/useAnalysis';

export const Scanner: React.FC = () => {
  const navigate = useNavigate();
  const { selectedFile, previewUrl, selectFile, clearFile } = useImageUpload();
  const { loading, stage, error, runAnalysis } = useAnalysis();

  const [mode, setMode] = useState<'full' | 'identify' | 'diagnose'>('full');
  const [showCamera, setShowCamera] = useState(false);

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    try {
      const data = await runAnalysis(selectedFile, true);
      if (data && data.scan_id) {
        navigate(`/results/${data.scan_id}`, { state: { result: data, previewUrl } });
      }
    } catch (err) {
      // Handled in useAnalysis hook
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Page Title */}
      <div className="text-center space-y-2">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 tracking-tight">Plant & Leaf Scanner</h1>
        <p className="text-sm text-gray-500 max-w-lg mx-auto">
          Capture or upload an image to run plant identification and leaf disease screening.
        </p>
      </div>

      {/* Mode Selector Tabs */}
      <div className="flex items-center justify-center">
        <div className="bg-gray-100 p-1 rounded-xl flex gap-1 border border-gray-200 text-xs sm:text-sm font-medium">
          <button
            onClick={() => setMode('full')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg transition-all ${
              mode === 'full'
                ? 'bg-white text-primary-950 font-semibold shadow-xs'
                : 'text-gray-500 hover:text-gray-900'
            }`}
          >
            <Layers className="w-4 h-4 text-primary-700" />
            <span>Full Analysis</span>
          </button>
          <button
            onClick={() => setMode('identify')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg transition-all ${
              mode === 'identify'
                ? 'bg-white text-primary-950 font-semibold shadow-xs'
                : 'text-gray-500 hover:text-gray-900'
            }`}
          >
            <Leaf className="w-4 h-4 text-green-600" />
            <span>Species Only</span>
          </button>
          <button
            onClick={() => setMode('diagnose')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg transition-all ${
              mode === 'diagnose'
                ? 'bg-white text-primary-950 font-semibold shadow-xs'
                : 'text-gray-500 hover:text-gray-900'
            }`}
          >
            <Stethoscope className="w-4 h-4 text-amber-600" />
            <span>Disease Only</span>
          </button>
        </div>
      </div>

      {/* Main Scanner Card */}
      <Card>
        <CardContent className="space-y-6 pt-4">
          {loading ? (
            <div className="py-8">
              <AnalysisProgress currentStage={stage} />
            </div>
          ) : (
            <>
              <ImageUploader
                selectedFile={selectedFile}
                previewUrl={previewUrl}
                onImageSelected={selectFile}
                onClear={clearFile}
                onOpenCamera={() => setShowCamera(true)}
                disabled={loading}
              />

              {error && (
                <div className="flex items-start gap-2.5 p-4 text-sm text-red-800 bg-red-50 border border-red-200 rounded-xl">
                  <AlertCircle className="w-5 h-5 flex-shrink-0 text-red-600 mt-0.5" />
                  <div className="flex-1">
                    <p className="font-semibold text-red-900">Analysis Could Not Complete</p>
                    <p className="text-xs text-red-700 mt-0.5">{error}</p>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 border-t border-gray-100">
                <div className="text-xs text-gray-400">
                  {selectedFile ? 'Ready to analyze with local ML models' : 'Select a leaf or plant image to proceed'}
                </div>
                <div className="flex items-center gap-3 w-full sm:w-auto">
                  {selectedFile && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={clearFile}
                      disabled={loading}
                    >
                      Clear
                    </Button>
                  )}
                  <Button
                    variant="primary"
                    size="md"
                    className="w-full sm:w-auto"
                    disabled={!selectedFile || loading}
                    loading={loading}
                    icon={<Sparkles className="w-4 h-4" />}
                    onClick={handleAnalyze}
                  >
                    Analyze Photo
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Photography Tips Card */}
      <Card className="bg-primary-50/40 border-primary-100">
        <div className="flex items-start gap-3">
          <HelpCircle className="w-5 h-5 text-primary-700 flex-shrink-0 mt-0.5" />
          <div className="space-y-1 text-xs text-primary-900">
            <h5 className="font-semibold text-sm">Best Practices for Reliable Inference</h5>
            <ul className="list-disc list-inside space-y-1 text-primary-800/90 pl-1">
              <li>Capture the affected leaf in sharp focus with good natural lighting.</li>
              <li>Avoid extreme shadows, flash glare, or highly blurred backgrounds.</li>
              <li>For disease diagnosis, frame the lesion or discoloration clearly in the center.</li>
              <li>Unsupported plant species will be reported conservatively rather than forced.</li>
            </ul>
          </div>
        </div>
      </Card>

      {/* Camera Capture Modal */}
      {showCamera && (
        <CameraCapture
          onCapture={selectFile}
          onClose={() => setShowCamera(false)}
        />
      )}
    </div>
  );
};
