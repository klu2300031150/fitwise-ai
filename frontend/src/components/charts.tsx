import { Bar, BarChart, CartesianGrid, Cell, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { SizeCell } from '../types'

const palette = ['#38bdf8', '#7dd3fc', '#f59e0b', '#f97316', '#94a3b8', '#e2e8f0']

export function SizeComparisonChart({ chart }: { chart: SizeCell[] }) {
  return (
    <div className="h-80 rounded-3xl border border-white/10 bg-slate-950/40 p-4">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chart} margin={{ top: 12, right: 24, left: 0, bottom: 12 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#24324a" />
          <XAxis dataKey="size" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip contentStyle={{ background: '#07111f', border: '1px solid #1e293b', borderRadius: 16 }} />
          <Legend />
          <Bar dataKey="chest" fill="#38bdf8" radius={[12, 12, 0, 0]} />
          <Bar dataKey="waist" fill="#f59e0b" radius={[12, 12, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export function RecommendationTrendChart({ chart }: { chart: Array<{ size: string; count: number }> }) {
  return (
    <div className="h-72 rounded-3xl border border-white/10 bg-slate-950/40 p-4">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chart} margin={{ top: 12, right: 24, left: 0, bottom: 12 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#24324a" />
          <XAxis dataKey="size" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip contentStyle={{ background: '#07111f', border: '1px solid #1e293b', borderRadius: 16 }} />
          <Bar dataKey="count" radius={[12, 12, 0, 0]}>
            {chart.map((entry, index) => (
              <Cell key={`cell-${entry.size}`} fill={palette[index % palette.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
