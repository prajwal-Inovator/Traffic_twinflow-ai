import { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import { useMap } from '../../hooks/useMap';
import { useTrafficStore } from '../../store/trafficStore';
import { cn } from '../../utils/cn';

interface DigitalTwinMapProps {
  className?: string;
  interactive?: boolean;
}

export const DigitalTwinMap = ({ className, interactive = true }: DigitalTwinMapProps) => {
  const containerId = 'twinflow-map';
  const map = useMap(containerId, {
    style: 'mapbox://styles/mapbox/dark-v11',
    center: [77.2090, 28.6139],
    zoom: 12,
    pitch: 45,
    bearing: 0,
    interactive,
  });

  const { junctions, vehicles, incidents } = useTrafficStore();

  // Add sources/layers when map loads
  useEffect(() => {
    if (!map) return;

    map.on('load', () => {
      // Add junction markers
      map.addSource('junctions', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: [],
        },
      });

      // Add vehicles as points
      map.addSource('vehicles', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: [],
        },
      });

      // Add incident markers
      map.addSource('incidents', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: [],
        },
      });

      // Add layers for vehicles and junctions
      map.addLayer({
        id: 'junctions-layer',
        type: 'circle',
        source: 'junctions',
        paint: {
          'circle-radius': 8,
          'circle-color': '#3b82f6',
          'circle-stroke-width': 2,
          'circle-stroke-color': '#ffffff',
        },
      });

      map.addLayer({
        id: 'vehicles-layer',
        type: 'circle',
        source: 'vehicles',
        paint: {
          'circle-radius': 4,
          'circle-color': '#22c55e',
          'circle-stroke-width': 1,
          'circle-stroke-color': '#ffffff',
        },
      });

      map.addLayer({
        id: 'incidents-layer',
        type: 'circle',
        source: 'incidents',
        paint: {
          'circle-radius': 12,
          'circle-color': '#ef4444',
          'circle-stroke-width': 2,
          'circle-stroke-color': '#ffffff',
        },
      });
    });

    // Cleanup: remove sources and layers on unmount
    return () => {
      if (map.getLayer('junctions-layer')) map.removeLayer('junctions-layer');
      if (map.getLayer('vehicles-layer')) map.removeLayer('vehicles-layer');
      if (map.getLayer('incidents-layer')) map.removeLayer('incidents-layer');
      if (map.getSource('junctions')) map.removeSource('junctions');
      if (map.getSource('vehicles')) map.removeSource('vehicles');
      if (map.getSource('incidents')) map.removeSource('incidents');
    };
  }, [map]);

  // Update data when store changes
  useEffect(() => {
    if (!map) return;

    const updateSource = (sourceId: string, features: any[]) => {
      const source = map.getSource(sourceId) as mapboxgl.GeoJSONSource;
      if (source) {
        source.setData({
          type: 'FeatureCollection',
          features,
        });
      }
    };

    // Convert junctions to GeoJSON features
    const junctionFeatures = junctions.map((j) => ({
      type: 'Feature' as const,
      geometry: {
        type: 'Point',
        coordinates: [j.lng, j.lat],
      },
      properties: {
        id: j.id,
        name: j.name,
        vehicleCount: j.vehicleCount,
        queueLength: j.queueLength,
        signalPhase: j.signalPhase,
      },
    }));

    // Convert vehicles to features
    const vehicleFeatures = vehicles.map((v) => ({
      type: 'Feature' as const,
      geometry: {
        type: 'Point',
        coordinates: [v.lng, v.lat],
      },
      properties: {
        id: v.id,
        type: v.type,
        speed: v.speed,
        heading: v.heading,
      },
    }));

    // Convert incidents
    const incidentFeatures = incidents.map((inc) => ({
      type: 'Feature' as const,
      geometry: {
        type: 'Point',
        coordinates: [inc.lng, inc.lat],
      },
      properties: {
        id: inc.id,
        type: inc.type,
        severity: inc.severity,
        description: inc.description,
      },
    }));

    updateSource('junctions', junctionFeatures);
    updateSource('vehicles', vehicleFeatures);
    updateSource('incidents', incidentFeatures);
  }, [map, junctions, vehicles, incidents]);

  return <div id={containerId} className={cn('w-full h-full', className)} />;
};