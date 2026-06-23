import { createRouter, createWebHistory } from 'vue-router'
import OrderList from '../views/OrderList.vue'
import OrderDetail from '../views/OrderDetail.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: OrderList },
    { path: '/orders/:orderNo', component: OrderDetail, props: true },
  ],
})
