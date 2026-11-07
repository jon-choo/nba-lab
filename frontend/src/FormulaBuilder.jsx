import { useEffect, useState } from 'react'
import { evaluateFormula, getStatDefinitions, searchPlayers } from './api'
import CustomStatForm from './CustomStatForm'

const SEASONS = Array.from({ length: 26 }, (_, i) => {
  const start = 2025 - i
  return `${start}-${String(start + 1).slice(-2)}`
})

function FormulaBuilder() {
  const [query, setQuery] = useState('')
  const [matches, setMatches] = useState([])
  const [player, setPlayer] = useState(null)
  const [season, setSeason] = useState(SEASONS[0])
  const [stats, setStats] = useState([])
  const [customStats, setCustomStats] = useState([])
  const [showCustomForm, setShowCustomForm] = useState(false)
  const [formula, setFormula] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    getStatDefinitions()
      .then(setStats)
      .catch((err) => setError(err.message))
  }, [])

  useEffect(() => {
    if (player || query.trim().length < 2) {
      setMatches([])
      return
    }

    let cancelled = false
    const timer = setTimeout(() => {
      searchPlayers(query)
        .then((data) => {
          if (!cancelled) setMatches(data)
        })
        .catch((err) => {
          if (!cancelled) setError(err.message)
        })
    }, 250)

    return () => {
      cancelled = true
      clearTimeout(timer)
    }
  }, [query, player])

  function pickPlayer(p) {
    setPlayer(p)
    setQuery(p.full_name)
    setMatches([])
  }

  function onQueryChange(e) {
    setQuery(e.target.value)
    setPlayer(null)
  }

  function addStat(name) {
    setFormula((f) => (f.trim() ? `${f.trim()} + ${name}` : name))
  }

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setResult(null)
    setLoading(true)
    try {
      const data = await evaluateFormula(player.full_name, season, formula, customStats)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const canSubmit = player && formula.trim() && !loading

  return (
    <form onSubmit={onSubmit} className="max-w-2xl mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">Custom stat builder</h1>

      <div className="grid grid-cols-3 gap-3">
        <div className="col-span-2 relative">
          <label className="block text-sm text-slate-400 mb-1">Player</label>
          <input
            value={query}
            onChange={onQueryChange}
            placeholder="Search a player..."
            className="w-full rounded bg-slate-900 border border-slate-700 px-3 py-2"
          />
          {matches.length > 0 && (
            <ul className="absolute z-10 mt-1 w-full rounded bg-slate-900 border border-slate-700">
              {matches.map((p) => (
                <li key={p.id}>
                  <button
                    type="button"
                    onClick={() => pickPlayer(p)}
                    className="w-full text-left px-3 py-2 hover:bg-slate-800"
                  >
                    {p.full_name}
                    {!p.is_active && (
                      <span className="text-slate-500 text-sm"> (retired)</span>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div>
          <label className="block text-sm text-slate-400 mb-1">Season</label>
          <select
            value={season}
            onChange={(e) => setSeason(e.target.value)}
            className="w-full rounded bg-slate-900 border border-slate-700 px-3 py-2"
          >
            {SEASONS.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm text-slate-400 mb-1">Formula</label>
        <input
          value={formula}
          onChange={(e) => setFormula(e.target.value)}
          placeholder="0.6 * MidRange_PullUp_PCT + 0.4 * RestrictedArea_PCT"
          className="w-full rounded bg-slate-900 border border-slate-700 px-3 py-2 font-mono"
        />
        <div className="flex flex-wrap gap-2 mt-3">
          {stats.map((name) => (
            <button
              key={name}
              type="button"
              onClick={() => addStat(name)}
              className="text-xs font-mono rounded-full border border-slate-700 px-3 py-1 hover:bg-slate-800"
            >
              {name}
            </button>
          ))}
          {customStats.map((s) => (
            <span
              key={s.name}
              className="inline-flex items-center text-xs font-mono rounded-full border border-orange-500 overflow-hidden"
            >
              <button
                type="button"
                onClick={() => addStat(s.name)}
                className="pl-3 pr-2 py-1 hover:bg-orange-500/10"
              >
                {s.name}
              </button>
              <button
                type="button"
                onClick={() => setCustomStats((list) => list.filter((x) => x.name !== s.name))}
                aria-label={`Remove ${s.name}`}
                className="px-2 py-1 text-orange-300 hover:bg-orange-500/20"
              >
                ×
              </button>
            </span>
          ))}
        </div>

        <button
          type="button"
          onClick={() => setShowCustomForm((v) => !v)}
          className="mt-4 text-sm text-orange-400 hover:underline"
        >
          {showCustomForm ? 'Hide custom stat builder' : '+ Create your own stat'}
        </button>

        {showCustomForm && (
          <div className="mt-3">
            <CustomStatForm
              takenNames={[...stats, ...customStats.map((s) => s.name)]}
              onAdd={(stat) => setCustomStats((list) => [...list, stat])}
            />
          </div>
        )}
      </div>

      <button
        type="submit"
        disabled={!canSubmit}
        className="rounded bg-orange-500 px-5 py-2 font-semibold disabled:opacity-40"
      >
        {loading ? 'Calculating...' : 'Calculate'}
      </button>

      {loading && (
        <p className="text-sm text-slate-400">
          First lookup for a player can take a few seconds while we fetch their shots.
        </p>
      )}

      {error && <p className="text-red-400">{error}</p>}

      {result && (
        <div className="rounded border border-slate-700 p-4 space-y-3">
          <p className="text-sm text-slate-400">Result</p>
          <p className="text-4xl font-bold">{result.result.toFixed(3)}</p>
          <table className="w-full text-sm">
            <thead className="text-slate-400 text-left">
              <tr>
                <th className="py-1">Stat</th>
                <th>Makes / Attempts</th>
                <th className="text-right">FG%</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(result.breakdown).map(([name, s]) => (
                <tr key={name} className="border-t border-slate-800">
                  <td className="py-1 font-mono">{name}</td>
                  <td>
                    {s.makes} / {s.attempts}
                  </td>
                  <td className="text-right">{(s.value * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </form>
  )
}

export default FormulaBuilder
