import React, { useEffect, useState } from 'react';
import {
  Cpu,
  Activity,
  HardDrive,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Layers,
  Terminal,
  ShieldCheck,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { getModelStatus, getHealth } from '../services/api';
import { ModelStatus } from '../types';

export const Settings: React.FC = () => {
  const [models, setModels] = useState<ModelStatus[]>([]);
  const [health, setHealth] = useState<{ status: string; version: string; environment: string } | null>(null);
  const [loading, setLoading] = useState(true);

  const loadTelemetry = async () => {
    try {
      setLoading(true);
      const [m, h] = await Promise.all([
        getModelStatus().catch(() => []),
        getHealth().catch(() => null),
      ]);
      setModels(m);
      setHealth(h);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTelemetry();
  }, []);

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 tracking-tight flex items-center gap-2">
            <Cpu className="w-6 h-6 text-primary-700" />
            <span>Model Telemetry & System Diagnostics</span>
          </h1>
          <p className="text-xs text-gray-500 mt-0.5">
            Real-time inference pipeline status, compute device metrics, and model provenance.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={loadTelemetry}
          loading={loading}
          icon={<RefreshCw className="w-3.5 h-3.5" />}
        >
          Refresh Telemetry
        </Button>
      </div>

      {loading ? (
        <div className="py-16">
          <LoadingSpinner text="Checking model pipelines..." />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Server Runtime Health */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <Activity className="w-4 h-4 text-green-600" />
                <span>FastAPI Service Health</span>
              </CardTitle>
              {health ? (
                <Badge variant="success" size="sm">Online</Badge>
              ) : (
                <Badge variant="error" size="sm">Disconnected</Badge>
              )}
            </CardHeader>
            <CardContent>
              {health ? (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
                  <div className="p-3 bg-gray-50 rounded-xl">
                    <span className="text-gray-400 block text-[11px]">Status</span>
                    <span className="font-semibold text-gray-800 uppercase">{health.status}</span>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-xl">
                    <span className="text-gray-400 block text-[11px]">API Version</span>
                    <span className="font-mono font-semibold text-gray-800">v{health.version}</span>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-xl">
                    <span className="text-gray-400 block text-[11px]">Environment</span>
                    <span className="font-semibold text-gray-800 capitalize">{health.environment}</span>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-xl">
                    <span className="text-gray-400 block text-[11px]">Database Driver</span>
                    <span className="font-semibold text-gray-800">SQLite + aiosqlite</span>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-red-600">
                  Backend server is unreachable. Ensure the FastAPI application is running on port 8000.
                </p>
              )}
            </CardContent>
          </Card>

          {/* Active Computer Vision Models */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <Layers className="w-4 h-4 text-primary-700" />
                <span>Integrated Computer Vision Pipelines</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {models.length === 0 ? (
                <div className="text-xs text-gray-500 py-4">No models reported by registry.</div>
              ) : (
                models.map((m, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl border border-gray-100 bg-gray-50/70 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-gray-900 text-sm">{m.name}</span>
                        <Badge
                          variant={m.status === 'loaded' ? 'success' : m.status === 'loading' ? 'warning' : 'neutral'}
                          size="sm"
                        >
                          {m.status}
                        </Badge>
                      </div>
                      <p className="text-gray-500 text-[11px]">Task: {m.task}</p>
                    </div>

                    <div className="flex flex-wrap items-center gap-3 text-gray-600">
                      <span className="bg-white px-2.5 py-1 rounded-md border border-gray-200 font-mono">
                        Device: {m.device.toUpperCase()}
                      </span>
                      {m.class_count && (
                        <span className="bg-white px-2.5 py-1 rounded-md border border-gray-200">
                          {m.class_count} classes
                        </span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          {/* Model Accuracy & Validation Integrity */}
          <Card className="bg-primary-50/30 border-primary-100">
            <CardHeader>
              <CardTitle className="text-sm font-semibold flex items-center gap-2 text-primary-950">
                <ShieldCheck className="w-4 h-4 text-primary-700" />
                <span>Evaluation Metrics & Model Transparency</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-xs text-primary-900 leading-relaxed">
              <p>
                In strict adherence to academic standards, PlantSathi AI displays{' '}
                <span className="font-semibold italic">"Evaluation not yet completed"</span> for datasets
                until an explicit, held-out test split is evaluated locally to prevent artificial claims of 99% accuracy.
              </p>
              <div className="p-3 bg-white rounded-xl border border-primary-200/60 font-mono text-[11px] text-gray-700">
                <span>Dataset: PlantVillage (54,305 leaf images, 38 classes)</span>
                <br />
                <span>Held-Out Split Evaluation: </span>
                <span className="text-amber-700 font-semibold">Evaluation not yet completed locally</span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};
