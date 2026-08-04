// frontend/src/hooks/useSimulation.ts
import { useQuery, useMutation } from '@tanstack/react-query';
import { simulationApi } from '../api/endpoints';
import { socketManager, TrafficEvents } from '../api/socket';
import { useEffect } from 'react';

export const useRippleEffects = (junctionId: string, horizons?: number[]) => {
  const query = useQuery({
    queryKey: ['ripple', junctionId, horizons],
    queryFn: async () => {
      const resp = await simulationApi.getRippleEffects(junctionId, horizons);
      return resp.data.data;
    },
    enabled: !!junctionId,
    staleTime: 60000,
  });

  useEffect(() => {
    const handler = (data: any) => {
      // Invalidate to refetch
      query.refetch();
    };
    socketManager.on(TrafficEvents.RIPPLE, handler);
    return () => {
      socketManager.off(TrafficEvents.RIPPLE, handler);
    };
  }, [query]);

  return query;
};

export const useRunSimulation = () => {
  return useMutation({
    mutationFn: (params: any) => simulationApi.runSimulation(params),
  });
};