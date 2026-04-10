/**
 * Format seconds → "Xm Ys" or "Xh Ym"
 */
export function formatDuration(seconds) {
  if (!seconds) return '0m 00s'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  if (h > 0) return `${h}h ${String(m).padStart(2, '0')}m`
  return `${m}m ${String(s).padStart(2, '0')}s`
}

/**
 * Format ISO string → "YYYY.MM.DD · HH:mm"
 */
export function formatDate(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  const y = d.getFullYear()
  const mo = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  return `${y}.${mo}.${day} · ${h}:${mi}`
}

/**
 * Format seconds-from-start → "MM:SS"
 */
export function formatFlightTime(sec) {
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

/**
 * Degrees → compass direction string
 */
export function degToCompass(deg) {
  const dirs = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
  return dirs[Math.round(deg / 22.5) % 16]
}

/**
 * Trigger a file download from a Blob/URL
 */
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

import api from './api'

export async function exportFlightCsv(flight) {
  try {
    const { data } = await api.get(`/export/${flight.id}/csv`, { responseType: 'blob' })
    downloadBlob(data, `${flight.mission_id}.csv`)
  } catch (e) {
    console.error('CSV export failed', e)
  }
}

export async function exportFlightGpx(flight) {
  try {
    const { data } = await api.get(`/export/${flight.id}/gpx`, { responseType: 'blob' })
    downloadBlob(data, `${flight.mission_id}.gpx`)
  } catch (e) {
    console.error('GPX export failed', e)
  }
}

export async function exportFlightKml(flight) {
  try {
    const { data } = await api.get(`/export/${flight.id}/kml`, { responseType: 'blob' })
    downloadBlob(data, `${flight.mission_id}.kml`)
  } catch (e) {
    console.error('KML export failed', e)
  }
}
