<script lang="ts" setup>
import { XMarkIcon } from '@heroicons/vue/24/solid'
import { computed } from 'vue'

const selectedRacks = defineModel<Array<string>>('selectedRacks', { required: true })
const selectedEquipmentTypes = defineModel<Array<string>>('selectedEquipmentTypes', {
  required: true
})
const selectedCategories = defineModel<Array<string>>('selectedCategories', { required: true })
const selectedTags = defineModel<Array<string>>('selectedTags', { required: true })
const inputEquipmentName = defineModel<string>('inputEquipmentName', { required: true })
const activeFilters = computed(() => {
  const filters: Array<{ key: string; value: string }> = []

  if (props.filteredRacks) {
    props.filteredRacks.forEach((rack) => {
      filters.push({ key: 'rack', value: rack })
    })
  }

  if (props.filteredCategories) {
    props.filteredCategories.forEach((category) => {
      filters.push({ key: 'category', value: category })
    })
  }

  if (props.filteredEquipmentTypes) {
    props.filteredEquipmentTypes.forEach((equipmentType) => {
      filters.push({ key: 'equipmentType', value: equipmentType })
    })
  }

  if (props.filteredTags) {
    props.filteredTags.forEach((tag) => {
      filters.push({ key: 'tag', value: tag })
    })
  }

  if (props.filteredinputEquipmentName) {
    filters.push({ key: 'equipmentName', value: props.filteredinputEquipmentName })
  }

  return filters
})

function removeFilter(key: string, filter: string) {
  if (key == 'rack') {
    selectedRacks.value = selectedRacks.value.filter((rack) => rack !== filter)
  } else if (key == 'category') {
    selectedCategories.value = selectedCategories.value.filter((category) => category !== filter)
  } else if (key == 'equipmentType') {
    selectedEquipmentTypes.value = selectedEquipmentTypes.value.filter(
      (equipmentType) => equipmentType !== filter
    )
  } else if (key == 'tag') {
    selectedTags.value = selectedTags.value.filter((tag) => tag !== filter)
  } else {
    inputEquipmentName.value = ''
  }
}

const props = defineProps({
  filteredRacks: {
    type: Array<string>,
    required: true
  },
  filteredCategories: {
    type: Array<string>
  },
  filteredEquipmentTypes: {
    type: Array<string>
  },
  filteredTags: {
    type: Array<string>
  },
  filteredinputEquipmentName: {
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
              class="ml-1 inline-flex h-5 w-5 flex-shrink-0 rounded-full p-1 text-gray-400 hover:bg-gray-200 hover:text-gray-500"
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
