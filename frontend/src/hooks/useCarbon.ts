// frontend/src/hooks/useCarbon.ts
import { useQuery } from '@tanstack/react-query';
import { carbonApi } from '../api/endpoints';

export const useCarbonReport = (from?: string, to?: string) => {
  return useQuery({
    queryKey: ['carbonReport', from, to],
    queryFn: async () => {
      const resp = await carbonApi.getReport(from, to);
      return resp.data.data;
    },
    staleTime: 300000,
  });
};

export const useCarbonDashboard = () => {
  return useQuery<any, Error>({
    queryKey: ['carbonDashboard'],
    queryFn: async () => {
      const resp = await carbonApi.getDashboardMetrics();
      return resp.data.data;
    },
    refetchInterval: 60000,
  });
};