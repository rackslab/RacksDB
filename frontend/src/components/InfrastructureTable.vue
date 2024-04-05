<!--Copyright (c) 2022-2024 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
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
import EquipmentTypeModal from '@/components/EquipmentTypeModal.vue'
import InfrastructureFilters from '@/components/InfrastructureFilters.vue'
import FiltersBar from '@/components/FiltersBar.vue'
import {
  BarsArrowDownIcon,
  BarsArrowUpIcon,
  ChevronDownIcon,
  ChevronUpIcon
} from '@heroicons/vue/24/outline'
import { FunnelIcon } from '@heroicons/vue/24/solid'

const props = defineProps({
  infrastructureDetails: {
    type: Object as PropType<Infrastructure>,
    required: true
  }
})

var showModal = ref(false)
var modalContent: Ref<
  NodeEquipmentType | NetworkEquipmentType | StorageEquipmentType | MiscEquipmentType | undefined
> = ref()
const alphabeticalOrder = ref(true)
const displayRacks: Ref<Record<string, boolean>> = ref({})
const showSlider = ref(false)
const inputEquipmentName: Ref<string> = ref('')
const selectedRacks: Ref<Array<string>> = ref([])
const selectedCategories: Ref<Array<string>> = ref([])
const selectedEquipmentTypes: Ref<Array<string>> = ref([])
const selectedTags: Ref<Array<string>> = ref([])
let equipmentCategories: Array<string> = []
let racks: Array<string> = []
let equipmentTypes: Array<string> = []
let tags: Array<string> = []
const infrastructureRacks: Ref<Array<string>> = ref([])
const racksEquipment: Record<string, Array<Node | Storage | Misc | Network>> = {}
const racksFilteredEquipment = computed(() => {
  let filteredEquipment: Record<string, Array<Node | Storage | Misc | Network>> = {}

  Object.keys(racksEquipment).forEach((rackName) => {
    filteredEquipment[rackName] = racksEquipment[rackName].filter((equipment) => {
      if (selectedRacks.value.length > 0 && !selectedRacks.value.includes(equipment.rack)) {
        return false
      }

      if (
        selectedCategories.value.length > 0 &&
        !selectedCategories.value.includes(equipment.equipmentType)
      ) {
        return false
      }

      if (
        selectedEquipmentTypes.value.length > 0 &&
        !selectedEquipmentTypes.value.includes(equipment.type.id)
      ) {
        return false
      }

      if (selectedTags.value.length > 0) {
        if (equipment.tags.filter((tag) => selectedTags.value.includes(tag)).length === 0) {
          return false
        }
      }

      if (inputEquipmentName.value !== '') {
        if (
          equipment.name
            .toLocaleLowerCase()
            .includes(inputEquipmentName.value.toLocaleLowerCase()) === false
        ) {
          return false
        }
      }

      return true
    })
  })

  return filteredEquipment
})

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

onMounted(() => {
  props.infrastructureDetails.layout.forEach((part) => {
    displayRacks.value[part.rack] = true
    infrastructureRacks.value.push(part.rack)
    racks.push(part.rack)
    racksEquipment[part.rack] = getRackEquipments(part.rack)
    racksEquipment[part.rack].forEach((equipment) => {
      if (!equipmentCategories.includes(equipment.equipmentType)) {
        equipmentCategories.push(equipment.equipmentType)
      }

      if (!equipmentTypes.includes(equipment.type.id)) {
        equipmentTypes.push(equipment.type.id)
      }

      equipment.tags.forEach((tag) => {
        if (!tags.includes(tag)) {
          tags.push(tag)
        }
      })
    })
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

  <FiltersBar
    v-show="
      selectedRacks.length > 0 ||
      selectedCategories.length > 0 ||
      selectedEquipmentTypes.length > 0 ||
      selectedTags.length > 0 ||
      inputEquipmentName.length > 0
    "
    v-model:selected-racks="selectedRacks"
    v-model:selected-equipment-types="selectedEquipmentTypes"
    v-model:selected-categories="selectedCategories"
    v-model:selected-tags="selectedTags"
    v-model:input-equipment-name="inputEquipmentName"
  />

  <!-- Slider -->
  <InfrastructureFilters
    @toggle-slider="toggleSlider"
    :showSlider="showSlider"
    :racks="racks"
    :equipmentCategories="equipmentCategories"
    :equipmentTypes="equipmentTypes"
    :tags="tags"
    v-model:selected-racks="selectedRacks"
    v-model:selected-equipment-types="selectedEquipmentTypes"
    v-model:selected-categories="selectedCategories"
    v-model:selected-tags="selectedTags"
    v-model:input-equipment-name="inputEquipmentName"
  />

  <div class="flex justify-center my-auto mx-auto pt-3">
    <table class="w-[60vw] text-center text-gray-500 dark:text-gray-400 table-fixed">
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
                <p class="ml-2">
                  {{ rack }}
                  <span class="text-sm font-light"
                    >({{ racksFilteredEquipment[rack].length }})</span
                  >
                </p>
              </div>
            </th>
          </tr>
          <template v-if="displayState">
            <tr
              v-for="equipment in racksFilteredEquipment[rack]"
              :key="equipment.name"
              class="border-b border-t dark:bg-gray-800 h-14 align-middle"
            >
              <td>{{ equipment.name }}</td>
              <td class="capitalize flex justify-center align-middle">
                <div
                  class="bg-yellow-500 p-2 mx-1 my-2 w-20 justify-center rounded-full text-white"
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
                    class="flex p-2 mx-1 my-2 w-20 justify-center bg-purple-700 rounded-full text-white"
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
