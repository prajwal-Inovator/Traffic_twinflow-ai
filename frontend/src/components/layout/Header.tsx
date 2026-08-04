import { Menu, Bell, Sun, Moon, User, LogOut } from 'lucide-react';
import { useUIStore } from '../../store/uiStore';
import { useAuthStore } from '../../store/authStore';
import { Button } from '../common/Button';
import { useNavigate } from 'react-router-dom';

export const Header = () => {
  const { theme, setTheme, toggleSidebar, notificationCount } = useUIStore();
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-40 flex h-16 items-center justify-between border-b border-slate-200 dark:border-twinflow-border bg-white/80 dark:bg-twinflow-dark/80 backdrop-blur px-4 md:px-6">
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          aria-label="Toggle sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>
        <span className="text-xl font-bold text-primary-600 dark:text-primary-400">
          TwinFlow AI
        </span>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>

        <button
          className="relative p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-5 h-5" />
          {notificationCount > 0 && (
            <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-[10px] rounded-full flex items-center justify-center">
              {notificationCount > 9 ? '9+' : notificationCount}
            </span>
          )}
        </button>

        {isAuthenticated ? (
          <div className="flex items-center gap-3">
            <span className="text-sm hidden md:inline">{user?.email}</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={logout}
              className="text-slate-500 dark:text-slate-400"
            >
              <LogOut className="w-4 h-4 mr-1" /> Logout
            </Button>
          </div>
        ) : (
          <Button variant="default" size="sm" onClick={() => navigate('/landing')}>
            <User className="w-4 h-4 mr-1" /> Login
          </Button>
        )}
      </div>
    </header>
  );
};