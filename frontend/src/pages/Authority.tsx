import { useJunctions, useLiveTraffic } from '../hooks/useTraffic';
import { useRecommendations } from '../hooks/useNegotiation';
import { Card } from '../components/common/Card';
import { Table } from '../components/common/Table'; // We'll create a simple table component
import { useState } from 'react';

export default function Authority() {
  const { data: junctions } = useJunctions();
  const { data: traffic } = useLiveTraffic();
  const { data: recommendations } = useRecommendations();
  const [selectedJunction, setSelectedJunction] = useState<string>('');

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Authority Dashboard</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Junction Overview">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">ID</th>
                  <th className="text-left p-2">Vehicles</th>
                  <th className="text-left p-2">Queue</th>
                  <th className="text-left p-2">Phase</th>
                </tr>
              </thead>
              <tbody>
                {junctions?.map((j: any) => (
                  <tr key={j.id} className="border-b hover:bg-slate-50 dark:hover:bg-slate-800">
                    <td className="p-2">{j.id}</td>
                    <td className="p-2">{j.vehicleCount}</td>
                    <td className="p-2">{j.queueLength}</td>
                    <td className="p-2 capitalize">{j.signalPhase}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card title="Master Recommendations">
          <div className="space-y-2">
            {recommendations?.map((rec: any) => (
              <div key={rec.junctionId} className="border-b pb-2">
                <div className="flex justify-between">
                  <span className="font-semibold">{rec.junctionId}</span>
                  <span className="text-xs bg-blue-100 dark:bg-blue-900 px-2 py-1 rounded">
                    Priority: {rec.priority}
                  </span>
                </div>
                <div className="text-sm">Green: {rec.greenTime}s | Red: {rec.redTime}s</div>
                <div className="text-xs text-slate-500">{rec.reason}</div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}