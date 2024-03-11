<!--Copyright (c) 2022-2024 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import type { Ref, PropType } from 'vue'
import type {
  Infrastructure,
  NodeEquipment,
  NetworkEquipment,
  StorageEquipment,
  MiscEquipment,
  NodeEquipmentType,
  NetworkEquipmentType,
  StorageEquipmentType,
  MiscEquipmentType
} from '@/composables/RacksDBAPI'
import { ref, onMounted } from 'vue'
import {
  BarsArrowDownIcon,
  BarsArrowUpIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'
import EquipmentTypeModal from '@/components/EquipmentTypeModal.vue'
import { FunnelIcon } from '@heroicons/vue/24/solid'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'

var showModal = ref(false)
var modalContent: Ref<
  NodeEquipmentType | NetworkEquipmentType | StorageEquipmentType | MiscEquipmentType | undefined
> = ref()
const alphabeticalOrder = ref(true)
const displayRacks: Ref<Record<string, boolean>> = ref({})
const showSlider = ref(false)

type EquipmentType = 'nodes' | 'storage' | 'network' | 'misc'

interface Node extends NodeEquipment {
  equipmentType: EquipmentType
}

interface Network extends NetworkEquipment {
  equipmentType: EquipmentType
}

interface Storage extends StorageEquipment {
  equipmentType: EquipmentType
}

interface Misc extends MiscEquipment {
  equipmentType: EquipmentType
}

function toggleSlider() {
  showSlider.value = !showSlider.value
}

function displayRackEquipment(rackName: string) {
  displayRacks.value[rackName] = !displayRacks.value[rackName]
}

function invertRacksSort() {
  const reversedDisplayRacks: Record<string, boolean> = {}

  Object.keys(displayRacks.value)
    .reverse()
    .forEach((rack) => {
      reversedDisplayRacks[rack] = displayRacks.value[rack]
    })
  displayRacks.value = reversedDisplayRacks
  alphabeticalOrder.value = !alphabeticalOrder.value
}

/*
 * This function returns the equipment of the current infrastructure in a given
 * rack. The equipment are then sorted by their position in the rack, first by
 * descending height and width.
 */
function getRackEquipments(rackName: string) {
  let equipments: Array<Node | Network | Storage | Misc> = []
  const parts = props.infrastructureDetails.layout.filter((part) => part.rack == rackName)

  /*
   * For every parts, insert all nodes, network equipments, etc... enriched
   * with equipmentType in equipments array.
   */
  parts.forEach((part) => {
    equipments.push(
      ...part.nodes.map((node) => {
        return { ...{ equipmentType: 'nodes' }, ...node } as Node
      })
    )
    equipments.push(
      ...part.network.map((network) => {
        return { ...{ equipmentType: 'network' }, ...network } as Network
      })
    )
    equipments.push(
      ...part.storage.map((storage) => {
        return { ...{ equipmentType: 'storage' }, ...storage } as Storage
      })
    )
    equipments.push(
      ...part.misc.map((misc) => {
        return { ...{ equipmentType: 'misc' }, ...misc } as Misc
      })
    )
  })
  /*
   * Sort equipment by slot in descending order, or in width descending orders
   * when in the same slot.
   */
  return equipments.sort((a, b) =>
    b.position.height == a.position.height
      ? b.position.width - a.position.width
      : b.position.height - a.position.height
  )
}

function toggleModal(
  equipment: NodeEquipmentType | NetworkEquipmentType | StorageEquipmentType | MiscEquipmentType
) {
  if (showModal.value) {
    showModal.value = !showModal.value
  } else {
    modalContent.value = equipment
    showModal.value = !showModal.value
  }
}
const props = defineProps({
  infrastructureDetails: {
    type: Object as PropType<Infrastructure>,
    required: true
  }
})

onMounted(() => {
  props.infrastructureDetails.layout.forEach((rack) => {
    displayRacks.value[rack.rack] = true
  })
})
</script>

<template>
  <div class="flex justify-center pt-5">
    <div class="flex justify-between min-w-[60vw]">
      <div
        @click="invertRacksSort()"
        class="flex pt-5 cursor-pointer hover:text-purple-700 hover:duration-100 duration-150"
      >
        <BarsArrowDownIcon v-if="alphabeticalOrder" class="h-7 w-7" />
        <BarsArrowUpIcon v-else class="h-7 w-7" />
        <p class="pl-2">Sort racks</p>
      </div>
      <div
        class="flex pt-5 cursor-pointer hover:text-purple-700 hover:duration-100 duration-150"
        @click="toggleSlider()"
      >
        <p class="pr-2">Filters</p>
        <FunnelIcon class="h-7 w-7" />
      </div>
    </div>
  </div>

  <!-- Slider -->
  <template>
    <TransitionRoot as="template" :show="showSlider">
      <Dialog as="div" class="relative z-10" @close="showSlider = false">
        <TransitionChild
          as="template"
          enter="ease-in-out duration-500"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="ease-in-out duration-500"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </TransitionChild>

        <div class="fixed inset-0 overflow-hidden">
          <div class="absolute inset-0 overflow-hidden">
            <div class="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
              <TransitionChild
                as="template"
                enter="transform transition ease-in-out duration-500 sm:duration-700"
                enter-from="translate-x-full"
                enter-to="translate-x-0"
                leave="transform transition ease-in-out duration-500 sm:duration-700"
                leave-from="translate-x-0"
                leave-to="translate-x-full"
              >
                <DialogPanel class="pointer-events-auto relative w-screen max-w-md">
                  <TransitionChild
                    as="template"
                    enter="ease-in-out duration-500"
                    enter-from="opacity-0"
                    enter-to="opacity-100"
                    leave="ease-in-out duration-500"
                    leave-from="opacity-100"
                    leave-to="opacity-0"
                  >
                    <div class="absolute left-0 top-0 -ml-8 flex pr-2 pt-4 sm:-ml-10 sm:pr-4">
                      <button
                        type="button"
                        class="relative rounded-md text-gray-300 hover:text-white focus:outline-none focus:ring-2 focus:ring-white"
                        @click="showSlider = false"
                      >
                        <span class="absolute -inset-2.5" />
                        <span class="sr-only">Close panel</span>
                        <XMarkIcon class="h-6 w-6" aria-hidden="true" />
                      </button>
                    </div>
                  </TransitionChild>
                  <div class="flex h-full flex-col overflow-y-scroll bg-white py-6 shadow-xl">
                    <div class="px-4 sm:px-6">
                      <DialogTitle class="text-lg font-semibold leading-6 text-gray-900"
                        >Filters</DialogTitle
                      >
                    </div>
                    <div class="relative mt-6 flex-1 px-4 sm:px-6">
                      <!-- Racks -->

                      <!-- Equipment category -->

                      <!-- Equipment types -->

                      <!-- Tags -->

                      <!-- Equipment name -->
                    </div>
                  </div>
                </DialogPanel>
              </TransitionChild>
            </div>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </template>

  <div class="flex justify-center my-auto mx-auto pt-5">
    <table class="min-w-[60vw] text-center text-gray-500 dark:text-gray-400 table-fixed">
      <thead
        class="border-b text-lg text-gray-700 uppercase bg-gray-100 dark:bg-gray-700 dark:text-gray-400 h-24"
      >
        <tr>
          <th scope="col" class="px-6 py-3">Name</th>
          <th scope="col" class="px-6 py-3">Category</th>
          <th scope="col" class="px-6 py-3">Equipment</th>
          <th scope="col" class="px-6 py-3">Tags</th>
        </tr>
      </thead>

      <tbody>
        <template v-for="(displayState, rack) in displayRacks" :key="rack">
          <tr class="border-b border-t bg-gray-50 h-14 text-lg">
            <th colspan="4">
              <div @click="displayRackEquipment(rack)" class="flex ml-2">
                <div v-if="displayRacks[rack]">
                  <ChevronDownIcon class="h-7 w-7 text-purple-700" />
                </div>
                <div v-else><ChevronUpIcon class="h-7 w-7 text-purple-700" /></div>
                <span class="ml-2">{{ rack }}</span>
              </div>
            </th>
          </tr>
          <template v-if="displayState">
            <tr
              v-for="equipment in getRackEquipments(rack)"
              :key="equipment.name"
              class="border-b border-t dark:bg-gray-800 h-14 align-middle"
            >
              <td>{{ equipment.name }}</td>
              <td class="capitalize flex justify-center align-middle">
                <div
                  v-if="equipment.equipmentType == 'nodes'"
                  class="bg-red-100 rounded-xl center items-center my-2 w-20 h-6"
                >
                  <span>{{ equipment.equipmentType }}</span>
                </div>
                <div
                  v-if="equipment.equipmentType == 'storage'"
                  class="bg-blue-100 rounded-xl center items-center my-2 w-20 h-6"
                >
                  <span>{{ equipment.equipmentType }}</span>
                </div>
                <div
                  v-if="equipment.equipmentType == 'network'"
                  class="bg-green-100 rounded-xl center items-center my-2 w-20 h-6"
                >
                  <span>{{ equipment.equipmentType }}</span>
                </div>
                <div
                  v-if="equipment.equipmentType == 'misc'"
                  class="bg-yellow-100 rounded-xl center items-center my-2 w-20 h-6"
                >
                  <span>{{ equipment.equipmentType }}</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <span
                  class="font-bold hover:text-purple-700 capitalize cursor-pointer"
                  @click="toggleModal(equipment.type)"
                  >{{ equipment.type.id }}</span
                >
              </td>
              <td class="flex justify-center align-middle">
                <template v-if="equipment.tags && equipment.tags.length > 0">
                  <div
                    v-for="tag in equipment.tags"
                    :key="tag"
                    class="flex p-2 mx-1 my-2 w-20 justify-center bg-purple-700 rounded-md text-white"
                  >
                    {{ tag }}
                  </div>
                </template>
                <template v-else> - </template>
              </td>
            </tr>
          </template>
        </template>
      </tbody>
    </table>
  </div>

  <EquipmentTypeModal
    v-if="modalContent"
    :showModal="showModal"
    :modalContent="modalContent"
    @toggle-modal="toggleModal"
  />
</template>
