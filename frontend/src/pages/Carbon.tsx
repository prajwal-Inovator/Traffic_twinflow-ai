import { useCarbonDashboard } from '../hooks/useCarbon';
import { Card } from '../components/common/Card';
import { CarbonChart } from '../components/charts/CarbonChart';
import { Spinner } from '../components/common/Spinner';

export default function Carbon() {
  const { data: metrics, isLoading } = useCarbonDashboard();

  if (isLoading) return <Spinner size="lg" className="h-screen" />;

  const data = [
    { date: 'Mon', co2: metrics?.daily_co2 || 0, fuel: metrics?.daily_fuel || 0 },
    // ... more days from API
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Carbon & Fuel Prediction</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card title="CO₂ Emissions">
          <div className="text-3xl font-bold text-red-500">{metrics?.total_co2 || 0} kg</div>
          <div className="text-sm text-slate-500">Today</div>
        </Card>
        <Card title="Fuel Consumption">
          <div className="text-3xl font-bold text-orange-500">{metrics?.total_fuel || 0} L</div>
          <div className="text-sm text-slate-500">Today</div>
        </Card>
        <Card title="Savings">
          <div className="text-3xl font-bold text-green-500">{metrics?.co2_saved || 0} kg</div>
          <div className="text-sm text-slate-500">CO₂ saved today</div>
        </Card>
      </div>
      <Card title="Trends">
        <CarbonChart data={data} />
      </Card>
    </div>
  );
}