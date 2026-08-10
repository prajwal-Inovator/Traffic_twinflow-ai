import { Routes, Route, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import { Spinner } from './components/common/Spinner';

// Lazy load pages for code splitting
const Landing = lazy(() => import('./pages/Landing'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const LiveDigitalTwin = lazy(() => import('./pages/LiveDigitalTwin'));
const TrafficPrediction = lazy(() => import('./pages/TrafficPrediction'));
const Simulation = lazy(() => import('./pages/Simulation'));
const Negotiation = lazy(() => import('./pages/Negotiation'));
const Emergency = lazy(() => import('./pages/Emergency'));
const Analytics = lazy(() => import('./pages/Analytics'));
const Carbon = lazy(() => import('./pages/Carbon'));
const Infrastructure = lazy(() => import('./pages/Infrastructure'));
const Settings = lazy(() => import('./pages/Settings'));
const Driver = lazy(() => import('./pages/Driver'));
const Authority = lazy(() => import('./pages/Authority'));

const withSuspense = (Component: React.LazyExoticComponent<React.ComponentType<any>>) => (
  <Suspense fallback={<Spinner size="lg" className="h-screen" />}>
    <Component />
  </Suspense>
);

export const AppRoutes = () => (
  <Routes>
    <Route path="/" element={<Navigate to="/dashboard" replace />} />
    <Route path="/landing" element={withSuspense(Landing)} />
    <Route path="/dashboard" element={withSuspense(Dashboard)} />
    <Route path="/digital-twin" element={withSuspense(LiveDigitalTwin)} />
    <Route path="/prediction" element={withSuspense(TrafficPrediction)} />
    <Route path="/simulation" element={withSuspense(Simulation)} />
    <Route path="/negotiation" element={withSuspense(Negotiation)} />
    <Route path="/emergency" element={withSuspense(Emergency)} />
    <Route path="/analytics" element={withSuspense(Analytics)} />
    <Route path="/carbon" element={withSuspense(Carbon)} />
    <Route path="/infrastructure" element={withSuspense(Infrastructure)} />
    <Route path="/settings" element={withSuspense(Settings)} />
    <Route path="/driver" element={withSuspense(Driver)} />
    <Route path="/authority" element={withSuspense(Authority)} />
  </Routes>
);