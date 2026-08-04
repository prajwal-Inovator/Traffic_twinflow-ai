// frontend/src/hooks/useAnalytics.ts
import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '../api/endpoints';

export const useDashboardMetrics = () => {
  return useQuery({
    queryKey: ['dashboardMetrics'],
    queryFn: async () => {
      const resp = await analyticsApi.getDashboardMetrics();
      return resp.data.data;
    },
    refetchInterval: 30000,
  });
};