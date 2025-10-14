/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later
*/

import { describe, test, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { getRouter } from 'vue-router-mock'

import ComboBox from '@/components/ComboBox.vue'

describe('ComboBox', () => {
  test('renders with datacenter items and filters correctly', async () => {
    const items = [
      { name: 'paris', rooms: [] },
      { name: 'london', rooms: [] }
    ]

    const wrapper = mount(ComboBox, {
      props: {
        itemType: 'datacenter',
        items
      }
    })

    expect(wrapper.text()).toContain('Select a datacenter')
  })

  test('renders with infrastructure items', () => {
    const items = [
      { name: 'core', description: 'Core infrastructure' },
      { name: 'edge', description: 'Edge infrastructure' }
    ]

    const wrapper = mount(ComboBox, {
      props: {
        itemType: 'infrastructure',
        items
      }
    })

    expect(wrapper.text()).toContain('Select an infrastructure')
  })

  test('navigates to correct route when item is selected', async () => {
    const router = getRouter()
    const items = [{ name: 'paris', rooms: [] }]

    const wrapper = mount(ComboBox, {
      props: {
        itemType: 'datacenter',
        items
      }
    })

    // Simulate item selection
    wrapper.vm.goToItem('paris')
    await nextTick()

    expect(router.push).toHaveBeenCalledWith({
      name: 'datacenterdetails',
      params: { name: 'paris' }
    })
  })
})
