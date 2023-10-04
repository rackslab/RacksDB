import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import DatacentersView from '../views/DatacentersView.vue'
import DatacenterDetailsView from '../views/DatacenterDetailsView.vue'
import DatacenterRoomView from '../views/DatacenterRoomView.vue'
import InfrastructuresView from '../views/InfrastructuresView.vue'
import InfrastructureDetailsView from '../views/InfrastructureDetailsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
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
      path: '/datacenters/:datacenterName',
      name: 'datacenterdetails',
      component: DatacenterDetailsView,
      props: true,
    },

    {
      path: '/datacenters/:datacenterName/:datacenterRoom',
      name: 'datacenterroom',
      component: DatacenterRoomView,
      props: true,
    },

    {
      path: '/infrastructures',
      name: 'infrastructures',
      component: InfrastructuresView,
    },

    {
      path: '/infrastructures/:infrastructureName',
      name: 'infrastructuresdetails',
      component: InfrastructureDetailsView,
      props: true,
    },

    
  ]
})

export default router
