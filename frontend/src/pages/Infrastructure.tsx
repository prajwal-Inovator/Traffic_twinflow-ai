import { useQuery } from '@tanstack/react-query';
import { infrastructureApi } from '../api/endpoints';
import { Card } from '../components/common/Card';
import { CheckCircle, XCircle } from 'lucide-react';

export default function Infrastructure() {
  const { data: health } = useQuery({
    queryKey: ['infraHealth'],
    queryFn: () => infrastructureApi.getHealth().then(res => res.data.data),
    refetchInterval: 60000,
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Infrastructure Health</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card title="Roads">
          <div className="flex items-center gap-2">
            {health?.roads_status === 'operational' ? (
              <CheckCircle className="text-green-500" />
            ) : (
              <XCircle className="text-red-500" />
            )}
            <span>{health?.roads_status || 'Unknown'}</span>
          </div>
        </Card>
        <Card title="Signals">
          <div>{health?.signals_operational || 0} / {health?.signals_total || 0} operational</div>
        </Card>
        <Card title="Cameras">
          <div>{health?.cameras_online || 0} online</div>
        </Card>
      </div>
    </div>
  );
}