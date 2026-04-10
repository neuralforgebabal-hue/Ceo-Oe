import React, { useEffect, useState } from 'react'
import { getTasks } from '../api/client'
import { ListTodo, RefreshCw, Clock, CheckCircle2, XCircle, Loader2 } from 'lucide-react'

const STATUS_META = {
  pending:  { color: '#ffaa00', icon: Clock,        label: 'Pending' },
  running:  { color: '#00d4ff', icon: Loader2,      label: 'Running' },
  done:     { color: '#00ff88', icon: CheckCircle2, label: 'Done' },
  failed:   { color: '#ff3366', icon: XCircle,      label: 'Failed' },
}

const PRIORITY_LABEL = { 1: 'URGENT', 2: 'HIGH', 3: 'MEDIUM', 4: 'LOW', 5: 'MINIMAL' }
const PRIORITY_COLOR = { 1: '#ff3366', 2: '#ffaa00', 3: '#00d4ff', 4: '#4a6280', 5: '#2d3f55' }

function TaskRow({ task }) {
  const [open, setOpen] = useState(false)
  const meta = STATUS_META[task.status] || STATUS_META.pending
  const Icon = meta.icon

  return (
    <>
      <tr onClick={() => setOpen(!open)}
          className="border-b border-border/50 hover:bg-surface/50 cursor-pointer transition-colors">
        <td className="px-4 py-3">
          <div className="flex items-center gap-2">
            <Icon size={13} style={{ color: meta.color }}
                  className={task.status === 'running' ? 'animate-spin' : ''} />
            <span className="text-xs" style={{ color: meta.color }}>{meta.label}</span>
          </div>
        </td>
        <td className="px-4 py-3">
          <span className="text-xs font-mono text-slate-300 capitalize">{task.agent}</span>
        </td>
        <td className="px-4 py-3">
          <span className="text-[10px] font-mono text-muted">{task.type}</span>
        </td>
        <td className="px-4 py-3">
          <span className="text-[10px] px-2 py-0.5 rounded font-mono"
                style={{ background: `${PRIORITY_COLOR[task.priority]}18`, color: PRIORITY_COLOR[task.priority] }}>
            {PRIORITY_LABEL[task.priority] || task.priority}
          </span>
        </td>
        <td className="px-4 py-3 text-[10px] text-muted font-mono">
          {task.created_at ? new Date(task.created_at).toLocaleString() : '—'}
        </td>
        <td className="px-4 py-3 text-[10px] text-muted font-mono">
          {task.completed_at && task.started_at
            ? `${Math.round((new Date(task.completed_at) - new Date(task.started_at)) / 1000)}s`
            : '—'}
        </td>
      </tr>
      {open && (task.result || task.error) && (
        <tr className="bg-void border-b border-border/30">
          <td colSpan={6} className="px-4 py-3">
            {task.error && (
              <div className="text-xs text-danger font-mono bg-danger/10 rounded p-2">{task.error}</div>
            )}
            {task.result && (
              <pre className="text-[11px] text-slate-400 font-mono bg-surface rounded p-3 max-h-48 overflow-auto">
                {JSON.stringify(task.result, null, 2)}
              </pre>
            )}
          </td>
        </tr>
      )}
    </>
  )
}

export default function TasksPage() {
  const [tasks, setTasks] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)

  const load = async () => {
    try {
      const r = await getTasks(filter === 'all' ? null : filter)
      setTasks(r.data)
    } catch (_) {}
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [filter])

  useEffect(() => {
    if (!autoRefresh) return
    const t = setInterval(load, 3000)
    return () => clearInterval(t)
  }, [autoRefresh, filter])

  const counts = tasks.reduce((acc, t) => {
    acc[t.status] = (acc[t.status] || 0) + 1
    return acc
  }, {})

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-lg font-bold text-accent">TASK QUEUE</h1>
          <p className="text-xs text-muted">{tasks.length} tasks total</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={() => setAutoRefresh(!autoRefresh)}
            className={`text-xs px-3 py-1.5 rounded-lg border transition-all ${
              autoRefresh ? 'border-success/40 text-success bg-success/10' : 'border-border text-muted'}`}>
            {autoRefresh ? '⟳ Auto' : 'Paused'}
          </button>
          <button onClick={load} className="btn-ghost flex items-center gap-1">
            <RefreshCw size={12} /> Refresh
          </button>
        </div>
      </div>

      {/* Status Summary */}
      <div className="grid grid-cols-4 gap-3">
        {Object.entries(STATUS_META).map(([status, meta]) => {
          const Icon = meta.icon
          return (
            <div key={status} className="panel p-3 flex items-center gap-3">
              <Icon size={16} style={{ color: meta.color }} />
              <div>
                <div className="text-lg font-bold font-display" style={{ color: meta.color }}>
                  {counts[status] || 0}
                </div>
                <div className="text-[10px] text-muted">{meta.label}</div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Filter */}
      <div className="flex gap-2">
        {['all', 'pending', 'running', 'done', 'failed'].map(s => (
          <button key={s} onClick={() => setFilter(s)}
            className={`px-3 py-1.5 rounded-lg text-xs capitalize transition-all
              ${filter === s ? 'bg-accent/15 text-accent border border-accent/30' : 'text-muted border border-transparent hover:text-slate-300'}`}>
            {s}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="panel overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left">
              {['Status', 'Agent', 'Type', 'Priority', 'Created', 'Duration'].map(h => (
                <th key={h} className="px-4 py-3 text-[10px] text-muted font-semibold tracking-wider">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading
              ? <tr><td colSpan={6} className="text-center text-muted py-12 text-xs">Loading...</td></tr>
              : tasks.length === 0
                ? <tr><td colSpan={6} className="text-center text-muted py-12 text-xs">
                    <ListTodo size={28} className="mx-auto mb-2 opacity-20" />
                    No tasks — run agents to create tasks
                  </td></tr>
                : tasks.map(t => <TaskRow key={t.id} task={t} />)
            }
          </tbody>
        </table>
      </div>
    </div>
  )
}
