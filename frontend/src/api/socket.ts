import { io, Socket } from 'socket.io-client';
import { TrafficUpdate } from '../types/traffic.types';
import { MasterRecommendation, RippleEffect } from '../types/negotiation.types';

class SocketManager {
  private socket: Socket | null = null;
  private listeners: Map<string, Set<Function>> = new Map();

  connect(token?: string) {
    if (this.socket?.connected) return;

    const socketUrl = import.meta.env.VITE_WS_URL;
    if (!socketUrl) {
      console.warn('[Socket] Missing VITE_WS_URL');
      return;
    }

    this.socket = io(socketUrl, {
      transports: ['websocket'],
      auth: token ? { token } : undefined,
      reconnection: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 1000,
    });

    this.socket.on('connect', () => {
      console.log('[Socket] Connected');
    });

    this.socket.on('disconnect', (reason) => {
      console.warn('[Socket] Disconnected:', reason);
    });

    // Generic event listener registration
    this.socket.onAny((event, ...args) => {
      const callbacks = this.listeners.get(event);
      if (callbacks) {
        callbacks.forEach((cb) => cb(...args));
      }
    });
  }

  on<T = any>(event: string, callback: (data: T) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
  }

  off(event: string, callback: Function) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.delete(callback);
      if (callbacks.size === 0) {
        this.listeners.delete(event);
      }
    }
  }

  emit(event: string, data: any) {
    if (this.socket) {
      this.socket.emit(event, data);
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }
}

export const socketManager = new SocketManager();

// Typed convenience events
export const TrafficEvents = {
  UPDATE: 'traffic:update',
  NEGOTIATION: 'negotiation:recommendation',
  RIPPLE: 'ripple:effect',
  INCIDENT: 'incident:alert',
};

export type TrafficUpdateEvent = (data: TrafficUpdate) => void;
export type RecommendationEvent = (data: MasterRecommendation[]) => void;
export type RippleEvent = (data: RippleEffect) => void;