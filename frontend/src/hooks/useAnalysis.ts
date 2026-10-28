import { useState } from 'react';
import { AnalysisResult } from '../types';
import { analyzeImage, ApiError } from '../services/api';

export function useAnalysis() {
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState(1);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = async (file: File, save: boolean = true) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setStage(1);

    // Realistic progression timer corresponding to stages
    const timer1 = setTimeout(() => setStage(2), 600);
    const timer2 = setTimeout(() => setStage(3), 1600);
    const timer3 = setTimeout(() => setStage(4), 2600);

    try {
      const data = await analyzeImage(file, save);
      setResult(data);
      return data;
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : 'Analysis failed. Please check backend connection.';
      setError(msg);
      throw err;
    } finally {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      setLoading(false);
    }
  };

  const reset = () => {
    setLoading(false);
    setStage(1);
    setResult(null);
    setError(null);
  };

  return {
    loading,
    stage,
    result,
    error,
    runAnalysis,
    reset,
  };
}
