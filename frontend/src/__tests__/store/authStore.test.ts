// frontend/src/__tests__/store/authStore.test.ts
import { renderHook, act } from '@testing-library/react';
import { useAuthStore } from '../../store/authStore';
import { apiClient } from '../../api/client';
import { vi } from 'vitest';

vi.mock('../../api/client');

describe('authStore', () => {
  it('initializes with default state', () => {
    const { result } = renderHook(() => useAuthStore());
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
  });

  it('login sets user and token', async () => {
    const mockResponse = {
      data: {
        data: {
          user: { id: '1', email: 'test@test.com', role: 'admin' },
          accessToken: 'fake-token',
          refreshToken: 'fake-refresh'
        }
      }
    };
    (apiClient.post as any).mockResolvedValueOnce(mockResponse);

    const { result } = renderHook(() => useAuthStore());
    await act(async () => {
      await result.current.login('test@test.com', 'password');
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual({ id: '1', email: 'test@test.com', role: 'admin' });
  });

  it('logout clears state', () => {
    const { result } = renderHook(() => useAuthStore());
    act(() => {
      result.current.logout();
    });
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
  });
});