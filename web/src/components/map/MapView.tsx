import { useEffect, useRef } from 'react';
import maplibregl, { type StyleSpecification } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { EUDR_COLOR, EUDR_LABEL, fmtHa, fmtScore } from '@/lib/format';

// Imagerie satellite Esri (libre, sans clé) — on voit réellement le couvert forestier.
const SAT_STYLE: StyleSpecification = {
  version: 8,
  sources: {
    esri: {
      type: 'raster',
      tiles: [
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      ],
      tileSize: 256,
      attribution: 'Imagerie © Esri · Maxar · Earthstar Geographics',
      maxzoom: 18,
    },
    labels: {
      type: 'raster',
      tiles: [
        'https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
      ],
      tileSize: 256,
      maxzoom: 18,
    },
  },
  layers: [
    { id: 'bg', type: 'background', paint: { 'background-color': '#04160f' } },
    { id: 'esri', type: 'raster', source: 'esri', paint: { 'raster-opacity': 0.95, 'raster-saturation': -0.15 } },
    { id: 'labels', type: 'raster', source: 'labels', paint: { 'raster-opacity': 0.5 } },
  ],
};

interface Props {
  parcels?: GeoJSON.FeatureCollection;
  protectedAreas?: GeoJSON.FeatureCollection;
  showProtected?: boolean;
  onSelect?: (props: Record<string, unknown>) => void;
  className?: string;
}

export function MapView({
  parcels,
  protectedAreas,
  showProtected = true,
  onSelect,
  className,
}: Props) {
  const container = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);

  useEffect(() => {
    if (!container.current || map.current) return;
    const m = new maplibregl.Map({
      container: container.current,
      style: SAT_STYLE,
      center: [-7.49, 6.55],
      zoom: 9,
      attributionControl: { compact: true },
    });
    m.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
    m.on('load', () => {
      m.addSource('protected', { type: 'geojson', data: emptyFC() });
      m.addLayer({
        id: 'protected-fill',
        type: 'fill',
        source: 'protected',
        paint: { 'fill-color': '#C0392B', 'fill-opacity': 0.08 },
      });
      m.addLayer({
        id: 'protected-line',
        type: 'line',
        source: 'protected',
        paint: { 'line-color': '#C0392B', 'line-opacity': 0.5, 'line-dasharray': [2, 2] },
      });

      m.addSource('parcels', { type: 'geojson', data: emptyFC() });
      m.addLayer({
        id: 'parcels-fill',
        type: 'fill',
        source: 'parcels',
        paint: {
          'fill-color': [
            'match',
            ['get', 'eudr_status'],
            'compliant',
            EUDR_COLOR.compliant,
            'at_risk',
            EUDR_COLOR.at_risk,
            'non_compliant',
            EUDR_COLOR.non_compliant,
            EUDR_COLOR.unassessed,
          ],
          'fill-opacity': 0.55,
        },
      });
      m.addLayer({
        id: 'parcels-line',
        type: 'line',
        source: 'parcels',
        paint: { 'line-color': '#F4EAD5', 'line-opacity': 0.35, 'line-width': 1 },
      });

      m.on('mouseenter', 'parcels-fill', () => (m.getCanvas().style.cursor = 'pointer'));
      m.on('mouseleave', 'parcels-fill', () => (m.getCanvas().style.cursor = ''));
      m.on('click', 'parcels-fill', (e) => {
        const f = e.features?.[0];
        if (!f) return;
        const p = f.properties as Record<string, unknown>;
        onSelect?.(p);
        new maplibregl.Popup({ closeButton: false, className: 'cs-popup' })
          .setLngLat(e.lngLat)
          .setHTML(
            `<div style="font:13px Inter,sans-serif;color:#F4EAD5">
               <strong style="color:#fff">${p.code ?? ''}</strong><br/>
               ${p.producer ?? '—'}<br/>
               ${fmtHa(Number(p.area_ha))} · score ${fmtScore(p.score == null ? null : Number(p.score))}<br/>
               <span style="color:${EUDR_COLOR[String(p.eudr_status)] ?? '#9AA0A6'}">
                 ${EUDR_LABEL[String(p.eudr_status)] ?? p.eudr_status}
               </span>
             </div>`,
          )
          .addTo(m);
      });
    });
    map.current = m;

    const ro = new ResizeObserver(() => m.resize());
    ro.observe(container.current);
    const onVisible = () => {
      if (!document.hidden) m.triggerRepaint();
    };
    document.addEventListener('visibilitychange', onVisible);

    return () => {
      ro.disconnect();
      document.removeEventListener('visibilitychange', onVisible);
      m.remove();
      map.current = null;
    };
  }, [onSelect]);

  useEffect(() => {
    const m = map.current;
    if (!m || !parcels) return;
    const apply = () => {
      (m.getSource('parcels') as maplibregl.GeoJSONSource | undefined)?.setData(parcels);
      const b = bounds(parcels);
      if (b) m.fitBounds(b, { padding: 48, maxZoom: 13, duration: 600 });
    };
    if (m.isStyleLoaded()) apply();
    else m.once('load', apply);
  }, [parcels]);

  useEffect(() => {
    const m = map.current;
    if (!m) return;
    const apply = () => {
      (m.getSource('protected') as maplibregl.GeoJSONSource | undefined)?.setData(
        showProtected && protectedAreas ? protectedAreas : emptyFC(),
      );
    };
    if (m.isStyleLoaded()) apply();
    else m.once('load', apply);
  }, [protectedAreas, showProtected]);

  return <div ref={container} className={className ?? 'h-[420px] w-full rounded-2xl'} />;
}

function emptyFC(): GeoJSON.FeatureCollection {
  return { type: 'FeatureCollection', features: [] };
}

function bounds(fc: GeoJSON.FeatureCollection): maplibregl.LngLatBoundsLike | null {
  let minX = 180,
    minY = 90,
    maxX = -180,
    maxY = -90,
    seen = false;
  const visit = (coords: GeoJSON.Position[]) => {
    for (const [x, y] of coords) {
      seen = true;
      minX = Math.min(minX, x);
      minY = Math.min(minY, y);
      maxX = Math.max(maxX, x);
      maxY = Math.max(maxY, y);
    }
  };
  for (const f of fc.features) {
    const g = f.geometry;
    if (g.type === 'Polygon') g.coordinates.forEach(visit);
    else if (g.type === 'MultiPolygon') g.coordinates.forEach((p) => p.forEach(visit));
  }
  return seen
    ? [
        [minX, minY],
        [maxX, maxY],
      ]
    : null;
}
