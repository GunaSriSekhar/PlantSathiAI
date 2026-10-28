import React, { useEffect, useState } from 'react';
import { Flower2, Plus, Trash2, Calendar, FileText, AlertCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { getSavedPlants, savePlant, deleteSavedPlant } from '../services/api';
import { SavedPlant } from '../types';

export const MyPlants: React.FC = () => {
  const [plants, setPlants] = useState<SavedPlant[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState('');
  const [scientificName, setScientificName] = useState('');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const loadPlants = async () => {
    try {
      setLoading(true);
      const data = await getSavedPlants();
      setPlants(data);
    } catch (err) {
      console.error('Error fetching saved plants:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPlants();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    try {
      setSubmitting(true);
      const newPlant = await savePlant({
        common_name: name.trim(),
        scientific_name: scientificName.trim() || undefined,
        notes: notes.trim() || undefined,
      });
      setPlants((prev) => [newPlant, ...prev]);
      setIsModalOpen(false);
      setName('');
      setScientificName('');
      setNotes('');
    } catch (err) {
      alert('Could not save plant.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Remove this plant from your saved collection?')) return;
    try {
      await deleteSavedPlant(id);
      setPlants((prev) => prev.filter((p) => p.id !== id));
    } catch (err) {
      alert('Could not remove plant.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 tracking-tight flex items-center gap-2">
            <Flower2 className="w-6 h-6 text-primary-700" />
            <span>My Plants Collection</span>
          </h1>
          <p className="text-xs text-gray-500 mt-0.5">
            Bookmarked species and personalized cultivation notes.
          </p>
        </div>

        <Button
          size="sm"
          icon={<Plus className="w-4 h-4" />}
          onClick={() => setIsModalOpen(true)}
        >
          Add Plant
        </Button>
      </div>

      {loading ? (
        <div className="py-16">
          <LoadingSpinner text="Loading saved plants..." />
        </div>
      ) : plants.length === 0 ? (
        <Card className="py-16 text-center space-y-3">
          <div className="w-12 h-12 mx-auto rounded-full bg-primary-100 text-primary-800 flex items-center justify-center">
            <Flower2 className="w-6 h-6" />
          </div>
          <h4 className="text-base font-semibold text-gray-800">No Plants Bookmarked Yet</h4>
          <p className="text-xs text-gray-500 max-w-sm mx-auto">
            Keep track of species in your garden, greenhouse, or farm by saving them with custom cultivation notes.
          </p>
          <Button
            size="sm"
            variant="outline"
            onClick={() => setIsModalOpen(true)}
            icon={<Plus className="w-4 h-4" />}
          >
            Add First Plant
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {plants.map((p) => (
            <Card key={p.id} hover className="flex flex-col justify-between">
              <div className="space-y-2">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-bold text-gray-900 text-base">{p.common_name}</h3>
                    {p.scientific_name && (
                      <p className="text-xs italic text-gray-400">{p.scientific_name}</p>
                    )}
                  </div>
                  <button
                    onClick={() => handleDelete(p.id)}
                    className="text-gray-300 hover:text-red-600 p-1 rounded-lg transition-colors"
                    title="Remove"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                {p.notes && (
                  <p className="text-xs text-gray-600 leading-relaxed bg-gray-50 p-3 rounded-lg border border-gray-100">
                    {p.notes}
                  </p>
                )}
              </div>

              <div className="pt-4 mt-3 border-t border-gray-100 flex items-center justify-between text-[11px] text-gray-400">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {new Date(p.created_at).toLocaleDateString()}
                </span>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Add Plant Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Bookmark a Plant"
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              Common Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. San Marzano Tomato, Golden Pothos"
              className="w-full px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              Scientific Name (Optional)
            </label>
            <input
              type="text"
              value={scientificName}
              onChange={(e) => setScientificName(e.target.value)}
              placeholder="e.g. Solanum lycopersicum"
              className="w-full px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              Care Notes (Optional)
            </label>
            <textarea
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. Planted in raised bed 2; needs afternoon shade; watered twice weekly."
              className="w-full px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-600"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setIsModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              size="sm"
              loading={submitting}
              disabled={!name.trim() || submitting}
            >
              Save Plant
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
