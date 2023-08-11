import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import DatacentersView from '../views/DatacentersView.vue'
import DatacenterDetailsView from '../views/DatacenterDetailsView.vue'
import DatacenterRoomView from '../views/DatacenterRoomView.vue'
import InfrastructuresView from '../views/InfrastructuresView.vue'
import InfrastructureDetailsView from '../views/InfrastructureDetailsView'

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
    path: '/datacenters/:datacenterName', // Use dynamic parameter
    name: 'datacenterdetails', 
    component: DatacenterDetailsView, // create a new component to display details of the datacenter
    props: true, // allow you to pass parameters as props to the component
  },

  {
    path: '/datacenters/:datacenterName/:datacenterRoom', // Use dynamic parameter
    name: 'datacenterroom', 
    component: DatacenterRoomView, // create a new component to display details of the datacenter
    props: true, // allow you to pass parameters as props to the component
  },

  {
    path: '/infrastructures',
    name: 'infrastructures',
    component: InfrastructuresView
  },

  {
    path: '/infrastructures/:infrastructureName',
    name: 'infrastructuredetails',
    component: InfrastructureDetailsView,
    props: true, // allow you to pass parameters as props to the component

  },

]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
