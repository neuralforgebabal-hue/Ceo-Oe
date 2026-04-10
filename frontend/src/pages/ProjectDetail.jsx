import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getProject, runAgent, runAllAgents, predictProject, improveProject } from '../api/client'
import {
  ArrowLeft, Bot, Shield, TrendingUp, Zap, Code2,
  DollarSign, Rocket, RefreshCw, GitBranch, Box,
  TestTube, FileText, AlertTriangle, CheckCircle2, Clock
} from 'lucide-react'

const AGENTS = [
  { id: 'ceo', label: 'CEO', icon: Bot, color: '#00d4ff' },
  { id: 'architect', label: 'Architect', icon: Code2, color: '#7b2fff' },
  { id: 'developer', label: 'Developer', icon: Code2, color: '#00ff88' },
  { id: 'security', label: 'Security', icon: Shield, color: '#ff3366' },
  { id: 'analyst', label: 'Analyst', icon: TrendingUp, color: '#ffaa00' },
  { id: 'monetization', label: 'Monetize', icon: DollarSign, color: '#f97316' },
  { id: 'deployment', label: 'Deploy', icon: Rocket, color: '#00d4ff' },
]

function Badge({ children, color = '#4a6280' }) {
  return (
    <span className="text-[10px] px-2 py-0.5 rounded-full font-mono"
          style={{ background: `${color}20`, color, border: `1px solid ${color}30` }}>
      {children}
    </span>
  )
}

function MetricBar({ label, value, max = 10, color }) {
  const pct = Math.min((value / max) * 100, 100)
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-muted">{label}</span>
        <span className="font-mono font-bold" style={{ color }}>{typeof value === 'number' ? value.toFixed(1) : value}</span>
      </div>
      <div className="h-1.5 rounded-full bg-border overflow-hidden">
        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  )
}

function ReportCard({ report }) {
  const [open, setOpen] = useState(false)
  const typeColors = {
    security: '#ff3366', architecture: '#7b2fff', developer: '#00ff88',
    analysis: '#ffaa00', monetization: '#f97316', deployment: '#00d4ff', ceo_analysis: '#00d4ff'
  }
  const color = typeColors[report.type] || '#4a6280'

  return (
    <div className="border border-border rounded-lg overflow-hidden">
      <button onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-3 hover:bg-surface transition-colors">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full" style={{ background: color }} />
          <span className="text-xs font-semibold capitalize" style={{ color }}>{report.type}</span>
          <span className="text-[10px] text-muted">by {report.agent}</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[10px] text-muted">{new Date(report.created_at).toLocaleString()}</span>
          <span className="text-muted text-xs">{open ? '▲' : '▼'}</span>
        </div>
      </button>
      {report.summary && (
        <div className="px-3 pb-2 text-xs text-muted border-t border-border/50 pt-2">{report.summary}</div>
      )}
      {open && report.content && (
        <div className="border-t border-border bg-void p-3 max-h-80 overflow-y-auto">
          <pre className="text-[11px] text-slate-400 whitespace-pre-wrap font-mono">
            {JSON.stringify(report.content, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

export default function ProjectDetail() {
  const { id } = useParams()
  const [data, setData] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [improvement, setImprovement] = useState(null)
  const [loading, setLoading] = useState(true)
  const [runningAgent, setRunningAgent] = useState(null)
  const [runningAll, setRunningAll] = useState(false)

  useEffect(() => { load() }, [id])

  const load = async () => {
    try { const r = await getProject(id); setData(r.data) }
    catch (_) {}
    finally { setLoading(false) }
  }

  const handleRunAgent = async (agentId) => {
    setRunningAgent(agentId)
    try { await runAgent(agentId, id); setTimeout(load, 2000) }
    finally { setRunningAgent(null) }
  }

  const handleRunAll = async () => {
    setRunningAll(true)
    try { await runAllAgents(id); setTimeout(load, 4000) }
    finally { setRunningAll(false) }
  }

  const handlePredict = async () => {
    try { const r = await predictProject(id); setPrediction(r.data) } catch (_) {}
  }

  const handleImprove = async () => {
    try { const r = await improveProject(id); setImprovement(r.data) } catch (_) {}
  }

  if (loading) return <div className="p-6 text-muted text-sm">Loading project...</div>
  if (!data) return <div className="p-6 text-danger text-sm">Project not found</div>

  const { project, reports } = data

  return (
    <div className="p-6 space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <Link to="/projects" className="text-muted hover:text-accent transition-colors">
            <ArrowLeft size={18} />
          </Link>
          <div>
            <h1 className="font-display text-lg font-bold text-accent">{project.name}</h1>
            <p className="text-xs text-muted font-mono mt-0.5">{project.path}</p>
          </div>
        </div>
        <button onClick={handleRunAll} disabled={runningAll}
          className="btn-primary flex items-center gap-2">
          <Bot size={13} className={runningAll ? 'animate-pulse' : ''} />
          {runningAll ? 'Running All...' : 'Run All Agents'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Left: Info + Scores */}
        <div className="space-y-4">
          {/* Project Info */}
          <div className="panel p-4 space-y-3">
            <div className="text-xs text-muted font-semibold tracking-wider">PROJECT INFO</div>
            <div className="flex flex-wrap gap-1.5">
              <Badge color="#3b82f6">{project.project_type}</Badge>
              {project.framework && <Badge color="#7b2fff">{project.framework}</Badge>}
              <Badge color="#4a6280">{project.language}</Badge>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-surface rounded p-2">
                <div className="text-muted">Files</div>
                <div className="font-bold text-slate-200">{project.file_count}</div>
              </div>
              <div className="bg-surface rounded p-2">
                <div className="text-muted">Lines</div>
                <div className="font-bold text-slate-200">{project.total_lines?.toLocaleString()}</div>
              </div>
            </div>
            <div className="flex flex-wrap gap-2 text-[10px]">
              {project.has_git && <span className="flex items-center gap-1 text-success"><GitBranch size={10} />Git</span>}
              {project.has_dockerfile && <span className="flex items-center gap-1 text-accent"><Box size={10} />Docker</span>}
              {project.has_tests && <span className="flex items-center gap-1 text-success"><TestTube size={10} />Tests</span>}
              {project.readme_exists && <span className="flex items-center gap-1 text-muted"><FileText size={10} />README</span>}
            </div>
          </div>

          {/* Scores */}
          <div className="panel p-4 space-y-3">
            <div className="text-xs text-muted font-semibold tracking-wider">SCORES</div>
            <MetricBar label="Profit Potential" value={project.profit_score} color="#00ff88" />
            <MetricBar label="Stability" value={project.stability_score} color="#00d4ff" />
            <MetricBar label="Complexity" value={project.complexity_score} color="#ffaa00" />
            <MetricBar label="Success Prediction" value={project.success_prediction} max={100} color="#7b2fff" />
          </div>

          {/* Engines */}
          <div className="panel p-4 space-y-2">
            <div className="text-xs text-muted font-semibold tracking-wider mb-3">INTELLIGENCE</div>
            <button onClick={handlePredict} className="btn-ghost w-full flex items-center gap-2 justify-center">
              <TrendingUp size={13} /> Predict Success
            </button>
            <button onClick={handleImprove} className="btn-ghost w-full flex items-center gap-2 justify-center">
              <Zap size={13} /> Suggest Improvements
            </button>
          </div>
        </div>

        {/* Right: Agents + Reports */}
        <div className="lg:col-span-2 space-y-4">
          {/* Agent Buttons */}
          <div className="panel p-4">
            <div className="text-xs text-muted font-semibold tracking-wider mb-3">RUN INDIVIDUAL AGENTS</div>
            <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
              {AGENTS.map(({ id: aId, label, icon: Icon, color }) => (
                <button key={aId} onClick={() => handleRunAgent(aId)}
                  disabled={runningAgent === aId}
                  className="flex flex-col items-center gap-1.5 p-3 rounded-lg border border-border
                             hover:border-opacity-60 transition-all duration-200 text-xs"
                  style={runningAgent === aId ? { borderColor: color, background: `${color}10` } : {}}>
                  <Icon size={16} style={{ color }} />
                  <span className="text-muted">{label}</span>
                  {runningAgent === aId && <RefreshCw size={10} className="animate-spin text-accent" />}
                </button>
              ))}
            </div>
          </div>

          {/* Prediction Result */}
          {prediction && (
            <div className="panel p-4 border-accent2/30">
              <div className="text-xs font-semibold text-accent2 mb-3">PREDICTION RESULT</div>
              <div className="grid grid-cols-2 gap-3 text-xs mb-3">
                <div className="bg-surface rounded p-2">
                  <div className="text-muted">Success Probability</div>
                  <div className="text-xl font-bold text-success">{prediction.success_probability}%</div>
                </div>
                <div className="bg-surface rounded p-2">
                  <div className="text-muted">Market Viability</div>
                  <div className="font-bold text-accent">{prediction.market_viability}</div>
                </div>
              </div>
              {prediction.risk_factors?.length > 0 && (
                <div className="space-y-1">
                  {prediction.risk_factors.slice(0, 3).map((r, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs">
                      <AlertTriangle size={11} className="text-warning flex-shrink-0" />
                      <span className="text-muted">{r.factor} — <span className="text-warning">{r.impact}</span></span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Improvement Result */}
          {improvement && improvement.improvement_plan && (
            <div className="panel p-4 border-success/20">
              <div className="text-xs font-semibold text-success mb-3">IMPROVEMENT PLAN</div>
              <div className="space-y-2">
                {improvement.improvement_plan.slice(0, 4).map((item, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs bg-surface rounded p-2">
                    <span className="w-4 h-4 rounded-full bg-success/20 text-success flex items-center justify-center text-[10px] flex-shrink-0">{item.priority}</span>
                    <div>
                      <div className="text-slate-300">{item.action}</div>
                      <div className="text-muted">{item.estimated_hours}h · {item.impact} impact</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Reports */}
          <div className="panel p-4">
            <div className="text-xs text-muted font-semibold tracking-wider mb-3">
              AGENT REPORTS ({reports?.length || 0})
            </div>
            {!reports?.length
              ? <div className="text-center text-muted text-xs py-6">No reports yet — run agents to generate</div>
              : <div className="space-y-2">{reports.map(r => <ReportCard key={r.id} report={r} />)}</div>
            }
          </div>
        </div>
      </div>
    </div>
  )
}
