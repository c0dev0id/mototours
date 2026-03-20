/**
 * Fetch a road-following route from the public OSRM server.
 * Mirrors RouteCalculator.kt exactly.
 *
 * Returns an array of { lat, lon } points, or null on any failure.
 */

const OSRM_BASE = 'https://router.project-osrm.org/route/v1/driving'

export async function fetchOsrmRoute(routePoints) {
  if (!routePoints || routePoints.length < 2) return null
  try {
    const coords = routePoints.map((p) => `${p.lon},${p.lat}`).join(';')
    const url = `${OSRM_BASE}/${coords}?overview=full&geometries=polyline`
    const resp = await fetch(url, { signal: AbortSignal.timeout(10_000) })
    if (!resp.ok) return null
    const json = await resp.json()
    if (json.code !== 'Ok') return null
    return decodePolyline(json.routes[0].geometry)
  } catch {
    return null
  }
}

/**
 * Decode a Google-encoded polyline string into [{ lat, lon }].
 * Direct JS port of decodePolyline() in RouteCalculator.kt.
 */
function decodePolyline(encoded) {
  const points = []
  let index = 0
  let lat = 0
  let lng = 0

  while (index < encoded.length) {
    let shift = 0
    let result = 0
    let b
    do {
      b = encoded.charCodeAt(index++) - 63
      result |= (b & 0x1f) << shift
      shift += 5
    } while (b >= 0x20)
    lat += result & 1 ? ~(result >> 1) : result >> 1

    shift = 0
    result = 0
    do {
      b = encoded.charCodeAt(index++) - 63
      result |= (b & 0x1f) << shift
      shift += 5
    } while (b >= 0x20)
    lng += result & 1 ? ~(result >> 1) : result >> 1

    points.push({ lat: lat / 1e5, lon: lng / 1e5 })
  }
  return points
}
