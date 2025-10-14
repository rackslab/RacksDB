/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT
*/

import { describe, test, expect } from 'vitest'
import { mount } from '@vue/test-utils'

import HomeView from '@/views/HomeView.vue'

describe('HomeView', () => {
  test('renders Overview title and stubs children', () => {
    const wrapper = mount(HomeView, {
      global: {
        stubs: {
          BreadCrumbs: true,
          HomeViewCards: true
        }
      }
    })

    expect(wrapper.text()).toContain('Overview')
  })
})
