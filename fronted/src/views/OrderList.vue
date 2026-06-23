<template>
  <div>
    <div class="page-title">Orders</div>

    <!-- Filters -->
    <div class="filters card mt-4">
      <input v-model="filters.order_no"      placeholder="Order #"       class="filter-input" @keyup.enter="load" />
      <input v-model="filters.company_name"  placeholder="Company"       class="filter-input" @keyup.enter="load" />
      <input v-model="filters.customer_name" placeholder="Customer"      class="filter-input" @keyup.enter="load" />
      <select v-model="filters.status" class="filter-input">
        <option value="">All status</option>
        <option value="completed">Completed</option>
        <option value="in-transit">In Transit</option>
      </select>
      <button class="btn-primary" @click="load">Search</button>
      <button class="btn-ghost"   @click="reset">Reset</button>
    </div>

    <!-- Loading / Error -->
    <div v-if="loading" class="state-msg">Loading orders…</div>
    <div v-else-if="error" class="state-msg error">{{ error }}</div>

    <!-- Table -->
    <div v-else class="card mt-4">
      <div class="card-header">{{ orders.length }} order{{ orders.length !== 1 ? 's' : '' }}</div>
      <table class="data-table">
        <thead>
          <tr>
            <th>Order #</th>
            <th>Date</th>
            <th>Status</th>
            <th>Company</th>
            <th>Customer</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="orders.length === 0">
            <td colspan="6" class="empty-row">No orders found.</td>
          </tr>
          <tr
            v-for="order in orders"
            :key="order.order_no"
            class="clickable-row"
            @click="goDetail(order.order_no)"
          >
            <td class="mono">{{ order.order_no }}</td>
            <td>{{ formatDate(order.order_data) }}</td>
            <td>
              <span :class="['badge', statusClass(order.status)]">
                {{ order.status }}
              </span>
            </td>
            <td>{{ order.company_name }}</td>
            <td>{{ order.customer_name }}</td>
            <td class="action-cell">
              <span class="view-link">View →</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchOrders } from '../api/index.js'

const router  = useRouter()
const orders  = ref([])
const loading = ref(false)
const error   = ref(null)

const filters = reactive({ order_no: '', company_name: '', customer_name: '', status: '' })

async function load() {
  loading.value = true
  error.value   = null
  try {
    const params = Object.fromEntries(
      Object.entries(filters).filter(([, v]) => v !== '')
    )
    orders.value = await fetchOrders(params)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function reset() {
  Object.assign(filters, { order_no: '', company_name: '', customer_name: '', status: '' })
  load()
}

function goDetail(orderNo) {
  router.push(`/orders/${encodeURIComponent(orderNo)}`)
}

function formatDate(d) {
  if (!d) return '—'
  const [y, m, day] = d.split('-')
  return `${day}/${m}/${y.slice(2)}`
}

function statusClass(s) {
  return s === 'completed' ? 'badge-completed' : 'badge-in-transit'
}

onMounted(load)
</script>

<style scoped>
.page-title { font-size: 1.4rem; font-weight: 700; color: #1e293b; }

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: .6rem;
  padding: .85rem 1rem;
  align-items: center;
}

.filter-input {
  padding: .4rem .75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: .85rem;
  color: #1e293b;
  background: #fff;
  outline: none;
  min-width: 140px;
}
.filter-input:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59,130,246,.15); }

.btn-primary {
  padding: .4rem 1rem;
  background: #1e3a5f;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: .85rem;
  cursor: pointer;
}
.btn-primary:hover { background: #1e40af; }

.btn-ghost {
  padding: .4rem 1rem;
  background: transparent;
  color: #64748b;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: .85rem;
  cursor: pointer;
}
.btn-ghost:hover { background: #f1f5f9; }

.clickable-row { cursor: pointer; transition: background .1s; }
.clickable-row:hover { background: #f8fafc; }

.mono { font-family: monospace; font-size: .85rem; }

.action-cell { text-align: right; }
.view-link { color: #3b82f6; font-size: .82rem; }

.empty-row { text-align: center; color: #94a3b8; padding: 2rem; }

.state-msg { margin-top: 1.5rem; text-align: center; color: #64748b; padding: 2rem; }
.state-msg.error { color: #dc2626; }
</style>
