import { useEffect } from 'react';
import mapboxgl from 'mapbox-gl';
import { useMap } from '../../hooks/useMap';
import { cn } from '../../utils/cn';

interface TrafficLayerProps {
  className?: string;
}

export const TrafficLayer = ({ className }: TrafficLayerProps) => {
  const containerId = 'traffic-layer-map';
  const map = useMap(containerId, {
    style: 'mapbox://styles/mapbox/dark-v11',
    center: [77.2090, 28.6139],
    zoom: 12,
    interactive: false,
  });

  useEffect(() => {
    if (!map) return;

    map.on('load', () => {
      // This is a placeholder; you would load traffic flow data via GeoJSON
      // and add a line layer with color coding by speed.
      map.addSource('traffic-flow', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: [],
        },
      });

      map.addLayer({
        id: 'traffic-flow-layer',
        type: 'line',
        source: 'traffic-flow',
        paint: {
          'line-width': 4,
          'line-color': [
            'interpolate',
            ['linear'],
            ['get', 'speed'],
            0, '#ef4444',
            10, '#f59e0b',
            20, '#22c55e',
            30, '#3b82f6',
          ],
          'line-opacity': 0.8,
        },
      });
    });

    return () => {
      if (map.getLayer('traffic-flow-layer')) map.removeLayer('traffic-flow-layer');
      if (map.getSource('traffic-flow')) map.removeSource('traffic-flow');
    };
  }, [map]);

  return <div id={containerId} className={cn('w-full h-full', className)} />;
};