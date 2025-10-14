/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later
*/

import { describe, test, expect } from 'vitest'
import { mount } from '@vue/test-utils'

import FiltersBar from '@/components/FiltersBar.vue'

describe('FiltersBar', () => {
  test('renders active filters as badges', () => {
    const wrapper = mount(FiltersBar, {
      props: {
        selectedRacks: ['R01', 'R02'],
        selectedEquipmentTypes: ['server'],
        selectedCategories: ['nodes'],
        selectedTags: ['prod'],
        inputEquipmentName: 'test-server'
      }
    })

    expect(wrapper.text()).toContain('R01')
    expect(wrapper.text()).toContain('R02')
    expect(wrapper.text()).toContain('server')
    expect(wrapper.text()).toContain('nodes')
    expect(wrapper.text()).toContain('prod')
    expect(wrapper.text()).toContain('test-server')
  })

  test('does not render empty filters', () => {
    const wrapper = mount(FiltersBar, {
      props: {
        selectedRacks: [],
        selectedEquipmentTypes: [],
        selectedCategories: [],
        selectedTags: [],
        inputEquipmentName: ''
      }
    })

    // Should only show "Filters" label and screen reader text
    expect(wrapper.text()).toContain('Filters')
    expect(wrapper.text()).toContain('active')
  })

  test('removes filter when X button is clicked', async () => {
    const wrapper = mount(FiltersBar, {
      props: {
        selectedRacks: ['R01'],
        selectedEquipmentTypes: [],
        selectedCategories: [],
        selectedTags: [],
        inputEquipmentName: ''
      }
    })

    // Find and click the X button for R01
    const removeButton = wrapper.find('button')
    await removeButton.trigger('click')

    // Check that the filter was removed
    expect(wrapper.vm.selectedRacks).toEqual([])
  })

  test('clears equipment name filter when X button is clicked', async () => {
    const wrapper = mount(FiltersBar, {
      props: {
        selectedRacks: [],
        selectedEquipmentTypes: [],
        selectedCategories: [],
        selectedTags: [],
        inputEquipmentName: 'test'
      }
    })

    // Find and click the X button for equipment name
    const removeButton = wrapper.find('button')
    await removeButton.trigger('click')

    // Check that the equipment name was cleared
    expect(wrapper.vm.inputEquipmentName).toBe('')
  })
})
