<script lang="ts" setup>
import type { Ref } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/solid'

const selectedRacks = defineModel<Array<string>>('selectedRacks', { required: true })
const selectedEquipmentTypes = defineModel<Array<string>>('selectedEquipmentTypes', {
  required: true
})
const selectedCategories = defineModel<Array<string>>('selectedCategories', { required: true })
const selectedTags = defineModel<Array<string>>('selectedTags', { required: true })
const inputEquipmentName = defineModel<string>('inputEquipmentName', { required: true })

const activeFiltersCategories: Array<{
  filters: Ref<string[] | string>
  key: string
  badgeClass: string
  buttonClass: string
}> = [
  {
    filters: selectedRacks,
    key: 'rack',
    badgeClass: 'bg-orange-700',
    buttonClass: 'hover:bg-orange-200 hover:text-orange-500'
  },
  {
    filters: selectedCategories,
    key: 'category',
    badgeClass: 'bg-yellow-500',
    buttonClass: 'hover:bg-yellow-200 hover:text-yellow-400'
  },
  {
    filters: selectedEquipmentTypes,
    key: 'equipmentType',
    badgeClass: 'bg-green-700',
    buttonClass: 'hover:bg-green-200 hover:text-green-500'
  },
  {
    filters: selectedTags,
    key: 'tag',
    badgeClass: 'bg-purple-700',
    buttonClass: 'hover:bg-purple-200 hover:text-purple-500'
  },
  {
    filters: inputEquipmentName,
    key: 'equipmentName',
    badgeClass: 'bg-blue-700',
    buttonClass: 'hover:bg-blue-200 hover:text-blue-500'
  }
]

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

// type guard to check for array of strings
function isStringArray(input: string | string[]): input is string[] {
  return Array.isArray(input)
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
          <template
            v-for="activeFiltersCategory in activeFiltersCategories"
            :key="activeFiltersCategory.key"
          >
            <span
              v-for="activeFilter in isStringArray(activeFiltersCategory.filters.value)
                ? activeFiltersCategory.filters.value
                : [activeFiltersCategory.filters.value]"
              :class="[
                'm-1 inline-flex items-center rounded-full border border-gray-200 py-1.5 pl-3 pr-2 text-sm font-medium text-white',
                activeFiltersCategory.badgeClass
              ]"
              :key="activeFilter"
            >
              <span>{{ activeFilter }}</span>
              <button
                type="button"
                :class="[
                  'ml-1 inline-flex h-5 w-5 flex-shrink-0 rounded-full p-1 text-white',
                  activeFiltersCategory.buttonClass
                ]"
                @click="removeFilter(activeFiltersCategory.key, activeFilter)"
              >
                <XMarkIcon />
              </button>
            </span>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>
