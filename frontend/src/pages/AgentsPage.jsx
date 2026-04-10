import React, { useEffect, useState } from 'react'
import { getAgents, getProjects, runAgent } from '../api/client'
import {
  Bot, Shield, TrendingUp, Code2, DollarSign,
  Rocket, Cpu, Activity, Play, Clock
} from 'lucide-react'

const AGENT_META = {
  ceo:          { icon: Cpu,        color: '#00d4ff', desc: 'Master orchestrator & decision maker' },
  architect:    { icon: Code2,      color: '#7b2fff', desc: 'System design & architecture analysis' },
  developer:    { icon: Code2,      color: '#00ff88', desc: 'Code quality, bugs & refactor suggestions' },
  security:     { icon: Shield,     color: '#ff3366', desc: 'Vulnerability scanning & secret detection' },
  analyst:      { icon: TrendingUp, color: '#ffaa00', desc: 'Performance metrics & technical debt' },
  monetization: { icon: DollarSign, color: '#f97316', desc: 'Revenue strategies & market analysis' },
  deployment:   { icon: Rocket,     color: '#00d4ff', desc: 'CI/CD, Docker & cloud deployment plans' },
}

function AgentCard({ agent, activity, projects, onRun }) {
  const meta = AGENT_META[agent.id] || { icon: Bot, color: '#4a6280', desc: '' }
  const Icon = meta.icon
  const status = activity?.[agent.id]?.status || agent.status || 'idle'
  const [selectedProject, setSelectedProject] = useState('')
  const [running, setRunning] = useState(false)

  const handleRun = async () => {
    if (!selectedProject) return
    setRunning(true)
    try { await onRun(agent.id, selectedProject) }
    finally { setRunning(false) }
  }

  return (
    <div className="panel-glow p-5 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center"
               style={{ background: `${meta.color}18`, border: `1px solid ${meta.color}30` }}>
            <Icon size={18} style={{ color: meta.color }} />
          </div>
          <div>
            <div className="font-semibold capitalize text-sm" style={{ color: meta.color }}>
              {agent.id} Agent
            </div>
            <div className="text-[10px] text-muted">{meta.desc}</div>
          </div>
        </div>
        <div className="flex items-center gap-1.5">
          <div className={`w-2 h-2 rounded-full ${
            status === 'active' ? 'animate-pulse' : ''
          }`} style={{ background: status === 'active' ? meta.color : status === 'error' ? '#ff3366' : '#4a6280' }} />
          <span className="text-[10px] text-muted capitalize">{status}</span>
        </div>
      </div>

      {/* Last Activity */}
      {activity?.[agent.id] && (
        <div className="bg-surface rounded-lg p-2 text-[10px] font-mono">
          <div className="text-muted flex items-center gap-1 mb-0.5">
            <Clock size={9} /> Last event
          </div>
          <div className="text-accent truncate">{activity[agent.id].last_event || '—'}</div>
          <div className="text-slate-600 mt-0.5">
            {activity[agent.id].last_active
              ? new Date(activity[agent.id].last_active).toLocaleTimeString()
              : '—'}
          </div>
        </div>
      )}

      {/* Run on project */}
      <div className="space-y-2">
        <select value={selectedProject} onChange={e => setSelectedProject(e.target.value)}
          className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-xs text-slate-300
                     focus:outline-none focus:border-accent/50">
          <option value="">Select project...</option>
          {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
        <button onClick={handleRun} disabled={!selectedProject || running}
          className="w-full py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-2
                     transition-all duration-200 disabled:opacity-40"
          style={{
            background: selectedProject ? `${meta.color}18` : 'transparent',
            border: `1px solid ${meta.color}${selectedProject ? '44' : '22'}`,
            color: meta.color
          }}>
          <Play size={11} className={running ? 'animate-pulse' : ''} />
          {running ? 'Running...' : 'Execute'}
        </button>
      </div>
    </div>
  )
}

function EventLog({ events }) {
  const typeColors = {
    AGENT_START: '#00d4ff', AGENT_DONE: '#00ff88',
    AGENT_ERROR: '#ff3366', CEO_PRIORITIZING: '#7b2fff'
  }
  return (
    <div className="panel p-4 h-80 flex flex-col">
      <div className="flex items-center gap-2 mb-3">
        <Activity size={14} className="text-accent" />
        <span className="text-xs font-semibold text-accent tracking-wider">AGENT EVENT LOG</span>
        <span className="ml-auto text-[10px] text-muted">{events.length} events</span>
      </div>
      <div className="flex-1 overflow-y-auto space-y-1 font-mono text-xs">
        {events.length === 0 && (
          <div className="text-muted text-center py-8 text-xs">Run an agent to see events</div>
        )}
        {events.slice(0, 80).map((e, i) => (
          <div key={i} className="grid grid-cols-[80px_90px_1fr] gap-2 items-center py-0.5 border-b border-border/30">
            <span className="text-slate-600 text-[10px]">
              {new Date(e.timestamp).toLocaleTimeString()}
            </span>
            <span className="px-1.5 py-0.5 rounded text-[10px] text-center"
                  style={{ background: `${typeColors[e.event_type] || '#4a6280'}18`,
                           color: typeColors[e.event_type] || '#4a6280' }}>
              {e.agent_id}
            </span>
            <span className="text-slate-400 truncate text-[10px]">
              {e.event_type}
              {e.data?.project && ` · ${e.data.project}`}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function AgentsPage({ wsEvents, agentActivity }) {
  const [agents, setAgents] = useState([])
  const [projects, setProjects] = useState([])

  useEffect(() => {
    getAgents().then(r => setAgents(r.data)).catch(() => {})
    getProjects().then(r => setProjects(r.data)).catch(() => {})
  }, [])

  const handleRun = async (agentId, projectId) => {
    await runAgent(agentId, projectId)
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="font-display text-lg font-bold text-accent">AGENT SYSTEM</h1>
        <p className="text-xs text-muted">7 autonomous agents · Multi-agent architecture</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        {Object.keys(AGENT_META).map(id => (
          <AgentCard
            key={id}
            agent={{ id, status: 'idle' }}
            activity={agentActivity}
            projects={projects}
            onRun={handleRun}
          />
        ))}
      </div>

      <EventLog events={wsEvents} />
    </div>
  )
}
