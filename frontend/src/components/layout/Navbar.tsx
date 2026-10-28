import React from 'react';
import { Link } from 'react-router-dom';
import { Sprout, Menu, Sparkles, Activity } from 'lucide-react';

interface NavbarProps {
  onToggleSidebar?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleSidebar }) => {
  return (
    <header className="sticky top-0 z-30 bg-white/90 backdrop-blur-md border-b border-gray-100 px-4 lg:px-8 py-3.5">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleSidebar}
            className="p-2 rounded-lg text-gray-600 hover:bg-gray-100 lg:hidden"
            aria-label="Toggle Navigation"
          >
            <Menu className="w-5 h-5" />
          </button>
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-primary-700 flex items-center justify-center text-white shadow-sm group-hover:bg-primary-800 transition-colors">
              <Sprout className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xl font-bold text-primary-950 tracking-tight">PlantSathi</span>
              <span className="text-xs font-semibold ml-1.5 px-1.5 py-0.5 rounded bg-primary-100 text-primary-800 uppercase tracking-wider">AI</span>
            </div>
          </Link>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/scanner"
            className="hidden sm:inline-flex items-center gap-2 bg-primary-700 hover:bg-primary-800 text-white text-sm font-medium px-4 py-2 rounded-lg shadow-sm transition-colors"
          >
            <Sparkles className="w-4 h-4" />
            <span>New Scan</span>
          </Link>
          <Link
            to="/settings"
            className="flex items-center gap-1.5 text-xs text-gray-600 bg-gray-50 hover:bg-gray-100 border border-gray-200 px-3 py-1.5 rounded-lg transition-colors"
          >
            <Activity className="w-3.5 h-3.5 text-green-600" />
            <span className="font-medium">Model Status</span>
          </Link>
        </div>
      </div>
    </header>
  );
};
