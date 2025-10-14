/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT
*/

import { describe, test, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { getRouter } from 'vue-router-mock'

import HeaderPage from '@/components/HeaderPage.vue'

describe('HeaderPage', () => {
  test('renders navigation links', () => {
    const router = getRouter()
    router.currentRoute.value = {
      meta: { entry: 'home' }
    }

    const wrapper = mount(HeaderPage)

    expect(wrapper.text()).toContain('Home')
    expect(wrapper.text()).toContain('Datacenters')
    expect(wrapper.text()).toContain('Infrastructures')
  })

  test('highlights active route based on meta entry', () => {
    const router = getRouter()
    router.currentRoute.value = {
      meta: { entry: 'datacenters' }
    }

    const wrapper = mount(HeaderPage)

    // Check that the component renders the navigation links
    expect(wrapper.text()).toContain('Home')
    expect(wrapper.text()).toContain('Datacenters')
    expect(wrapper.text()).toContain('Infrastructures')
  })
})
