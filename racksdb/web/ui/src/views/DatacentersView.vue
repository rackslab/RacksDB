<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { useRacksDBAPI } from '@/composables/RacksDBAPI'
import { ref, onMounted } from 'vue'
import SearchBar from '@/components/SearchBar.vue'
import type { Ref } from 'vue'
import type { Datacenter } from '@/composables/RacksDBAPI'
import BreadCrumbs from '@/components/BreadCrumbs.vue'

const http = useHttp()
const racksDBAPI = useRacksDBAPI(http)
const datacenters: Ref<Array<Datacenter>> = ref([])

async function getDatacenters() {
  datacenters.value = await racksDBAPI.datacenters()
}

onMounted(() => {
  getDatacenters()
})
</script>

<template>
  <BreadCrumbs />

  <SearchBar
    v-if="datacenters.length"
    viewTitle="Datacenter View"
    searchedItem="datacenter"
    :items="datacenters"
  />

  <!-- map code will be here -->
</template>
