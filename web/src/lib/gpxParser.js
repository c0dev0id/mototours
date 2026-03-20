/**
 * Parses a GPX 1.1 XML string into a structured object.
 * Returns { name, waypoints, routePoints }
 */
export function parseGpx(xmlText) {
  const parser = new DOMParser()
  const doc = parser.parseFromString(xmlText, 'application/xml')

  const name = doc.querySelector('metadata > name')?.textContent?.trim() ?? ''

  // Waypoints <wpt>
  const waypoints = [...doc.querySelectorAll('wpt')].map((wpt) => ({
    lat: parseFloat(wpt.getAttribute('lat')),
    lon: parseFloat(wpt.getAttribute('lon')),
    name: wpt.querySelector('name')?.textContent?.trim() ?? '',
    description: wpt.querySelector('desc')?.textContent?.trim() ?? '',
    type: normaliseType(wpt.querySelector('type')?.textContent?.trim() ?? ''),
    symbol: wpt.querySelector('sym')?.textContent?.trim() ?? '',
  }))

  // Route points <rte> > <rtept>
  const routePoints = [...doc.querySelectorAll('rte rtept')].map((pt) => ({
    lat: parseFloat(pt.getAttribute('lat')),
    lon: parseFloat(pt.getAttribute('lon')),
  }))

  // Fallback: track points <trk> > <trkpt>
  const trackPoints =
    routePoints.length === 0
      ? [...doc.querySelectorAll('trk trkpt')].map((pt) => ({
          lat: parseFloat(pt.getAttribute('lat')),
          lon: parseFloat(pt.getAttribute('lon')),
        }))
      : []

  return {
    name,
    waypoints,
    routePoints: routePoints.length > 0 ? routePoints : trackPoints,
  }
}

const TYPE_MAP = {
  'start/end': 'START',
  start: 'START',
  end: 'END',
  via: 'VIA',
  midpoint: 'MIDPOINT',
  overnight: 'OVERNIGHT',
}

function normaliseType(raw) {
  return TYPE_MAP[raw.toLowerCase()] ?? 'VIA'
}

/** Returns a Leaflet-compatible colour string for a waypoint type */
export function waypointColor(type) {
  switch (type) {
    case 'START': return '#2ecc71'
    case 'END': return '#e74c3c'
    case 'OVERNIGHT': return '#9b59b6'
    case 'MIDPOINT': return '#e67e22'
    default: return '#3498db'
  }
}

/** Day-route colours (cycling palette, similar to the Android app) */
const DAY_COLOURS = ['#C8611A', '#2C5530', '#1a6bc8', '#8B1AC8', '#c81a6b', '#6bc81a']

export function dayColor(index) {
  return DAY_COLOURS[index % DAY_COLOURS.length]
}
