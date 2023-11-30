<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { ref, onMounted } from 'vue'
import SearchBar from '@/components/SearchBar.vue'
import type { Ref } from 'vue'
import type { Datacenter } from '@/composables/RacksDBAPI'

const datacenters: Ref<Array<Datacenter>> = ref([])
const http = useHttp()

async function getDatacenters() {
  try {
    const resp = await http.get('datacenters')
    datacenters.value = resp.data as Datacenter[]
  } catch (error) {
    console.error('Error during datacenters data recovery', error)
  }
}

onMounted(() => {
  getDatacenters()
})

</script>

<template>
  <SearchBar
    v-if="datacenters.length"
    viewTitle="Datacenter View"
    searchedItem="datacenter"
    :items="datacenters"
  />

  <!-- map code will be here -->
</template>
