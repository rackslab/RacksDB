<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { useRacksDBAPI } from '@/composables/RacksDBAPI'
import { ref, onMounted } from 'vue'
import HomeViewCard from '@/components/HomeViewCard.vue'
import type { Ref } from 'vue'
import type { Infrastructure, Datacenter } from '@/composables/RacksDBAPI'

const http = useHttp()
const racksDBAPI = useRacksDBAPI(http)
const datacenters: Ref<Array<Datacenter>> = ref([])
const infrastructures: Ref<Array<Infrastructure>> = ref([])

async function getDatacenters() {
  datacenters.value = await racksDBAPI.datacenters()
}

async function getInfrastructures() {
  infrastructures.value = await racksDBAPI.infrastructures()
}

onMounted(() => {
  getDatacenters()
  getInfrastructures()
})
</script>

<template>
  <section>
    <div class="flex justify-center items-center w-full h-full text-purple-700">
      <h1 class="text-5xl font-medium flex justify-center py-20 z-10">Overview of your database</h1>
    </div>
  </section>

  <div class="flex justify-around pt-32 px-32">
    <HomeViewCard
      title="datacenter"
      route="datacenters"
      :nbItem="datacenters.length"
      :datacentersArray="datacenters"
    />

    <HomeViewCard
      title="infrastructure"
      route="infrastructures"
      :nbItem="infrastructures.length"
      :infrastructuresArray="infrastructures"
    />
  </div>
</template>
