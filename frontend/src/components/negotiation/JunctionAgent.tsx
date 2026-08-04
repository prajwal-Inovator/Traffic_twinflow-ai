import { Card } from '../common/Card';
import { Junction } from '../../types/traffic.types';
import { cn } from '../../utils/cn';

interface JunctionAgentProps {
  junction: Junction;
  onTriggerNegotiation?: (id: string) => void;
}

export const JunctionAgent = ({ junction, onTriggerNegotiation }: JunctionAgentProps) => {
  const signalColor = {
    red: 'bg-red-500',
    yellow: 'bg-yellow-500',
    green: 'bg-green-500',
  }[junction.signalPhase] || 'bg-gray-500';

  return (
    <Card
      title={junction.name || `Junction ${junction.id}`}
      subtitle={`${junction.vehicleCount} vehicles · ${junction.queueLength} queue`}
      actions={
        <button
          onClick={() => onTriggerNegotiation?.(junction.id)}
          className="text-xs bg-primary-600 hover:bg-primary-700 text-white px-3 py-1 rounded"
        >
          Negotiate
        </button>
      }
    >
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div>
          <span className="text-slate-500 dark:text-slate-400">Signal</span>
          <div className="flex items-center gap-2 mt-1">
            <span className={cn('w-3 h-3 rounded-full', signalColor)} />
            <span className="capitalize">{junction.signalPhase}</span>
          </div>
        </div>
        <div>
          <span className="text-slate-500 dark:text-slate-400">Delay</span>
          <div className="font-medium">{junction.currentDelay}s</div>
        </div>
        <div>
          <span className="text-slate-500 dark:text-slate-400">Pollution</span>
          <div className="font-medium">{junction.pollution} AQI</div>
        </div>
        <div>
          <span className="text-slate-500 dark:text-slate-400">Predicted</span>
          <div className="font-medium">{junction.predictedVehicles} vehicles</div>
        </div>
      </div>
    </Card>
  );
};