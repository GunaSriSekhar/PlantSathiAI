import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  History,
  Trash2,
  RefreshCw,
  ExternalLink,
  ScanLine,
  CheckCircle,
  AlertTriangle,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { getScans, deleteScan } from '../services/api';
import { ScanSummary } from '../types';

export const ScanHistory: React.FC = () => {
  const [scans, setScans] = useState<ScanSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchHistory = async () => {
    try {
      setRefreshing(true);
      const data = await getScans(50, 0);
      setScans(data);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this scan from history?')) return;
    try {
      setDeletingId(id);
      await deleteScan(id);
      setScans((prev) => prev.filter((s) => s.id !== id));
    } catch (err) {
      alert('Could not delete scan.');
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 tracking-tight flex items-center gap-2">
            <History className="w-6 h-6 text-primary-700" />
            <span>Scan History</span>
          </h1>
          <p className="text-xs text-gray-500 mt-0.5">
            Database records for all previous plant identification and pathology sessions.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchHistory}
            loading={refreshing}
            icon={<RefreshCw className="w-3.5 h-3.5" />}
          >
            Refresh
          </Button>
          <Link to="/scanner">
            <Button size="sm" icon={<ScanLine className="w-3.5 h-3.5" />}>
              New Scan
            </Button>
          </Link>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="py-16">
              <LoadingSpinner text="Querying database..." />
            </div>
          ) : scans.length === 0 ? (
            <div className="py-16 text-center space-y-3">
              <div className="w-12 h-12 mx-auto rounded-full bg-gray-100 text-gray-400 flex items-center justify-center">
                <ScanLine className="w-6 h-6" />
              </div>
              <h4 className="text-sm font-semibold text-gray-700">No Historical Records Found</h4>
              <p className="text-xs text-gray-400 max-w-sm mx-auto">
                Scan records are permanently stored in your SQLite database. Start by running an image analysis.
              </p>
              <Link to="/scanner">
                <Button size="sm" className="mt-2">
                  Launch Scanner
                </Button>
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-gray-100 bg-gray-50/50 text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
                    <th className="py-3 px-5">Date & Time</th>
                    <th className="py-3 px-5">Plant Species</th>
                    <th className="py-3 px-5">Pathology Condition</th>
                    <th className="py-3 px-5">Confidence</th>
                    <th className="py-3 px-5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {scans.map((scan) => (
                    <tr key={scan.id} className="hover:bg-gray-50/70 transition-colors">
                      <td className="py-3.5 px-5 text-xs text-gray-500 whitespace-nowrap">
                        {new Date(scan.created_at).toLocaleString()}
                      </td>
                      <td className="py-3.5 px-5 font-semibold text-gray-900">
                        {scan.plant_common_name || 'Unidentified'}
                      </td>
                      <td className="py-3.5 px-5">
                        {scan.disease_status === 'healthy' ? (
                          <Badge variant="success" size="sm">Healthy</Badge>
                        ) : scan.disease_label ? (
                          <span className="text-xs text-gray-700 font-medium">
                            {scan.disease_label.replace(/___/g, ' → ').replace(/_/g, ' ')}
                          </span>
                        ) : (
                          <span className="text-xs text-gray-400">Undetermined</span>
                        )}
                      </td>
                      <td className="py-3.5 px-5 text-xs font-mono text-gray-600">
                        {scan.disease_confidence
                          ? `${Math.round(scan.disease_confidence * 100)}%`
                          : '—'}
                      </td>
                      <td className="py-3.5 px-5 text-right whitespace-nowrap">
                        <div className="flex items-center justify-end gap-2">
                          <Link
                            to={`/results/${scan.id}`}
                            className="p-1.5 text-gray-400 hover:text-primary-700 rounded-lg hover:bg-gray-100 transition-colors"
                            title="View Details"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={() => handleDelete(scan.id)}
                            disabled={deletingId === scan.id}
                            className="p-1.5 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
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
