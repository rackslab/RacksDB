<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT -->

<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { useRacksDBAPI } from '@/composables/RacksDBAPI'
import { ref, onMounted } from 'vue'
import type { Ref } from 'vue'
import type { Infrastructure } from '@/composables/RacksDBAPI'
import BreadCrumbs from '@/components/BreadCrumbs.vue'
import ComboBox from '@/components/ComboBox.vue'

const http = useHttp()
const racksDBAPI = useRacksDBAPI(http)
const infrastructures: Ref<Array<Infrastructure>> = ref([])

async function getInfrastructures() {
  infrastructures.value = await racksDBAPI.infrastructures()
}

onMounted(() => {
  getInfrastructures()
})
</script>

<template>
  <BreadCrumbs />

  <ComboBox itemType="infrastructure" :items="infrastructures" />
</template>
