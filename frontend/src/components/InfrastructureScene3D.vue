<!--Copyright (c) 2026 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT -->

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import {
  ArrowPathIcon,
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon,
  HomeIcon
} from '@heroicons/vue/24/outline'
import { useHttp } from '@/plugins/http'
import { useRacksDBAPI } from '@/composables/RacksDBAPI'
import type { CameraMode, HoveredEquipment, InfrastructureViewer } from '@/lib/scene3d'

const props = defineProps({
  infrastructureName: {
    type: String,
    required: true
  }
})

const racksDBAPI = useRacksDBAPI(useHttp())

const wrapper = ref<HTMLElement | null>(null)
const container = ref<HTMLElement | null>(null)
const loading = ref(true)
const error = ref(false)
const hovered = ref<HoveredEquipment | null>(null)
const fullscreen = ref(false)
const cameraMode = ref<CameraMode>('free')

let viewer: InfrastructureViewer | null = null
let unmounted = false

function onFullscreenChange() {
  fullscreen.value = document.fullscreenElement === wrapper.value
}

function toggleTurntable() {
  viewer?.setMode(cameraMode.value === 'turntable' ? 'free' : 'turntable')
}

function toggleFullscreen() {
  if (document.fullscreenElement) {
    document.exitFullscreen()
  } else {
    wrapper.value?.requestFullscreen()
  }
}

onMounted(async () => {
  document.addEventListener('fullscreenchange', onFullscreenChange)
  try {
    const data = await racksDBAPI.infrastructureGlb(props.infrastructureName)
    // Load three.js and the viewer dynamically, only when 3D view is displayed.
    const { createViewer } = await import('@/lib/scene3d')
    if (unmounted || !container.value) return
    viewer = await createViewer(
      container.value,
      data,
      (equipment) => {
        hovered.value = equipment
      },
      (mode) => {
        cameraMode.value = mode
      }
    )
    // Component may have been unmounted while the scene was loading.
    if (unmounted) {
      viewer.dispose()
      viewer = null
    }
  } catch (err) {
    console.error(`Unable to display 3D representation of ${props.infrastructureName}`, err)
    error.value = true
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  unmounted = true
  document.removeEventListener('fullscreenchange', onFullscreenChange)
  viewer?.dispose()
  viewer = null
})
</script>

<template>
  <div
    ref="wrapper"
    class="relative mx-auto w-full max-w-6xl overflow-hidden rounded-lg border border-gray-200 bg-gray-100 dark:border-gray-700 dark:bg-gray-800"
    :class="fullscreen ? 'h-screen max-w-none rounded-none' : 'h-[32rem]'"
  >
    <div
      ref="container"
      class="h-full w-full"
      role="img"
      :aria-label="`3D representation of infrastructure ${infrastructureName}`"
    />

    <p
      v-if="loading"
      class="absolute inset-0 flex items-center justify-center text-sm text-gray-600 dark:text-gray-300"
    >
      Loading 3D representation…
    </p>
    <p
      v-else-if="error"
      class="absolute inset-0 flex items-center justify-center text-sm text-red-600"
    >
      Unable to load 3D representation of infrastructure {{ infrastructureName }}
    </p>

    <div v-if="!loading && !error" class="absolute right-2 top-2 flex gap-2">
      <button
        type="button"
        title="Orbit around racks"
        :aria-pressed="cameraMode === 'turntable'"
        class="rounded-lg border p-1.5 shadow-sm"
        :class="
          cameraMode === 'turntable'
            ? 'border-purple-700 bg-purple-700 text-white hover:bg-purple-800'
            : 'border-gray-300 bg-white/90 text-gray-700 hover:bg-white dark:border-gray-600 dark:bg-gray-800/90 dark:text-gray-200'
        "
        @click="toggleTurntable"
      >
        <ArrowPathIcon class="h-5 w-5" />
        <span class="sr-only">Orbit around racks</span>
      </button>
      <button
        type="button"
        title="Reset view"
        class="rounded-lg border border-gray-300 bg-white/90 p-1.5 text-gray-700 shadow-sm hover:bg-white dark:border-gray-600 dark:bg-gray-800/90 dark:text-gray-200"
        @click="viewer?.resetCamera()"
      >
        <HomeIcon class="h-5 w-5" />
        <span class="sr-only">Reset view</span>
      </button>
      <button
        type="button"
        :title="fullscreen ? 'Exit fullscreen' : 'Fullscreen'"
        class="rounded-lg border border-gray-300 bg-white/90 p-1.5 text-gray-700 shadow-sm hover:bg-white dark:border-gray-600 dark:bg-gray-800/90 dark:text-gray-200"
        @click="toggleFullscreen"
      >
        <ArrowsPointingInIcon v-if="fullscreen" class="h-5 w-5" />
        <ArrowsPointingOutIcon v-else class="h-5 w-5" />
        <span class="sr-only">{{ fullscreen ? 'Exit fullscreen' : 'Fullscreen' }}</span>
      </button>
    </div>

    <div
      v-if="hovered"
      class="pointer-events-none absolute bottom-2 left-2 rounded-md border border-gray-200 bg-white/90 px-3 py-1.5 text-sm text-gray-800 shadow-sm dark:border-gray-600 dark:bg-gray-800/90 dark:text-gray-100"
    >
      <span class="font-semibold">{{ hovered.name }}</span>
      <span class="text-gray-500 dark:text-gray-400">
        · {{ hovered.category }} {{ hovered.type }} · rack {{ hovered.rack }}</span
      >
    </div>
  </div>
</template>
