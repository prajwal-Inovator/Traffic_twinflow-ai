import { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import { useMap } from '../../hooks/useMap';
import { RippleEffect } from '../../types/negotiation.types';
import { cn } from '../../utils/cn';

interface RippleHeatmapProps {
  rippleData: RippleEffect | null;
  className?: string;
}

export const RippleHeatmap = ({ rippleData, className }: RippleHeatmapProps) => {
  const containerId = 'ripple-heatmap';
  const map = useMap(containerId, {
    style: 'mapbox://styles/mapbox/dark-v11',
    center: [77.2090, 28.6139],
    zoom: 12,
    interactive: false,
  });

  const heatmapLayerId = 'ripple-heat';

  useEffect(() => {
    if (!map) return;

    map.on('load', () => {
      map.addSource('ripple-source', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: [],
        },
      });

      map.addLayer(
        {
          id: heatmapLayerId,
          type: 'heatmap',
          source: 'ripple-source',
          paint: {
            'heatmap-weight': [
              'interpolate',
              ['linear'],
              ['get', 'strength'],
              0, 0,
              1, 1,
            ],
            'heatmap-intensity': 0.8,
            'heatmap-color': [
              'interpolate',
              ['linear'],
              ['heatmap-density'],
              0, 'rgba(0,0,255,0)',
              0.2, 'rgba(0,0,255,0.5)',
              0.4, 'rgba(0,255,255,0.7)',
              0.6, 'rgba(255,255,0,0.8)',
              0.8, 'rgba(255,165,0,0.9)',
              1, 'rgba(255,0,0,1)',
            ],
            'heatmap-radius': 30,
            'heatmap-opacity': 0.7,
          },
        },
        'waterway-label'
      );
    });

    return () => {
      if (map.getLayer(heatmapLayerId)) map.removeLayer(heatmapLayerId);
      if (map.getSource('ripple-source')) map.removeSource('ripple-source');
    };
  }, [map]);

  // Update heatmap data when rippleData changes
  useEffect(() => {
    if (!map || !rippleData) return;

    const source = map.getSource('ripple-source') as mapboxgl.GeoJSONSource;
    if (!source) return;

    // Build features from affected junctions with strength
    const features = rippleData.affectedJunctions.map((jid) => {
      // In real implementation, we would get lat/lng from a junction store
      // For now, we generate dummy points around the center
      const lat = 28.6139 + (Math.random() - 0.5) * 0.02;
      const lng = 77.2090 + (Math.random() - 0.5) * 0.02;
      return {
        type: 'Feature' as const,
        geometry: {
          type: 'Point',
          coordinates: [lng, lat],
        },
        properties: {
          strength: rippleData.propagationStrength * (0.5 + Math.random() * 0.5),
        },
      };
    });

    source.setData({
      type: 'FeatureCollection',
      features,
    });
  }, [map, rippleData]);

  return <div id={containerId} className={cn('w-full h-full', className)} />;
};