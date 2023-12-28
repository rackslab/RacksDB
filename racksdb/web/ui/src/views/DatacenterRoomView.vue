<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { useRacksDBAPI } from '@/composables/RacksDBAPI'
import { ref, onMounted, computed } from 'vue'
import type { Ref } from 'vue'
import BreadCrumbs from '@/components/BreadCrumbs.vue'
import type { Infrastructure, Rack } from '@/composables/RacksDBAPI'
import { Switch, SwitchGroup, SwitchLabel } from '@headlessui/vue'

const http = useHttp()
const racksDBAPI = useRacksDBAPI(http)
let infrastructures: Array<Infrastructure> = []
const rackDetails: Ref<Array<Rack>> = ref([])
const blobURL = ref()
const showImg = ref(false)
const input = ref('')
const hideEmpty = ref(false)
var filteredRacks = computed(() => {
  let result: Array<Rack> = rackDetails.value

  result = result.filter((room) => room.room === props.datacenterRoom)

  if (hideEmpty.value) {
    result = result.filter((rack) => rack.fillrate > 0)
  }

  if (input.value !== '') {
    result = result.filter((rack) => rack.name.toLowerCase().includes(input.value.toLowerCase()))
  }

  return result
})

function toggleImageModal() {
  if (showImg.value) {
    showImg.value = false
  } else {
    showImg.value = true
  }
}

async function getInfrastructureImg() {
  try {
    blobURL.value = URL.createObjectURL(await racksDBAPI.roomImageSvg(props.datacenterRoom))
  } catch (error) {
    console.error(`Error getting ${props.datacenterRoom}: ` + error)
  }
}

async function getDatacenters() {
  // Get datacenters and filter using the prop datacenterName
  let datacenterDetails = (await racksDBAPI.datacenters()).filter(
    (datacenter) => datacenter.name === props.datacenterName
  )[0]

  // Loop on datacenterDetails to get all the rack it contains
  datacenterDetails.rooms.forEach((room) => {
    room.rows.forEach((row) => {
      row.racks.forEach((rack) => {
        rackDetails.value.push({
          name: rack.name,
          fillrate: rack.fillrate,
          room: room.name
        })
      })
    })
  })
}

async function getInfrastructures() {
  infrastructures = await racksDBAPI.infrastructures()
}

onMounted(() => {
  getDatacenters()
  getInfrastructures()
  getInfrastructureImg()
})

const props = defineProps({
  datacenterName: String,
  datacenterRoom: {
    type: String,
    required: true
  }
})
</script>

<template>
  <BreadCrumbs :datacenterName="props.datacenterName" :datacenterRoom="props.datacenterRoom" />

  <div class="flex justify-end items-center p-4 px-20">
    <input
      type="text"
      v-model="input"
      class="w-96 rounded-md focus:border-purple-700 focus:outline-none border-2 border-solid bg-white py-1.5 pl-3 pr-10 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 sm:text-sm sm:leading-6"
      placeholder="Filter rack by name"
      required
    />
  </div>

  <div class="pb-10">
    <img
      v-if="blobURL"
      @click="toggleImageModal()"
      :src="blobURL"
      class="h-96 max-w-500 mx-auto p-10 border-2 border-black transition-transform transform duration-150 hover:scale-105 hover:border-violet-700 cursor-pointer"
      alt=""
    />
  </div>

  <div
    v-if="showImg"
    class="fixed top-0 left-0 flex flex-col items-center justify-center w-screen h-screen bg-gray-300 bg-opacity-50 dark:bg-gray-900 dark:bg-opacity-50 backdrop-blur-md z-50"
  >
    <div
      class="max-w-4xl bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700"
    >
      <img v-if="blobURL" :src="blobURL" class="w-full" alt="" />

      <div class="pt-5 flex justify-center">
        <button
          type="button"
          @click="toggleImageModal()"
          class="py-2.5 px-5 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-purple-700 focus:z-10 focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700"
        >
          close
        </button>
      </div>
    </div>
  </div>

  <div class="flex justify-center pt-5">
    <SwitchGroup>
      <div class="pt-5">
        <SwitchLabel class="mx-4">Hide empty racks</SwitchLabel>
        <Switch
          v-model="hideEmpty"
          :class="hideEmpty ? 'bg-purple-900' : 'bg-purple-700'"
          class="relative inline-flex h-[28px] w-[64px] shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus-visible:ring-2 focus-visible:ring-white/75"
        >
          <span
            aria-hidden="true"
            :class="hideEmpty ? 'translate-x-9' : 'translate-x-0'"
            class="pointer-events-none inline-block h-[24px] w-[24px] transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out"
          />
        </Switch>
      </div>
    </SwitchGroup>
  </div>

  <div class="flex justify-center pb-10">
    <table class="min-w-[75vw] text-base text-center text-gray-500 dark:text-gray-400 table-fixed">
      <thead
        class="text-lg text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400 h-24"
      >
        <tr>
          <th scope="col" class="w-24">Name</th>
          <th scope="col" class="w-24">Fill rate</th>
          <th scope="col" class="w-24">List of infrastructures</th>
        </tr>
      </thead>

      <template v-if="filteredRacks.length > 0">
        <tbody>
          <tr
            v-for="rack in filteredRacks"
            :key="rack.name"
            class="h-24 my-4 border-gray-200 border-b-2"
          >
            <td>{{ rack.name }}</td>
            <td>{{ (rack.fillrate * 100).toFixed(0) }}%</td>
            <td>-</td>
          </tr>
        </tbody>
      </template>
      <template v-else>
        <tbody class="h-24 my-4 border-gray-200 border-b-2">
          <tr>
            <td colspan="3">No data available</td>
          </tr>
        </tbody>
      </template>
    </table>
  </div>
</template>
