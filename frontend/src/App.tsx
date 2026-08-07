import { NavLink, Route, Routes } from 'react-router-dom'
import { AdminDashboard } from './pages/AdminDashboard'
import { CustomerFitAssistant } from './pages/CustomerFitAssistant'
import { LandingPage } from './pages/LandingPage'
import { SellerDashboard } from './pages/SellerDashboard'

const navItemClass = ({ isActive }: { isActive: boolean }) =>
  `rounded-full px-4 py-2 text-sm font-semibold transition ${isActive ? 'bg-white text-slate-950' : 'text-slate-300 hover:bg-white/10 hover:text-white'}`

export default function App() {
  return (
    <div className="min-h-screen bg-hero-radial text-slate-100">
      <header className="sticky top-0 z-50 border-b border-white/10 bg-ink-950/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <div>
            <div className="text-xs uppercase tracking-[0.35em] text-accent-300">FitWise AI</div>
            <div className="text-lg font-bold text-white">Dynamic Size & Fit Chart Generator</div>
          </div>
          <nav className="flex flex-wrap gap-2">
            <NavLink to="/" className={navItemClass} end>Home</NavLink>
            <NavLink to="/seller" className={navItemClass}>Seller</NavLink>
            <NavLink to="/customer" className={navItemClass}>Customer</NavLink>
            <NavLink to="/admin" className={navItemClass}>Admin</NavLink>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/seller" element={<SellerDashboard />} />
          <Route path="/customer" element={<CustomerFitAssistant />} />
          <Route path="/admin" element={<AdminDashboard />} />
        </Routes>
      </main>
    </div>
  )
}
