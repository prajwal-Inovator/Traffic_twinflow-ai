import { useDashboardMetrics } from '../hooks/useAnalytics';
import { useLiveTraffic } from '../hooks/useTraffic';
import { Card } from '../components/common/Card';
import { CongestionChart } from '../components/charts/CongestionChart';
import { CarbonChart } from '../components/charts/CarbonChart';
import { Spinner } from '../components/common/Spinner';
import { useTrafficStore } from '../store/trafficStore';
import { AlertTriangle, Car, Clock, Leaf } from 'lucide-react';

export default function Dashboard() {
  const { data: metrics, isLoading: metricsLoading } = useDashboardMetrics();
  const { data: traffic, isLoading: trafficLoading } = useLiveTraffic();
  const { incidents } = useTrafficStore();

  if (metricsLoading || trafficLoading) {
    return <Spinner size="lg" className="h-screen" />;
  }

  const stats = [
    { label: 'Live Vehicles', value: traffic?.vehicles?.length || 0, icon: Car },
    { label: 'Active Incidents', value: incidents?.filter(i => !i.resolved).length || 0, icon: AlertTriangle },
    { label: 'Avg Speed', value: metrics?.average_speed || 0, icon: Clock, suffix: ' km/h' },
    { label: 'CO₂ Saved Today', value: metrics?.co2_saved_today || 0, icon: Leaf, suffix: ' kg' },
  ];

  // Sample congestion data for chart (we can use real predictions)
  const congestionData = [
    { timestamp: '08:00', congestion: 45 },
    { timestamp: '08:30', congestion: 60 },
    { timestamp: '09:00', congestion: 78 },
    { timestamp: '09:30', congestion: 85 },
    { timestamp: '10:00', congestion: 70 },
    { timestamp: '10:30', congestion: 55 },
    { timestamp: '11:00', congestion: 40 },
  ];

  const carbonData = [
    { date: 'Mon', co2: 120, fuel: 45 },
    { date: 'Tue', co2: 135, fuel: 50 },
    { date: 'Wed', co2: 110, fuel: 40 },
    { date: 'Thu', co2: 150, fuel: 55 },
    { date: 'Fri', co2: 170, fuel: 60 },
    { date: 'Sat', co2: 90, fuel: 30 },
    { date: 'Sun', co2: 80, fuel: 25 },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-slate-500 dark:text-slate-400">{stat.label}</div>
                <div className="text-2xl font-bold mt-1">
                  {stat.value}{stat.suffix || ''}
                </div>
              </div>
              <stat.icon className="w-8 h-8 text-primary-500" />
            </div>
          </Card>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Congestion Forecast">
          <CongestionChart data={congestionData} />
        </Card>
        <Card title="Carbon & Fuel Savings">
          <CarbonChart data={carbonData} />
        </Card>
      </div>

      {/* Recent Incidents */}
      <Card title="Recent Incidents">
        {incidents && incidents.length > 0 ? (
          <div className="space-y-2">
            {incidents.slice(0, 5).map((inc) => (
              <div key={inc.id} className="flex items-center justify-between p-2 bg-slate-50 dark:bg-slate-800 rounded">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${
                    inc.severity === 'critical' ? 'bg-red-500' :
                    inc.severity === 'high' ? 'bg-orange-500' :
                    inc.severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                  }`} />
                  <span>{inc.description}</span>
                </div>
                <span className="text-xs text-slate-500">{new Date(inc.start_time).toLocaleTimeString()}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center text-slate-500 py-4">No recent incidents</div>
        )}
      </Card>
    </div>
  );
}