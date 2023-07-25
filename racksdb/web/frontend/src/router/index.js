import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import DatacentersView from '../views/DatacentersView.vue'
import InfrastructuresView from '../views/InfrastructuresView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },

  {
    path: '/datacenters',
    name: 'datacenters',
    component: DatacentersView
  },

  {
    path: '/infrastructures',
    name: 'infrastructures',
    component: InfrastructuresView
  },


]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
