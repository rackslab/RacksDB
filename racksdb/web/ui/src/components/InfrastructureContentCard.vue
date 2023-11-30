<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { ref } from 'vue'
import type { Ref, PropType } from 'vue'
import type {
  Infrastructure,
  NodeEquipment,
  NetworkEquipment,
  StorageEquipment
} from '@/composables/RacksDBAPI'

var showPopUp = ref(false)
var popUpContent: Ref<NodeEquipment | NetworkEquipment | StorageEquipment | undefined> = ref()
type equipmentType = 'nodes' | 'storage' | 'network'

const props = defineProps({
  rack: String,
  equipment: {
    type: String as PropType<equipmentType>,
    required: true
  },
  name: {
    type: String,
    required: true
  },
  id: String,
  infrastructure: {
    type: Object as PropType<Infrastructure>,
    required: true
  }
})

function popUp(name: string, equipment: equipmentType) {
  if (showPopUp.value) {
    showPopUp.value = !showPopUp.value
  } else {
    var layout = props.infrastructure.layout

    for (var y = 0; y < layout.length; y++) {
      var result = layout[y][equipment].find((item) => item.name === name)
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
</script>

<template>
  <div class="w-full max-w-lg pt-32 px-32">
    <div
      class="w-60 p-6 bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700 transition-transform hover:scale-105"
    >
      <h2 class="text-2xl font-semibold flex justify-center text-purple-700 capitalize">
        {{ rack }}
      </h2>
      <h3 class="flex justify-center text-purple-700 capitalize">{{ equipment }}</h3>

      <ul role="list" class="space-y-5 my-7">
        <li class="flex space-x-3 items-center">
          <span
            class="text-base font-normal leading-tight dark:text-gray-400 capitalize text-purple-700"
            >{{ name }}</span
          >
        </li>

        <li class="flex space-x-3 items-center">
          <span
            class="text-base font-normal leading-tight dark:text-gray-400 capitalize text-purple-700 cursor-pointer"
            @click="popUp(name, equipment)"
            >{{ id }}</span
          >
        </li>
      </ul>
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
  </div>
</template>
