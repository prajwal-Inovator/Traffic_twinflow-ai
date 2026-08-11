// frontend/src/hooks/useCarbon.ts
import { useQuery } from '@tanstack/react-query';
import { carbonApi } from '../api/endpoints';

export const useCarbonReport = (from?: string, to?: string) => {
  return useQuery({
    queryKey: ['carbonReport', from, to],
    queryFn: async () => {
      const resp = await carbonApi.getReport(from, to);\r\n      console.log('Carbon report response', resp.data);\r\n      if (!resp.data?.data) {\r\n        console.error('Carbon report API returned empty response', resp.data);\r\n      }\r\n      return resp.data.data;
    },
    staleTime: 300000,
  });
};

export const useCarbonDashboard = () => {
  return useQuery<any, Error>({
    queryKey: ['carbonDashboard'],
    queryFn: async () => {
      const resp = await carbonApi.getDashboardMetrics();\r\n      console.log('Carbon dashboard response', resp.data);\r\n      if (!resp.data?.data) {\r\n        console.error('Carbon API returned empty response', resp.data);\r\n      }\r\n      return resp.data.data;
    },
    refetchInterval: 60000,
  });
};
