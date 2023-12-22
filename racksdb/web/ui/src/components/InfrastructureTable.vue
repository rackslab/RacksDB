<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import type { Ref, PropType } from 'vue'
import type {
  Infrastructure,
  NodeEquipment,
  NetworkEquipment,
  StorageEquipment
} from '@/composables/RacksDBAPI'
import { ref } from 'vue'

const rack = ref()
const showRack = ref(false)
const showInfrastructureRacks = ref(true)
var showPopUp = ref(false)
var popUpContent: Ref<NodeEquipment | NetworkEquipment | StorageEquipment | undefined> = ref()
type equipmentType = 'nodes' | 'storage' | 'network'

// This function changes the display and filter the infrastructure to only get the data from a rack
function rackDetails(rackName: string) {
  showRack.value = true
  showInfrastructureRacks.value = false
  var layout = props.infrastructureDetails.layout

  for (let index = 0; index < layout!.length; index++) {
    rack.value = layout!.filter((rack) => rack.rack === rackName)
  }
}

function allInfrastructurDetails() {
  showRack.value = false
  showInfrastructureRacks.value = true
}

function popUp(name: string, equipment: equipmentType) {
  if (showPopUp.value) {
    showPopUp.value = !showPopUp.value
  } else {
    var layout = props.infrastructureDetails.layout

    for (let x = 0; x < layout.length; x++) {
      var result = layout[x][equipment].find((item) => item.name == name)
      if (result) {
        popUpContent.value = result
        break
      }
    }
    showPopUp.value = true
  }
}

function closePopUp() {
  showPopUp.value = !showPopUp.value
}

const props = defineProps({
  infrastructureDetails: {
    type: Object as PropType<Infrastructure>,
    required: true
  },
  infrastructure: {
    type: Array<Infrastructure>,
    default() {
      return []
    }
  }
})
</script>

<template>
  <div
    class="flex justify-center pb-10"
    v-for="infrastructure in props.infrastructure"
    :key="infrastructure.name"
  >
    <div v-if="infrastructure.name == props.infrastructureDetails.name" class="flex">
      <div class="pt-10 px-5">
        <button
          type="button"
          @click="allInfrastructurDetails()"
          class="py-2.5 px-5 mr-2 mb-2 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700"
        >
          All
        </button>
      </div>
      <div v-for="rack in props.infrastructureDetails.layout" :key="rack.rack" class="pt-10 px-5">
        <button
          type="button"
          @click="rackDetails(rack.rack)"
          class="py-2.5 px-5 mr-2 mb-2 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700"
        >
          {{ rack.rack }}
        </button>
      </div>
    </div>
  </div>

  <div v-show="showInfrastructureRacks">
    <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
      <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
        <tr>
          <th scope="col" class="px-6 py-3">Name</th>
          <th scope="col" class="px-6 py-3">Equipment</th>
          <th scope="col" class="px-6 py-3">ID</th>
        </tr>
      </thead>

      <template v-for="layout in infrastructureDetails?.layout" :key="layout.rack">
        <tr v-for="node in layout.nodes" :key="node.name">
          <td
            scope="row"
            class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white capitalize"
          >
            {{ node.name }} <span class="text-xs font-thin italic lowercase">, node</span>
          </td>
          <td class="px-6 py-4">{{ node.rack }}</td>
          <td @click="popUp(node.name, 'nodes')" class="px-6 py-4 capitalize cursor-pointer">
            {{ node.type.id }}
          </td>
        </tr>

        <tr v-for="storage in layout.storage" :key="storage.name">
          <td
            scope="row"
            class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white capitalize"
          >
            {{ storage.name }} <span class="text-xs font-thin italic lowercase">, storage</span>
          </td>
          <td class="px-6 py-4">{{ storage.rack }}</td>
          <td @click="popUp(storage.name, 'storage')" class="px-6 py-4 capitalize cursor-pointer">
            {{ storage.type.id }}
          </td>
        </tr>

        <tr v-for="network in layout.network" :key="network.name">
          <td
            scope="row"
            class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white capitalize"
          >
            {{ network.name }} <span class="text-xs font-thin italic lowercase">, network</span>
          </td>
          <td class="px-6 py-4">{{ network.rack }}</td>
          <td @click="popUp(network.name, 'network')" class="px-6 py-4 capitalize cursor-pointer">
            {{ network.type.id }}
          </td>
        </tr>
      </template>
    </table>
  </div>

  <div v-show="showRack">
    <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
      <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
        <tr>
          <th scope="col" class="px-6 py-3">Name</th>
          <th scope="col" class="px-6 py-3">Equipment</th>
          <th scope="col" class="px-6 py-3">ID</th>
        </tr>
      </thead>

      <template v-for="layout in rack" :key="layout.rack">
        <tr v-for="node in layout.nodes" :key="node.name">
          <td
            scope="row"
            class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white capitalize"
          >
            {{ node.name }} <span class="text-xs font-thin italic lowercase">, node</span>
          </td>
          <td class="px-6 py-4">{{ node.rack }}</td>
          <td @click="popUp(node.name, 'nodes')" class="px-6 py-4 capitalize cursor-pointer">
            {{ node.type.id }}
          </td>
        </tr>

        <tr v-for="storage in layout.storage" :key="storage.name">
          <td
            scope="row"
            class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white capitalize"
          >
            {{ storage.name }}<span class="text-xs font-thin italic lowercase">, storage</span>
          </td>
          <td class="px-6 py-4">{{ storage.rack }}</td>
          <td @click="popUp(storage.name, 'storage')" class="px-6 py-4 capitalize cursor-pointer">
            {{ storage.type.id }}
          </td>
        </tr>

        <tr v-for="network in layout.network" :key="network.name">
          <td
            scope="row"
            class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white capitalize"
          >
            {{ network.name }} <span class="text-xs font-thin italic lowercase">, network</span>
          </td>
          <td class="px-6 py-4">{{ network.rack }}</td>
          <td @click="popUp(network.name, 'network')" class="px-6 py-4 capitalize cursor-pointer">
            {{ network.type.id }}
          </td>
        </tr>
      </template>
    </table>
  </div>

  <div
    v-if="showPopUp && popUpContent"
    class="fixed top-0 left-0 flex flex-col items-center justify-center w-screen h-screen bg-gray-300 bg-opacity-50 dark:bg-gray-900 dark:bg-opacity-50 backdrop-blur-md z-50"
  >
    <div
      class="max-w-4xl bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700"
    >
      <div v-if="'cpu' in popUpContent['type']">
        <p class="font-semibold flex justify-center text-purple-700 text-xl capitalize py-5">
          {{ popUpContent.type.id }}
        </p>

        <div class="pt-5">
          <p class="pl-5">
            Model: <span class="italic text-sm">{{ popUpContent.type.model }}</span>
          </p>
          <p class="pl-5">
            Height: <span class="italic text-sm">{{ popUpContent.type.height }}</span>
          </p>
          <p class="pl-5">
            Width: <span class="italic text-sm">{{ popUpContent.type.width }}</span>
          </p>
          <p class="pl-5">
            Specs:
            <span class="italic text-sm"
              ><a :href="popUpContent.type.specs" target="_blank">{{
                popUpContent.type.specs
              }}</a></span
            >
          </p>
        </div>

        <div class="pt-5">
          <p class="font-medium">CPU:</p>
          <p class="pl-5">
            Sockets: <span class="italic text-sm">{{ popUpContent.type.cpu.sockets }}</span>
          </p>
          <p class="pl-5">
            Model: <span class="italic text-sm">{{ popUpContent.type.cpu.model }}</span>
          </p>
          <p class="pl-5">
            Specs:
            <span class="italic text-sm"
              ><a :href="popUpContent.type.specs" target="_blank">{{
                popUpContent.type.cpu.specs
              }}</a></span
            >
          </p>
          <p class="pl-5">
            Cores: <span class="italic text-sm">{{ popUpContent.type.cpu.cores }}</span>
          </p>
        </div>

        <div class="pt-5">
          <p class="font-medium">RAM:</p>
          <p class="pl-5">
            Dimm: <span class="italic text-sm">{{ popUpContent.type.ram.dimm }}</span>
          </p>
          <p class="pl-5">
            Size:
            <span class="italic text-sm">{{ popUpContent.type.ram.size / 1024 ** 3 }}GB</span>
          </p>
        </div>

        <div class="pt-5">
          <p class="font-medium">Storage:</p>
          <div v-for="storage in popUpContent.type.storage" :key="storage.model">
            <p class="pl-5">
              Type: <span class="italic text-sm">{{ storage.type }}</span>
            </p>
            <p class="pl-5">
              Model: <span class="italic text-sm">{{ storage.model }}</span>
            </p>
            <p class="pl-5">
              Size: <span class="italic text-sm">{{ storage.size }}</span>
            </p>
          </div>
        </div>

        <div class="pt-5">
          <p class="font-medium">Netifs:</p>
          <div v-for="netif in popUpContent.type.netifs" :key="netif.type">
            <p class="pl-5">
              Type: <span class="italic text-sm">{{ netif.type }}</span>
            </p>
            <p class="pl-5">
              Bandwith:
              <span class="italic text-sm">{{ (netif.bandwidth * 8) / 1000 ** 3 }}Gb/s</span>
            </p>
          </div>
        </div>
      </div>

      <div v-else-if="'disks' in popUpContent['type']">
        <p class="font-semibold flex justify-center text-purple-700 text-xl capitalize py-5">
          {{ popUpContent.type.id }}
        </p>

        <div class="pt-5">
          <p class="pl-5">
            Model: <span class="italic text-sm">{{ popUpContent.type.model }}</span>
          </p>
          <p class="pl-5">
            Height: <span class="italic text-sm">{{ popUpContent.type.height }}</span>
          </p>
        </div>

        <div class="pt-5">
          <p class="font-medium">Disks:</p>
          <div v-for="disk in popUpContent.type.disks" :key="disk.model">
            <p class="pl-5">
              Type: <span class="italic text-sm">{{ disk.type }}</span>
            </p>
            <p class="pl-5">
              Size: <span class="italic text-sm">{{ disk.size / 1024 ** 4 }}TB</span>
            </p>
            <p class="pl-5">
              Model: <span class="italic text-sm">{{ disk.model }}</span>
            </p>
            <p class="pl-5">
              Number: <span class="italic text-sm">{{ disk.number }}</span>
            </p>
          </div>
        </div>
      </div>

      <div v-else-if="'netifs' in popUpContent['type']">
        <p class="font-semibold flex justify-center text-purple-700 text-xl capitalize py-5">
          {{ popUpContent.type.id }}
        </p>

        <div class="pt-5">
          <p class="pl-5">Model: {{ popUpContent.type.model }}</p>
          <p class="pl-5">Height: {{ popUpContent.type.height }}</p>
          <p class="pl-5">Width: {{ popUpContent.type.width }}</p>
        </div>

        <div class="pt-5">
          <p class="font-medium">Netif:</p>
          <div v-for="netif in popUpContent.type.netifs" :key="netif.type">
            <p class="pl-5">
              Type: <span class="italic text-sm">{{ netif.type }}</span>
            </p>
            <p class="pl-5">
              Bandwidth:
              <span class="italic text-sm">{{ (netif.bandwidth * 8) / 1000 ** 3 }}Gb/s</span>
            </p>
            <p class="pl-5">
              Number: <span class="italic text-sm">{{ netif.number }}</span>
            </p>
          </div>
        </div>
      </div>
      <div class="pt-5 flex justify-center">
        <button
          type="button"
          @click="closePopUp()"
          class="py-2.5 px-5 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-purple-700 focus:z-10 focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700"
        >
          close
        </button>
      </div>
    </div>
  </div>
</template>
