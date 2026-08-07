import { useEffect, useMemo, useState } from 'react'
import { generateChart, listProducts, uploadProduct } from '../lib/api'
import type { Product, SizeChart } from '../types'
import { Button, Input, Label, Panel, Select, StatChip } from '../components/ui'
import { SizeComparisonChart } from '../components/charts'

const defaultToken = localStorage.getItem('fitwise_token') || ''

export function SellerDashboard() {
  const [token, setToken] = useState(defaultToken)
  const [products, setProducts] = useState<Product[]>([])
  const [selectedChart, setSelectedChart] = useState<SizeChart | null>(null)
  const [status, setStatus] = useState('')
  const [form, setForm] = useState({
    product_name: 'Aero Performance Tee',
    product_category: 'Tops',
    fabric_type: 'Cotton Elastane Blend',
    gsm: '180',
    stretch_percentage: '8',
    weave_type: 'Jersey Knit',
  })
  const [files, setFiles] = useState<{ front?: File; back?: File; flat?: File; tech?: File }>({})

  useEffect(() => {
    if (!token) return
    listProducts(token)
      .then(setProducts)
      .catch(() => setStatus('Login first to load your products.'))
  }, [token])

  const chartData = useMemo(() => selectedChart?.sizes ?? [], [selectedChart])

  async function submitUpload() {
    if (!token) {
      setStatus('Login first and paste your token here.')
      return
    }
    const data = new FormData()
    data.append('product_name', form.product_name)
    data.append('product_category', form.product_category)
    data.append('fabric_type', form.fabric_type)
    data.append('gsm', form.gsm)
    data.append('stretch_percentage', form.stretch_percentage)
    data.append('weave_type', form.weave_type)
    if (files.front) data.append('front_image', files.front)
    if (files.back) data.append('back_image', files.back)
    if (files.flat) data.append('flat_lay_image', files.flat)
    if (files.tech) data.append('tech_pack', files.tech)
    try {
      const result = await uploadProduct(token, data)
      setStatus(`Uploaded ${result.product.name} and generated a chart.`)
      setSelectedChart(result.chart)
      const refreshed = await listProducts(token)
      setProducts(refreshed)
    } catch (error) {
      setStatus(error instanceof Error ? error.message : 'Upload failed')
    }
  }

  async function regenerate(productId: string) {
    if (!token) return
    setStatus('Regenerating chart...')
    const chart = await generateChart(token, productId)
    setSelectedChart(chart)
    setStatus('Chart regenerated successfully.')
  }

  return (
    <div className="space-y-8">
      <Panel className="space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-3xl font-bold text-white">Seller Dashboard</h2>
            <p className="mt-2 text-sm text-slate-300">Upload product assets, generate the size chart, and inspect explainability.</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <StatChip label="Products" value={`${products.length}`} />
            <StatChip label="Mode" value="Seller" />
            <StatChip label="Cache" value="Redis-ready" />
          </div>
        </div>
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <div>
            <Label>Access token</Label>
            <Input value={token} onChange={(event) => { localStorage.setItem('fitwise_token', event.target.value); setToken(event.target.value) }} placeholder="Paste JWT token from /auth/login" />
          </div>
          <div>
            <Label>Product name</Label>
            <Input value={form.product_name} onChange={(event) => setForm({ ...form, product_name: event.target.value })} />
          </div>
          <div>
            <Label>Category</Label>
            <Input value={form.product_category} onChange={(event) => setForm({ ...form, product_category: event.target.value })} />
          </div>
          <div>
            <Label>Fabric type</Label>
            <Input value={form.fabric_type} onChange={(event) => setForm({ ...form, fabric_type: event.target.value })} />
          </div>
          <div>
            <Label>GSM</Label>
            <Input type="number" value={form.gsm} onChange={(event) => setForm({ ...form, gsm: event.target.value })} />
          </div>
          <div>
            <Label>Stretch %</Label>
            <Input type="number" value={form.stretch_percentage} onChange={(event) => setForm({ ...form, stretch_percentage: event.target.value })} />
          </div>
          <div>
            <Label>Weave type</Label>
            <Input value={form.weave_type} onChange={(event) => setForm({ ...form, weave_type: event.target.value })} />
          </div>
          <div>
            <Label>Front image</Label>
            <Input type="file" accept="image/*" onChange={(event) => setFiles({ ...files, front: event.target.files?.[0] })} />
          </div>
          <div>
            <Label>Back image</Label>
            <Input type="file" accept="image/*" onChange={(event) => setFiles({ ...files, back: event.target.files?.[0] })} />
          </div>
          <div>
            <Label>Flat-lay image</Label>
            <Input type="file" accept="image/*" onChange={(event) => setFiles({ ...files, flat: event.target.files?.[0] })} />
          </div>
          <div className="md:col-span-2">
            <Label>Tech pack PDF / text</Label>
            <Input type="file" accept=".pdf,.txt" onChange={(event) => setFiles({ ...files, tech: event.target.files?.[0] })} />
          </div>
        </div>
        <div className="flex flex-wrap gap-3">
          <Button onClick={submitUpload}>Upload and Generate Chart</Button>
          <Button variant="secondary" onClick={() => token && listProducts(token).then(setProducts)}>Refresh Products</Button>
        </div>
        <p className="text-sm text-slate-300">{status}</p>
      </Panel>

      <div className="grid gap-6 xl:grid-cols-[1fr_1.1fr]">
        <Panel className="space-y-4">
          <h3 className="text-xl font-semibold text-white">Your Products</h3>
          <div className="space-y-3">
            {products.map((product) => (
              <div key={product.id} className="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="font-semibold text-white">{product.name}</div>
                    <div className="text-sm text-slate-400">{product.category} · {product.status}</div>
                  </div>
                  <Button variant="secondary" onClick={() => regenerate(product.id)}>Generate</Button>
                </div>
                <div className="mt-3 text-xs text-slate-400">
                  Validation: {(product.validation_summary?.alerts ?? ['Ready']).join(' • ')}
                </div>
              </div>
            ))}
            {!products.length && <p className="text-sm text-slate-400">No products yet. Upload the first SKU to begin.</p>}
          </div>
        </Panel>
        <Panel className="space-y-4">
          <h3 className="text-xl font-semibold text-white">Generated Size Chart</h3>
          {selectedChart ? (
            <>
              <SizeComparisonChart chart={chartData} />
              <div className="grid gap-3 md:grid-cols-2">
                {selectedChart.notes.map((note) => (
                  <div key={note} className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">{note}</div>
                ))}
              </div>
            </>
          ) : (
            <p className="text-sm text-slate-400">Upload a product or regenerate one of your existing SKUs to inspect the chart.</p>
          )}
        </Panel>
      </div>
    </div>
  )
}
