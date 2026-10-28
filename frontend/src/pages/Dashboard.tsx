import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ScanLine,
  Stethoscope,
  Bot,
  History,
  Activity,
  ArrowRight,
  Sparkles,
  Calendar,
  AlertTriangle,
  CheckCircle,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { getScans, getModelStatus } from '../services/api';
import { ScanSummary, ModelStatus } from '../types';

export const Dashboard: React.FC = () => {
  const [scans, setScans] = useState<ScanSummary[]>([]);
  const [models, setModels] = useState<ModelStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setLoading(true);
        const [scansData, modelsData] = await Promise.all([
          getScans(5, 0).catch(() => []),
          getModelStatus().catch(() => []),
        ]);
        setScans(scansData);
        setModels(modelsData);
      } catch (err) {
        setError('Could not connect to the backend server. Make sure the FastAPI service is running.');
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 tracking-tight">Plant Intelligence Hub</h1>
          <p className="text-sm text-gray-500 mt-1">
            Real-time inference telemetry and recent plant health assessments.
          </p>
        </div>
        <Link to="/scanner">
          <Button icon={<Sparkles className="w-4 h-4" />}>
            New Plant Scan
          </Button>
        </Link>
      </div>

      {/* Quick Action Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <Link to="/scanner" className="group">
          <Card hover className="h-full border-l-4 border-l-primary-600">
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-xl bg-primary-100 text-primary-800 flex items-center justify-center group-hover:scale-105 transition-transform">
                <ScanLine className="w-5 h-5" />
              </div>
              <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-primary-700 transition-colors" />
            </div>
            <h3 className="font-semibold text-gray-900">Identify Plant Species</h3>
            <p className="text-xs text-gray-500 mt-1">Predict species and botanical classifications from photos.</p>
          </Card>
        </Link>

        <Link to="/diagnose" className="group">
          <Card hover className="h-full border-l-4 border-l-amber-600">
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center group-hover:scale-105 transition-transform">
                <Stethoscope className="w-5 h-5" />
              </div>
              <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-amber-700 transition-colors" />
            </div>
            <h3 className="font-semibold text-gray-900">Diagnose Leaf Disease</h3>
            <p className="text-xs text-gray-500 mt-1">Screen for 38 leaf pathogens including blights, spots, and rusts.</p>
          </Card>
        </Link>

        <Link to="/doctor" className="group">
          <Card hover className="h-full border-l-4 border-l-blue-600">
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-800 flex items-center justify-center group-hover:scale-105 transition-transform">
                <Bot className="w-5 h-5" />
              </div>
              <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-blue-700 transition-colors" />
            </div>
            <h3 className="font-semibold text-gray-900">AI Plant Doctor</h3>
            <p className="text-xs text-gray-500 mt-1">Consult rule-based agronomic assistant for treatment advice.</p>
          </Card>
        </Link>
      </div>

      {/* Model Status Card */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-primary-700" />
            <CardTitle>Inference Engine Status</CardTitle>
          </div>
          <Link to="/settings" className="text-xs text-primary-700 hover:underline font-medium">
            Full Telemetry
          </Link>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-3.5 rounded-xl bg-gray-50 border border-gray-100 flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold text-gray-700 block">Disease Model (MobileNetV2)</span>
                <span className="text-[11px] text-gray-400">PlantVillage • 38 classes</span>
              </div>
              <Badge variant="success" size="sm">Available</Badge>
            </div>
            <div className="p-3.5 rounded-xl bg-gray-50 border border-gray-100 flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold text-gray-700 block">Plant Species Model (ViT)</span>
                <span className="text-[11px] text-gray-400">Botanical Vision Pipeline</span>
              </div>
              <Badge variant="success" size="sm">Available</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Scans Table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-primary-700" />
            <CardTitle>Recent Scan History</CardTitle>
          </div>
          <Link to="/history" className="text-xs text-primary-700 hover:underline font-medium">
            View All ({scans.length})
          </Link>
        </CardHeader>
        <CardContent>
          {loading ? (
            <LoadingSpinner text="Retrieving scan records..." />
          ) : error ? (
            <div className="p-4 text-center text-sm text-amber-700 bg-amber-50 rounded-xl">
              {error}
            </div>
          ) : scans.length === 0 ? (
            <div className="py-12 text-center space-y-3">
              <div className="w-12 h-12 mx-auto rounded-full bg-gray-100 text-gray-400 flex items-center justify-center">
                <ScanLine className="w-6 h-6" />
              </div>
              <h4 className="text-sm font-semibold text-gray-700">No Scans Recorded Yet</h4>
              <p className="text-xs text-gray-400 max-w-sm mx-auto">
                Scan history strictly reflects actual records saved in the SQLite database.
                Upload your first plant photo to begin tracking.
              </p>
              <Link to="/scanner">
                <Button size="sm" variant="outline" className="mt-2">
                  Take First Scan
                </Button>
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-gray-100 text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
                    <th className="pb-3">Plant</th>
                    <th className="pb-3">Condition</th>
                    <th className="pb-3">Confidence</th>
                    <th className="pb-3">Timestamp</th>
                    <th className="pb-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {scans.map((scan) => (
                    <tr key={scan.id} className="hover:bg-gray-50/70 transition-colors">
                      <td className="py-3 font-medium text-gray-900">
                        {scan.plant_common_name || 'Unidentified Plant'}
                      </td>
                      <td className="py-3">
                        {scan.disease_status === 'healthy' ? (
                          <Badge variant="success" size="sm">Healthy</Badge>
                        ) : scan.disease_label ? (
                          <span className="text-xs text-gray-700 font-medium truncate max-w-[200px] block">
                            {scan.disease_label.replace(/___/g, ' → ').replace(/_/g, ' ')}
                          </span>
                        ) : (
                          <span className="text-xs text-gray-400">Undetermined</span>
                        )}
                      </td>
                      <td className="py-3 text-xs text-gray-600">
                        {scan.disease_confidence ? `${Math.round(scan.disease_confidence * 100)}%` : 'N/A'}
                      </td>
                      <td className="py-3 text-xs text-gray-400">
                        {new Date(scan.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 text-right">
                        <Link
                          to={`/results/${scan.id}`}
                          className="text-xs font-semibold text-primary-700 hover:text-primary-900"
                        >
                          Details →
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
