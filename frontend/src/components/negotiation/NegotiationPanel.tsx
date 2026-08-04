import { Card } from '../common/Card';
import { MasterRecommendation } from '../../types/negotiation.types';
import { cn } from '../../utils/cn';

interface NegotiationPanelProps {
  recommendations: MasterRecommendation[];
  onApply?: (rec: MasterRecommendation) => void;
}

export const NegotiationPanel = ({ recommendations, onApply }: NegotiationPanelProps) => {
  if (!recommendations.length) {
    return (
      <Card>
        <div className="text-center text-slate-500 dark:text-slate-400 py-8">
          No active negotiations. Waiting for traffic data.
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {recommendations.map((rec) => (
        <Card
          key={rec.junctionId}
          title={`Junction ${rec.junctionId}`}
          subtitle={`Confidence: ${(rec.confidence * 100).toFixed(0)}%`}
          actions={
            <button
              onClick={() => onApply?.(rec)}
              className="text-xs bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded"
            >
              Apply
            </button>
          }
        >
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-slate-500 dark:text-slate-400">Green Time</span>
              <div className="font-medium">{rec.greenTime}s</div>
            </div>
            <div>
              <span className="text-slate-500 dark:text-slate-400">Red Time</span>
              <div className="font-medium">{rec.redTime}s</div>
            </div>
            <div>
              <span className="text-slate-500 dark:text-slate-400">Priority</span>
              <div className="font-medium">{(rec.priority * 100).toFixed(0)}%</div>
            </div>
            <div>
              <span className="text-slate-500 dark:text-slate-400">Reason</span>
              <div className="text-xs truncate" title={rec.reason}>
                {rec.reason}
              </div>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
};