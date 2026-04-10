import React, { useEffect, useState } from 'react'
import { getMemories, getBusEvents, getSharedState } from '../api/client'
import { Brain, Activity, Database, RefreshCw, CheckCircle2, XCircle } from 'lucide-react'

const AGENT_COLORS = {
  ceo: '#00d4ff', architect: '#7b2fff', developer: '#00ff88',
  security: '#ff3366', analyst: '#ffaa00', monetization: '#f97316', deployment: '#06b6d4'
}

function MemoryEntry({ memory }) {
  const [open, setOpen] = useState(false)
  const color = AGENT_COLORS[memory.agent_id] || '#4a6280'
  return (
    <div className="border-b border-border/40 last:border-0">
      <button onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-surface/50 transition-colors text-left">
        <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: color }} />
        <span className="text-xs font-semibold w-24 flex-shrink-0 capitalize" style={{ color }}>
          {memory.agent_id}
        </span>
        <span className="text-xs text-muted font-mono flex-1">{memory.action}</span>
        <div className="flex items-center gap-2 flex-shrink-0">
          {memory.success
            ? <CheckCircle2 size={12} className="text-success" />
            : <XCircle size={12} className="text-danger" />}
          <span className="text-[10px] text-slate-600">
            {memory.created_at ? new Date(memory.created_at).toLocaleTimeString() : '—'}
          </span>
        </div>
      </button>
      {open && memory.result && (
        <div className="px-4 pb-3">
          <div className="bg-void rounded p-3 text-[11px] font-mono text-slate-400 max-h-40 overflow-auto">
            {memory.result}
          </div>
          {memory.tags?.length > 0 && (
            <div className="flex gap-1 mt-2">
              {memory.tags.map((t, i) => (
                <span key={i} className="text-[10px] px-2 py-0.5 rounded-full bg-surface text-muted border border-border">{t}</span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function MemoryPage({ wsEvents }) {
  const [memories, setMemories] = useState([])
  const [state, setState] = useState({})
  const [agentStates, setAgentStates] = useState({})
  const [activeTab, setActiveTab] = useState('memories')

  const load = async () => {
    try {
      const [memR, stateR] = await Promise.all([getMemories(100), getSharedState()])
      setMemories(memR.data)
      setState(stateR.data.state || {})
      setAgentStates(stateR.data.agents || {})
    } catch (_) {}
  }

  useEffect(() => { load() }, [])

  const agentMemCount = memories.reduce((acc, m) => {
    acc[m.agent_id] = (acc[m.agent_id] || 0) + 1
    return acc
  }, {})

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-lg font-bold text-accent">MEMORY SYSTEM</h1>
          <p className="text-xs text-muted">Shared agent memory · {memories.length} entries</p>
        </div>
        <button onClick={load} className="btn-ghost flex items-center gap-2">
          <RefreshCw size={13} /> Refresh
        </button>
      </div>

      {/* Agent Memory Breakdown */}
      <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-7 gap-2">
        {Object.entries(AGENT_COLORS).map(([agent, color]) => (
          <div key={agent} className="panel p-3 text-center">
            <div className="text-xl font-bold font-display" style={{ color }}>
              {agentMemCount[agent] || 0}
            </div>
            <div className="text-[10px] text-muted capitalize mt-1">{agent}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1">
        {[
          { id: 'memories', label: 'Memories', icon: Database },
          { id: 'live', label: 'Live Events', icon: Activity },
          { id: 'state', label: 'Shared State', icon: Brain },
        ].map(({ id, label, icon: Icon }) => (
          <button key={id} onClick={() => setActiveTab(id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium transition-all
              ${activeTab === id ? 'bg-accent/15 text-accent border border-accent/30' : 'text-muted border border-transparent hover:text-slate-300'}`}>
            <Icon size={13} /> {label}
          </button>
        ))}
      </div>

      {activeTab === 'memories' && (
        <div className="panel overflow-hidden">
          <div className="divide-y divide-transparent max-h-[520px] overflow-y-auto">
            {memories.length === 0
              ? <div className="text-center text-muted py-12 text-sm">
                  <Brain size={32} className="mx-auto mb-2 opacity-20" />
                  No memories yet — run agents to populate
                </div>
              : memories.map(m => <MemoryEntry key={m.id} memory={m} />)
            }
          </div>
        </div>
      )}

      {activeTab === 'live' && (
        <div className="panel p-4 max-h-[520px] overflow-y-auto space-y-1 font-mono text-xs">
          {wsEvents.length === 0
            ? <div className="text-center text-muted py-12">No live events yet</div>
            : wsEvents.map((e, i) => {
                const color = AGENT_COLORS[e.agent_id] || '#4a6280'
                return (
                  <div key={i} className="flex gap-2 py-1.5 border-b border-border/30">
                    <span className="text-slate-600 w-20 flex-shrink-0">
                      {new Date(e.timestamp).toLocaleTimeString()}
                    </span>
                    <span className="w-24 flex-shrink-0 font-semibold capitalize truncate" style={{ color }}>
                      {e.agent_id}
                    </span>
                    <span className="text-slate-400">{e.event_type}</span>
                    {e.data?.project && (
                      <span className="text-muted ml-auto text-[10px]">· {e.data.project}</span>
                    )}
                  </div>
                )
              })
          }
        </div>
      )}

      {activeTab === 'state' && (
        <div className="space-y-4">
          <div className="panel p-4">
            <div className="text-xs text-muted font-semibold tracking-wider mb-3">AGENT STATES</div>
            {Object.keys(agentStates).length === 0
              ? <div className="text-muted text-xs text-center py-4">No agent state recorded yet</div>
              : <div className="space-y-2">
                  {Object.entries(agentStates).map(([agent, s]) => {
                    const color = AGENT_COLORS[agent] || '#4a6280'
                    return (
                      <div key={agent} className="flex items-center gap-3 text-xs bg-surface rounded p-3">
                        <div className="w-2 h-2 rounded-full" style={{ background: color }} />
                        <span className="w-24 font-semibold capitalize" style={{ color }}>{agent}</span>
                        <span className="text-muted">{s.last_event}</span>
                        <span className="ml-auto text-slate-600 text-[10px]">
                          {s.last_active ? new Date(s.last_active).toLocaleTimeString() : '—'}
                        </span>
                      </div>
                    )
                  })}
                </div>
            }
          </div>

          <div className="panel p-4">
            <div className="text-xs text-muted font-semibold tracking-wider mb-3">SHARED STATE KEYS</div>
            {Object.keys(state).length === 0
              ? <div className="text-muted text-xs text-center py-4">No shared state yet</div>
              : <div className="space-y-2 max-h-72 overflow-y-auto">
                  {Object.entries(state).map(([key, val]) => (
                    <div key={key} className="bg-surface rounded p-2">
                      <div className="text-[10px] text-accent font-mono mb-1">{key}</div>
                      <pre className="text-[10px] text-slate-400 font-mono whitespace-pre-wrap overflow-auto max-h-24">
                        {JSON.stringify(val, null, 2)}
                      </pre>
                    </div>
                  ))}
                </div>
            }
          </div>
        </div>
      )}
    </div>
  )
}
