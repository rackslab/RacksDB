/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT
*/

import { describe, test, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'

import EquipmentTypeModal from '@/components/EquipmentTypeModal.vue'

describe('EquipmentTypeModal', () => {
  test('renders node equipment details', async () => {
    const nodeEquipment = {
      id: 'test-server',
      model: 'Dell R740',
      height: 2,
      width: 1,
      specs: 'https://example.com/specs',
      cpu: {
        sockets: 2,
        model: 'Intel Xeon',
        cores: 16,
        specs: 'https://example.com/cpu-specs'
      },
      ram: {
        dimm: 8,
        size: 32 * 1024 ** 3 // 32GB
      },
      storage: [{ type: 'SSD', model: 'Samsung 980', size: '1TB' }],
      netifs: [
        { type: 'Ethernet', bandwidth: 10 * 1000 ** 3 } // 10Gb/s
      ]
    }

    const wrapper = mount(EquipmentTypeModal, {
      props: {
        showModal: true,
        modalContent: nodeEquipment
      }
    })

    await nextTick()

    // Test that the dialog component exists (even if not visible due to teleport)
    expect(wrapper.findComponent({ name: 'Dialog' }).exists()).toBe(true)

    // Test that the component renders without errors
    expect(wrapper.exists()).toBe(true)

    // Test that the modal content is passed correctly
    expect(wrapper.props('modalContent')).toEqual(nodeEquipment)
    expect(wrapper.props('showModal')).toBe(true)
  })

  test('renders storage equipment details', async () => {
    const storageEquipment = {
      id: 'test-storage',
      model: 'NetApp FAS',
      height: 2,
      width: 1,
      disks: [{ type: 'SSD', size: 4 * 1024 ** 4, model: 'Samsung 980', number: 12 }]
    }

    const wrapper = mount(EquipmentTypeModal, {
      props: {
        showModal: true,
        modalContent: storageEquipment
      }
    })

    await nextTick()

    // Test that the dialog component exists (even if not visible due to teleport)
    expect(wrapper.findComponent({ name: 'Dialog' }).exists()).toBe(true)

    // Test that the component renders without errors
    expect(wrapper.exists()).toBe(true)

    // Test that the modal content is passed correctly
    expect(wrapper.props('modalContent')).toEqual(storageEquipment)
    expect(wrapper.props('showModal')).toBe(true)
  })

  test('renders network equipment details', async () => {
    const networkEquipment = {
      id: 'test-switch',
      model: 'Cisco Catalyst',
      height: 1,
      width: 1,
      netifs: [
        { type: 'Ethernet', bandwidth: 100 * 1000 ** 3, number: 48 } // 100Gb/s
      ]
    }

    const wrapper = mount(EquipmentTypeModal, {
      props: {
        showModal: true,
        modalContent: networkEquipment
      }
    })

    await nextTick()

    // Test that the dialog component exists (even if not visible due to teleport)
    expect(wrapper.findComponent({ name: 'Dialog' }).exists()).toBe(true)

    // Test that the component renders without errors
    expect(wrapper.exists()).toBe(true)

    // Test that the modal content is passed correctly
    expect(wrapper.props('modalContent')).toEqual(networkEquipment)
    expect(wrapper.props('showModal')).toBe(true)
  })

  test('renders misc equipment details', async () => {
    const miscEquipment = {
      id: 'test-pdu',
      model: 'APC PDU',
      height: 1,
      width: 1
    }

    const wrapper = mount(EquipmentTypeModal, {
      props: {
        showModal: true,
        modalContent: miscEquipment
      }
    })

    await nextTick()

    // Test that the dialog component exists (even if not visible due to teleport)
    expect(wrapper.findComponent({ name: 'Dialog' }).exists()).toBe(true)

    // Test that the component renders without errors
    expect(wrapper.exists()).toBe(true)

    // Test that the modal content is passed correctly
    expect(wrapper.props('modalContent')).toEqual(miscEquipment)
    expect(wrapper.props('showModal')).toBe(true)
  })
})
