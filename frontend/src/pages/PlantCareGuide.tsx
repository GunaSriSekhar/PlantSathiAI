import React, { useState } from 'react';
import {
  BookOpen,
  Droplets,
  Sun,
  Sprout,
  ShieldAlert,
  Scissors,
  CheckCircle2,
  ChevronRight,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';

export const PlantCareGuide: React.FC = () => {
  const [activeCategory, setActiveCategory] = useState<'watering' | 'sunlight' | 'soil' | 'disease' | 'pruning'>('watering');

  const categories = [
    { id: 'watering', label: 'Irrigation & Moisture', icon: Droplets },
    { id: 'sunlight', label: 'Sunlight & Photoperiod', icon: Sun },
    { id: 'soil', label: 'Soil, pH & Nutrition', icon: Sprout },
    { id: 'disease', label: 'Disease Prevention', icon: ShieldAlert },
    { id: 'pruning', label: 'Pruning & Canopy', icon: Scissors },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 tracking-tight flex items-center gap-2">
          <BookOpen className="w-6 h-6 text-primary-700" />
          <span>Plant Care Knowledge Base</span>
        </h1>
        <p className="text-xs text-gray-500 mt-0.5">
          Practical horticultural principles and disease management guidelines.
        </p>
      </div>

      {/* Category Pills */}
      <div className="flex gap-2 overflow-x-auto pb-1">
        {categories.map((c) => (
          <button
            key={c.id}
            onClick={() => setActiveCategory(c.id as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-medium whitespace-nowrap transition-all ${
              activeCategory === c.id
                ? 'bg-primary-700 text-white shadow-sm'
                : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
          >
            <c.icon className="w-4 h-4" />
            <span>{c.label}</span>
          </button>
        ))}
      </div>

      {/* Guide Content */}
      {activeCategory === 'watering' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="space-y-3">
            <h3 className="font-bold text-gray-900 text-base">The 'Soak and Dry' Principle</h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              Most cultivated plants and garden crops thrive on deep, infrequent irrigation rather than daily surface sprinkles.
              Deep watering encourages downward taproot and lateral root penetration, increasing drought tolerance.
            </p>
            <div className="bg-primary-50 p-3 rounded-lg text-xs text-primary-900 space-y-1">
              <span className="font-semibold block">Key Rule:</span>
              <span>Test the top 2 inches of soil with your finger. Water only when dry to the touch.</span>
            </div>
          </Card>

          <Card className="space-y-3">
            <h3 className="font-bold text-gray-900 text-base">Basal Watering vs Foliage Wetting</h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              Fungal spores (such as Early Blight, Late Blight, and Septoria) require free moisture on foliage to germinate.
              Always apply water directly to the soil or drip line early in the morning so any accidental splashing evaporates before nightfall.
            </p>
            <div className="bg-amber-50 p-3 rounded-lg text-xs text-amber-900 space-y-1">
              <span className="font-semibold block">Foliar Warning:</span>
              <span>Avoid overhead sprinklers during humid or rainy weather cycles.</span>
            </div>
          </Card>
        </div>
      )}

      {activeCategory === 'sunlight' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="space-y-3">
            <h3 className="font-bold text-gray-900 text-base">Full Sun Requirements (6–8+ Hours)</h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              Fruiting and nightshade crops including tomatoes, peppers, potatoes, and corn require full, unobstructed sunlight
              to photosynthesize sufficient carbohydrates for blossom development and fruit setting.
            </p>
          </Card>

          <Card className="space-y-3">
            <h3 className="font-bold text-gray-900 text-base">Managing Leaf Scorch & Thermal Stress</h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              In hot arid climates, afternoon temperatures above 35°C (95°F) cause pollen sterilization and leaf margin scorch.
              Use 30% shade cloth during peak mid-afternoon hours while ensuring morning eastern light remains unobstructed.
            </p>
          </Card>
        </div>
      )}

      {activeCategory === 'soil' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="space-y-3">
            <h3 className="font-bold text-gray-900 text-base">Soil Drainage & Aeration</h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              Heavy clay soils trap excess water around root zones, suffocating aerobic root respiration and enabling
              Pythium and Phytophthora root rot. Amend clay soils with well-aged organic compost, leaf mold, or coarse perlite.
            </p>
          </Card>

          <Card className="space-y-3">
            <h3 className="font-bold text-gray-900 text-base">Target pH Ranges</h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              Nutrient availability directly depends on soil pH. Most vegetables prefer slightly acidic to neutral soil (pH 6.0–6.8).
              Blueberries and rhododendrons require acidic soil (pH 4.5–5.5), whereas brassicas prefer near-neutral (pH 6.5–7.2)
              to suppress clubroot fungal disease.
            </p>
          </Card>
        </div>
      )}

      {activeCategory === 'disease' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="space-y-3">
            <h3 className="font-bold text-gray-900 text-base">Crop Rotation (3-Year Cycle)</h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              Never plant members of the same botanical family (e.g. Solanaceae: tomatoes, potatoes, eggplants, peppers)
              in the exact same soil bed in consecutive years. Fungal sclerotia and resting spores survive in soil for 24–36 months.
            </p>
          </Card>

          <Card className="space-y-3">
            <h3 className="font-bold text-gray-900 text-base">Sanitation & Tool Sterilization</h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              Pruning shears and hand tools transmit bacterial spot and viral mosaic pathogens from infected leaves to healthy branches.
              Dip pruning blades in 70% isopropyl alcohol or a 10% bleach solution between cuts.
            </p>
          </Card>
        </div>
      )}

      {activeCategory === 'pruning' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="space-y-3">
            <h3 className="font-bold text-gray-900 text-base">Lower Canopy Clearance</h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              Prune all bottom leaves within 12–18 inches of the soil line on indeterminate tomatoes and peppers once established.
              This prevents soil-borne fungal spores from splashing onto lower foliage during rainstorms.
            </p>
          </Card>

          <Card className="space-y-3">
            <h3 className="font-bold text-gray-900 text-base">Improving Canopy Airflow</h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              Thin crowded interior suckers to ensure sunlight penetrates into the center of the plant.
              Good air circulation accelerates drying of dewy leaves, denying mildew spores the hours of dampness needed for infection.
            </p>
          </Card>
        </div>
      )}
    </div>
  );
};
