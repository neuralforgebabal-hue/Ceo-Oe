import React, { useEffect, useState } from 'react'
import { getProjectStats, scanProjects } from '../api/client'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis
} from 'recharts'
import {
  FolderGit2, Bot, CheckCircle2, Database,
  TrendingUp, RefreshCw, Activity, AlertTriangle
} from 'lucide-react'

const AGENT_COLORS = {
  ceo: '#00d4ff', architect: '#7b2fff', developer: '#00ff88',
  security: '#ff3366', analyst: '#ffaa00', monetization: '#ff6b35', deployment: '#00d4ff'
}

function StatCard({ label, value, icon: Icon, color = 'accent', sub }) {
  return (
    <div className="panel-glow p-5 flex items-start gap-4">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0`}
           style={{ background: `${color}18`, border: `1px solid ${color}33` }}>
        <Icon size={18} style={{ color }} />
      </div>
      <div>
        <div className="text-2xl font-bold font-display" style={{ color }}>{value}</div>
        <div className="text-xs text-muted mt-0.5">{label}</div>
        {sub && <div className="text-xs text-slate-500 mt-1">{sub}</div>}
      </div>
    </div>
  )
}

function ScoreBar({ label, value, color }) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-muted">{label}</span>
        <span className="font-mono" style={{ color }}>{value.toFixed(1)}</span>
      </div>
      <div className="score-bar">
        <div className="score-fill" style={{ width: `${value * 10}%`, background: color }} />
      </div>
    </div>
  )
}

function LiveFeed({ events }) {
  const typeColors = {
    AGENT_START: '#00d4ff', AGENT_DONE: '#00ff88',
    AGENT_ERROR: '#ff3366', CEO_PRIORITIZING: '#7b2fff',
    default: '#4a6280'
  }
  return (
    <div className="panel p-4 h-72 flex flex-col">
      <div className="flex items-center gap-2 mb-3">
        <Activity size={14} className="text-accent" />
        <span className="text-xs font-semibold text-accent tracking-wider">LIVE FEED</span>
        <span className="ml-auto w-2 h-2 rounded-full bg-success animate-pulse" />
      </div>
      <div className="flex-1 overflow-y-auto space-y-1.5 font-mono text-xs">
        {events.length === 0 && (
          <div className="text-muted text-center py-8">Waiting for agent events...</div>
        )}
        {events.slice(0, 40).map((e, i) => (
          <div key={i} className="flex gap-2 items-start">
            <span className="text-[10px] text-slate-600 w-20 flex-shrink-0 pt-0.5">
              {new Date(e.timestamp).toLocaleTimeString()}
            </span>
            <span className="px-1.5 py-0.5 rounded text-[10px] flex-shrink-0"
                  style={{ background: `${typeColors[e.event_type] || typeColors.default}20`,
                           color: typeColors[e.event_type] || typeColors.default }}>
              {e.agent_id}
            </span>
            <span className="text-slate-400 truncate">{e.event_type}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function Dashboard({ wsEvents, agentActivity }) {
  const [stats, setStats] = useState(null)
  const [scanning, setScanning] = useState(false)
  const [error, setError] = useState(null)

  const loadStats = async () => {
    try {
      const r = await getProjectStats()
      setStats(r.data)
    } catch (e) {
      setError('Backend offline — start the server first')
    }
  }

  useEffect(() => { loadStats() }, [])

  const handleScan = async () => {
    setScanning(true)
    try {
      await scanProjects()
      await loadStats()
    } catch (e) {
      setError('Scan failed')
    } finally {
      setScanning(false)
    }
  }

  const typeData = stats ? Object.entries(stats.type_distribution || {}).map(([name, count]) => ({ name, count })) : []
  const topProjects = stats?.top_projects || []

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-xl font-bold text-accent glow-text">COMMAND CENTER</h1>
          <p className="text-xs text-muted mt-1">AI Operating System · Real-time intelligence</p>
        </div>
        <button onClick={handleScan} disabled={scanning} className="btn-primary flex items-center gap-2">
          <RefreshCw size={14} className={scanning ? 'animate-spin' : ''} />
          {scanning ? 'Scanning...' : 'Scan Projects'}
        </button>
      </div>

      {error && (
        <div className="panel border-danger/30 p-4 flex items-center gap-3 text-sm text-danger">
          <AlertTriangle size={16} /> {error}
        </div>
      )}

      {/* Stat Cards */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard label="Total Projects" value={stats?.total_projects ?? '—'}
                  icon={FolderGit2} color="#00d4ff" />
        <StatCard label="Tasks Run" value={stats?.total_tasks ?? '—'}
                  icon={Bot} color="#7b2fff" />
        <StatCard label="Completed" value={stats?.completed_tasks ?? '—'}
                  icon={CheckCircle2} color="#00ff88" />
        <StatCard label="Memories Stored" value={stats?.total_memories ?? '—'}
                  icon={Database} color="#ffaa00" />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Project Types */}
        <div className="panel p-4 col-span-1">
          <div className="text-xs text-muted mb-3 font-semibold tracking-wider">PROJECT TYPES</div>
          {typeData.length === 0
            ? <div className="text-center text-muted text-xs py-8">No data — run a scan</div>
            : <ResponsiveContainer width="100%" height={160}>
                <BarChart data={typeData}>
                  <XAxis dataKey="name" tick={{ fill: '#4a6280', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: '#4a6280', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ background: '#0d1829', border: '1px solid #1a2d4a', borderRadius: 8, fontSize: 12 }} />
                  <Bar dataKey="count" fill="#00d4ff" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
          }
        </div>

        {/* Avg Scores */}
        <div className="panel p-4 col-span-1 space-y-3">
          <div className="text-xs text-muted mb-3 font-semibold tracking-wider">AVERAGE SCORES</div>
          <ScoreBar label="Profit Potential" value={stats?.average_profit_score || 0} color="#00ff88" />
          <ScoreBar label="Stability" value={stats?.average_stability_score || 0} color="#00d4ff" />
          <div className="pt-2 border-t border-border text-xs text-muted">
            Across {stats?.total_projects || 0} projects
          </div>
        </div>

        {/* Top Projects */}
        <div className="panel p-4 col-span-1">
          <div className="text-xs text-muted mb-3 font-semibold tracking-wider">TOP PROJECTS</div>
          <div className="space-y-2">
            {topProjects.length === 0 && <div className="text-center text-muted text-xs py-4">Scan to populate</div>}
            {topProjects.map((p, i) => (
              <div key={i} className="flex items-center gap-2">
                <span className="text-xs font-mono text-muted w-4">{i + 1}</span>
                <span className="text-sm text-slate-300 flex-1 truncate">{p.name}</span>
                <span className="text-xs font-mono text-success">{p.profit?.toFixed(1)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Live Feed + Agent Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <LiveFeed events={wsEvents} />

        {/* Agent Status Grid */}
        <div className="panel p-4">
          <div className="text-xs text-muted mb-3 font-semibold tracking-wider">AGENT STATUS</div>
          <div className="grid grid-cols-2 gap-2">
            {['ceo', 'architect', 'developer', 'security', 'analyst', 'monetization', 'deployment'].map(agent => {
              const status = agentActivity[agent]?.status || 'idle'
              const lastEvent = agentActivity[agent]?.last_event || 'Standing by'
              const color = AGENT_COLORS[agent] || '#4a6280'
              return (
                <div key={agent} className="bg-surface rounded-lg p-3 flex items-center gap-3 border border-border">
                  <div className={`status-dot ${status}`} style={status === 'active' ? { background: color } : {}} />
                  <div className="min-w-0">
                    <div className="text-xs font-semibold capitalize" style={{ color }}>{agent}</div>
                    <div className="text-[10px] text-muted truncate">{lastEvent}</div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
