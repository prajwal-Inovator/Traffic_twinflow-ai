import { BrowserRouter } from 'react-router-dom';
import { useEffect } from 'react';
import { useUIStore } from './store/uiStore';
import { AppRoutes } from './routes';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { Footer } from './components/layout/Footer';

function App() {
  const { sidebarOpen } = useUIStore();

  useEffect(() => {
    // Listen for system theme preference
    const darkModeMedia = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e: MediaQueryListEvent) => {
      document.documentElement.classList.toggle('dark', e.matches);
    };
    darkModeMedia.addEventListener('change', handler);
    return () => darkModeMedia.removeEventListener('change', handler);
  }, []);

  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        <Header />
        <div className="flex flex-1 overflow-hidden">
          <Sidebar />
          <main
            className={`flex-1 transition-all duration-300 ${
              sidebarOpen ? 'ml-64' : 'ml-0'
            } p-4 md:p-6 overflow-y-auto bg-slate-50 dark:bg-twinflow-dark`}
          >
            <AppRoutes />
          </main>
        </div>
        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;