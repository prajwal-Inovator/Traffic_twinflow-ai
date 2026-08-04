import { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';

export const useMap = (containerId: string, options: Partial<mapboxgl.MapboxOptions>) => {
  const [map, setMap] = useState<mapboxgl.Map | null>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    if (!containerId || mapRef.current) return;

    const token = import.meta.env.VITE_MAPBOX_TOKEN;
    if (!token) {
      console.warn('Missing VITE_MAPBOX_TOKEN');
      return;
    }

    mapboxgl.accessToken = token;
    const mapInstance = new mapboxgl.Map({
      container: containerId,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: [77.2090, 28.6139], // Delhi (default)
      zoom: 12,
      ...options,
    });

    mapInstance.on('load', () => {
      setMap(mapInstance);
    });

    mapRef.current = mapInstance;

    return () => {
      mapInstance.remove();
      mapRef.current = null;
      setMap(null);
    };
  }, [containerId, options]);

  return map;
};