import { useState } from 'react';
import { useCongestionForecast } from '../hooks/usePrediction';
import { useJunctions } from '../hooks/useTraffic';
import { Card } from '../components/common/Card';
import { CongestionChart } from '../components/charts/CongestionChart';
import { Spinner } from '../components/common/Spinner';

export default function TrafficPrediction() {
  const [selectedJunction, setSelectedJunction] = useState<string>('');
  const { data: junctions, isLoading: junctionsLoading } = useJunctions();
  const { data: forecast, isLoading: forecastLoading } = useCongestionForecast(selectedJunction, 30);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Traffic Prediction</h1>

      <Card title="Select Junction">
        <select
          className="w-full p-2 border rounded bg-white dark:bg-slate-800"
          value={selectedJunction}
          onChange={(e) => setSelectedJunction(e.target.value)}
        >
          <option value="">-- Select a junction --</option>
          {junctions?.map((j: any) => (
            <option key={j.id} value={j.id}>{j.name || j.id}</option>
          ))}
        </select>
      </Card>

      {selectedJunction && (
        <>
          {forecastLoading ? (
            <Spinner />
          ) : (
            <Card title={`Congestion Forecast for ${selectedJunction}`}>
              <CongestionChart data={forecast || []} />
            </Card>
          )}
        </>
      )}
    </div>
  );
}