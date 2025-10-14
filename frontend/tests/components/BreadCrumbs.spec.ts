/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later
*/

import { describe, test, expect } from 'vitest'
import { mount } from '@vue/test-utils'

import { getRouter } from 'vue-router-mock'

import BreadCrumbs from '@/components/BreadCrumbs.vue'

describe('BreadCrumbs', () => {
  test('renders logo and datacenter breadcrumb when route meta entry is datacenters', () => {
    const router = getRouter()
    router.currentRoute.value = {
      meta: { entry: 'datacenters' },
      name: 'datacenterdetails'
    }

    const wrapper = mount(BreadCrumbs, {
      props: {
        datacenterName: 'paris'
      }
    })

    expect(wrapper.find('img[alt="Rackslab logo"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Datacenters')
    expect(wrapper.text()).toContain('paris')
  })

  test('renders infrastructure breadcrumb when route meta entry is infrastructures', () => {
    const router = getRouter()
    router.currentRoute.value = {
      meta: { entry: 'infrastructures' },
      name: 'infrastructuredetails'
    }

    const wrapper = mount(BreadCrumbs, {
      props: {
        infrastructureName: 'core'
      }
    })

    expect(wrapper.text()).toContain('Infrastructures')
    expect(wrapper.text()).toContain('core')
  })

  test('renders room breadcrumb when route name is datacenterroom', () => {
    const router = getRouter()
    router.currentRoute.value = {
      meta: { entry: 'datacenters' },
      name: 'datacenterroom'
    }

    const wrapper = mount(BreadCrumbs, {
      props: {
        datacenterName: 'paris',
        datacenterRoom: 'room1'
      }
    })

    expect(wrapper.text()).toContain('paris')
    expect(wrapper.text()).toContain('room1')
  })
})
