/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later
*/

import { describe, test, expect } from 'vitest'
import { mount } from '@vue/test-utils'

import DatacenterListInfrastructures from '@/components/DatacenterListInfrastructures.vue'

describe('DatacenterListInfrastructures', () => {
  test('renders infrastructure links when infrastructures are provided', () => {
    const wrapper = mount(DatacenterListInfrastructures, {
      props: {
        infrastructures: ['core', 'edge', 'storage']
      }
    })

    expect(wrapper.text()).toContain('core')
    expect(wrapper.text()).toContain('edge')
    expect(wrapper.text()).toContain('storage')
    expect(wrapper.text()).toContain(',') // comma separators
  })

  test('renders dash when no infrastructures are provided', () => {
    const wrapper = mount(DatacenterListInfrastructures, {
      props: {
        infrastructures: []
      }
    })

    expect(wrapper.text()).toContain('-')
  })

  test('renders single infrastructure without comma', () => {
    const wrapper = mount(DatacenterListInfrastructures, {
      props: {
        infrastructures: ['core']
      }
    })

    expect(wrapper.text()).toContain('core')
    expect(wrapper.text()).not.toContain(',')
  })
})
