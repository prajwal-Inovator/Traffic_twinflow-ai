// frontend/src/hooks/useTraffic.ts
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { trafficApi } from '../api/endpoints';
import { useTrafficStore } from '../store/trafficStore';
import { useEffect } from 'react';
import { socketManager, TrafficEvents } from '../api/socket';
import { TrafficUpdate, Junction } from '../types/traffic.types';

export const useLiveTraffic = () => {
  const { setLiveData, setLoading, setError } = useTrafficStore();
  const queryClient = useQueryClient();

  const query = useQuery<TrafficUpdate, Error>({
    queryKey: ['liveTraffic'],
    queryFn: async () => {
      const resp = await trafficApi.getLiveTraffic();
      return (resp.data.data as TrafficUpdate) || {
        timestamp: new Date().toISOString(),
        junctions: [],
        vehicles: [],
        incidents: [],
      };
    },
    refetchInterval: 10000, // 10 seconds
    staleTime: 5000,
  });

  // Update store when data arrives
  useEffect(() => {
    if (query.data) {
      setLiveData(query.data);
    }
  }, [query.data, setLiveData]);

  // WebSocket real‑time updates
  useEffect(() => {
    const handler = (data: any) => {
      setLiveData(data);
      queryClient.invalidateQueries({ queryKey: ['liveTraffic'] });
    };
    socketManager.on(TrafficEvents.UPDATE, handler);
    return () => {
      socketManager.off(TrafficEvents.UPDATE, handler);
    };
  }, [queryClient, setLiveData]);

  return query;
};

export const useJunctions = () => {
  return useQuery<Junction[], Error>({
    queryKey: ['junctions'],
    queryFn: async () => {
      const resp = await trafficApi.getJunctions();
      return (resp.data.data as Junction[]) || [];
    },
    staleTime: 60000,
  });
};

export const useIncidents = () => {
  return useQuery({
    queryKey: ['incidents'],
    queryFn: async () => {
      const resp = await trafficApi.getIncidents();
      return resp.data.data;
    },
    refetchInterval: 30000,
  });
};