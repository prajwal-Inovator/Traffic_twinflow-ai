import { useState } from 'react';
import { useSpeedRecommendation, useLaneRecommendation, useDepartureOptimization } from '../hooks/useRecommendation';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Spinner } from '../components/common/Spinner';

export default function Driver() {
  const [junctionId, setJunctionId] = useState('');
  const [vehicleData, setVehicleData] = useState({ speed: 30, type: 'car' });
  
  const speedRec = useSpeedRecommendation(junctionId, vehicleData);
  const laneRec = useLaneRecommendation(junctionId, vehicleData);
  const departureRec = useDepartureOptimization(junctionId, vehicleData);

  const handleGetRecommendations = () => {
    speedRec.mutate();
    laneRec.mutate();
    departureRec.mutate();
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Driver Recommendations</h1>

      <Card title="Vehicle & Route">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Junction ID</label>
            <input
              type="text"
              value={junctionId}
              onChange={(e) => setJunctionId(e.target.value)}
              className="w-full p-2 border rounded"
              placeholder="Enter junction ID"
            />
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