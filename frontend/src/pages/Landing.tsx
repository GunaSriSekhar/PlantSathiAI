import React from 'react';
import { Link } from 'react-router-dom';
import {
  ScanLine,
  Stethoscope,
  Bot,
  ShieldCheck,
  Cpu,
  ArrowRight,
  Sparkles,
  Layers,
  Leaf,
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';

export const Landing: React.FC = () => {
  return (
    <div className="space-y-16 py-4">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-b from-primary-900 to-primary-950 text-white p-8 sm:p-12 lg:p-16 shadow-medium">
        <div className="relative z-10 max-w-3xl space-y-6">
          <Badge variant="success" className="bg-primary-800/80 text-primary-200 border-primary-700">
            <Sparkles className="w-3.5 h-3.5 mr-1" />
            B.Tech Computer Science (AI & Data Science) Minor Project
          </Badge>

          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight leading-tight">
            Production-Oriented Plant Intelligence & Disease Diagnosis
          </h1>

          <p className="text-base sm:text-lg text-primary-100/90 leading-relaxed max-w-2xl">
            PlantSathi AI connects dedicated computer vision classification with agronomic rule-based
            care guidance. Predict plant species and classify 38 crop pathogen conditions using real ML inference.
          </p>

          <div className="flex flex-wrap gap-4 pt-2">
            <Link to="/scanner">
              <Button
                size="lg"
                className="bg-white text-primary-950 hover:bg-primary-50 font-semibold shadow-md"
                icon={<ScanLine className="w-5 h-5 text-primary-700" />}
              >
                Start Plant Scanner
              </Button>
            </Link>
            <Link to="/diagnose">
              <Button
                variant="outline"
                size="lg"
                className="border-primary-400/50 text-white hover:bg-primary-800/50"
                icon={<Stethoscope className="w-5 h-5" />}
              >
                Diagnose Leaf Disease
              </Button>
            </Link>
          </div>
        </div>

        {/* Decorative background blur */}
        <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-primary-600/20 rounded-full blur-3xl pointer-events-none" />
      </section>

      {/* Core Capabilities */}
      <section className="space-y-8">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">
            Engineered for Precision & Scientific Integrity
          </h2>
          <p className="text-sm text-gray-500">
            Distinguishing species identification from disease classification as two distinct machine learning tasks.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card hover className="space-y-4">
            <div className="w-12 h-12 rounded-xl bg-primary-100 text-primary-800 flex items-center justify-center">
              <Leaf className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-gray-900">1. Plant Species Identification</h3>
            <p className="text-sm text-gray-600 leading-relaxed">
              Vision Transformer image classifier evaluating botanical morphological markers. Returns top candidate species with calibrated probability bands.
            </p>
          </Card>

          <Card hover className="space-y-4">
            <div className="w-12 h-12 rounded-xl bg-primary-100 text-primary-800 flex items-center justify-center">
              <Stethoscope className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-gray-900">2. Plant Disease Classification</h3>
            <p className="text-sm text-gray-600 leading-relaxed">
              PlantVillage-trained MobileNetV2 architecture recognizing 38 crop-disease combinations across tomatoes, potatoes, apples, peppers, and grapes.
            </p>
          </Card>

          <Card hover className="space-y-4">
            <div className="w-12 h-12 rounded-xl bg-primary-100 text-primary-800 flex items-center justify-center">
              <Bot className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-gray-900">3. AI Plant Doctor</h3>
            <p className="text-sm text-gray-600 leading-relaxed">
              Transparent, rule-based expert assistance tailored to scan results for watering, sunlight, soil fertility, pruning, and organic disease management.
            </p>
          </Card>
        </div>
      </section>

      {/* Transparency Note */}
      <section className="bg-primary-50/70 border border-primary-200/80 rounded-2xl p-6 sm:p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
        <div className="space-y-2 max-w-2xl">
          <div className="flex items-center gap-2 text-primary-900 font-bold text-base">
            <ShieldCheck className="w-5 h-5 text-primary-700" />
            <span>Honest Machine Learning Without Hallucination</span>
          </div>
          <p className="text-xs sm:text-sm text-primary-800 leading-relaxed">
            PlantSathi never substitutes arbitrary LLM guesses for visual inference. Predictions are computed
            using genuine convolutional / transformer backbones with conservative uncertainty thresholds and out-of-distribution handling.
          </p>
        </div>
        <Link to="/settings" className="flex-shrink-0">
          <Button variant="outline" size="sm" icon={<Cpu className="w-4 h-4" />}>
            Inspect Models
          </Button>
        </Link>
      </section>

      {/* 3 Step Workflow */}
      <section className="space-y-8">
        <div className="text-center max-w-xl mx-auto space-y-2">
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900">How It Works</h2>
          <p className="text-xs sm:text-sm text-gray-500">Three streamlined steps from leaf capture to actionable care</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-center">
          <div className="p-6 bg-white rounded-2xl border border-gray-100 shadow-soft space-y-3">
            <div className="w-10 h-10 mx-auto rounded-full bg-primary-100 text-primary-800 font-bold flex items-center justify-center">
              1
            </div>
            <h4 className="font-semibold text-gray-900">Upload or Capture</h4>
            <p className="text-xs text-gray-500">Provide a clear photo of an affected leaf or whole plant in natural lighting.</p>
          </div>

          <div className="p-6 bg-white rounded-2xl border border-gray-100 shadow-soft space-y-3">
            <div className="w-10 h-10 mx-auto rounded-full bg-primary-100 text-primary-800 font-bold flex items-center justify-center">
              2
            </div>
            <h4 className="font-semibold text-gray-900">Dual CV Inference</h4>
            <p className="text-xs text-gray-500">Identifies plant species and screens leaf pathology across 38 documented classes.</p>
          </div>

          <div className="p-6 bg-white rounded-2xl border border-gray-100 shadow-soft space-y-3">
            <div className="w-10 h-10 mx-auto rounded-full bg-primary-100 text-primary-800 font-bold flex items-center justify-center">
              3
            </div>
            <h4 className="font-semibold text-gray-900">Evidence-Based Care</h4>
            <p className="text-xs text-gray-500">Receive precise disease management protocols and chat with the AI Plant Doctor.</p>
          </div>
        </div>
      </section>
    </div>
  );
};
