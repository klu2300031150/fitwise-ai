import { useEffect, useState, type ReactNode } from 'react'
import { createProduct, listProducts, deleteProduct } from '../lib/api'
import type { Product } from '../types'
import { Button, Input, Label, Panel } from '../components/ui'

export function SellerDashboard() {
  const [products, setProducts] = useState<Product[]>([])
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
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
    listProducts()
      .then((items) => {
        setProducts(items)
        setSelectedProduct(items[0] ?? null)
      })
      .catch(() => setStatus('Unable to load products.'))
  }, [])

  async function submitUpload() {
    const data = new FormData()
    data.append('product_name', form.product_name)
    data.append('category', form.product_category)
    data.append('fabric_type', form.fabric_type)
    data.append('gsm', form.gsm)
    data.append('stretch_percentage', form.stretch_percentage)
    data.append('weave_type', form.weave_type)
    if (files.front) data.append('front_image', files.front)
    if (files.back) data.append('back_image', files.back)
    if (files.flat) data.append('flat_lay_image', files.flat)
    if (files.tech) data.append('tech_pack', files.tech)
    try {
      const result = await createProduct(data)
      setStatus(result.message)
      setSelectedProduct(result.product)
      const refreshed = await listProducts()
      setProducts(refreshed)
    } catch (error) {
      setStatus(error instanceof Error ? error.message : 'Upload failed')
    }
  }

  return (
    <div className="space-y-8">
      <Panel className="space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-3xl font-bold text-white">Seller Dashboard</h2>
            <p className="mt-2 text-sm text-slate-300">Upload a product, generate the size chart, and preview the sizing table.</p>
          </div>
        </div>
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <Field label="Product name"><Input value={form.product_name} onChange={(event) => setForm({ ...form, product_name: event.target.value })} /></Field>
          <Field label="Category"><Input value={form.product_category} onChange={(event) => setForm({ ...form, product_category: event.target.value })} /></Field>
          <Field label="Fabric type"><Input value={form.fabric_type} onChange={(event) => setForm({ ...form, fabric_type: event.target.value })} /></Field>
          <Field label="GSM"><Input type="number" value={form.gsm} onChange={(event) => setForm({ ...form, gsm: event.target.value })} /></Field>
          <Field label="Stretch %"><Input type="number" value={form.stretch_percentage} onChange={(event) => setForm({ ...form, stretch_percentage: event.target.value })} /></Field>
          <Field label="Weave type"><Input value={form.weave_type} onChange={(event) => setForm({ ...form, weave_type: event.target.value })} /></Field>
          <Field label="Front image"><Input type="file" accept="image/*" onChange={(event) => setFiles({ ...files, front: event.target.files?.[0] })} /></Field>
          <Field label="Back image"><Input type="file" accept="image/*" onChange={(event) => setFiles({ ...files, back: event.target.files?.[0] })} /></Field>
          <Field label="Flat-lay image"><Input type="file" accept="image/*" onChange={(event) => setFiles({ ...files, flat: event.target.files?.[0] })} /></Field>
          <div className="md:col-span-2"><Field label="Tech pack PDF / text"><Input type="file" accept=".pdf,.txt" onChange={(event) => setFiles({ ...files, tech: event.target.files?.[0] })} /></Field></div>
        </div>
        <div className="flex flex-wrap gap-3">
          <Button onClick={submitUpload}>Upload and Generate Chart</Button>
          <Button variant="secondary" onClick={() => listProducts().then(setProducts)}>Refresh Products</Button>
        </div>
        <p className="text-sm text-slate-300">{status}</p>
      </Panel>

      <div className="grid gap-6 xl:grid-cols-[1fr_1.1fr]">
        <Panel className="space-y-4">
          <h3 className="text-xl font-semibold text-white">Your Products</h3>
          <div className="space-y-3">
            {products.map((product) => (
              <div key={product.id} className={`w-full rounded-2xl border p-4 transition ${selectedProduct?.id === product.id ? 'border-accent-300 bg-accent-300/10' : 'border-white/10 bg-slate-950/40'}`}>
                <div className="flex items-center justify-between">
                  <div className="text-left" style={{ flex: 1 }}>
                    <button type="button" onClick={() => setSelectedProduct(product)} className="text-left w-full">
                      <div className="font-semibold text-white">{product.name}</div>
                      <div className="text-sm text-slate-400">{product.category} · {product.fabric_type}</div>
                    </button>
                  </div>
                  <div>
                    <Button
                      onClick={async () => {
                        const ok = window.confirm(`Delete product \"${product.name}\"? This cannot be undone.`)
                        if (!ok) return
                        setStatus('Deleting product...')
                        try {
                          await deleteProduct(product.id)
                          const refreshed = await listProducts()
                          setProducts(refreshed)
                          setSelectedProduct((prev) => (prev && prev.id === product.id ? null : prev))
                          setStatus('Product deleted successfully.')
                        } catch (err) {
                          setStatus(err instanceof Error ? err.message : 'Delete failed')
                        }
                      }}
                      className="bg-red-600 hover:bg-red-500"
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              </div>
            ))}
            {!products.length && <p className="text-sm text-slate-400">No products yet. Upload the first SKU to begin.</p>}
          </div>
        </Panel>
        <Panel className="space-y-4">
          <h3 className="text-xl font-semibold text-white">Generated Size Chart</h3>
          {selectedProduct ? (
            <>
              <div className="space-y-2 rounded-3xl border border-white/10 bg-slate-950/40 p-4 text-sm text-slate-300">
                {selectedProduct.chart.sizes.map((row) => (
                  <div key={row.size} className="flex items-center justify-between rounded-2xl bg-white/5 px-4 py-3">
                    <span className="font-semibold text-white">{row.size}</span>
                    <span>Chest {row.chest} · Waist {row.waist} · Hip {row.hip}</span>
                  </div>
                ))}
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                {selectedProduct.explanation.map((note) => (
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

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div>
      <Label>{label}</Label>
      {children}
    </div>
  )
}
