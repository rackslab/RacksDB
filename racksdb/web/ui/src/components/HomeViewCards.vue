<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { useRacksDBAPI } from '@/composables/RacksDBAPI'
import { ref, onMounted } from 'vue'
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
  <div class="cards flex justify-around pt-32 px-32">
    <div
      class="w-full max-w-sm p-4 bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700"
    >
      <router-link to="datacenters">
        <h2 class="text-2xl font-semibold flex justify-center text-purple-700 capitalize">
          {{ datacenters.length }} datacenter
          <span v-if="datacenters.length > 1" class="lowercase">s</span>
        </h2>
      </router-link>

      <ul
        role="list"
        class="space-y-5 my-7"
        v-for="datacenter in datacenters"
        :key="datacenter.name"
      >
        <li class="flex space-x-3 items-center">
          <router-link :to="{ name: 'datacenterdetails', params: { name: datacenter.name } }">
            <span
              class="text-base font-normal leading-tight dark:text-gray-400 capitalize text-purple-700"
              >{{ datacenter.name }},</span
            >
          </router-link>
          <span class="lowercase italic text-gray-500"> {{ datacenter.tags.join(', ') }} </span>
        </li>
      </ul>
    </div>
  </div>

  <div class="cards flex justify-around pt-32 px-32">
    <div
      class="w-full max-w-sm p-4 bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700"
    >
      <router-link to="infrastructures">
        <h2 class="text-2xl font-semibold flex justify-center text-purple-700 capitalize">
          {{ infrastructures.length }} infrastructure
          <span v-if="infrastructures.length > 1" class="lowercase">s</span>
        </h2>
      </router-link>

      <ul
        role="list"
        class="space-y-5 my-7"
        v-for="infrastructure in infrastructures"
        :key="infrastructure.name"
      >
        <li class="flex space-x-3 items-center">
          <router-link
            :to="{ name: 'infrastructuredetails', params: { name: infrastructure.name } }"
          >
            <span
              class="text-base font-normal leading-tight dark:text-gray-400 capitalize text-purple-700"
              >{{ infrastructure.name }},</span
            >
          </router-link>
          <span class="lowercase italic text-gray-500"> {{ infrastructure.description }} </span>
        </li>
      </ul>
    </div>
  </div>
</template>
