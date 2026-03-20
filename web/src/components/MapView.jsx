import { useEffect, useRef, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { parseGpx, waypointColor, dayColor } from '../lib/gpxParser.js'
import styles from './MapView.module.css'

/**
 * MapView can be used in two ways:
 *  1. As a full-page route: /tour/:slug/day/:dayNum/map  — reads from URL params
 *  2. As an inline component in TourDetail: <MapView inline gpxFiles={[...]} />
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
      // Dynamically import Leaflet to avoid SSR issues
      const L = (await import('leaflet')).default

      if (cancelled || !mapRef.current) return

      // Init map if not yet created
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

      // Determine which GPX files to load
      let filesToLoad = []
      if (inline && propGpxFiles) {
        filesToLoad = propGpxFiles
      } else if (slug) {
        // Full-page mode: load tours.json to find this tour
        try {
          const resp = await fetch('data/tours.json')
          const tours = await resp.json()
          const tour = tours.find((t) => t.slug === slug)
          if (!tour) { setError('Tour not found'); setLoading(false); return }

          if (dayNum) {
            const entry = tour.gpxFiles?.find((g) => g.dayNumber === parseInt(dayNum, 10))
            filesToLoad = entry ? [entry] : []
          } else {
            filesToLoad = tour.gpxFiles ?? []
          }
        } catch (e) {
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
          const gpxResp = await fetch(`data/gpx/${entry.file}`)
          const gpxText = await gpxResp.text()
          if (cancelled) return
          const gpxData = parseGpx(gpxText)

          // Draw route polyline
          if (gpxData.routePoints.length > 0) {
            const latlngs = gpxData.routePoints.map((p) => [p.lat, p.lon])
            L.polyline(latlngs, { color, weight: 3, opacity: 0.85 }).addTo(leafletMap.current)
            bounds.push(...latlngs)
          }

          // Draw waypoint markers
          for (const wpt of gpxData.waypoints) {
            const wColor = waypointColor(wpt.type)
            const marker = L.circleMarker([wpt.lat, wpt.lon], {
              radius: wpt.type === 'START' || wpt.type === 'END' ? 8 : 6,
              color: wColor,
              fillColor: wColor,
              fillOpacity: 0.9,
              weight: 2,
            })
            const popupLines = [
              `<strong>${wpt.name}</strong>`,
              wpt.type !== 'VIA' ? `<em>${wpt.type}</em>` : '',
              wpt.description,
            ].filter(Boolean).join('<br>')
            marker.bindPopup(popupLines)
            marker.addTo(leafletMap.current)
          }
        } catch (e) {
          console.warn('Failed to load GPX', entry.file, e)
        }
      }

      // Fit bounds
      if (bounds.length > 0) {
        leafletMap.current.fitBounds(L.latLngBounds(bounds), { padding: [20, 20] })
      } else {
        // Default to Hockenheim area
        leafletMap.current.setView([49.32, 8.56], 9)
      }

      setLoading(false)
    }

    init().catch((e) => { setError(e.message); setLoading(false) })

    return () => { cancelled = true }
  }, [slug, dayNum, inline, propGpxFiles])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (leafletMap.current) {
        leafletMap.current.remove()
        leafletMap.current = null
      }
    }
  }, [])

  const containerClass = inline ? styles.inlineMap : styles.fullMap

  return (
    <div className={containerClass}>
      {!inline && (
        <button className={styles.backBtn} onClick={() => navigate(-1)} aria-label="Back">
          ← Back
        </button>
      )}
      {loading && <div className={styles.overlay}>Loading map…</div>}
      {error && <div className={styles.overlay + ' ' + styles.error}>{error}</div>}
      <div ref={mapRef} className={styles.leaflet} />
    </div>
  )
}
