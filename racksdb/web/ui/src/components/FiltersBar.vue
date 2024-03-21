<script lang="ts" setup>
import { computed } from 'vue'

const activeFilters = computed(() => {
  const filters: Array<{ key: string; value: string }> = []

  if (props.selectedRacks) {
    props.selectedRacks.forEach((rack) => {
      filters.push({ key: 'rack', value: rack })
    })
  }

  if (props.selectedCategories) {
    props.selectedCategories.forEach((category) => {
      filters.push({ key: 'category', value: category })
    })
  }

  if (props.selectedEquipmentTypes) {
    props.selectedEquipmentTypes.forEach((equipmentType) => {
      filters.push({ key: 'equipmentType', value: equipmentType })
    })
  }

  if (props.selectedTags) {
    props.selectedTags.forEach((tag) => {
      filters.push({ key: 'tag', value: tag })
    })
  }

  if (props.inputEquipmentName) {
    filters.push({ key: 'equipmentName', value: props.inputEquipmentName })
  }

  return filters
})

const props = defineProps({
  selectedRacks: {
    type: Array<string>
  },
  selectedCategories: {
    type: Array<string>
  },
  selectedEquipmentTypes: {
    type: Array<string>
  },
  selectedTags: {
    type: Array<string>
  },
  inputEquipmentName: {
    type: String
  }
})
</script>

<template>
  <div class="bg-gray-100 flex justify-center w-[60vw] mt-3 mx-auto">
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
            class="m-1 inline-flex items-center rounded-full border border-gray-200 bg-white py-1.5 pl-3 pr-2 text-sm font-medium text-gray-900"
          >
            <span>{{ activeFilter.value }}</span>
            <button
              type="button"
              class="ml-1 inline-flex h-4 w-4 flex-shrink-0 rounded-full p-1 text-gray-400 hover:bg-gray-200 hover:text-gray-500"
            >
              <span class="sr-only">Remove filter for {{ activeFilter.value }}</span>
              <svg class="h-2 w-2" stroke="currentColor" fill="none" viewBox="0 0 8 8">
                <path stroke-linecap="round" stroke-width="1.5" d="M1 1l6 6m0-6L1 7" />
              </svg>
            </button>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
