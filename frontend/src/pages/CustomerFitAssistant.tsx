import { useEffect, useState } from 'react'
import { listProducts, recommendSize } from '../lib/api'
import type { Product, RecommendationResponse, SizeCell } from '../types'
import { Button, Input, Label, Panel, Select } from '../components/ui'

export function CustomerFitAssistant() {
  const [products, setProducts] = useState<Product[]>([])
  const [selectedProductId, setSelectedProductId] = useState('')
  const [result, setResult] = useState<RecommendationResponse | null>(null)
  const [form, setForm] = useState({
    height: '175',
    weight: '72',
    chest: '96',
    waist: '82',
    hip: '98',
  })

  useEffect(() => {
    listProducts().then((items) => {
      setProducts(items)
      setSelectedProductId(items[0]?.id ?? '')
    })
  }, [])

  async function handleRecommend() {
    if (!selectedProductId) return
    const payload = {
      product_id: selectedProductId,
      height: Number(form.height),
      weight: Number(form.weight),
      chest: Number(form.chest),
      waist: Number(form.waist),
      hip: Number(form.hip),
    }
    const recommendation = await recommendSize(payload)
    setResult(recommendation)
  }

  return (
    <div className="space-y-8">
      <Panel className="space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-3xl font-bold text-white">Customer Fit Assistant</h2>
            <p className="mt-2 text-sm text-slate-300">Choose a product, enter body measurements, and get a size recommendation instantly.</p>
          </div>
        </div>
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <div>
            <Label>Product</Label>
            <Select value={selectedProductId} onChange={(event) => setSelectedProductId(event.target.value)}>
              <option value="">Select a product</option>
              {products.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name}
                </option>
              ))}
            </Select>
          </div>
        </div>
      </Panel>

      <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Panel className="space-y-4">
          <h3 className="text-xl font-semibold text-white">Fit Inputs</h3>
          <div className="grid gap-4 md:grid-cols-2">
            {(['height', 'weight', 'chest', 'waist', 'hip'] as const).map((field) => (
              <div key={field}>
                <Label>{field}</Label>
                <Input value={form[field]} onChange={(event) => setForm({ ...form, [field]: event.target.value })} />
              </div>
            ))}
          </div>
          <Button onClick={handleRecommend}>Get Recommendation</Button>
        </Panel>

        <Panel className="space-y-4">
          <h3 className="text-xl font-semibold text-white">Recommendation Result</h3>
          {result ? (
            <>
              <div className="rounded-3xl border border-accent-300/20 bg-accent-300/10 p-5">
                <div className="text-xs uppercase tracking-[0.28em] text-accent-100">Recommended Size</div>
                <div className="mt-2 text-5xl font-black text-white">{result.recommended_size}</div>
                <div className="mt-2 text-sm text-slate-300">Confidence: {(result.confidence_score * 100).toFixed(1)}%</div>
              </div>
              <div className="space-y-2">
                {result.reason.map((item) => (
                  <div key={item} className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">{item}</div>
                ))}
              </div>
              <div className="rounded-3xl border border-white/10 bg-slate-950/40 p-4">
                <div className="mb-3 text-sm font-semibold text-white">Chart preview</div>
                <div className="grid gap-2 md:grid-cols-2">
                  {result.size_table.slice(0, 4).map((size) => (
                    <SizePreview key={size.size} row={size} />
                  ))}
                </div>
              </div>
            </>
          ) : (
            <p className="text-sm text-slate-400">Choose a product and click recommendation to see the fit result.</p>
          )}
        </Panel>
      </div>
    </div>
  )
}

function SizePreview({ row }: { row: SizeCell }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
      <div className="flex items-center justify-between">
        <span className="font-semibold text-white">{row.size}</span>
        <span>{Math.round(row.confidence * 100)}%</span>
      </div>
      <div className="mt-2 text-xs text-slate-400">Chest {row.chest} cm · Waist {row.waist} cm</div>
    </div>
  )
}
