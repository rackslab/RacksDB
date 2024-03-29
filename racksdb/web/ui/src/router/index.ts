/*Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later */

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
      component: HomeView,
      meta: { entry: 'home' }
    },

    {
      path: '/datacenters',
      name: 'datacenters',
      component: DatacentersView,
      meta: { entry: 'datacenters' }
    },

    {
      path: '/datacenters/:name',
      name: 'datacenterdetails',
      component: DatacenterDetailsView,
      props: true,
      meta: { entry: 'datacenters' }
    },

    {
      path: '/datacenters/:datacenterName/:datacenterRoom',
      name: 'datacenterroom',
      component: DatacenterRoomView,
      props: true,
      meta: { entry: 'datacenters' }
    },

    {
      path: '/infrastructures',
      name: 'infrastructures',
      component: InfrastructuresView,
      meta: { entry: 'infrastructures' }
    },

    {
      path: '/infrastructures/:name',
      name: 'infrastructuredetails',
      component: InfrastructureDetailsView,
      props: true,
      meta: { entry: 'infrastructures' }
    }
  ]
})

export default router
