<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { useRacksDBAPI } from '@/composables/RacksDBAPI'
import { ref, onMounted, watch } from 'vue'
import SearchBar from '@/components/SearchBar.vue'
import type { Ref } from 'vue'
import type { Datacenter, DatacenterRoom } from '@/composables/RacksDBAPI'

const http = useHttp()
const racksDBAPI = useRacksDBAPI(http)
const datacenters: Ref<Array<Datacenter>> = ref([])
const datacenterDetails: Ref<Datacenter | undefined> = ref()

// Get the room and sum all the racks in the array with .reduce()
function roomNbRacks(room: DatacenterRoom) {
  return room.rows.reduce((result, row) => result + row.nbracks, 0)
}

async function getDatacenters() {
  datacenters.value = await racksDBAPI.datacenters()
  datacenterDetails.value = datacenters.value.filter(
      (datacenter) => datacenter.name === props.name
    )[0]
}

onMounted(() => {
  getDatacenters()
})

// Using watch to trigger getDatacenter() when the value of props.name change
watch(
  () => props.name,
  () => {
    getDatacenters()
  }
)

const props = defineProps({
  name: String
})
</script>

<template>
  <SearchBar
    v-if="datacenters.length"
    viewTitle="Datacenter Details"
    searchedItem="datacenter"
    :items="datacenters"
  />

  <div v-if="datacenterDetails">
    <div class="relative overflow-x-auto py-20">
      <h2 class="text-3xl font-medium flex justify-center capitalize py-16">
        {{ name }} Datacenter
      </h2>
      <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
        <thead
          class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400"
        >
          <tr>
            <th scope="col" class="px-6 py-3">Name</th>
            <th scope="col" class="px-6 py-3">Area (m²)</th>
            <th scope="col" class="px-6 py-3">Number of racks</th>
            <th scope="col">Access to the room</th>
          </tr>
        </thead>

        <tbody v-for="room in datacenterDetails.rooms" :key="room.name">
          <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 text-black">
            <th
              scope="row"
              class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white"
            >
              <span>{{ room.name }} </span>
            </th>
            <td class="px-6 py-4">
              <span class="text-black"
                >{{ (room.dimensions.width * room.dimensions.depth) / 10 ** 6 }}m²</span
              ><br />
              <div class="italic text-gray-500 text-xs">
                width: {{ room.dimensions.width / 10 ** 3 }}m<br />
                depth: {{ room.dimensions.depth / 10 ** 3 }}m
              </div>
            </td>
            <td class="px-6 py-4">
              {{ roomNbRacks(room) }}
            </td>
            <td>
              <router-link
                :to="{
                  name: 'datacenterroom',
                  params: { datacenterName: props.name, datacenterRoom: room.name }
                }"
              >
                <button
                  class="py-2.5 px-5 mr-2 mb-2 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700"
                >
                  Access to the room
                </button>
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div v-else>
    <p>No data availaible for this datacenter</p>
  </div>
</template>
