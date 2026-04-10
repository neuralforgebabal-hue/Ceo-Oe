import React, { useState, useEffect } from 'react'
import { generateProject, getTemplates } from '../api/client'
import { Zap, FolderPlus, CheckCircle2, AlertTriangle, Loader2, FileText } from 'lucide-react'

const TEMPLATE_ICONS = {
  telegram_bot: '🤖', flask_api: '🐍', fastapi_app: '⚡',
  web_scraper: '🕷️', ai_agent: '🧠'
}

const EXAMPLE_PROMPTS = [
  'A Telegram bot that monitors crypto prices and sends alerts',
  'A REST API for managing personal tasks with authentication',
  'A web scraper that collects and exports job listings from LinkedIn',
  'An AI assistant that summarizes YouTube videos via URL',
  'A FastAPI backend for a SaaS subscription management system',
]

export default function GeneratorPage() {
  const [description, setDescription] = useState('')
  const [template, setTemplate] = useState('flask_api')
  const [outputName, setOutputName] = useState('')
  const [templates, setTemplates] = useState({})
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getTemplates().then(r => setTemplates(r.data.details || {})).catch(() => {})
  }, [])

  const handleGenerate = async () => {
    if (!description.trim()) return
    setLoading(true)
    setResult(null)
    setError(null)
    try {
      const r = await generateProject(description, template, outputName || null)
      setResult(r.data)
    } catch (e) {
      setError('Generation failed. Check your AI provider config.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="font-display text-lg font-bold text-accent">PROJECT GENERATOR</h1>
        <p className="text-xs text-muted">AI generates a complete working project from your description</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <div className="space-y-4">
          {/* Description */}
          <div className="panel p-4 space-y-3">
            <label className="text-xs font-semibold text-muted tracking-wider">PROJECT DESCRIPTION</label>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder="Describe what you want to build..."
              rows={5}
              className="w-full bg-surface border border-border rounded-lg p-3 text-sm text-slate-300
                         placeholder:text-muted focus:outline-none focus:border-accent/50 resize-none font-body"
            />
            <div className="text-[10px] text-muted">Examples:</div>
            <div className="space-y-1">
              {EXAMPLE_PROMPTS.map((p, i) => (
                <button key={i} onClick={() => setDescription(p)}
                  className="w-full text-left text-[11px] text-muted hover:text-accent transition-colors
                             px-2 py-1.5 rounded hover:bg-accent/5 border border-transparent hover:border-accent/20">
                  → {p}
                </button>
              ))}
            </div>
          </div>

          {/* Template Selection */}
          <div className="panel p-4 space-y-3">
            <label className="text-xs font-semibold text-muted tracking-wider">TEMPLATE</label>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(templates).map(([key, info]) => (
                <button key={key} onClick={() => setTemplate(key)}
                  className={`p-3 rounded-lg border text-left transition-all duration-200
                    ${template === key
                      ? 'border-accent/50 bg-accent/10 text-accent'
                      : 'border-border text-muted hover:border-accent/30 hover:text-slate-300'}`}>
                  <div className="text-lg mb-1">{TEMPLATE_ICONS[key] || '📦'}</div>
                  <div className="text-xs font-medium">{key.replace('_', ' ')}</div>
                  <div className="text-[10px] mt-0.5 opacity-70">{info.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Output name */}
          <div className="panel p-4 space-y-2">
            <label className="text-xs font-semibold text-muted tracking-wider">OUTPUT NAME (optional)</label>
            <input value={outputName} onChange={e => setOutputName(e.target.value)}
              placeholder="my_awesome_project"
              className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm text-slate-300
                         placeholder:text-muted focus:outline-none focus:border-accent/50 font-mono" />
          </div>

          <button onClick={handleGenerate} disabled={loading || !description.trim()}
            className="w-full btn-primary py-3 flex items-center justify-center gap-2 text-sm disabled:opacity-40">
            {loading
              ? <><Loader2 size={16} className="animate-spin" /> Generating with AI...</>
              : <><Zap size={16} /> Generate Project</>
            }
          </button>
        </div>

        {/* Result */}
        <div className="space-y-4">
          {!result && !error && !loading && (
            <div className="panel p-8 text-center text-muted h-full flex flex-col items-center justify-center">
              <FolderPlus size={40} className="mb-3 opacity-20" />
              <p className="text-sm">Describe your project and hit Generate</p>
              <p className="text-xs mt-1">AI will create the full structure + code</p>
            </div>
          )}

          {loading && (
            <div className="panel p-8 text-center">
              <Loader2 size={32} className="animate-spin text-accent mx-auto mb-3" />
              <p className="text-sm text-muted">AI is building your project...</p>
              <p className="text-xs text-muted mt-1">This takes 10–30 seconds</p>
            </div>
          )}

          {error && (
            <div className="panel p-4 border-danger/30 text-sm text-danger flex items-center gap-2">
              <AlertTriangle size={16} /> {error}
            </div>
          )}

          {result && !result.error && (
            <div className="space-y-4">
              <div className="panel p-4 border-success/20">
                <div className="flex items-center gap-2 mb-3">
                  <CheckCircle2 size={16} className="text-success" />
                  <span className="text-sm font-semibold text-success">Project Generated!</span>
                </div>
                <div className="text-xs text-muted mb-1">Name</div>
                <div className="font-mono text-sm text-accent mb-3">{result.project_name}</div>
                {result.output_path && (
                  <>
                    <div className="text-xs text-muted mb-1">Saved to</div>
                    <div className="font-mono text-xs text-slate-300 bg-surface rounded p-2">{result.output_path}</div>
                  </>
                )}
              </div>

              {result.tech_stack?.length > 0 && (
                <div className="panel p-4">
                  <div className="text-xs text-muted mb-2 font-semibold tracking-wider">TECH STACK</div>
                  <div className="flex flex-wrap gap-1.5">
                    {result.tech_stack.map((t, i) => (
                      <span key={i} className="tag bg-accent/10 text-accent border border-accent/20">{t}</span>
                    ))}
                  </div>
                </div>
              )}

              {result.files?.length > 0 && (
                <div className="panel p-4">
                  <div className="text-xs text-muted mb-2 font-semibold tracking-wider">
                    FILES CREATED ({result.files.length})
                  </div>
                  <div className="space-y-1 max-h-60 overflow-y-auto">
                    {result.files.map((f, i) => (
                      <div key={i} className="flex items-center gap-2 text-xs">
                        <FileText size={11} className="text-muted flex-shrink-0" />
                        <span className="font-mono text-slate-300">{f.path}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {result.setup_instructions?.length > 0 && (
                <div className="panel p-4">
                  <div className="text-xs text-muted mb-2 font-semibold tracking-wider">SETUP</div>
                  <div className="space-y-1">
                    {result.setup_instructions.map((s, i) => (
                      <div key={i} className="font-mono text-xs bg-surface rounded px-3 py-1.5 text-slate-300">
                        $ {s}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
