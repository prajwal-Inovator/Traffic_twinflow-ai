import { create } from 'zustand';
import { TrafficUpdate, Junction, Vehicle, Incident } from '../types/traffic.types';
import { MasterRecommendation } from '../types/negotiation.types';

interface TrafficState {
  liveData: TrafficUpdate | null;
  junctions: Junction[];
  vehicles: Vehicle[];
  incidents: Incident[];
  recommendations: MasterRecommendation[];
  isLoading: boolean;
  error: string | null;
  setLiveData: (data: TrafficUpdate) => void;
  updateJunctions: (junctions: Junction[]) => void;
  updateVehicles: (vehicles: Vehicle[]) => void;
  updateIncidents: (incidents: Incident[]) => void;
  setRecommendations: (recs: MasterRecommendation[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useTrafficStore = create<TrafficState>((set) => ({
  liveData: null,
  junctions: [],
  vehicles: [],
  incidents: [],
  recommendations: [],
  isLoading: false,
  error: null,
  setLiveData: (data) =>
    set({
      liveData: data,
      junctions: data.junctions,
      vehicles: data.vehicles,
      incidents: data.incidents || [],
    }),
  updateJunctions: (junctions) => set({ junctions }),
  updateVehicles: (vehicles) => set({ vehicles }),
  updateIncidents: (incidents) => set({ incidents }),
  setRecommendations: (recommendations) => set({ recommendations }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
}));