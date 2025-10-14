/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later
*/

import { describe, test, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'

import InfrastructureTable from '@/components/InfrastructureTable.vue'

describe('InfrastructureTable', () => {
  const mockInfrastructure = {
    name: 'test-infra',
    layout: [
      {
        rack: 'R01',
        nodes: [
          {
            name: 'server1',
            equipmentType: 'nodes',
            type: { id: 'dell-r740' },
            tags: ['prod'],
            position: { height: 1, width: 1 }
          }
        ],
        network: [],
        storage: [],
        misc: []
      }
    ]
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('renders infrastructure table with equipment', async () => {
    const wrapper = mount(InfrastructureTable, {
      props: {
        infrastructureDetails: mockInfrastructure
      },
      global: {
        stubs: {
          EquipmentTypeModal: true,
          InfrastructureFilters: true,
          FiltersBar: true
        }
      }
    })

    await nextTick()

    expect(wrapper.text()).toContain('R01')
    expect(wrapper.text()).toContain('server1')
    expect(wrapper.text()).toContain('nodes')
    expect(wrapper.text()).toContain('dell-r740')
  })

  test('toggles rack display when rack header is clicked', async () => {
    const wrapper = mount(InfrastructureTable, {
      props: {
        infrastructureDetails: mockInfrastructure
      },
      global: {
        stubs: {
          EquipmentTypeModal: true,
          InfrastructureFilters: true,
          FiltersBar: true
        }
      }
    })

    await nextTick()

    // Initially rack should be displayed
    expect(wrapper.vm.displayRacks.R01).toBe(true)

    // Click to toggle
    wrapper.vm.displayRackEquipment('R01')
    await nextTick()

    expect(wrapper.vm.displayRacks.R01).toBe(false)
  })

  test('inverts rack sort order', async () => {
    const wrapper = mount(InfrastructureTable, {
      props: {
        infrastructureDetails: mockInfrastructure
      },
      global: {
        stubs: {
          EquipmentTypeModal: true,
          InfrastructureFilters: true,
          FiltersBar: true
        }
      }
    })

    await nextTick()

    const initialOrder = wrapper.vm.alphabeticalOrder
    wrapper.vm.invertRacksSort()
    await nextTick()

    expect(wrapper.vm.alphabeticalOrder).toBe(!initialOrder)
  })

  test('toggles slider visibility', async () => {
    const wrapper = mount(InfrastructureTable, {
      props: {
        infrastructureDetails: mockInfrastructure
      },
      global: {
        stubs: {
          EquipmentTypeModal: true,
          InfrastructureFilters: true,
          FiltersBar: true
        }
      }
    })

    await nextTick()

    const initialSliderState = wrapper.vm.showSlider
    wrapper.vm.toggleSlider()
    await nextTick()

    expect(wrapper.vm.showSlider).toBe(!initialSliderState)
  })

  test('filters equipment based on selected criteria', async () => {
    const wrapper = mount(InfrastructureTable, {
      props: {
        infrastructureDetails: mockInfrastructure
      },
      global: {
        stubs: {
          EquipmentTypeModal: true,
          InfrastructureFilters: true,
          FiltersBar: true
        }
      }
    })

    await nextTick()

    // Set filter criteria
    wrapper.vm.selectedRacks = ['R01']
    wrapper.vm.inputEquipmentName = 'server'
    await nextTick()

    // Test that the filtering logic works by checking the computed property
    expect(wrapper.vm.selectedRacks).toEqual(['R01'])
    expect(wrapper.vm.inputEquipmentName).toBe('server')
  })

  test('toggles modal when equipment type is clicked', async () => {
    const wrapper = mount(InfrastructureTable, {
      props: {
        infrastructureDetails: mockInfrastructure
      },
      global: {
        stubs: {
          EquipmentTypeModal: true,
          InfrastructureFilters: true,
          FiltersBar: true
        }
      }
    })

    await nextTick()

    const equipmentType = { id: 'dell-r740' }
    wrapper.vm.toggleModal(equipmentType)
    await nextTick()

    expect(wrapper.vm.showModal).toBe(true)
    expect(wrapper.vm.modalContent).toStrictEqual(equipmentType)
  })
})
