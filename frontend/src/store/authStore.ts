import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { apiClient } from '../api/client';

interface AuthState {
  user: { id: string; email: string; role: 'admin' | 'authority' | 'driver' | 'emergency' } | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshAccessToken: (refreshToken: string) => Promise<string>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      login: async (email, password) => {
        try {
          const response = await apiClient.post('/auth/login', { email, password });
          const { user, accessToken, refreshToken } = response.data.data;
          set({ user, accessToken, refreshToken, isAuthenticated: true });
          const { socketManager } = await import('../api/socket');
          socketManager.connect(accessToken);
        } catch (error: any) {
          const message = error?.response?.data?.message || error?.message || 'Login failed';
          throw new Error(message);
        }
      },

      logout: async () => {
        set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false });
        const { socketManager } = await import('../api/socket');
        socketManager.disconnect();
        // Optionally call logout API
        apiClient.post('/auth/logout').catch(() => {});
      },

      refreshAccessToken: async (refreshToken) => {
        const response = await apiClient.post('/auth/refresh', { refreshToken });
        const { accessToken } = response.data.data;
        set({ accessToken });
        return accessToken;
      },
    }),
    {
      name: 'twinflow-auth',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);