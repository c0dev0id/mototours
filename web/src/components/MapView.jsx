import { useEffect, useRef, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { parseGpx, dayColor } from '../lib/gpxParser.js'
import { fetchOsrmRoute } from '../lib/routeCalculator.js'
import styles from './MapView.module.css'

// ---------------------------------------------------------------------------
// SVG waypoint icons
// ---------------------------------------------------------------------------

const ICON_SIZE = [28, 28]
const ICON_ANCHOR = [14, 14]

function svgIcon(svgContent, color) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 28 28">${svgContent}</svg>`
}

const ICONS = {
  START: (color = '#2ecc71') => svgIcon(
    `<circle cx="14" cy="14" r="12" fill="${color}" stroke="#fff" stroke-width="2"/>
     <polygon points="11,9 11,19 20,14" fill="#fff"/>`,
    color,
  ),
  END: (color = '#e74c3c') => svgIcon(
    `<circle cx="14" cy="14" r="12" fill="${color}" stroke="#fff" stroke-width="2"/>
     <rect x="9" y="9" width="10" height="10" fill="#fff" rx="1"/>`,
    color,
  ),
  VIA: (color = '#3498db') => svgIcon(
    `<circle cx="14" cy="14" r="12" fill="${color}" stroke="#fff" stroke-width="2"/>
     <circle cx="14" cy="14" r="4" fill="#fff"/>`,
    color,
  ),
  MIDPOINT: (color = '#e67e22') => svgIcon(
    `<circle cx="14" cy="14" r="12" fill="${color}" stroke="#fff" stroke-width="2"/>
     <path d="M9 17 Q9 11 14 11 Q19 11 19 17 Z" fill="#fff"/>
     <rect x="12" y="17" width="4" height="2" fill="#fff" rx="1"/>
     <path d="M16 10 Q18 8 18 6" stroke="#fff" stroke-width="1.5" fill="none" stroke-linecap="round"/>`,
    color,
  ),
  OVERNIGHT: (color = '#9b59b6') => svgIcon(
    `<circle cx="14" cy="14" r="12" fill="${color}" stroke="#fff" stroke-width="2"/>
     <path d="M16 9 A6 6 0 1 0 16 19 A4 4 0 1 1 16 9 Z" fill="#fff"/>`,
    color,
  ),
  // POI category icons — used for VIA waypoints with a known <sym>, and OPTIONAL type
  Summit: (color = '#8B6914') => svgIcon(
    `<circle cx="14" cy="14" r="12" fill="${color}" stroke="#fff" stroke-width="2"/>
     <polygon points="14,6 8,20 20,20" fill="#fff"/>`,
    color,
  ),
  'Scenic Area': (color = '#16a085') => svgIcon(
    `<circle cx="14" cy="14" r="12" fill="${color}" stroke="#fff" stroke-width="2"/>
     <ellipse cx="14" cy="14" rx="6" ry="4" fill="none" stroke="#fff" stroke-width="1.5"/>
     <circle cx="14" cy="14" r="2" fill="#fff"/>`,
    color,
  ),
  Castle: (color = '#7f8c8d') => svgIcon(
    `<circle cx="14" cy="14" r="12" fill="${color}" stroke="#fff" stroke-width="2"/>
     <rect x="9" y="12" width="6" height="7" fill="#fff"/>
     <rect x="16" y="12" width="3" height="7" fill="#fff"/>
     <rect x="8" y="10" width="2" height="3" fill="#fff"/>
     <rect x="11" y="10" width="2" height="3" fill="#fff"/>
     <rect x="15" y="10" width="2" height="3" fill="#fff"/>
     <rect x="18" y="10" width="2" height="3" fill="#fff"/>`,
    color,
  ),
  Waterfall: (color = '#2980b9') => svgIcon(
    `<circle cx="14" cy="14" r="12" fill="${color}" stroke="#fff" stroke-width="2"/>
     <path d="M10 8 Q10 12 12 14 Q14 16 12 20" stroke="#fff" stroke-width="1.8" fill="none" stroke-linecap="round"/>
     <path d="M14 7 Q14 11 16 13 Q18 15 16 19" stroke="#fff" stroke-width="1.8" fill="none" stroke-linecap="round"/>`,
    color,
  ),
  Lake: (color = '#2471a3') => svgIcon(
    `<circle cx="14" cy="14" r="12" fill="${color}" stroke="#fff" stroke-width="2"/>
     <path d="M14 7 C14 7 9 13 9 16 A5 5 0 0 0 19 16 C19 13 14 7 14 7 Z" fill="#fff"/>`,
    color,
  ),
  Museum: (color = '#5d6d7e') => svgIcon(
    `<circle cx="14" cy="14" r="12" fill="${color}" stroke="#fff" stroke-width="2"/>
     <polygon points="14,7 7,12 21,12" fill="#fff"/>
     <rect x="8" y="12" width="2" height="7" fill="#fff"/>
     <rect x="13" y="12" width="2" height="7" fill="#fff"/>
     <rect x="18" y="12" width="2" height="7" fill="#fff"/>
     <rect x="7" y="19" width="14" height="1.5" fill="#fff"/>`,
    color,
  ),
  Monastery: (color = '#6c3483') => svgIcon(
    `<circle cx="14" cy="14" r="12" fill="${color}" stroke="#fff" stroke-width="2"/>
     <rect x="12.5" y="7" width="3" height="10" fill="#fff" rx="1"/>
     <rect x="8" y="11" width="12" height="3" fill="#fff" rx="1"/>`,
    color,
  ),
  Spa: (color = '#148f77') => svgIcon(
    `<circle cx="14" cy="14" r="12" fill="${color}" stroke="#fff" stroke-width="2"/>
     <path d="M14 8 C11 10 9 13 11 15 C13 17 15 13 14 11 C13 9 11 9 11 12" stroke="#fff" stroke-width="1.8" fill="none" stroke-linecap="round"/>
     <path d="M14 8 C17 10 19 13 17 15 C15 17 13 13 14 11" stroke="#fff" stroke-width="1.8" fill="none" stroke-linecap="round"/>
     <path d="M10 18 Q14 16 18 18" stroke="#fff" stroke-width="1.8" fill="none" stroke-linecap="round"/>`,
    color,
  ),
  Winery: (color = '#922b21') => svgIcon(
    `<circle cx="14" cy="14" r="12" fill="${color}" stroke="#fff" stroke-width="2"/>
     <path d="M11 8 Q10 12 12 14 Q14 16 14 20" stroke="#fff" stroke-width="1.8" fill="none" stroke-linecap="round"/>
     <path d="M17 8 Q18 12 16 14 Q14 16 14 20" stroke="#fff" stroke-width="1.8" fill="none" stroke-linecap="round"/>
     <path d="M11 8 L17 8" stroke="#fff" stroke-width="1.8" stroke-linecap="round"/>
     <path d="M10 12 Q14 14 18 12" stroke="#fff" stroke-width="1.2" fill="none"/>`,
    color,
  ),
  OPTIONAL: (color = '#5d9cbb') => svgIcon(
    `<circle cx="14" cy="14" r="12" fill="${color}" stroke="#fff" stroke-width="2" opacity="0.85"/>
     <circle cx="14" cy="10" r="1.5" fill="#fff"/>
     <rect x="12.5" y="13" width="3" height="7" fill="#fff" rx="1"/>`,
    color,
  ),
}

const TYPE_COLOR = {
  START: '#2ecc71',
  END: '#e74c3c',
  VIA: '#3498db',
  MIDPOINT: '#e67e22',
  OVERNIGHT: '#9b59b6',
  OPTIONAL: '#5d9cbb',
}

// GPX <sym> values that map to a specific category icon for VIA waypoints
const SYM_ICON = {
  'Summit': 'Summit',
  'Scenic Area': 'Scenic Area',
  'Castle': 'Castle',
  'Waterfall': 'Waterfall',
  'Lake': 'Lake',
  'Museum': 'Museum',
  'Monastery': 'Monastery',
  'Spa': 'Spa',
  'Winery': 'Winery',
}

function makeLeafletIcon(L, type, symbol = '') {
  // VIA and OPTIONAL waypoints with a recognised symbol get a category-specific icon
  if ((type === 'VIA' || type === 'OPTIONAL') && symbol && SYM_ICON[symbol]) {
    const iconFn = ICONS[SYM_ICON[symbol]]
    return L.divIcon({
      html: iconFn(),
      className: '',
      iconSize: ICON_SIZE,
      iconAnchor: ICON_ANCHOR,
      popupAnchor: [0, -14],
    })
  }
  const color = TYPE_COLOR[type] ?? TYPE_COLOR.VIA
  const iconFn = ICONS[type] ?? ICONS.VIA
  return L.divIcon({
    html: iconFn(color),
    className: '',
    iconSize: ICON_SIZE,
    iconAnchor: ICON_ANCHOR,
    popupAnchor: [0, -14],
  })
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * MapView can be used in two ways:
 *  1. Full-page route: /tour/:slug/day/:dayNum/map  — reads from URL params
 *  2. Inline in TourDetail: <MapView inline gpxFiles={[...]} />
 */
export default function MapView({ inline = false, gpxFiles: propGpxFiles }) {
  const { slug, dayNum } = useParams()
  const navigate = useNavigate()
  const mapRef = useRef(null)
  const leafletMap = useRef(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function init() {
      const L = (await import('leaflet')).default
      if (cancelled || !mapRef.current) return

      if (!leafletMap.current) {
        leafletMap.current = L.map(mapRef.current, {
          zoomControl: !inline,
          attributionControl: true,
          scrollWheelZoom: !inline,
          dragging: !inline,
          doubleClickZoom: !inline,
          touchZoom: !inline,
        })
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
          maxZoom: 19,
        }).addTo(leafletMap.current)
      }

      // Resolve which GPX files to render
      let filesToLoad = []
      if (inline && propGpxFiles) {
        filesToLoad = propGpxFiles
      } else if (slug) {
        try {
          const resp = await fetch('data/tours.json')
          const tours = await resp.json()
          const tour = tours.find((t) => t.slug === slug)
          if (!tour) { setError('Tour not found'); setLoading(false); return }
          filesToLoad = dayNum
            ? (tour.gpxFiles?.filter((g) => g.dayNumber === parseInt(dayNum, 10)) ?? [])
            : (tour.gpxFiles ?? [])
        } catch {
          setError('Failed to load tour data')
          setLoading(false)
          return
        }
      }

      const bounds = []

      for (let i = 0; i < filesToLoad.length; i++) {
        const entry = filesToLoad[i]
        const color = dayColor(i)
        try {
          const gpxText = await fetch(`data/gpx/${entry.file}`).then((r) => r.text())
          if (cancelled) return
          const gpxData = parseGpx(gpxText)

          // Try road-snapped route; fall back to raw GPX points
          let latlngs = null
          if (gpxData.routePoints.length >= 2) {
            const snapped = await fetchOsrmRoute(gpxData.routePoints)
            if (snapped && snapped.length > 1) {
              latlngs = snapped.map((p) => [p.lat, p.lon])
            }
          }
          if (!latlngs && gpxData.routePoints.length > 0) {
            latlngs = gpxData.routePoints.map((p) => [p.lat, p.lon])
          }

          if (latlngs) {
            L.polyline(latlngs, { color, weight: 4, opacity: 0.85 }).addTo(leafletMap.current)
            bounds.push(...latlngs)
          }

          // Waypoint markers with SVG icons
          for (const wpt of gpxData.waypoints) {
            const icon = makeLeafletIcon(L, wpt.type, wpt.symbol)
            const marker = L.marker([wpt.lat, wpt.lon], { icon })
            const popupLines = [
              `<strong>${wpt.name}</strong>`,
              wpt.type !== 'VIA' ? `<em>${wpt.type}</em>` : '',
              wpt.description,
            ].filter(Boolean).join('<br>')
            marker.bindPopup(popupLines)
            marker.addTo(leafletMap.current)
            bounds.push([wpt.lat, wpt.lon])
          }
        } catch (e) {
          console.warn('Failed to load GPX', entry.file, e)
        }
      }

      if (bounds.length > 0) {
        leafletMap.current.fitBounds(L.latLngBounds(bounds), { padding: [20, 20] })
      } else {
        leafletMap.current.setView([49.32, 8.56], 9)
      }

      setLoading(false)
    }

    init().catch((e) => { setError(e.message); setLoading(false) })
    return () => { cancelled = true }
  }, [slug, dayNum, inline, propGpxFiles])

  useEffect(() => {
    return () => {
      if (leafletMap.current) {
        leafletMap.current.remove()
        leafletMap.current = null
      }
    }
  }, [])

  return (
    <div className={inline ? styles.inlineMap : styles.fullMap}>
      {!inline && (
        <button className={styles.backBtn} onClick={() => navigate(-1)} aria-label="Back">
          ← Back
        </button>
      )}
      {loading && <div className={styles.overlay}>Loading map…</div>}
      {error && <div className={`${styles.overlay} ${styles.error}`}>{error}</div>}
      <div ref={mapRef} className={styles.leaflet} />
    </div>
  )
}
