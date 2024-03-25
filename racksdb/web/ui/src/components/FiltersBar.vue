<script lang="ts" setup>
import { computed } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/solid'

const selectedRacks = defineModel<Array<string>>('selectedRacks', { required: true })
const selectedEquipmentTypes = defineModel<Array<string>>('selectedEquipmentTypes', {
  required: true
})
const selectedCategories = defineModel<Array<string>>('selectedCategories', { required: true })
const selectedTags = defineModel<Array<string>>('selectedTags', { required: true })
const inputEquipmentName = defineModel<string>('inputEquipmentName', { required: true })
const activeFilters = computed(() => {
  const filters: Array<{ key: string; value: string }> = []

  if (selectedRacks.value) {
    selectedRacks.value.forEach((rack) => {
      filters.push({ key: 'rack', value: rack })
    })
  }

  if (selectedCategories.value) {
    selectedCategories.value.forEach((category) => {
      filters.push({ key: 'category', value: category })
    })
  }

  if (selectedEquipmentTypes.value) {
    selectedEquipmentTypes.value.forEach((equipmentType) => {
      filters.push({ key: 'equipmentType', value: equipmentType })
    })
  }

  if (selectedTags.value) {
    selectedTags.value.forEach((tag) => {
      filters.push({ key: 'tag', value: tag })
    })
  }

  if (inputEquipmentName.value) {
    filters.push({ key: 'equipmentName', value: inputEquipmentName.value })
  }

  return filters
})

function removeFilter(key: string, filter: string) {
  switch (key) {
    case 'rack':
      selectedRacks.value = selectedRacks.value.filter((rack) => rack !== filter)
      break
    case 'category':
      selectedCategories.value = selectedCategories.value.filter((category) => category !== filter)
      break
    case 'equipmentType':
      selectedEquipmentTypes.value = selectedEquipmentTypes.value.filter(
        (equipmentType) => equipmentType !== filter
      )
      break
    case 'tag':
      selectedTags.value = selectedTags.value.filter((tag) => tag !== filter)
      break
    case 'equipmentName':
      inputEquipmentName.value = ''
      break
  }
}
</script>

<template>
  <div class="bg-gray-100 flex justify-center w-[60vw] mt-3 mx-auto h-auto">
    <div class="min-w-[60vw] px-4 py-3 sm:flex sm:items-center sm:px-6 lg:px-8">
      <h3 class="text-sm font-medium text-gray-500">
        Filters
        <span class="sr-only">, active</span>
      </h3>

      <div aria-hidden="true" class="hidden h-5 w-px bg-gray-300 sm:ml-4 sm:block" />

      <div class="mt-2 sm:ml-4 sm:mt-0">
        <div class="-m-1 flex flex-wrap items-center">
          <span
            v-for="activeFilter in activeFilters"
            :key="activeFilter.key"
            :class="[
              'm-1 inline-flex items-center rounded-full border border-gray-200 py-1.5 pl-3 pr-2 text-sm font-medium text-gray-600',
              activeFilter.key === 'rack'
                ? 'bg-orange-100'
                : activeFilter.key === 'category'
                ? 'bg-green-100'
                : activeFilter.key === 'equipmentType'
                ? 'bg-yellow-100'
                : activeFilter.key === 'tag'
                ? 'bg-zinc-100'
                : activeFilter.key === 'equipmentName'
                ? 'bg-violet-100'
                : 'bg-gray-200'
            ]"
          >
            <span>{{ activeFilter.value }}</span>
            <button
              type="button"
              :class="[
                'ml-1 inline-flex h-5 w-5 flex-shrink-0 rounded-full p-1 text-gray-400',
                activeFilter.key === 'rack'
                  ? 'hover:bg-orange-200 hover:text-orange-500'
                  : activeFilter.key === 'category'
                  ? 'hover:bg-green-200 hover:text-green-500'
                  : activeFilter.key === 'equipmentType'
                  ? 'hover:bg-yellow-200 hover:text-yellow-500'
                  : activeFilter.key === 'tag'
                  ? 'hover:bg-zinc-200 hover:text-zinc-500'
                  : activeFilter.key === 'equipmentName'
                  ? 'hover:bg-violet-200 hover:text-violet-500'
                  : 'hover:bg-gray-200 hover:text-gray-500'
              ]"
              @click="removeFilter(activeFilter.key, activeFilter.value)"
            >
              <XMarkIcon />
            </button>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
