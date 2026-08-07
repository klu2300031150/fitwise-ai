import type { ReactNode } from 'react'

export function Panel({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`rounded-3xl border border-white/10 bg-white/10 p-6 shadow-glow backdrop-blur-xl ${className}`}>{children}</div>
}

export function Button({
  children,
  onClick,
  type = 'button',
  variant = 'primary',
  className = '',
  disabled = false,
}: {
  children: ReactNode
  onClick?: () => void
  type?: 'button' | 'submit'
  variant?: 'primary' | 'secondary' | 'ghost'
  className?: string
  disabled?: boolean
}) {
  const variants = {
    primary: 'bg-accent-500 text-slate-950 hover:bg-accent-300',
    secondary: 'bg-white/10 text-white hover:bg-white/15 border border-white/10',
    ghost: 'bg-transparent text-slate-200 hover:bg-white/5',
  }
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`inline-flex items-center justify-center rounded-2xl px-4 py-3 text-sm font-semibold transition ${variants[variant]} disabled:cursor-not-allowed disabled:opacity-60 ${className}`}
    >
      {children}
    </button>
  )
}

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={`w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-sm text-white placeholder:text-slate-400 outline-none transition focus:border-accent-300 ${props.className ?? ''}`} />
}

export function Select(props: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return <select {...props} className={`w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-sm text-white outline-none transition focus:border-accent-300 ${props.className ?? ''}`} />
}

export function Label({ children }: { children: ReactNode }) {
  return <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{children}</label>
}

export function StatChip({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
      <div className="text-[11px] uppercase tracking-[0.25em] text-slate-400">{label}</div>
      <div className="mt-1 text-lg font-semibold text-white">{value}</div>
    </div>
  )
}
