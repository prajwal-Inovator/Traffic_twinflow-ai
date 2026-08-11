import { apiClient } from './client';
import { ApiResponse, PaginatedResponse } from '../types/api.types';
import { TrafficUpdate, Junction, Incident, Vehicle } from '../types/traffic.types';
import { MasterRecommendation, RippleEffect } from '../types/negotiation.types';

export const trafficApi = {
  getLiveTraffic: () =>
    apiClient.get<ApiResponse<TrafficUpdate>>('/v1/traffic/live'),

  getJunctions: (params?: { lat?: number; lng?: number; radius?: number }) =>
    apiClient.get<ApiResponse<Junction[]>>('/junctions', { params }),

  getIncidents: () =>
    apiClient.get<ApiResponse<Incident[]>>('/emergency'),

  getVehicles: () =>
    apiClient.get<ApiResponse<Vehicle[]>>('/v1/traffic/vehicles'),
};

export const predictionApi = {
  getCongestionForecast: (junctionId: string, minutes: number = 30) =>
    apiClient.get<ApiResponse<{ timestamp: string; congestion: number }[]>>(
      `/v1/prediction/congestion/${junctionId}`,
      { params: { minutes } }
    ),
};

export const negotiationApi = {
  getRecommendations: (junctionId?: string) =>
    apiClient.get<ApiResponse<MasterRecommendation[]>>('/negotiation', {
      params: { junctionId },
    }),
  triggerNegotiation: (junctionId: string) =>
    apiClient.post<ApiResponse<{ negotiationId: string }>>(
      `/negotiation/trigger/${junctionId}`
    ),
};

export const simulationApi = {
  runSimulation: (params: { duration: number; junctionIds?: string[] }) =>
    apiClient.post<ApiResponse<{ simulationId: string }>>('/v1/simulation/run', params),
  getRippleEffects: (junctionId: string, horizons?: number[]) =>
    apiClient.get<ApiResponse<RippleEffect[]>>(`/v1/simulation/ripple/${junctionId}`, {
      params: { horizons: horizons?.join(',') },
    }),
};

export const carbonApi = {
  getReport: (from?: string, to?: string) =>
    apiClient.get<ApiResponse<any>>('/carbon/report', { params: { from, to } }),
  getDashboardMetrics: () =>
    apiClient.get<ApiResponse<any>>('/carbon'),
};

export const recommendationApi = {
  getRecommendation: (junctionId: string, vehicleData?: any) =>
    apiClient.post<ApiResponse<any>>(`/v1/recommendation/${junctionId}`, vehicleData || {}),
  getLaneRecommendation: (junctionId: string, vehicleData?: any) =>
    apiClient.post<ApiResponse<any>>(`/v1/recommendation/lane/${junctionId}`, vehicleData || {}),
  getDepartureOptimization: (junctionId: string, vehicleData?: any) =>
    apiClient.post<ApiResponse<any>>(`/v1/recommendation/departure/${junctionId}`, vehicleData || {}),
};

export const infrastructureApi = {
  getHealth: () =>
    apiClient.get<ApiResponse<any>>('/infrastructure'),
  getRoads: () =>
    apiClient.get<ApiResponse<any>>('/infrastructure/roads'),
};

export const analyticsApi = {
  getDashboardMetrics: () =>
    apiClient.get<ApiResponse<any>>('/analytics'),
};
