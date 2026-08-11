import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { useNavigate } from 'react-router-dom';

export default function Landing() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  if (isAuthenticated) {
    navigate('/dashboard');
    return null;
  }

  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await login(email, password);
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || 'Login failed.');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[80vh]">
      <Card title="Welcome to TwinFlow AI" className="w-full max-w-md">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-2 border rounded text-slate-900 dark:text-slate-100 bg-white dark:bg-slate-800"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-2 border rounded text-slate-900 dark:text-slate-100 bg-white dark:bg-slate-800"
              required
            />
          </div>
          <Button type="submit" className="w-full">Login</Button>
        </form>
        {error && <div className="mt-3 text-sm text-red-500">{error}</div>}
        <div className="mt-4 text-center text-sm text-slate-500">
          Demo: admin@twinflow.ai / admin123
        </div>
      </Card>
    </div>
  );
}