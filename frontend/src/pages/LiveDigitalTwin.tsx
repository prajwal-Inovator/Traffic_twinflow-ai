import { DigitalTwinMap } from '../components/map/DigitalTwinMap';
import { RippleHeatmap } from '../components/map/RippleHeatmap';
import { TrafficLayer } from '../components/map/TrafficLayer';
import { useLiveTraffic } from '../hooks/useTraffic';
import { useRecommendations } from '../hooks/useNegotiation';
import { useRippleEffects } from '../hooks/useSimulation';
import { Card } from '../components/common/Card';
import { useState } from 'react';

export default function LiveDigitalTwin() {
  const { data: traffic } = useLiveTraffic();
  const { data: recommendations } = useRecommendations();
  const [selectedJunction, setSelectedJunction] = useState<string | null>(null);
  const { data: rippleData } = useRippleEffects(selectedJunction || '', [5, 10, 20, 30]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Live Digital Twin</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map */}
        <div className="lg:col-span-2 h-[600px]">
          <Card className="h-full p-0 overflow-hidden">
            <DigitalTwinMap className="w-full h-full" />
          </Card>
        </div>

        {/* Side panel */}
        <div className="space-y-4">
          <Card title="Traffic Overview">
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Vehicles:</span>
                <span className="font-semibold">{traffic?.vehicles?.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Junctions:</span>
                <span className="font-semibold">{traffic?.junctions?.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Active Incidents:</span>
                <span className="font-semibold text-red-500">{traffic?.incidents?.filter(i => !i.resolved).length || 0}</span>
              </div>
            </div>
          </Card>

          {/* Ripple Heatmap */}
          <Card title="Ripple Heatmap" className="h-[300px]">
            {selectedJunction ? (
              <RippleHeatmap rippleData={rippleData?.[0] || null} className="w-full h-full" />
            ) : (
              <div className="flex items-center justify-center h-full text-slate-400">
                Select a junction to view ripple effects
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}