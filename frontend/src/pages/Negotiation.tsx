import { useRecommendations, useTriggerNegotiation } from '../hooks/useNegotiation';
import { useJunctions } from '../hooks/useTraffic';
import { JunctionAgent } from '../components/negotiation/JunctionAgent';
import { NegotiationPanel } from '../components/negotiation/NegotiationPanel';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { useState } from 'react';

export default function Negotiation() {
  const { data: recommendations } = useRecommendations();
  const { data: junctions } = useJunctions();
  const { mutate: triggerNegotiation } = useTriggerNegotiation();
  const [selectedJunction, setSelectedJunction] = useState<string | null>(null);

  const handleTrigger = (id: string) => {
    triggerNegotiation(id);
    setSelectedJunction(id);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Junction Negotiation</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Junction Agents */}
        <div>
          <Card title="Junction Agents">
            <div className="space-y-4 max-h-[600px] overflow-y-auto">
              {junctions?.map((j: any) => (
                <JunctionAgent
                  key={j.id}
                  junction={j}
                  onTriggerNegotiation={handleTrigger}
                />
              ))}
            </div>
          </Card>
        </div>

        {/* Recommendations */}
        <div>
          <Card title="Master Recommendations">
            <NegotiationPanel
              recommendations={recommendations || []}
              onApply={(rec) => {
                // In production, apply recommendation via API
                console.log('Applying:', rec);
              }}
            />
          </Card>
        </div>
      </div>
    </div>
  );
}