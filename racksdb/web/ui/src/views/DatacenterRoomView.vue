<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { useRacksDBAPI } from '@/composables/RacksDBAPI'
import { useRacksDBIMGAPI } from '@/composables/RacksDBIMG'
import { ref, onMounted } from 'vue'
import SearchBar from '@/components/SearchBar.vue'
import type { Ref } from 'vue'
import type { Datacenter, Infrastructure, Rack } from '@/composables/RacksDBAPI'

const http = useHttp()
const racksDBAPI = useRacksDBAPI(http)
const racksDBIMG = useRacksDBIMGAPI(http)
const datacenters: Ref<Array<Datacenter>> = ref([])
const infrastructures: Ref<Array<Infrastructure>> = ref([])
const datacenterDetails: Ref<Datacenter | undefined> = ref()
const racks: Ref<Array<Rack>> = ref([])
const rackDetails: Ref<Array<Rack>> = ref([])
const blobURL = ref()

async function getInfrastructureImg() {
  try {
    const myBlob = await racksDBIMG.roomImageSvg(props.datacenterRoom)
    blobURL.value = URL.createObjectURL(myBlob)
  } catch (error) {
    console.error(`Error getting ${props.datacenterRoom}: ` + error)
  }
}

// this function checks if a rack is part of an infrastructure and if it's the case it returns the infrastructure name(s)
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
  <SearchBar
    v-if="datacenters.length"
    viewTitle="Datacenter Room"
    searchedItem="datacenter"
    :items="datacenters"
  />

  <h2 class="flex justify-center py-10 capitalize text-3xl">{{ datacenterRoom }} room</h2>

  <img v-if="blobURL" :src="blobURL" class="" alt="" />

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
