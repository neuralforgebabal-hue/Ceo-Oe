import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getProjects, scanProjects, runAllAgents } from '../api/client'
import {
  FolderGit2, RefreshCw, Search, Bot, ChevronRight,
  Shield, TrendingUp, Zap, GitBranch, Box, TestTube
} from 'lucide-react'

const TYPE_COLORS = {
  python: '#3b82f6', bot: '#00d4ff', web: '#7b2fff',
  ai: '#00ff88', node: '#f59e0b', unknown: '#4a6280'
}

const TYPE_LABELS = {
  python: 'Python', bot: 'Bot', web: 'Web', ai: 'AI', node: 'Node', unknown: '?'
}

function ScorePill({ value, color }) {
  return (
    <div className="flex items-center gap-1">
      <div className="w-12 h-1 rounded-full bg-border overflow-hidden">
        <div className="h-full rounded-full" style={{ width: `${value * 10}%`, background: color }} />
      </div>
      <span className="text-[10px] font-mono" style={{ color }}>{value.toFixed(1)}</span>
    </div>
  )
}

function ProjectCard({ project, onRunAgents }) {
  const typeColor = TYPE_COLORS[project.project_type] || '#4a6280'
  const [running, setRunning] = useState(false)

  const handleRun = async (e) => {
    e.preventDefault()
    setRunning(true)
    try { await onRunAgents(project.id) } finally { setRunning(false) }
  }

  return (
    <Link to={`/projects/${project.id}`}
      className="panel-glow block p-4 hover:border-accent/40 transition-all duration-200">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold"
               style={{ background: `${typeColor}18`, color: typeColor, border: `1px solid ${typeColor}33` }}>
            {TYPE_LABELS[project.project_type]?.[0] || '?'}
          </div>
          <div>
            <div className="font-semibold text-slate-200 text-sm truncate max-w-36">{project.name}</div>
            <div className="text-[10px] text-muted font-mono">{project.framework || project.language}</div>
          </div>
        </div>
        <ChevronRight size={14} className="text-muted mt-1" />
      </div>

      <div className="space-y-1.5 mb-3">
        <ScorePill value={project.profit_score || 0} color="#00ff88" />
        <ScorePill value={project.stability_score || 0} color="#00d4ff" />
        <ScorePill value={(project.success_prediction || 0) / 10} color="#7b2fff" />
      </div>

      <div className="flex items-center gap-2 mb-3">
        {project.has_git && <GitBranch size={11} className="text-muted" />}
        {project.has_dockerfile && <Box size={11} className="text-muted" />}
        {project.has_tests && <TestTube size={11} className="text-success" />}
        <span className="text-[10px] text-muted ml-auto">{project.file_count} files · {project.total_lines?.toLocaleString()} lines</span>
      </div>

      <button onClick={handleRun} disabled={running}
        className="w-full text-xs py-1.5 rounded-lg border border-accent/20 text-accent
                   hover:bg-accent/10 transition-all duration-200 flex items-center justify-center gap-1">
        <Bot size={11} className={running ? 'animate-pulse' : ''} />
        {running ? 'Running...' : 'Run Agents'}
      </button>
    </Link>
  )
}

export default function Projects() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [scanning, setScanning] = useState(false)
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('all')

  useEffect(() => { load() }, [])

  const load = async () => {
    try { const r = await getProjects(); setProjects(r.data) }
    catch (_) {}
    finally { setLoading(false) }
  }

  const handleScan = async () => {
    setScanning(true)
    try { await scanProjects(); await load() }
    finally { setScanning(false) }
  }

  const handleRunAgents = async (projectId) => {
    await runAllAgents(projectId)
  }

  const types = ['all', ...new Set(projects.map(p => p.project_type))]
  const filtered = projects.filter(p => {
    const matchSearch = p.name.toLowerCase().includes(search.toLowerCase())
    const matchFilter = filter === 'all' || p.project_type === filter
    return matchSearch && matchFilter
  })

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-lg font-bold text-accent">PROJECTS</h1>
          <p className="text-xs text-muted">{projects.length} projects scanned</p>
        </div>
        <button onClick={handleScan} disabled={scanning} className="btn-primary flex items-center gap-2">
          <RefreshCw size={13} className={scanning ? 'animate-spin' : ''} />
          {scanning ? 'Scanning...' : 'Scan ~/'}
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-64">
          <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
          <input value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search projects..."
            className="w-full bg-surface border border-border rounded-lg pl-8 pr-3 py-2 text-sm
                       text-slate-300 placeholder:text-muted focus:outline-none focus:border-accent/50" />
        </div>
        <div className="flex gap-1">
          {types.map(t => (
            <button key={t} onClick={() => setFilter(t)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-all
                ${filter === t ? 'bg-accent/15 text-accent border border-accent/30' : 'text-muted hover:text-slate-300 border border-transparent'}`}>
              {t}
            </button>
          ))}
        </div>
      </div>

      {loading
        ? <div className="text-center text-muted py-16 text-sm">Loading projects...</div>
        : filtered.length === 0
          ? <div className="text-center text-muted py-16">
              <FolderGit2 size={32} className="mx-auto mb-3 opacity-30" />
              <p className="text-sm">No projects found. Run a scan first.</p>
            </div>
          : <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filtered.map(p => <ProjectCard key={p.id} project={p} onRunAgents={handleRunAgents} />)}
            </div>
      }
    </div>
  )
}
