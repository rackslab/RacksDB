<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { ref, onMounted, inject, watch } from 'vue'
import SearchBar from '@/components/SearchBar.vue'
import InfrastructureCards from '@/components/InfrastructureCards.vue'
import InfrastructureTable from '@/components/InfrastructureTable.vue'
//import { injectionKey } from '@/plugins/runtimeConfiguration'
import type { Ref } from 'vue'
import type { Infrastructure } from '@/composables/RacksDBAPI'
import { Squares2X2Icon, TableCellsIcon } from '@heroicons/vue/24/outline'

const http = useHttp()
const infrastructures: Ref<Array<Infrastructure>> = ref([])
const infrastructureDetails: Ref<Infrastructure | undefined> = ref()
//const showFullImg = ref(false)
const cardsView = ref(true)

// this function changes the display by assigning the opposite value to cardsView
function changeView() {
  cardsView.value = !cardsView.value
}

/*
function toggleImageModal() {
  showFullImg.value = !showFullImg.value
}
*/

async function getInfrastructures() {
  try {
    const resp = await http.get('infrastructures')
    infrastructures.value = resp.data as Infrastructure[]
    infrastructureDetails.value = infrastructures.value.filter(
      (infrastructure) => infrastructure.name === props.name
    )[0]
  } catch (error) {
    console.error('Error during infrastructures data recovery', error)
  }
}

onMounted(() => {
  getInfrastructures()
})

// Using watch to trigger getDatacenter() when the value of props.name change
watch(
  () => props.name,
  () => {
    getInfrastructures()
  }
)

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

  <!--
  <img
    :src="`${inject(injectionKey)!.api_server}/draw/infrastructure/${props.name}.svg`"
    alt=""
    @click="toggleImageModal()"
    class="h-96 max-w-500 mx-auto p-10"
  />

  <div
    v-show="showFullImg"
    class="fixed top-0 left-0 flex flex-col items-center justify-center w-screen h-screen bg-gray-300 bg-opacity-50 dark:bg-gray-900 dark:bg-opacity-50 backdrop-blur-md z-50"
  >
    <img
      :src="`${inject(injectionKey)!.api_server}/draw/infrastructure/${props.name}.svg`"
      alt=""
      @click="toggleImageModal()"
      class="h-screen max-w-full bg-white"
    />
  </div>
  -->

  <div class="flex justify-center pb-5">
    <div v-if="cardsView" class="flex">
      <Squares2X2Icon @click="changeView()" class="h-20 w-20" />
      <TableCellsIcon @click="changeView()" class="h-10 w-10" />
    </div>

    <div v-if="!cardsView" class="flex">
      <Squares2X2Icon @click="changeView()" class="h-10 w-10" />
      <TableCellsIcon @click="changeView()" class="h-20 w-20" />
    </div>
  </div>

  <div v-if="infrastructureDetails">
    <div v-show="cardsView" class="flex justify-center pb-10">
      <div v-for="rack in infrastructureDetails.layout" :key="rack.rack">
        <div v-for="item in rack.nodes" :key="item.name">
          <InfrastructureCards
            v-if="infrastructureDetails"
            :infrastructure="infrastructureDetails"
            :rack="item.rack"
            equipment="nodes"
            :name="item.name"
            :id="item.type.id"
          />
        </div>
        <div v-for="item in rack.storage" :key="item.name">
          <InfrastructureCards
            v-if="infrastructureDetails"
            :infrastructure="infrastructureDetails"
            :rack="item.rack"
            equipment="storage"
            :name="item.name"
            :id="item.type.id"
          />
        </div>
        <div v-for="item in rack.network" :key="item.name">
          <InfrastructureCards
            v-if="infrastructureDetails"
            :infrastructure="infrastructureDetails"
            :rack="item.rack"
            equipment="network"
            :name="item.name"
            :id="item.type.id"
          />
        </div>
      </div>
    </div>
  </div>

  <div v-show="!cardsView" class="pb-10">
    <InfrastructureTable
      v-if="infrastructureDetails"
      :infrastructure="infrastructures"
      :infrastructureDetails="infrastructureDetails"
    />
  </div>
</template>
