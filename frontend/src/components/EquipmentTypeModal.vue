<!--Copyright (c) 2022-2024 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT -->

<script setup lang="ts">
import type { PropType } from 'vue'
import type {
  NodeEquipmentType,
  NetworkEquipmentType,
  StorageEquipmentType,
  MiscEquipmentType
} from '@/composables/RacksDBAPI'
import { Dialog, DialogPanel } from '@headlessui/vue'

function strTruncateLimit(str: string, limit: number): string {
  if (str.length < limit) return str
  const edge_limit = limit / 2
  return str.slice(0, edge_limit) + '...' + str.slice(-edge_limit)
}

defineProps({
  showModal: Boolean,
  modalContent: {
    type: Object as PropType<
      | NodeEquipmentType
      | NetworkEquipmentType
      | StorageEquipmentType
      | MiscEquipmentType
      | undefined
    >,
    required: true
  }
})
</script>

<template>
  <Dialog
    v-if="modalContent"
    :open="showModal"
    @close="$emit('toggleModal')"
    class="fixed top-0 left-0 flex flex-col items-center justify-center w-screen h-screen bg-gray-300 bg-opacity-50 dark:bg-gray-900 dark:bg-opacity-50 backdrop-blur-md z-50"
  >
    <DialogPanel
      class="max-w-4xl bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700"
    >
      <!-- Node -->
      <div v-if="'cpu' in modalContent">
        <p class="font-semibold flex justify-center text-purple-700 text-xl capitalize py-5">
          {{ modalContent.id }}
        </p>

        <div class="pt-5">
          <p class="pl-5">
            Model: <span class="italic text-sm">{{ modalContent.model }}</span>
          </p>
          <p class="pl-5">
            Height: <span class="italic text-sm">{{ modalContent.height }}</span>
          </p>
          <p class="pl-5">
            Width: <span class="italic text-sm">{{ modalContent.width }}</span>
          </p>
          <p class="pl-5">
            Specs:
            <span class="italic text-sm"
              ><a
                :href="modalContent.specs"
                target="_blank"
                class="font-bold hover:text-purple-700"
                >{{ strTruncateLimit(modalContent.specs, 50) }}</a
              ></span
            >
          </p>
        </div>

        <div class="pt-5">
          <p class="font-medium">CPU:</p>
          <p class="pl-5">
            Sockets: <span class="italic text-sm">{{ modalContent.cpu.sockets }}</span>
          </p>
          <p class="pl-5">
            Model: <span class="italic text-sm">{{ modalContent.cpu.model }}</span>
          </p>
          <p class="pl-5">
            Specs:
            <span class="italic text-sm"
              ><a
                :href="modalContent.cpu.specs"
                target="_blank"
                class="font-bold hover:text-purple-700"
                >{{ strTruncateLimit(modalContent.specs, 50) }}</a
              ></span
            >
          </p>
          <p class="pl-5">
            Cores: <span class="italic text-sm">{{ modalContent.cpu.cores }}</span>
          </p>
        </div>

        <div class="pt-5">
          <p class="font-medium">RAM:</p>
          <p class="pl-5">
            Dimm: <span class="italic text-sm">{{ modalContent.ram.dimm }}</span>
          </p>
          <p class="pl-5">
            Size:
            <span class="italic text-sm">{{ modalContent.ram.size / 1024 ** 3 }}GB</span>
          </p>
        </div>

        <div class="pt-5">
          <p class="font-medium">Storage:</p>
          <div v-for="storage in modalContent.storage" :key="storage.model">
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
          <div v-for="netif in modalContent.netifs" :key="netif.type">
            <p class="pl-5">
              Type: <span class="italic text-sm">{{ netif.type }}</span>
            </p>
            <p class="pl-5">
              Bandwith:
              <span class="italic text-sm">{{ netif.bandwidth / 1000 ** 3 }}Gb/s</span>
            </p>
          </div>
        </div>
      </div>

      <!-- Storage -->
      <div v-else-if="'disks' in modalContent">
        <p class="font-semibold flex justify-center text-purple-700 text-xl capitalize py-5">
          {{ modalContent.id }}
        </p>

        <div class="pt-5">
          <p class="pl-5">
            Model: <span class="italic text-sm">{{ modalContent.model }}</span>
          </p>
          <p class="pl-5">
            Height: <span class="italic text-sm">{{ modalContent.height }}</span>
          </p>
        </div>

        <div class="pt-5">
          <p class="font-medium">Disks:</p>
          <div v-for="disk in modalContent.disks" :key="disk.model">
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

      <!-- Network -->
      <div v-else-if="'netifs' in modalContent">
        <p class="font-semibold flex justify-center text-purple-700 text-xl capitalize py-5">
          {{ modalContent.id }}
        </p>

        <div class="pt-5">
          <p class="pl-5">Model: {{ modalContent.model }}</p>
          <p class="pl-5">Height: {{ modalContent.height }}</p>
          <p class="pl-5">Width: {{ modalContent.width }}</p>
        </div>

        <div class="pt-5">
          <p class="font-medium">Netif:</p>
          <div v-for="netif in modalContent.netifs" :key="netif.type">
            <p class="pl-5">
              Type: <span class="italic text-sm">{{ netif.type }}</span>
            </p>
            <p class="pl-5">
              Bandwidth:
              <span class="italic text-sm">{{ netif.bandwidth / 1000 ** 3 }}Gb/s</span>
            </p>
            <p class="pl-5">
              Number: <span class="italic text-sm">{{ netif.number }}</span>
            </p>
          </div>
        </div>
      </div>

      <!-- Misc -->
      <div v-else>
        <p class="font-semibold flex justify-center text-purple-700 text-xl capitalize py-5">
          {{ modalContent.id }}
        </p>

        <div class="pt-5">
          <p class="pl-5">Model: {{ modalContent.model }}</p>
          <p class="pl-5">Height: {{ modalContent.height }}</p>
          <p class="pl-5">Width: {{ modalContent.width }}</p>
        </div>
      </div>

      <div class="pt-5 flex justify-center">
        <button
          @click="$emit('toggleModal')"
          type="button"
          class="py-2.5 px-5 text-sm font-medium text-white focus:outline-none bg-purple-700 rounded-lg border"
        >
          close
        </button>
      </div>
    </DialogPanel>
  </Dialog>
</template>
