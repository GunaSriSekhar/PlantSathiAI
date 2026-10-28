import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { Landing } from './pages/Landing';
import { Dashboard } from './pages/Dashboard';
import { Scanner } from './pages/Scanner';
import { AnalysisResult } from './pages/AnalysisResult';
import { AiDoctor } from './pages/AiDoctor';
import { MyPlants } from './pages/MyPlants';
import { ScanHistory } from './pages/ScanHistory';
import { PlantCareGuide } from './pages/PlantCareGuide';
import { Settings } from './pages/Settings';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Landing />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="scanner" element={<Scanner />} />
          <Route path="identify" element={<Scanner />} />
          <Route path="diagnose" element={<Scanner />} />
          <Route path="results/:scanId" element={<AnalysisResult />} />
          <Route path="doctor" element={<AiDoctor />} />
          <Route path="plants" element={<MyPlants />} />
          <Route path="history" element={<ScanHistory />} />
          <Route path="care" element={<PlantCareGuide />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
