import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Map,
  TrendingUp,
  PlayCircle,
  GitBranch,
  AlertTriangle,
  BarChart3,
  Cloud,
  Building2,
  Settings,
  User,
  Shield,
} from 'lucide-react';
import { useUIStore } from '../../store/uiStore';
import { cn } from '../../utils/cn';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/digital-twin', label: 'Live Digital Twin', icon: Map },
  { path: '/prediction', label: 'Traffic Prediction', icon: TrendingUp },
  { path: '/simulation', label: 'Simulation', icon: PlayCircle },
  { path: '/negotiation', label: 'Negotiation', icon: GitBranch },
  { path: '/emergency', label: 'Emergency', icon: AlertTriangle },
  { path: '/analytics', label: 'Analytics', icon: BarChart3 },
  { path: '/carbon', label: 'Carbon', icon: Cloud },
  { path: '/infrastructure', label: 'Infrastructure', icon: Building2 },
  { path: '/driver', label: 'Driver', icon: User },
  { path: '/authority', label: 'Authority', icon: Shield },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export const Sidebar = () => {
  const { sidebarOpen } = useUIStore();

  return (
    <aside
      className={cn(
        'fixed left-0 top-16 z-30 h-[calc(100vh-4rem)] w-64 transform border-r border-slate-200 dark:border-twinflow-border bg-white dark:bg-twinflow-dark transition-transform duration-300 ease-in-out overflow-y-auto',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      )}
    >
      <nav className="p-4 space-y-1">
        {navItems.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
                isActive
                  ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              )
            }
          >
            <Icon className="w-4 h-4" />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};