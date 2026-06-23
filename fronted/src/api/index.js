const BASE = '/api'

async function request(path) {
  const res = await fetch(BASE + path)
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`)
  return res.json()
}

export const fetchOrders = (params = {}) => {
  const q = new URLSearchParams(params).toString()
  return request(`/orders/${q ? '?' + q : ''}`)
}

export const fetchSKUs = (orderNo) =>
  request(`/sku/?order_no=${encodeURIComponent(orderNo)}`)

export const fetchTracking = (assignedTracking) =>
  request(`/tracking/?assigned_tracking=${encodeURIComponent(assignedTracking)}`)

export const fetchInvoice = (orderNo) =>
  request(`/invoice/${encodeURIComponent(orderNo)}`)

export const fetchAuspostShipments = (orderNo) =>
  request(`/auspost/shipments/${encodeURIComponent(orderNo)}`)
