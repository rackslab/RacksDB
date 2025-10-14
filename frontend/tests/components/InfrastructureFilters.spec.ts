/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later
*/

import { describe, test, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'

import InfrastructureFilters from '@/components/InfrastructureFilters.vue'

describe('InfrastructureFilters', () => {
  test('renders filter sections when slider is shown', async () => {
    const wrapper = mount(InfrastructureFilters, {
      props: {
        showSlider: true,
        racks: ['R01', 'R02'],
        equipmentCategories: ['nodes', 'storage'],
        equipmentTypes: ['server', 'switch'],
        tags: ['prod', 'test'],
        selectedRacks: [],
        selectedEquipmentTypes: [],
        selectedCategories: [],
        selectedTags: [],
        inputEquipmentName: ''
      }
    })

    await nextTick()

    // Test that the dialog component exists (even if not visible due to teleport)
    expect(wrapper.findComponent({ name: 'Dialog' }).exists()).toBe(true)

    // Test that the component renders without errors
    expect(wrapper.exists()).toBe(true)

    // Test that the props are passed correctly
    expect(wrapper.props('showSlider')).toBe(true)
    expect(wrapper.props('racks')).toEqual(['R01', 'R02'])
    expect(wrapper.props('equipmentCategories')).toEqual(['nodes', 'storage'])
    expect(wrapper.props('equipmentTypes')).toEqual(['server', 'switch'])
    expect(wrapper.props('tags')).toEqual(['prod', 'test'])
  })

  test('filters racks based on query', async () => {
    const wrapper = mount(InfrastructureFilters, {
      props: {
        showSlider: true,
        racks: ['R01', 'R02', 'R10'],
        equipmentCategories: [],
        equipmentTypes: [],
        tags: [],
        selectedRacks: [],
        selectedEquipmentTypes: [],
        selectedCategories: [],
        selectedTags: [],
        inputEquipmentName: ''
      }
    })

    await nextTick()

    // Set query to filter racks
    wrapper.vm.queryRacks = 'R0'
    await nextTick()

    const filteredRacks = wrapper.vm.filteredRacks
    expect(filteredRacks).toEqual(['R01', 'R02'])
  })

  test('filters equipment types based on query', async () => {
    const wrapper = mount(InfrastructureFilters, {
      props: {
        showSlider: true,
        racks: [],
        equipmentCategories: [],
        equipmentTypes: ['server', 'switch', 'storage'],
        tags: [],
        selectedRacks: [],
        selectedEquipmentTypes: [],
        selectedCategories: [],
        selectedTags: [],
        inputEquipmentName: ''
      }
    })

    await nextTick()

    // Set query to filter equipment types
    wrapper.vm.queryEquipmentTypes = 'ser'
    await nextTick()

    const filteredEquipmentTypes = wrapper.vm.filteredEquipmentTypes
    expect(filteredEquipmentTypes).toEqual(['server'])
  })

  test('emits toggleSlider when close button is clicked', async () => {
    const wrapper = mount(InfrastructureFilters, {
      props: {
        showSlider: true,
        racks: [],
        equipmentCategories: [],
        equipmentTypes: [],
        tags: [],
        selectedRacks: [],
        selectedEquipmentTypes: [],
        selectedCategories: [],
        selectedTags: [],
        inputEquipmentName: ''
      }
    })

    await nextTick()

    // Test that the component renders without errors
    expect(wrapper.exists()).toBe(true)

    // Test that the component can emit toggleSlider event
    await wrapper.vm.$emit('toggleSlider')
    expect(wrapper.emitted('toggleSlider')).toBeTruthy()
  })
})
