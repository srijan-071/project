import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Home from './pages/Home';
import Intelligence from './pages/Intelligence';
import MarketPulse from './pages/MarketPulse';
import BatchAnalysis from './pages/BatchAnalysis';
import Compare from './pages/Compare';
import ModelLab from './pages/ModelLab';
import Architecture from './pages/Architecture';
import History from './pages/History';
import Documentation from './pages/Documentation';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="intelligence" element={<Intelligence />} />
          <Route path="market-pulse" element={<MarketPulse />} />
          <Route path="batch" element={<BatchAnalysis />} />
          <Route path="compare" element={<Compare />} />
          <Route path="model-lab" element={<ModelLab />} />
          <Route path="architecture" element={<Architecture />} />
          <Route path="history" element={<History />} />
          <Route path="docs" element={<Documentation />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
