<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { ref, onMounted } from 'vue'
import SearchBar from '@/components/SearchBar.vue'
import type { Ref } from 'vue'
import type { Infrastructure } from '@/composables/RacksDBAPI'

const infrastructures: Ref<Array<Infrastructure>> = ref([])
const http = useHttp()

async function getInfrastructure() {
  try {
    const resp = await http.get('infrastructures')
    infrastructures.value = resp.data as Infrastructure[]
  } catch (error) {
    console.error('Error during infrastructures data recovery', error)
  }
}

onMounted(() => {
  getInfrastructure()
})
</script>

<template>
  <SearchBar
    v-if="infrastructures.length"
    viewTitle="Infrastructure View"
    searchedItem="infrastructure"
    :items="infrastructures"
  />
</template>
