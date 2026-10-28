import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  ScanLine,
  Stethoscope,
  Bot,
  Flower2,
  History,
  BookOpen,
  Settings,
  HelpCircle,
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Plant Scanner', path: '/scanner', icon: ScanLine },
    { label: 'Diagnose Leaf', path: '/diagnose', icon: Stethoscope },
    { label: 'AI Plant Doctor', path: '/doctor', icon: Bot },
    { label: 'My Plants', path: '/plants', icon: Flower2 },
    { label: 'Scan History', path: '/history', icon: History },
    { label: 'Care Guides', path: '/care', icon: BookOpen },
    { label: 'Model Telemetry', path: '/settings', icon: Settings },
  ];

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-black/30 lg:hidden backdrop-blur-xs"
        />
      )}

      <aside
        className={`fixed lg:sticky top-0 lg:top-[61px] left-0 z-40 h-full lg:h-[calc(100vh-61px)] w-64 bg-white border-r border-gray-100 flex flex-col justify-between transition-transform duration-200 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="p-4 space-y-1 overflow-y-auto">
          <div className="text-[11px] font-bold text-gray-400 uppercase tracking-wider px-3 mb-2">
            Intelligence
          </div>
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-primary-50 text-primary-900 font-semibold shadow-xs'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`
              }
            >
              <item.icon className="w-4 h-4 text-primary-700" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>

        <div className="p-4 border-t border-gray-100 bg-gray-50/50">
          <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
            <HelpCircle className="w-3.5 h-3.5 text-primary-600" />
            <span className="font-semibold text-gray-700">B.Tech Minor Project</span>
          </div>
          <p className="text-[11px] text-gray-400 leading-normal">
            Dual-pipeline CV engine for plant identification & disease diagnosis.
          </p>
        </div>
      </aside>
    </>
  );
};
