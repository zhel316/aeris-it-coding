<template>
  <div id="app">
    <header class="app-header">
      <span class="logo">Aeris IT</span>
      <span class="title">Order Management</span>
    </header>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f1f5f9;
  color: #1e293b;
  font-size: 14px;
  line-height: 1.5;
}

.app-header {
  background: #1e3a5f;
  color: #fff;
  padding: 0 2rem;
  height: 56px;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 4px rgba(0,0,0,.2);
}

.logo {
  font-weight: 700;
  font-size: 1rem;
  letter-spacing: .5px;
  color: #93c5fd;
}

.title {
  font-size: 0.9rem;
  color: #cbd5e1;
}

.app-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

/* ── shared card ── */
.card {
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}

.card-header {
  padding: .75rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  font-weight: 600;
  font-size: .85rem;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: .4px;
}

/* ── shared table ── */
.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f8fafc;
  padding: .6rem 1rem;
  text-align: left;
  font-size: .8rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: .4px;
  border-bottom: 1px solid #e2e8f0;
}

.data-table td {
  padding: .7rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
}

.data-table tbody tr:last-child td { border-bottom: none; }

/* ── status badge ── */
.badge {
  display: inline-block;
  padding: .2rem .6rem;
  border-radius: 999px;
  font-size: .75rem;
  font-weight: 600;
  text-transform: capitalize;
  white-space: nowrap;
}

.badge-completed  { background: #dcfce7; color: #15803d; }
.badge-in-transit { background: #fef3c7; color: #b45309; }

/* ── utility ── */
.mt-2 { margin-top: .5rem; }
.mt-4 { margin-top: 1rem; }
.mt-6 { margin-top: 1.5rem; }
</style>
