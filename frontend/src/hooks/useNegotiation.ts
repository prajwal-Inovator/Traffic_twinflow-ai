// frontend/src/hooks/useNegotiation.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { negotiationApi } from '../api/endpoints';
import { socketManager, TrafficEvents } from '../api/socket';
import { useEffect } from 'react';
import { useTrafficStore } from '../store/trafficStore';
import { MasterRecommendation } from '../types/negotiation.types';

export const useRecommendations = (junctionId?: string) => {
  const { setRecommendations } = useTrafficStore();
  const queryClient = useQueryClient();

  const query = useQuery<MasterRecommendation[], Error>({
    queryKey: ['recommendations', junctionId],
    queryFn: async () => {
      const resp = await negotiationApi.getRecommendations(junctionId);
      return (resp.data.data as MasterRecommendation[]) || [];
    },
    refetchInterval: 5000,
  });

  useEffect(() => {
    if (query.data) {
      setRecommendations(query.data);
    }
  }, [query.data, setRecommendations]);

  // WebSocket for real‑time recommendations
  useEffect(() => {
    const handler = (data: any) => {
      setRecommendations(data);
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    };
    socketManager.on(TrafficEvents.NEGOTIATION, handler);
    return () => {
      socketManager.off(TrafficEvents.NEGOTIATION, handler);
    };
  }, [queryClient, setRecommendations]);

  return query;
};

export const useTriggerNegotiation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (junctionId: string) => negotiationApi.triggerNegotiation(junctionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    },
  });
};