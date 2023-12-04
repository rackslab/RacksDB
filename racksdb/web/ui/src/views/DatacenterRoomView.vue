<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { useHttp } from '@/plugins/http'
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

/*
function toggleImageModal() {
  showFullImg.value = !showFullImg.value
}
*/

// this function checks in which infrastructures the rack is present and returns the infrastructure name(s)
function listInfrastructures() {
  const rack = rackDetails.value
  const infrastructure = infrastructures.value
  const infrastructureNames = []

  for (let index = 0; index < rack.length; index++) {
    const rackName = rack[index].name

    for (let x = 0; x < infrastructure.length; x++) {
      for (let y = 0; y < infrastructure[x].layout.length; y++) {
        const infrastructuresRacks = infrastructure[x].layout[y].rack

        if (infrastructuresRacks == rackName) {
          infrastructureNames.push(infrastructure[x].name)
          return infrastructureNames
        }
      }
    }
  }
}

async function getInfrastructures() {
  try {
    const resp = await http.get('infrastructures')
    infrastructures.value = resp.data as Infrastructure[]
  } catch (error) {
    console.error('Error during infrastructures data recovery', error)
  }
}

async function getRacks() {
  try {
    const resp = await http.get('racks')
    racks.value = resp.data as Rack[]
    rackDetails.value = racks.value.filter((rack) => rack.room === props.datacenterRoom)
  } catch (error) {
    console.error('Error during racks data recovery', error)
  }
}

async function getDatacenters() {
  try {
    const resp = await http.get('datacenters')
    datacenters.value = resp.data as Datacenter[]
    datacenterDetails.value = datacenters.value.filter(
      (datacenter) => datacenter.name === props.datacenterName
    )[0]
  } catch (error) {
    console.error('Error during datacenters data recovery', error)
  }
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
                <td class="capitalize">{{ listInfrastructures()?.join(' , ') }}</td>
              </tr>
            </tbody>
          </template>
        </template>
      </template>
    </table>
  </div>
</template>
