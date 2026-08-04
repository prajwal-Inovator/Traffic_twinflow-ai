export interface NegotiationMessage {
  junctionId: string;
  timestamp: string;
  data: JunctionNegotiationData;
}

export interface JunctionNegotiationData {
  vehicleCount: number;
  queueLength: number;
  signalPhase: 'red' | 'yellow' | 'green';
  predictedVehicles: number;
  emergencyStatus: boolean;
  busPriority: boolean;
  pollution: number;
  weather: string;
  currentDelay: number;
}

export interface MasterRecommendation {
  junctionId: string;
  greenTime: number;
  redTime: number;
  priority: number; // 0-1
  confidence: number; // 0-1
  reason: string;
  timestamp: string;
}

export interface RippleEffect {
  junctionId: string;
  timeHorizon: 5 | 10 | 20 | 30; // minutes
  predictedCongestion: number; // 0-100
  affectedJunctions: string[];
  propagationStrength: number;
}