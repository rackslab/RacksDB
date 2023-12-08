<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { useRacksDBAPI } from '@/composables/RacksDBAPI'
import { useRacksDBIMGAPI } from '@/composables/RacksDBIMG'
import { ref, onMounted, watch } from 'vue'
import SearchBar from '@/components/SearchBar.vue'
import InfrastructureCard from '@/components/InfrastructureCard.vue'
import InfrastructureTable from '@/components/InfrastructureTable.vue'
import type { Ref } from 'vue'
import type { Infrastructure } from '@/composables/RacksDBAPI'
import { Squares2X2Icon, TableCellsIcon } from '@heroicons/vue/24/outline'

const http = useHttp()
const racksDBAPI = useRacksDBAPI(http)
const racksDBIMG = useRacksDBIMGAPI(http)
const infrastructures: Ref<Array<Infrastructure>> = ref([])
const infrastructureDetails: Ref<Infrastructure | undefined> = ref()
const cardsView = ref(true)
const blobURL = ref()

async function getInfrastructureImg() {
  try {
    const myBlob = await racksDBIMG.infrastructureImageSvg(props.name)
    blobURL.value = URL.createObjectURL(myBlob)
  } catch (error) {
    console.error(`Error getting ${props.name}: ` + error)
  }
}

// this function changes the display by assigning the opposite value to cardsView
function changeView() {
  cardsView.value = !cardsView.value
}

async function getInfrastructures() {
  infrastructures.value = await racksDBAPI.infrastructures()
  infrastructureDetails.value = infrastructures.value.filter(
    (infrastructure) => infrastructure.name === props.name
  )[0]
}

onMounted(() => {
  getInfrastructures()
  getInfrastructureImg()
})

// Using watch to trigger getDatacenter() when the value of props.name change
watch(
  () => props.name,
  () => {
    getInfrastructures()
    getInfrastructureImg()
  }
)

const props = defineProps({
  name: {
    type: String,
    required: true
  }
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

  <img v-if="blobURL" :src="blobURL" class="" alt="" />

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
          <InfrastructureCard
            v-if="infrastructureDetails"
            :infrastructure="infrastructureDetails"
            :rack="item.rack"
            equipment="nodes"
            :name="item.name"
            :id="item.type.id"
          />
        </div>
        <div v-for="item in rack.storage" :key="item.name">
          <InfrastructureCard
            v-if="infrastructureDetails"
            :infrastructure="infrastructureDetails"
            :rack="item.rack"
            equipment="storage"
            :name="item.name"
            :id="item.type.id"
          />
        </div>
        <div v-for="item in rack.network" :key="item.name">
          <InfrastructureCard
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
