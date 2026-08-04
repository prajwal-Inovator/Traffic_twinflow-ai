import { useUIStore } from '../store/uiStore';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';

export default function Settings() {
  const { theme, setTheme } = useUIStore();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>
      <Card title="Appearance">
        <div className="flex items-center gap-4">
          <span>Theme:</span>
          <Button
            variant={theme === 'dark' ? 'default' : 'outline'}
            onClick={() => setTheme('dark')}
          >
            Dark
          </Button>
          <Button
            variant={theme === 'light' ? 'default' : 'outline'}
            onClick={() => setTheme('light')}
          >
            Light
          </Button>
        </div>
      </Card>
      <Card title="Notifications">
        <div className="space-y-2">
          <label className="flex items-center gap-2">
            <input type="checkbox" defaultChecked /> Email alerts
          </label>
          <label className="flex items-center gap-2">
            <input type="checkbox" defaultChecked /> Push notifications
          </label>
        </div>
      </Card>
    </div>
  );
}