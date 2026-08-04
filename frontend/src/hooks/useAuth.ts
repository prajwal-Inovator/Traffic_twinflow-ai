import { useAuthStore } from '../store/authStore';

export const useAuth = () => {
  const { user, isAuthenticated, login, logout, refreshAccessToken } = useAuthStore();
  return { user, isAuthenticated, login, logout, refreshAccessToken };
};