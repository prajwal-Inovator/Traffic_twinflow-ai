import { useState, useEffect } from 'react';
import { useSpeedRecommendation, useLaneRecommendation, useDepartureOptimization } from '../hooks/useRecommendation';
import { useJunctions } from '../hooks/useTraffic';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Spinner } from '../components/common/Spinner';

export default function Driver() {
  const [junctionId, setJunctionId] = useState('');
  const [vehicleData, setVehicleData] = useState({ speed: 30, type: 'car' });
  const { data: junctions, isLoading: junctionsLoading } = useJunctions();

  useEffect(() => {
    if (!junctionId && junctions?.[0]?.id) {
      setJunctionId(junctions[0].id);
    }
  }, [junctions, junctionId]);
  
  const speedRec = useSpeedRecommendation(junctionId, vehicleData);
  const laneRec = useLaneRecommendation(junctionId, vehicleData);
  const departureRec = useDepartureOptimization(junctionId, vehicleData);

  const handleGetRecommendations = () => {
    speedRec.mutate(undefined, { onError: (err) => console.log('Speed recommendation error', err) });
    laneRec.mutate(undefined, { onError: (err) => console.log('Lane recommendation error', err) });
    departureRec.mutate(undefined, { onError: (err) => console.log('Departure recommendation error', err) });
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Driver Recommendations</h1>

      <Card title="Vehicle & Route">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Junction ID</label>
            {junctionsLoading ? (
              <Spinner size="sm" />
            ) : (
              <select
                className="w-full p-2 border rounded bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
                value={junctionId}
                onChange={(e) => setJunctionId(e.target.value)}
              >
                <option value="">Select a junction</option>
                {junctions?.map((j: any) => (
                  <option key={j.id} value={j.id}>
                    {j.name || j.id}
                  </option>
                ))}
              </select>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Current Speed (km/h)</label>
            <input
              type="number"
              value={vehicleData.speed}
              onChange={(e) => setVehicleData({ ...vehicleData, speed: parseInt(e.target.value) })}
              className="w-full p-2 border rounded"
            />
          </div>
          <Button onClick={handleGetRecommendations} disabled={speedRec.isPending}>
            {speedRec.isPending ? <Spinner size="sm" /> : 'Get Recommendations'}
          </Button>
        </div>
      </Card>

      {speedRec.data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card title="Speed">
            <div className="text-2xl font-bold text-blue-500">{(speedRec.data?.data as any)?.optimal_speed ?? (speedRec.data?.data as any)?.optimalSpeed} km/h</div>
            <div className="text-sm text-slate-500">Expected delay: {(speedRec.data?.data as any)?.expected_delay ?? (speedRec.data?.data as any)?.expectedDelay}s</div>
          </Card>
          <Card title="Lane">
            <div className="text-2xl font-bold text-green-500">Lane {(laneRec.data?.data as any)?.optimal_lane ?? (laneRec.data?.data as any)?.optimalLane}</div>
            <div className="text-sm text-slate-500">Confidence: {(laneRec.data?.data as any)?.confidence}</div>
          </Card>
          <Card title="Departure">
            <div className="text-sm font-semibold">{new Date(((departureRec.data?.data as any)?.departure_time ?? (departureRec.data?.data as any)?.departureTime) || Date.now()).toLocaleTimeString()}</div>
            <div className="text-sm text-slate-500">Fuel saved: {(departureRec.data?.data as any)?.fuel_saved ?? (departureRec.data?.data as any)?.fuelSaved} L</div>
          </Card>
        </div>
      )}
    </div>
  );
}