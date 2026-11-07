const BASE_URL = ''

async function request(path, options) {
  const res = await fetch(`${BASE_URL}${path}`, options)
  const data = await res.json().catch(() => null)

  if (!res.ok) {
    const detail = data?.detail
    const message = Array.isArray(detail)
      ? detail.map((d) => (typeof d === 'string' ? d : d.msg)).join(', ')
      : detail
    throw new Error(message || `Request failed (${res.status})`)
  }

  return data
}

export function searchPlayers(query) {
  return request(`/api/players/search?q=${encodeURIComponent(query)}`)
}

export function getStatDefinitions() {
  return request('/api/stats/definitions')
}

export function getStatOptions() {
  return request('/api/stats/options')
}

export function evaluateFormula(player, season, formula, customStats = []) {
  return request('/api/formula/evaluate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ player, season, formula, custom_stats: customStats }),
  })
}
