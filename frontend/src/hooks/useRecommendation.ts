// frontend/src/hooks/useRecommendation.ts
import { useQuery, useMutation } from '@tanstack/react-query';
import { recommendationApi } from '../api/endpoints';

export const useSpeedRecommendation = (junctionId: string, vehicleData?: any) => {
  return useMutation({
    mutationFn: () => recommendationApi.getRecommendation(junctionId, vehicleData),
  });
};

export const useLaneRecommendation = (junctionId: string, vehicleData?: any) => {
  return useMutation({
    mutationFn: () => recommendationApi.getLaneRecommendation(junctionId, vehicleData),
  });
};

export const useDepartureOptimization = (junctionId: string, vehicleData?: any) => {
  return useMutation({
    mutationFn: () => recommendationApi.getDepartureOptimization(junctionId, vehicleData),
  });
};