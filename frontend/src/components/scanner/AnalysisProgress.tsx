import React from 'react';
import { CheckCircle2, CircleDashed, Loader2 } from 'lucide-react';

interface Stage {
  id: number;
  label: string;
  description: string;
}

interface AnalysisProgressProps {
  currentStage?: number; // 1 to 4
}

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({ currentStage = 2 }) => {
  const stages: Stage[] = [
    { id: 1, label: 'Image Preprocessing', description: 'Checking dimensions, EXIF tags, and RGB normalization' },
    { id: 2, label: 'Plant Identification', description: 'Evaluating species morphology via Vision Transformer' },
    { id: 3, label: 'Disease Diagnosis', description: 'Screening leaf tissue against 38 plant pathogen classes' },
    { id: 4, label: 'Agronomic Guidance', description: 'Formulating evidence-based care and prevention steps' },
  ];

  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-soft max-w-lg mx-auto">
      <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-100">
        <Loader2 className="w-6 h-6 text-primary-700 animate-spin" />
        <div>
          <h4 className="text-base font-semibold text-gray-900">Inference in Progress</h4>
          <p className="text-xs text-gray-500">Executing genuine computer vision pipelines...</p>
        </div>
      </div>

      <div className="space-y-4">
        {stages.map((stage) => {
          const isCompleted = currentStage > stage.id;
          const isCurrent = currentStage === stage.id;

          return (
            <div key={stage.id} className="flex items-start gap-3">
              <div className="mt-0.5">
                {isCompleted ? (
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                ) : isCurrent ? (
                  <Loader2 className="w-5 h-5 text-primary-700 animate-spin" />
                ) : (
                  <CircleDashed className="w-5 h-5 text-gray-300" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span
                    className={`text-sm font-medium ${
                      isCurrent
                        ? 'text-primary-950 font-semibold'
                        : isCompleted
                        ? 'text-gray-800'
                        : 'text-gray-400'
                    }`}
                  >
                    {stage.label}
                  </span>
                  {isCurrent && (
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-primary-700 bg-primary-50 px-2 py-0.5 rounded-full">
                      Running
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-400 mt-0.5">{stage.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
