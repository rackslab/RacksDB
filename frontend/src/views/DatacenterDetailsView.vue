<!--Copyright (c) 2022-2024 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { useRacksDBAPI } from '@/composables/RacksDBAPI'
import { ref, onMounted, watch, computed } from 'vue'
import type { Ref } from 'vue'
import type { Datacenter, DatacenterRoom } from '@/composables/RacksDBAPI'
import BreadCrumbs from '@/components/BreadCrumbs.vue'
import { BarsArrowDownIcon, BarsArrowUpIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'
import { useRouter } from 'vue-router'

const router = useRouter()
const http = useHttp()
const racksDBAPI = useRacksDBAPI(http)
const datacenterDetails: Ref<Datacenter | undefined> = ref()
const alphabeticalOrder = ref(true)
const input = ref('')
const filteredRooms = computed(() =>
  input.value === ''
    ? datacenterDetails.value?.rooms
    : datacenterDetails.value?.rooms.filter((item) => {
        return item.name.toLocaleLowerCase().includes(input.value.toLocaleLowerCase())
      })
)

function goToRoom(room: string) {
  router.push({
    name: 'datacenterroom',
    params: { datacenterName: props.name, datacenterRoom: room }
  })
}

function invertRoomSort() {
  if (datacenterDetails.value) {
    datacenterDetails.value.rooms.reverse()
  }
  alphabeticalOrder.value = !alphabeticalOrder.value
}

// Get the room and return the sum of all the racks in the array with .reduce()
function roomNbRacks(room: DatacenterRoom) {
  return room.rows.reduce((result, row) => result + row.nbracks, 0)
}

async function getDatacenters() {
  datacenterDetails.value = (await racksDBAPI.datacenters()).filter(
    (datacenter) => datacenter.name === props.name
  )[0]
}

onMounted(() => {
  getDatacenters()
})

const props = defineProps({
  name: String
})
</script>

<template>
  <BreadCrumbs :datacenterName="props.name" />

  <div class="flex justify-end items-center p-4 px-20">
    <input
      type="text"
      v-model="input"
      class="w-96 rounded-md focus:border-purple-700 focus:outline-none border-2 border-solid bg-white py-1.5 pl-3 pr-10 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 sm:text-sm sm:leading-6"
      :placeholder="`Filter room by name`"
      required
    />
  </div>

  <div v-if="filteredRooms" class="flex justify-center my-auto mx-auto">
    <div class="relative overflow-x-auto py-20">
      <div @click="invertRoomSort()" class="flex">
        <div v-if="alphabeticalOrder">
          <BarsArrowDownIcon class="h-7 w-7" />
        </div>
        <div v-else>
          <BarsArrowUpIcon class="h-7 w-7" />
        </div>
        <p>Sort rooms</p>
      </div>

      <table
        class="min-w-[60vw] max-w-[60vw] text-base text-center text-gray-500 dark:text-gray-400 table-fixed"
      >
        <thead
          class="text-lg text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400 h-24"
        >
          <tr>
            <th scope="col" class="w-96">Name</th>
            <th scope="col" class="w-96">Area (m²)</th>
            <th scope="col" class="w-96">Number of racks</th>
            <th class="w-0.5"></th>
          </tr>
        </thead>

        <template v-if="filteredRooms.length > 0">
          <tbody class="cursor-pointer h-24">
            <tr
              v-for="room in filteredRooms"
              :key="room.name"
              @click="goToRoom(room.name)"
              class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 text-black hover:bg-purple-50"
            >
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
              <td class="align-middle">
                <ChevronRightIcon class="h-7 w-7" />
              </td>
            </tr>
          </tbody>
        </template>
        <template v-else>
          <tbody class="h-24 border-gray-200 border-b-2">
            <tr>
              <td colspan="3" class="px-6 py-4">No data available</td>
              <td class="h-7 w-7"></td>
            </tr>
          </tbody>
        </template>
      </table>
    </div>
  </div>
</template>
