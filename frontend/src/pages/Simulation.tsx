import { useState } from 'react';
import { useRunSimulation, useRippleEffects } from '../hooks/useSimulation';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Spinner } from '../components/common/Spinner';

export default function Simulation() {
  const [junctionId, setJunctionId] = useState('');
  const [duration, setDuration] = useState(300);
  const { mutate: runSim, isPending, data: simResult } = useRunSimulation();
  const { data: rippleData } = useRippleEffects(junctionId, [5, 10, 20, 30]);

  const handleRun = () => {
    runSim({ junctionId, duration });
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Traffic Simulation (SUMO)</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="Simulation Controls">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Junction ID</label>
              <input
                type="text"
                value={junctionId}
                onChange={(e) => setJunctionId(e.target.value)}
                className="w-full p-2 border rounded bg-white dark:bg-slate-800"
                placeholder="Enter junction ID"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Duration (seconds)</label>
              <input
                type="number"
                value={duration}
                onChange={(e) => setDuration(parseInt(e.target.value))}
                className="w-full p-2 border rounded bg-white dark:bg-slate-800"
                min={60}
                max={3600}
              />
            </div>
            <Button onClick={handleRun} disabled={isPending || !junctionId}>
              {isPending ? <Spinner size="sm" /> : 'Run Simulation'}
            </Button>
          </div>
        </Card>

        <Card title="Simulation Results">
          {simResult ? (
            <div className="space-y-2 text-sm">
              <div>Simulation ID: {simResult.simulation_id}</div>
              <div>Status: {simResult.status}</div>
              <div>Time: {new Date().toLocaleString()}</div>
            </div>
          ) : (
            <div className="text-slate-400">No results yet</div>
          )}
        </Card>
      </div>

      {rippleData && rippleData.length > 0 && (
        <Card title="Ripple Effects">
          <div className="space-y-4">
            {rippleData.map((effect: any) => (
              <div key={effect.id} className="border-b pb-2">
                <div className="flex justify-between">
                  <span>Horizon: {effect.time_horizon} min</span>
                  <span>Congestion: {effect.predicted_congestion.toFixed(1)}%</span>
                </div>
                <div className="text-xs text-slate-500">
                  Affected: {effect.affected_junctions.join(', ')}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}