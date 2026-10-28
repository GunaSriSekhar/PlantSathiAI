import React, { useEffect, useState } from 'react';
import { useParams, useLocation, Link, useNavigate } from 'react-router-dom';
import {
  Leaf,
  Stethoscope,
  Bot,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  ArrowLeft,
  Sparkles,
  Info,
  Layers,
  Clock,
  Cpu,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Alert } from '../components/ui/Alert';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { getScan } from '../services/api';
import { AnalysisResult as IAnalysisResult } from '../types';

export const AnalysisResult: React.FC = () => {
  const { scanId } = useParams<{ scanId: string }>();
  const location = useLocation();
  const navigate = useNavigate();

  const [result, setResult] = useState<IAnalysisResult | null>(
    location.state?.result || null
  );
  const [previewUrl] = useState<string | null>(location.state?.previewUrl || null);
  const [loading, setLoading] = useState(!result);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!result && scanId) {
      setLoading(true);
      getScan(scanId)
        .then((detail) => {
          setResult({
            scan_id: detail.id,
            created_at: detail.created_at,
            plant: {
              common_name: detail.plant_common_name,
              scientific_name: detail.plant_scientific_name,
              confidence: detail.plant_confidence,
              confidence_level: detail.plant_confidence_level || 'unknown',
              reliable: Boolean(detail.plant_confidence && detail.plant_confidence >= 0.15),
              supported: detail.plant_supported,
              candidates: detail.plant_top_candidates || [],
            },
            disease: {
              status: detail.disease_status,
              label: detail.disease_label,
              crop: detail.disease_crop,
              disease_name: detail.disease_name,
              is_healthy: detail.disease_is_healthy,
              confidence: detail.disease_confidence,
              confidence_level: detail.disease_confidence_level || 'unknown',
              supported: detail.disease_supported,
            },
            recommendations: detail.recommendations || [],
            warnings: detail.warnings || [],
            models: {
              identification: detail.plant_model,
              diagnosis: detail.disease_model,
            },
            analysis_duration_ms: detail.analysis_duration_ms,
            image_filename: detail.image_filename,
          });
        })
        .catch((err) => {
          setError('Could not retrieve scan details from database.');
        })
        .finally(() => setLoading(false));
    }
  }, [scanId, result]);

  if (loading) {
    return (
      <div className="py-20 text-center">
        <LoadingSpinner text="Loading analysis results..." size="lg" />
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="max-w-xl mx-auto py-12 text-center space-y-4">
        <Alert variant="error" title="Record Not Found">
          {error || 'The requested scan record could not be found.'}
        </Alert>
        <Link to="/scanner">
          <Button variant="outline" size="sm" icon={<ArrowLeft className="w-4 h-4" />}>
            Back to Scanner
          </Button>
        </Link>
      </div>
    );
  }

  const { plant, disease, recommendations, warnings, models } = result;

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      {/* Top Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/scanner')}
          className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-900 font-medium"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Scan another plant</span>
        </button>
        <div className="flex items-center gap-2">
          <Link to={`/doctor?scan_id=${result.scan_id}`}>
            <Button size="sm" variant="outline" icon={<Bot className="w-4 h-4 text-primary-700" />}>
              Consult AI Doctor
            </Button>
          </Link>
        </div>
      </div>

      {/* Main Verdict Card */}
      <Card className="overflow-hidden p-0 border border-gray-100 shadow-medium">
        <div className="grid grid-cols-1 md:grid-cols-3">
          {/* Image Display */}
          <div className="bg-gray-100 md:col-span-1 min-h-[220px] flex items-center justify-center relative overflow-hidden border-b md:border-b-0 md:border-r border-gray-100">
            {previewUrl ? (
              <img
                src={previewUrl}
                alt="Analyzed plant"
                className="w-full h-full object-cover min-h-[220px]"
              />
            ) : (
              <div className="p-6 text-center text-gray-400">
                <Leaf className="w-12 h-12 mx-auto mb-2 text-primary-300" />
                <span className="text-xs">Image analyzed on server</span>
              </div>
            )}
          </div>

          {/* Core Findings */}
          <div className="p-6 md:col-span-2 space-y-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider block">
                  Identified Species
                </span>
                <h2 className="text-2xl font-bold text-gray-900 tracking-tight mt-0.5">
                  {plant.common_name || 'Plant Species Uncertain'}
                </h2>
                {plant.scientific_name && (
                  <p className="text-xs italic text-gray-500">{plant.scientific_name}</p>
                )}
              </div>
              <Badge
                variant={plant.reliable ? 'success' : 'warning'}
                size="md"
              >
                {plant.confidence ? `${Math.round(plant.confidence * 100)}% Confidence` : 'Uncalibrated'}
              </Badge>
            </div>

            {/* Disease Status Section */}
            <div className="p-4 rounded-xl bg-gray-50 border border-gray-100 space-y-2">
              <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider block">
                Leaf Pathology Diagnosis
              </span>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {disease.is_healthy ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : (
                    <Stethoscope className="w-5 h-5 text-amber-600" />
                  )}
                  <span className="font-semibold text-gray-900">
                    {disease.disease_name || disease.label || 'Condition Not Diagnosed'}
                  </span>
                </div>
                {disease.is_healthy ? (
                  <Badge variant="success" size="sm">Healthy Foliage</Badge>
                ) : (
                  <Badge variant="warning" size="sm">Pathogen Detected</Badge>
                )}
              </div>
              {disease.confidence && (
                <div className="text-xs text-gray-500 flex items-center justify-between pt-1 border-t border-gray-200/50">
                  <span>Model Score: {Math.round(disease.confidence * 100)}%</span>
                  <span className="capitalize text-gray-400">Class: {disease.crop}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* Warnings & Notices */}
      {warnings.length > 0 && (
        <div className="space-y-2">
          {warnings.map((w, idx) => (
            <Alert key={idx} variant="warning" title="Model Advisory">
              {w}
            </Alert>
          ))}
        </div>
      )}

      {/* Top Species Candidates (Multi-class classification transparency) */}
      {plant.candidates && plant.candidates.length > 1 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Layers className="w-4 h-4 text-primary-700" />
              <span>Alternative Species Candidates</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2.5">
              {plant.candidates.map((cand) => (
                <div key={cand.rank} className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400 w-4 font-mono font-bold">#{cand.rank}</span>
                    <span className="font-medium text-gray-800">{cand.label}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-24 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary-600 rounded-full"
                        style={{ width: `${Math.round(cand.score * 100)}%` }}
                      />
                    </div>
                    <span className="font-mono text-gray-500 w-9 text-right">
                      {Math.round(cand.score * 100)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Care Recommendations */}
      {recommendations.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-gray-900 tracking-tight">Evidence-Based Care Protocol</h3>
            <span className="text-xs text-gray-400">{recommendations.length} action items</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {recommendations.map((rec, i) => (
              <Card key={i} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-primary-800 bg-primary-50 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
                    {rec.category}
                  </span>
                  <Badge
                    variant={rec.urgency === 'high' ? 'error' : rec.urgency === 'medium' ? 'warning' : 'neutral'}
                    size="sm"
                  >
                    {rec.urgency} urgency
                  </Badge>
                </div>
                <h4 className="font-semibold text-gray-900 text-sm">{rec.title}</h4>
                <p className="text-xs text-gray-600 leading-relaxed">{rec.description}</p>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Model Attribution Footer */}
      <div className="p-4 rounded-xl bg-gray-50 border border-gray-200/60 text-xs text-gray-500 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-gray-400" />
          <span>
            Identification: <span className="font-mono text-gray-700">{models.identification}</span>
          </span>
          <span className="text-gray-300">•</span>
          <span>
            Diagnosis: <span className="font-mono text-gray-700">{models.diagnosis}</span>
          </span>
        </div>
        {result.analysis_duration_ms && (
          <div className="flex items-center gap-1.5 text-gray-400">
            <Clock className="w-3.5 h-3.5" />
            <span>{result.analysis_duration_ms} ms</span>
          </div>
        )}
      </div>

      {/* Preliminary Warning Disclaimer */}
      <p className="text-[11px] text-gray-400 text-center leading-normal max-w-xl mx-auto">
        Disclaimer: Image-based predictions are preliminary screening assessments. Visual symptoms
        can overlap across fungal infections, viral conditions, and nutritional deficiencies.
        Always consult a qualified local agricultural extension officer for severe infestations.
      </p>
    </div>
  );
};
