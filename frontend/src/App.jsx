import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, FolderGit2, Bot, ListTodo,
  Brain, Zap, Terminal, Wifi, WifiOff, ChevronRight
} from 'lucide-react'
import { useWebSocket } from './hooks/useWebSocket'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import ProjectDetail from './pages/ProjectDetail'
import AgentsPage from './pages/AgentsPage'
import TasksPage from './pages/TasksPage'
import GeneratorPage from './pages/GeneratorPage'
import MemoryPage from './pages/MemoryPage'

const NAV = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/projects', icon: FolderGit2, label: 'Projects' },
  { to: '/agents', icon: Bot, label: 'Agents' },
  { to: '/tasks', icon: ListTodo, label: 'Tasks' },
  { to: '/generator', icon: Zap, label: 'Generator' },
  { to: '/memory', icon: Brain, label: 'Memory' },
]

function Sidebar({ connected, liveEvents }) {
  return (
    <aside className="w-56 min-h-screen bg-panel border-r border-border flex flex-col">
      {/* Logo */}
      <div className="p-5 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-accent2 flex items-center justify-center">
            <Terminal size={16} className="text-void" />
          </div>
          <div>
            <div className="font-display text-xs font-bold text-accent tracking-wider">CEO AI</div>
            <div className="text-[10px] text-muted font-mono">OPERATING SYSTEM</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-3 space-y-1">
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 group
               ${isActive
                 ? 'bg-accent/10 text-accent border border-accent/20'
                 : 'text-muted hover:text-slate-300 hover:bg-surface'
               }`
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={16} className={isActive ? 'text-accent' : ''} />
                <span className="font-medium">{label}</span>
                {isActive && <ChevronRight size={12} className="ml-auto text-accent" />}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Status */}
      <div className="p-4 border-t border-border">
        <div className="flex items-center gap-2 text-xs">
          {connected
            ? <><Wifi size={12} className="text-success" /><span className="text-success">Live</span></>
            : <><WifiOff size={12} className="text-danger" /><span className="text-danger">Offline</span></>
          }
          <span className="ml-auto text-muted font-mono">{liveEvents} events</span>
        </div>
      </div>
    </aside>
  )
}

function AppContent() {
  const { events, connected, agentActivity } = useWebSocket()

  return (
    <div className="flex min-h-screen bg-void grid-bg">
      <Sidebar connected={connected} liveEvents={events.length} />
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Dashboard wsEvents={events} agentActivity={agentActivity} />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/projects/:id" element={<ProjectDetail />} />
          <Route path="/agents" element={<AgentsPage wsEvents={events} agentActivity={agentActivity} />} />
          <Route path="/tasks" element={<TasksPage />} />
          <Route path="/generator" element={<GeneratorPage />} />
          <Route path="/memory" element={<MemoryPage wsEvents={events} />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  )
}
