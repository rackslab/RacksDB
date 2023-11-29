<script setup lang="ts">
import type { PropType } from 'vue';
import type { Infrastructure } from '@/views/InfrastructuresView.vue'
import { ref } from 'vue'

const rack = ref()
const showRack = ref(false)
const showInfrastructureRacks = ref(true)

function rackDetails(rackName: string) {
  showRack.value = true
  showInfrastructureRacks.value = false
  var layout = props.infrastructureDetails.layout

  for (let index = 0; index < layout!.length; index++) {
    rack.value = layout!.filter((rack) => rack.rack === rackName)
  }
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
      class="flex justify-center pb-28"
      v-for="infrastructure in props.infrastructure"
      :key="infrastructure.name"
    >
      <div v-for="rack in infrastructure.layout" :key="rack.rack">
        <button
          type="button"
          @click="rackDetails(rack.rack)"
          class="py-2.5 px-5 mr-2 mb-2 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700"
        >
          {{ rack.rack }}
        </button>
      </div>
    </div>

    <div v-show="showInfrastructureRacks">
      <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
        <thead
          class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400"
        >
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
              {{ node.name }}
            </td>
            <td class="px-6 py-4">Node {{ node.rack }}</td>
            <td class="px-6 py-4 capitalize">{{ node.type.id }}</td>
          </tr>

          <tr v-for="storage in layout.storage" :key="storage.name">
            <td
              scope="row"
              class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white capitalize"
            >
              {{ storage.name }}
            </td>
            <td class="px-6 py-4">Storage {{ storage.rack }}</td>
            <td class="px-6 py-4 capitalize">{{ storage.type.id }}</td>
          </tr>

          <tr v-for="network in layout.network" :key="network.name">
            <td
              scope="row"
              class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white capitalize"
            >
              {{ network.name }}
            </td>
            <td class="px-6 py-4">Network {{ network.rack }}</td>
            <td class="px-6 py-4 capitalize">{{ network.type.id }}</td>
          </tr>
        </template>
      </table>
    </div>

    <div v-show="showRack">
      <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
        <thead
          class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400"
        >
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
              {{ node.name }}
            </td>
            <td class="px-6 py-4">Node {{ node.rack }}</td>
            <td class="px-6 py-4 capitalize">{{ node.type.id }}</td>
          </tr>

          <tr v-for="storage in layout.storage" :key="storage.name">
            <td
              scope="row"
              class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white capitalize"
            >
              {{ storage.name }}
            </td>
            <td class="px-6 py-4">Storage {{ storage.rack }}</td>
            <td class="px-6 py-4 capitalize">{{ storage.type.id }}</td>
          </tr>

          <tr v-for="network in layout.network" :key="network.name">
            <td
              scope="row"
              class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white capitalize"
            >
              {{ network.name }}
            </td>
            <td class="px-6 py-4">Network {{ network.rack }}</td>
            <td class="px-6 py-4 capitalize">{{ network.type.id }}</td>
          </tr>
        </template>
      </table>
    </div>
</template>
