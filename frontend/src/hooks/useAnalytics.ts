// frontend/src/hooks/useAnalytics.ts
import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '../api/endpoints';

export const useDashboardMetrics = () => {
  return useQuery<any, Error>({
    queryKey: ['dashboardMetrics'],
    queryFn: async () => {
      const resp = await analyticsApi.getDashboardMetrics();\r\n      console.log('Analytics dashboard response', resp.data);\r\n      if (!resp.data?.data) {\r\n        console.error('Analytics API returned empty response', resp.data);\r\n      }\r\n      return resp.data.data;
    },
    refetchInterval: 30000,
  });
};
