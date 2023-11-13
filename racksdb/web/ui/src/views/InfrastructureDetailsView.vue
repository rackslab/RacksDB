<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { ref, onMounted, inject } from 'vue'
import SearchBar from '@/components/SearchBar.vue'
import InfrastructureCards from '@/components/InfrastructureCards.vue'
import { injectionKey } from '@/plugins/runtimeConfiguration'
import type { Ref } from 'vue'
import type { Infrastructure } from '@/views/InfrastructuresView.vue'

const http = useHttp()
const infrastructures: Ref<Array<Infrastructure>> = ref([])
const infrastructureDetails: Ref<Infrastructure | undefined> = ref()
const showFullImg = ref(false)
const rack = ref()
const cardsView = ref(true)
const tableView = ref(false)
const showRack = ref(false)
const showInfrastructureRacks = ref(true)

function choseView() {
  if (cardsView.value) {
    cardsView.value = !cardsView.value
    tableView.value = !tableView.value
  } else {
    tableView.value = !tableView.value
    cardsView.value = !cardsView.value
  }
}

function openImg() {
  showFullImg.value = !showFullImg.value
}

function rackDetails(rackName: string) {
  showRack.value = true
  showInfrastructureRacks.value = false
  var layout = infrastructureDetails.value?.layout

  for (let index = 0; index < layout!.length; index++) {
    rack.value = layout!.filter((rack) => rack.rack === rackName)
  }
}

async function getInfrastructure() {
  try {
    const resp = await http.get('infrastructures')
    infrastructures.value = resp.data as Infrastructure[]
    infrastructureDetails.value = infrastructures.value.filter(
      (infrastructure) => infrastructure.name === props.name
    )[0]
  } catch (error) {
    console.error('Error during infrastructure data recovery', error)
  }
}

onMounted(() => {
  getInfrastructure()
})

const props = defineProps({
  name: String
})
</script>

<template>
  <SearchBar
    v-if="infrastructures.length"
    viewTitle="Infrastructure Details"
    searchedItem="infrastructure"
    :items="infrastructures"
  />

  <h2 class="text-3xl font-medium flex justify-center capitalize py-16">
    {{ name }} Infrastructure
  </h2>

  <img
    :src="`${inject(injectionKey)!.api_server}/draw/infrastructure/${props.name}.svg`"
    alt=""
    @click="openImg()"
    class="h-96 max-w-500 mx-auto p-10"
  />

  <div
    v-show="showFullImg"
    class="fixed top-0 left-0 flex flex-col items-center justify-center w-screen h-screen bg-gray-300 bg-opacity-50 dark:bg-gray-900 dark:bg-opacity-50 backdrop-blur-md z-50"
  >
    <img
      :src="`${inject(injectionKey)!.api_server}/draw/infrastructure/${props.name}.svg`"
      alt=""
      @click="openImg()"
      class="h-screen max-w-full bg-white"
    />
  </div>

  <div class="flex justify-end mr-36">
    <img @click="choseView()" src="/assets/cards.svg" alt="" />
    <img @click="choseView()" src="/assets/table.svg" alt="" />
  </div>

  <div v-show="cardsView">
    <InfrastructureCards
      v-if="infrastructureDetails"
      :infrastructure="infrastructureDetails"
      searchItem="nodes"
    />
    <InfrastructureCards
      v-if="infrastructureDetails"
      :infrastructure="infrastructureDetails"
      searchItem="storage"
    />
    <InfrastructureCards
      v-if="infrastructureDetails"
      :infrastructure="infrastructureDetails"
      searchItem="network"
    />
  </div>

  <div v-show="tableView" class="pb-10">
    <div
      class="flex justify-center pb-28"
      v-for="infrastructure in infrastructures"
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
  </div>
</template>
