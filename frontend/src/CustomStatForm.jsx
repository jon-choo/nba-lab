import { useEffect, useState } from 'react'
import { getStatOptions } from './api'

const NAME_PATTERN = /^[A-Za-z_][A-Za-z0-9_]{0,39}$/

function Toggle({ active, onClick, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`text-xs rounded-full border px-3 py-1 ${
        active
          ? 'bg-orange-500 border-orange-500 text-white'
          : 'border-slate-700 hover:bg-slate-800'
      }`}
    >
      {children}
    </button>
  )
}

function toggleItem(list, item) {
  return list.includes(item) ? list.filter((x) => x !== item) : [...list, item]
}

function CustomStatForm({ takenNames, onAdd }) {
  const [options, setOptions] = useState({ zones: [], shot_types: [] })
  const [name, setName] = useState('')
  const [zones, setZones] = useState([])
  const [shotTypes, setShotTypes] = useState([])
  const [shotMatch, setShotMatch] = useState('any')
  const [error, setError] = useState('')

  useEffect(() => {
    getStatOptions()
      .then(setOptions)
      .catch((err) => setError(err.message))
  }, [])

  function submit() {
    if (!NAME_PATTERN.test(name)) {
      setError('Name must use letters, numbers and underscores, and not start with a number')
    } else if (takenNames.includes(name)) {
      setError(`A stat named ${name} already exists`)
    } else if (zones.length === 0 && shotTypes.length === 0) {
      setError('Pick at least one zone or shot type')
    } else {
      onAdd({ name, zones, shot_types: shotTypes, shot_match: shotMatch })
      setName('')
      setZones([])
      setShotTypes([])
      setShotMatch('any')
      setError('')
    }
  }

  return (
    <div className="rounded border border-slate-700 p-4 space-y-4">
      <div>
        <label className="block text-sm text-slate-400 mb-1">Stat name</label>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="MyPullUp"
          className="w-full rounded bg-slate-900 border border-slate-700 px-3 py-2 font-mono"
        />
      </div>

      <div>
        <p className="text-sm text-slate-400 mb-2">Zones (any of these)</p>
        <div className="flex flex-wrap gap-2">
          {options.zones.map((z) => (
            <Toggle key={z} active={zones.includes(z)} onClick={() => setZones(toggleItem(zones, z))}>
              {z}
            </Toggle>
          ))}
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm text-slate-400">Shot types</p>
          {shotTypes.length > 1 && (
            <div className="flex gap-2 text-xs">
              <Toggle active={shotMatch === 'any'} onClick={() => setShotMatch('any')}>
                Match any
              </Toggle>
              <Toggle active={shotMatch === 'all'} onClick={() => setShotMatch('all')}>
                Match all
              </Toggle>
            </div>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          {options.shot_types.map((t) => (
            <Toggle
              key={t}
              active={shotTypes.includes(t)}
              onClick={() => setShotTypes(toggleItem(shotTypes, t))}
            >
              {t}
            </Toggle>
          ))}
        </div>
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      <button
        type="button"
        onClick={submit}
        className="rounded border border-orange-500 text-orange-400 px-4 py-1.5 text-sm hover:bg-orange-500/10"
      >
        Add stat
      </button>
    </div>
  )
}

export default CustomStatForm
