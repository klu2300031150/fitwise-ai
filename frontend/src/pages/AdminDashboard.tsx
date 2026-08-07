import { useEffect, useState } from 'react'
import { adminSummary } from '../lib/api'
import type { AdminSummary } from '../types'
import { Button, Input, Label, Panel, StatChip } from '../components/ui'
import { RecommendationTrendChart } from '../components/charts'

export function AdminDashboard() {
  const [token, setToken] = useState(localStorage.getItem('fitwise_token') || '')
  const [summary, setSummary] = useState<AdminSummary | null>(null)

  useEffect(() => {
    if (!token) return
    adminSummary(token).then(setSummary).catch(() => setSummary(null))
  }, [token])

  return (
    <div className="space-y-8">
      <Panel className="space-y-5">
        <div>
          <h2 className="text-3xl font-bold text-white">Admin Dashboard</h2>
          <p className="mt-2 text-sm text-slate-300">Monitor recommendation health, validation alerts, and fit trends.</p>
        </div>
        <div className="grid gap-3 md:grid-cols-[1fr_auto]">
          <div>
            <Label>Admin token</Label>
            <Input value={token} onChange={(event) => { localStorage.setItem('fitwise_token', event.target.value); setToken(event.target.value) }} placeholder="Paste JWT token from /auth/login" />
          </div>
          <div className="flex items-end">
            <Button variant="secondary" onClick={() => token && adminSummary(token).then(setSummary)}>Refresh</Button>
          </div>
        </div>
        <div className="grid gap-3 sm:grid-cols-4">
          <StatChip label="Products" value={`${summary?.total_products ?? 0}`} />
          <StatChip label="Recommendations" value={`${summary?.total_recommendations ?? 0}`} />
          <StatChip label="Cache hit rate" value={`${Math.round((summary?.cache_hit_rate ?? 0) * 100)}%`} />
          <StatChip label="Alerts" value={`${summary?.validation_alerts.length ?? 0}`} />
        </div>
      </Panel>

      <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Panel className="space-y-4">
          <h3 className="text-xl font-semibold text-white">Validation Alerts</h3>
          <div className="space-y-3">
            {(summary?.validation_alerts ?? ['No alerts yet.']).map((alert) => (
              <div key={alert} className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">{alert}</div>
            ))}
          </div>
        </Panel>
        <Panel className="space-y-4">
          <h3 className="text-xl font-semibold text-white">Sizing Trends</h3>
          <RecommendationTrendChart chart={summary?.top_sizing_trends ?? []} />
        </Panel>
      </div>
    </div>
  )
}
