import { useEffect, useRef } from 'react';
import { socketManager } from '../api/socket';

export function useWebSocket<T = any>(
  event: string,
  callback: (data: T) => void,
  deps: any[] = []
) {
  const callbackRef = useRef(callback);
  callbackRef.current = callback;

  useEffect(() => {
    const handler = (data: T) => callbackRef.current(data);
    socketManager.on(event, handler);
    return () => {
      socketManager.off(event, handler);
    };
  }, [event, ...deps]);
}