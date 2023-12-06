<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { useRacksDBAPI } from '@/composables/RacksDBAPI'
import { ref, onMounted, inject } from 'vue'
import SearchBar from '@/components/SearchBar.vue'
// import { injectionKey } from '@/plugins/runtimeConfiguration'
import type { Ref } from 'vue'
import type { Datacenter, Infrastructure, Rack } from '@/composables/RacksDBAPI'

const datacenters: Ref<Array<Datacenter>> = ref([])
const infrastructures: Ref<Array<Infrastructure>> = ref([])
const datacenterDetails: Ref<Datacenter | undefined> = ref()
const racks: Ref<Array<Rack>> = ref([])
const rackDetails: Ref<Array<Rack>> = ref([])
//const showFullImg = ref(false)
const http = useHttp()
const racksDBAPI = useRacksDBAPI(http)

/*
function toggleImageModal() {
  showFullImg.value = !showFullImg.value
}
*/

// this function checks in which infrastructures the rack is present and returns the infrastructure name(s)
function listInfrastructures(rackName: string) {
  const infrastructureNames: Array<String> = []

  infrastructures.value.forEach((infrastructure) => {
    infrastructure.layout.forEach((layout) => {
      if (rackName == layout.rack) {
        infrastructureNames.push(infrastructure.name)
      }
    })
  })
  return infrastructureNames
}

async function getDatacenters() {
  datacenters.value = await racksDBAPI.datacenters()
  datacenterDetails.value = datacenters.value.filter(
      (datacenter) => datacenter.name === props.datacenterName
    )[0]
}

async function getInfrastructures() {
  infrastructures.value = await racksDBAPI.infrastructures()
}

async function getRacks() {
  racks.value = await racksDBAPI.racks()
  rackDetails.value = racks.value.filter((rack) => rack.room === props.datacenterRoom)
}

onMounted(() => {
  getDatacenters()
  getInfrastructures()
  getRacks()
})

const props = defineProps({
  datacenterName: String,
  datacenterRoom: String
})
</script>

<template>
  <SearchBar
    v-if="datacenters.length"
    viewTitle="Datacenter Room"
    searchedItem="datacenter"
    :items="datacenters"
  />

  <h2 class="flex justify-center py-10 capitalize text-3xl">{{ datacenterRoom }} room</h2>

  <!--
  <img
    :src="`${inject(injectionKey)!.api_server}/draw/room/${props.datacenterRoom}.svg`"
    alt=""
    @click="toggleImageModal()"
    class="h-96 max-w-500 mx-auto p-10"
  />

  <div
    v-show="showFullImg"
    class="fixed top-0 left-0 flex flex-col items-center justify-center w-screen h-screen bg-gray-300 bg-opacity-50 dark:bg-gray-900 dark:bg-opacity-50 backdrop-blur-md z-50"
  >
    <img
      :src="`${inject(injectionKey)!.api_server}/draw/room/${props.datacenterRoom}.svg`"
      alt=""
      @click="toggleImageModal()"
      class="h-screen max-w-full bg-white"
    />
  </div>
  -->

  <div class="flex justify-center">
    <table
      v-if="datacenterDetails"
      class="w-screen text-base text-center text-gray-500 dark:text-gray-400"
    >
      <thead class="text-lg text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
        <tr>
          <th scope="col" class="px-6 py-3">Name</th>
          <th scope="col" class="px-6 py-3">Fill rate</th>
          <th scope="col" class="px-6 py-3">List of infrastructures</th>
        </tr>
      </thead>

      <template v-for="room in datacenterDetails.rooms" :key="room">
        <template v-for="row in room.rows" :key="row">
          <template v-for="rack in row.racks" :key="rack">
            <tbody>
              <tr>
                <td>{{ rack.name }}</td>
                <td>{{ (rack.fillrate * 100).toFixed(0) }}%</td>
                <td class="capitalize">{{ listInfrastructures(rack.name).join(' , ') }}</td>
              </tr>
            </tbody>
          </template>
        </template>
      </template>
    </table>
  </div>
</template>
