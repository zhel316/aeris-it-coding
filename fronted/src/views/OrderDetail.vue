<template>
  <div>
    <button class="back-btn" @click="$router.back()">← Back to Orders</button>

    <div v-if="loading" class="state-msg">Loading order…</div>
    <div v-else-if="error" class="state-msg error">{{ error }}</div>

    <template v-else-if="order">
      <!-- Header -->
      <div class="order-header mt-4">
        <div>
          <span class="order-no">{{ order.order_no }}</span>
          <span :class="['badge', statusClass(order.status), 'ml-3']">{{ order.status }}</span>
        </div>
        <div class="order-date">Order date: {{ formatDate(order.order_data) }}</div>
      </div>

      <!-- Company/Customer + Tracking -->
      <div class="two-col mt-6">
        <div class="card">
          <div class="card-header">Company &amp; Customer</div>
          <dl class="info-grid">
            <dt>Company</dt>   <dd>{{ order.company_name }}</dd>
            <dt>Customer</dt>  <dd>{{ order.customer_name }}</dd>
            <dt>Phone</dt>     <dd>{{ order.phone }}</dd>
            <dt>Email</dt>     <dd><a :href="`mailto:${order.email}`">{{ order.email }}</a></dd>
            <dt>Address</dt>   <dd>{{ order.address }}</dd>
          </dl>
        </div>

        <div class="card">
          <div class="card-header">Tracking</div>
          <div v-if="trackingLoading" class="inner-msg">Loading…</div>
          <table v-else class="data-table">
            <thead><tr><th>Label</th><th>Tracking No</th><th>Logistics</th></tr></thead>
            <tbody>
              <tr v-if="trackingList.length === 0">
                <td colspan="3" class="empty-row">No tracking assigned.</td>
              </tr>
              <tr v-for="t in trackingList" :key="t.assigned_tracking">
                <td><span class="track-tag">{{ t.assigned_tracking }}</span></td>
                <td class="mono">{{ t.track_no }}</td>
                <td>{{ t.logistics_company }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- AusPost Shipments -->
      <div class="card mt-6">
        <div class="card-header">AusPost Shipments</div>
        <div v-if="shipmentsLoading" class="inner-msg">Fetching shipments from AusPost…</div>
        <div v-else-if="shipmentsError" class="inner-msg error-msg">{{ shipmentsError }}</div>
        <template v-else>
          <div v-if="auspostShipments.length === 0" class="empty-row" style="padding:1.5rem;text-align:center">
            No shipments found for this order in AusPost.
          </div>
          <template v-else>
            <div v-for="s in auspostShipments" :key="s.shipment_id" class="shipment-block">

              <!-- Shipment header row -->
              <div class="shipment-header">
                <div class="shipment-ref-row">
                  <span class="mono bold">{{ s.shipment_reference }}</span>
                  <span v-if="s.tracking_status" :class="['badge', trackingStatusClass(s.tracking_status)]">
                    {{ s.tracking_status }}
                  </span>
                  <span v-else :class="['badge', shipmentStatusClass(s.status)]">{{ s.status }}</span>
                </div>
                <div class="shipment-cost">
                  ${{ fmt(s.total_cost) }}
                  <span class="gst-note">(incl. GST ${{ fmt(s.total_gst) }})</span>
                </div>
              </div>

              <!-- Items table -->
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Article ID</th>
                    <th>Consignment</th>
                    <th>Product</th>
                    <th>Weight</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in s.items" :key="item.article_id">
                    <td class="mono">{{ item.article_id }}</td>
                    <td class="mono">{{ item.consignment_id }}</td>
                    <td><span class="product-badge">{{ item.product_name }}</span></td>
                    <td>{{ item.weight }} kg</td>
                    <td>
                      <span v-if="item.tracking_status" :class="['badge', trackingStatusClass(item.tracking_status)]">
                        {{ item.tracking_status }}
                      </span>
                      <span v-else :class="['badge', shipmentStatusClass(item.status)]">{{ item.status }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>

              <!-- Tracking events timeline -->
              <div v-if="s.tracking_events && s.tracking_events.length" class="timeline-section">
                <div class="timeline-title">Tracking Events</div>
                <div class="timeline">
                  <div
                    v-for="(evt, idx) in s.tracking_events"
                    :key="idx"
                    class="timeline-item"
                    :class="{ 'timeline-item--first': idx === 0 }"
                  >
                    <div class="tl-dot" :class="idx === 0 ? 'tl-dot--active' : ''"></div>
                    <div class="tl-content">
                      <div class="tl-desc" :class="idx === 0 ? 'tl-desc--active' : ''">{{ evt.description }}</div>
                      <div class="tl-meta">
                        <span v-if="evt.location" class="tl-location">{{ evt.location }}</span>
                        <span class="tl-date">{{ formatEventDate(evt.date) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

            </div>

            <!-- Shipping cost summary -->
            <div class="shipping-total">
              <span>Total Shipping Cost</span>
              <span class="bold">${{ fmt(totalShippingCost) }}</span>
            </div>
          </template>
        </template>
      </div>

      <!-- Invoice -->
      <div class="card mt-6">
        <div class="card-header">Invoice</div>
        <div v-if="invoiceLoading" class="inner-msg">Loading product details…</div>
        <template v-else>
          <table class="data-table invoice-table">
            <thead>
              <tr>
                <th style="width:80px"></th>
                <th>SKU</th>
                <th>Product Name</th>
                <th class="num-col">RRP (incl. GST)</th>
                <th class="num-col">Qty</th>
                <th class="num-col">Line Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!invoice || invoice.items.length === 0">
                <td colspan="6" class="empty-row">No items.</td>
              </tr>
              <tr v-for="item in invoice.items" :key="item.sku_id">
                <td class="img-cell"><img :src="item.image_url" :alt="item.sku_id" class="sku-img" /></td>
                <td class="mono bold">{{ item.sku_id }}</td>
                <td class="product-name">{{ item.product_name }}</td>
                <td class="num-col">${{ fmt(item.rrp) }}</td>
                <td class="num-col">{{ item.qty }}</td>
                <td class="num-col bold">${{ fmt(item.line_total) }}</td>
              </tr>
            </tbody>
          </table>

          <div class="summary-box" v-if="invoice">
            <div class="summary-row">
              <span>Subtotal</span>
              <span>${{ fmt(invoice.subtotal) }}</span>
            </div>
            <div class="summary-row gst-row">
              <span>GST (10% of subtotal)</span>
              <span>${{ fmt(invoice.gst) }}</span>
            </div>
            <div class="summary-row">
              <span>Shipment Fee</span>
              <span>${{ fmt(invoice.shipment_fee) }}</span>
            </div>
            <div class="summary-row total-row">
              <span>Total</span>
              <span>${{ fmt(invoice.total) }}</span>
            </div>
          </div>
        </template>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { fetchOrders, fetchSKUs, fetchTracking, fetchInvoice, fetchAuspostShipments } from '../api/index.js'

const props = defineProps({ orderNo: String })
const route = useRoute()
const resolvedOrderNo = props.orderNo || decodeURIComponent(route.params.orderNo)

const order             = ref(null)
const skus              = ref([])
const trackingList      = ref([])
const invoice           = ref(null)
const auspostShipments  = ref([])

const loading           = ref(true)
const skuLoading        = ref(true)
const trackingLoading   = ref(true)
const invoiceLoading    = ref(true)
const shipmentsLoading  = ref(true)
const shipmentsError    = ref(null)
const error             = ref(null)

const totalShippingCost = computed(() =>
  auspostShipments.value.reduce((sum, s) => sum + (s.total_cost || 0), 0)
)

async function loadOrder() {
  try {
    const list = await fetchOrders({ order_no: resolvedOrderNo })
    order.value = list.find(o => o.order_no === resolvedOrderNo) ?? null
    if (!order.value) throw new Error('Order not found')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function loadSKUs() {
  try { skus.value = await fetchSKUs(resolvedOrderNo) }
  finally { skuLoading.value = false }
  await loadTracking()
}

async function loadTracking() {
  const labels = [...new Set(skus.value.map(s => s.assigned_tracking).filter(Boolean))]
  try {
    const results = await Promise.all(labels.map(l => fetchTracking(l)))
    trackingList.value = results.flat()
  } finally { trackingLoading.value = false }
}

async function loadInvoice() {
  try { invoice.value = await fetchInvoice(resolvedOrderNo) }
  catch { invoice.value = null }
  finally { invoiceLoading.value = false }
}

async function loadAuspostShipments() {
  try {
    const data = await fetchAuspostShipments(resolvedOrderNo)
    auspostShipments.value = data.shipments || []
  } catch (e) {
    shipmentsError.value = `Could not load AusPost shipments: ${e.message}`
  } finally {
    shipmentsLoading.value = false
  }
}

function formatDate(d) {
  if (!d) return '—'
  const [y, m, day] = d.split('-')
  return `${day}/${m}/${y.slice(2)}`
}

function statusClass(s) {
  return s === 'completed' ? 'badge-completed' : 'badge-in-transit'
}

function shipmentStatusClass(s) {
  const map = { Created: 'badge-created', Despatch: 'badge-despatch', Delivered: 'badge-completed' }
  return map[s] || 'badge-created'
}

function trackingStatusClass(s) {
  if (!s) return 'badge-created'
  const l = s.toLowerCase()
  if (l.includes('delivered')) return 'badge-completed'
  if (l.includes('out for delivery')) return 'badge-out-delivery'
  if (l.includes('in transit')) return 'badge-in-transit'
  if (l.includes('picked up')) return 'badge-picked-up'
  return 'badge-created'
}

function formatEventDate(d) {
  if (!d) return ''
  const dt = new Date(d)
  return dt.toLocaleString('en-AU', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function fmt(n) { return Number(n || 0).toFixed(2) }

onMounted(async () => {
  await loadOrder()
  if (order.value) {
    await Promise.all([loadSKUs(), loadInvoice(), loadAuspostShipments()])
  } else {
    skuLoading.value = false
    trackingLoading.value = false
    invoiceLoading.value = false
    shipmentsLoading.value = false
  }
})
</script>

<style scoped>
.back-btn { background: none; border: none; color: #3b82f6; font-size: .85rem; cursor: pointer; padding: 0; }
.back-btn:hover { text-decoration: underline; }

.order-header { display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: .5rem; }
.order-no { font-size: 1.3rem; font-weight: 700; font-family: monospace; color: #1e293b; }
.order-date { color: #64748b; font-size: .85rem; }
.ml-3 { margin-left: .75rem; }

.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; }
@media (max-width: 700px) { .two-col { grid-template-columns: 1fr; } }

.info-grid { display: grid; grid-template-columns: 110px 1fr; gap: 0; padding: .5rem 0; }
.info-grid dt { padding: .55rem 1.25rem; font-size: .8rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: .3px; border-bottom: 1px solid #f1f5f9; }
.info-grid dd { padding: .55rem 1rem .55rem 0; color: #1e293b; border-bottom: 1px solid #f1f5f9; }
.info-grid dd:last-child, .info-grid dt:nth-last-child(2) { border-bottom: none; }
.info-grid a { color: #3b82f6; text-decoration: none; }
.info-grid a:hover { text-decoration: underline; }

.track-tag { display: inline-block; padding: .15rem .55rem; background: #dbeafe; color: #1d4ed8; border-radius: 4px; font-size: .78rem; font-weight: 600; }

/* AusPost shipment blocks */
.shipment-block { border-bottom: 1px solid #f1f5f9; }
.shipment-block:last-of-type { border-bottom: none; }

.shipment-header { display: flex; justify-content: space-between; align-items: center; padding: .75rem 1.25rem; background: #f8fafc; }
.shipment-ref-row { display: flex; align-items: center; gap: .75rem; }
.shipment-cost { font-size: .9rem; font-weight: 600; color: #1e293b; }
.gst-note { font-weight: 400; color: #64748b; font-size: .8rem; }

.badge-created      { background: #e0f2fe; color: #0369a1; }
.badge-despatch     { background: #fef3c7; color: #b45309; }
.badge-out-delivery { background: #fef3c7; color: #b45309; }
.badge-picked-up    { background: #ede9fe; color: #7c3aed; }

.product-badge { display: inline-block; padding: .15rem .55rem; background: #f0fdf4; color: #15803d; border-radius: 4px; font-size: .78rem; font-weight: 600; }

/* Timeline */
.timeline-section { padding: .75rem 1.25rem 1rem; background: #fafafa; border-top: 1px solid #f1f5f9; }
.timeline-title { font-size: .75rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: .4px; margin-bottom: .75rem; }
.timeline { display: flex; flex-direction: column; gap: 0; padding-left: .25rem; }

.timeline-item { display: flex; gap: .75rem; position: relative; padding-bottom: .75rem; }
.timeline-item:last-child { padding-bottom: 0; }
.timeline-item:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 14px;
  bottom: 0;
  width: 1px;
  background: #e2e8f0;
}

.tl-dot {
  width: 13px; height: 13px; border-radius: 50%;
  background: #cbd5e1; border: 2px solid #fff;
  box-shadow: 0 0 0 1px #cbd5e1;
  flex-shrink: 0; margin-top: 2px;
}
.tl-dot--active { background: #1e3a5f; box-shadow: 0 0 0 1px #1e3a5f; }

.tl-content { flex: 1; }
.tl-desc { font-size: .85rem; color: #475569; }
.tl-desc--active { font-weight: 600; color: #1e293b; }
.tl-meta { display: flex; gap: .75rem; margin-top: .15rem; font-size: .75rem; color: #94a3b8; }
.tl-location::after { content: '·'; margin-left: .75rem; }

.shipping-total { display: flex; justify-content: flex-end; gap: 3rem; padding: .75rem 1.25rem; background: #f8fafc; border-top: 1px solid #e2e8f0; font-size: .9rem; color: #475569; }

/* Invoice */
.invoice-table .num-col { text-align: right; }
.img-cell { padding: .5rem 1rem; }
.sku-img { width: 56px; height: 56px; object-fit: cover; border-radius: 6px; border: 1px solid #e2e8f0; display: block; }
.product-name { color: #334155; max-width: 280px; }

.summary-box { display: flex; flex-direction: column; align-items: flex-end; padding: 1rem 1.25rem 1.25rem; border-top: 1px solid #e2e8f0; gap: .35rem; }
.summary-row { display: flex; gap: 3rem; font-size: .88rem; color: #475569; min-width: 320px; justify-content: space-between; }
.gst-row { color: #64748b; font-size: .82rem; }
.total-row { margin-top: .4rem; padding-top: .5rem; border-top: 2px solid #1e3a5f; font-size: 1rem; font-weight: 700; color: #1e293b; }

.mono { font-family: monospace; font-size: .85rem; }
.bold { font-weight: 600; }
.empty-row { text-align: center; color: #94a3b8; padding: 1.5rem; }
.inner-msg { padding: 1.5rem; text-align: center; color: #94a3b8; font-size: .85rem; }
.error-msg { color: #dc2626 !important; }
.state-msg { margin-top: 1.5rem; text-align: center; color: #64748b; padding: 2rem; }
.state-msg.error { color: #dc2626; }
</style>
