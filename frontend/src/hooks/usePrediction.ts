// frontend/src/hooks/usePrediction.ts
import { useQuery } from '@tanstack/react-query';
import { predictionApi } from '../api/endpoints';

export const useCongestionForecast = (junctionId: string, minutes: number = 30) => {
  return useQuery({
    queryKey: ['congestion', junctionId, minutes],
    queryFn: async () => {
      const resp = await predictionApi.getCongestionForecast(junctionId, minutes);
      return resp.data.data;
    },
    enabled: !!junctionId,
    staleTime: 60000,
  });
};