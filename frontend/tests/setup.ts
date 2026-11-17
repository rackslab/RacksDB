/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT
*/

import { vi } from 'vitest'
import { createRouterMock, injectRouterMock } from 'vue-router-mock'
import { RouterLinkStub } from '@vue/test-utils'

// Mock object URLs functions, which may be missing or not mockable in JSDOM,
// to prevent console errors and spy on calls in tests.
URL.createObjectURL = vi.fn(() => 'blob:mock-url')
URL.revokeObjectURL = vi.fn()

// Mock ResizeObserver for Headless UI components. Vitest mocks must be
// implemented with class to be called with new keyword.
global.ResizeObserver = vi.fn().mockImplementation(
  class {
    observe = vi.fn()
    unobserve = vi.fn()
    disconnect = vi.fn()
  }
)

// Create router mock with Vitest spy
const router = createRouterMock({
  spy: {
    create: vi.fn,
    reset: vi.clearAllMocks
  },
  // Add any default routes here
  routes: [
    { path: '/', name: 'home' },
    { path: '/datacenters', name: 'datacenters' },
    { path: '/datacenters/:name', name: 'datacenterdetails' },
    { path: '/datacenters/:datacenterName/:datacenterRoom', name: 'datacenterroom' },
    { path: '/infrastructures', name: 'infrastructures' },
    { path: '/infrastructures/:name', name: 'infrastructuredetails' }
  ]
})

// Inject router mock globally
injectRouterMock(router)

// Make router available globally for tests
global.routerMock = router

// Configure global stubs for Vue Test Utils
import { config } from '@vue/test-utils'

config.global.stubs = {
  RouterLink: RouterLinkStub
}
