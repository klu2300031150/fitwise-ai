import { Link } from 'react-router-dom'
import { Button, Panel, StatChip } from '../components/ui'

export function LandingPage() {
  return (
    <div className="space-y-10">
      <section className="grid gap-8 lg:grid-cols-[1.25fr_0.75fr] lg:items-center">
        <div className="space-y-6">
          <div className="inline-flex rounded-full border border-accent-300/30 bg-accent-300/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.28em] text-accent-100">
            Dynamic size intelligence for apparel sellers
          </div>
          <h1 className="max-w-3xl text-5xl font-black tracking-tight text-white md:text-7xl">
            Generate fit charts and size recommendations in one workflow.
          </h1>
          <p className="max-w-2xl text-lg leading-8 text-slate-300">
            FitWise AI keeps sizing simple. Sellers upload product details and files, the backend generates a size chart, and customers get a recommendation from a clean rule-based fit engine.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link to="/seller"><Button>Open Seller Dashboard</Button></Link>
            <Link to="/customer"><Button variant="secondary">Try Fit Assistant</Button></Link>
          </div>
        </div>
        <Panel className="relative overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(56,189,248,0.28),_transparent_45%)]" />
          <div className="relative space-y-5">
            <div className="text-xs uppercase tracking-[0.3em] text-slate-400">Why FitWise</div>
            <div className="grid grid-cols-2 gap-3">
              <StatChip label="Pages" value="3" />
              <StatChip label="Database" value="SQLite" />
              <StatChip label="AI" value="Rule-based" />
              <StatChip label="Deploy" value="Docker Compose" />
            </div>
            <div className="rounded-3xl border border-white/10 bg-slate-950/55 p-4 text-sm leading-7 text-slate-300">
              Sellers upload product images and a tech pack. FitWise then saves the product, creates a size chart, and returns a size recommendation with a short explanation.
            </div>
          </div>
        </Panel>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {[
          ['Seller dashboard', 'Upload product details and generate a chart immediately.'],
          ['Customer fit assistant', 'Enter body measurements and get a size recommendation.'],
          ['Demo product', 'A demo product is seeded on startup so the app works immediately.'],
        ].map(([title, body]) => (
          <Panel key={title} className="space-y-3">
            <h3 className="text-xl font-semibold text-white">{title}</h3>
            <p className="text-sm leading-7 text-slate-300">{body}</p>
          </Panel>
        ))}
      </section>
    </div>
  )
}
