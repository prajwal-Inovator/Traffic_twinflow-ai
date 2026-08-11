import { useQuery } from '@tanstack/react-query';
import { trafficApi } from '../api/endpoints';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Spinner } from '../components/common/Spinner';
import { AlertTriangle, CheckCircle } from 'lucide-react';

export default function Emergency() {
  const { data: incidents, refetch, isLoading, isError, error } = useQuery<any[], Error>({
    queryKey: ['emergencies'],
    queryFn: async () => {
      const resp = await trafficApi.getIncidents();
      return (resp.data.data as any[]) || [];
    },
    refetchInterval: 10000,
  });

  if (isLoading) return <Spinner size="lg" className="h-screen" />;
  if (isError) return <div className="text-center text-red-500 py-10">Unable to load emergency incidents: {String(error)}</div>;

  const activeEmergencies = incidents?.filter((i: any) => !i.resolved && i.severity === 'critical');

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Emergency Corridor</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="Active Emergencies">
          {activeEmergencies && activeEmergencies.length > 0 ? (
            activeEmergencies.map((inc: any) => (
              <div key={inc.id} className="flex items-center justify-between p-3 bg-red-50 dark:bg-red-900/20 rounded mb-2">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="text-red-500" />
                  <span>{inc.description}</span>
                </div>
                <Button variant="danger" size="sm" onClick={() => {
                  // Activate corridor
                  console.log('Activating corridor for', inc.id);
                }}>
                  Activate Corridor
                </Button>
              </div>
            ))
          ) : (
            <div className="text-center text-green-500 py-4">
              <CheckCircle className="inline mr-2" /> No active emergencies
            </div>
          )}
        </Card>

        <Card title="Emergency Response">
          <div className="space-y-2 text-sm">
            <div>Total incidents: {incidents?.length || 0}</div>
            <div>Resolved: {incidents?.filter((i: any) => i.resolved).length || 0}</div>
            <Button variant="outline" onClick={() => refetch()}>Refresh</Button>
          </div>
        </Card>
      </div>
    </div>
  );
}