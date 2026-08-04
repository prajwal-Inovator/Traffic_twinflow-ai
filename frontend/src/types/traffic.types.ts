export interface Vehicle {
  id: string;
  type: 'car' | 'bus' | 'truck' | 'motorcycle' | 'emergency';
  speed: number;
  heading: number;
  lat: number;
  lng: number;
  junctionId?: string;
  lane?: number;
}

export interface Junction {
  id: string;
  name: string;
  lat: number;
  lng: number;
  vehicleCount: number;
  queueLength: number;
  signalPhase: 'red' | 'yellow' | 'green';
  greenTime: number;
  redTime: number;
  emergencyStatus: boolean;
  busPriority: boolean;
  pollution: number; // AQI or CO2 index
  weather: 'clear' | 'rain' | 'fog' | 'snow';
  currentDelay: number; // seconds
  predictedVehicles: number; // next interval
}

export interface TrafficUpdate {
  timestamp: string;
  junctions: Junction[];
  vehicles: Vehicle[];
  incidents: Incident[];
}

export interface Incident {
  id: string;
  type: 'accident' | 'roadwork' | 'hazard' | 'congestion';
  severity: 'low' | 'medium' | 'high' | 'critical';
  lat: number;
  lng: number;
  description: string;
  startTime: string;
  endTime?: string;
}