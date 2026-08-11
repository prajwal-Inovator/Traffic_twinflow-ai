import { useDashboardMetrics } from '../hooks/useAnalytics';
import { Card } from '../components/common/Card';
import { BaseChart } from '../components/charts/BaseChart';
import { Spinner } from '../components/common/Spinner';

export default function Analytics() {
  const { data: metrics, isLoading, isError, error } = useDashboardMetrics();

  if (isLoading) return <Spinner size="lg" className="h-screen" />;
  if (isError) return <div className="text-center text-red-500 py-10">Unable to load analytics: {String(error)}</div>;

  const pieOption = {
    tooltip: { trigger: 'item' },
    legend: { top: '5%', left: 'center' },
    series: [
      {
        name: 'Traffic Distribution',
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { value: metrics?.car_percentage || 60, name: 'Cars' },
          { value: metrics?.bus_percentage || 15, name: 'Buses' },
          { value: metrics?.truck_percentage || 20, name: 'Trucks' },
          { value: metrics?.emergency_percentage || 5, name: 'Emergency' },
        ],
      },
    ],
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Analytics</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="Vehicle Type Distribution">
          <BaseChart option={pieOption} height={300} />
        </Card>
        <Card title="Performance Metrics">
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Average Speed</span>
              <span className="font-semibold">{metrics?.avg_speed ?? '-'} km/h</span>
            </div>
            <div className="flex justify-between">
              <span>Total Vehicles Today</span>
              <span className="font-semibold">{metrics?.total_vehicles ?? '-'}</span>
            </div>
            <div className="flex justify-between">
              <span>Incidents Resolved</span>
              <span className="font-semibold">{metrics?.resolved_incidents ?? '-'}</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}