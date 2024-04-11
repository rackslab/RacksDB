<!--Copyright (c) 2022-2024 Rackslab

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
  <div class="w-full flex justify-center">
    <div
      class="flex flex-col w-[800px] min-h-[500px] bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700 mr-10"
    >
      <div class="flex justify-center">
        <router-link to="datacenters">
          <h2
            class="text-2xl font-semibold flex justify-center text-purple-700 hover:text-purple-500 capitalize"
          >
            {{ datacenters.length }} datacenter
            <span v-if="datacenters.length > 1" class="lowercase">s</span>
          </h2>
        </router-link>
      </div>

      <div class="pt-10">
        <div class="my-7" v-for="datacenter in datacenters" :key="datacenter.name">
          <router-link :to="{ name: 'datacenterdetails', params: { name: datacenter.name } }">
            <span
              class="text-base font-normal leading-tight dark:text-gray-400 capitalize text-purple-700 hover:font-medium"
              >{{ datacenter.name }}</span
            >
          </router-link>

          <div class="flex justify-between">
            <span v-if="datacenter.rooms.length > 1">{{ datacenter.rooms.length }} rooms</span>
            <span v-else>{{ datacenter.rooms.length }} room</span>

            <div class="flex justify-end">
              <div v-for="tag in datacenter.tags" :key="tag" class="px-1">
                <span class="p-2 bg-purple-700 rounded-md text-white">#{{ tag }}</span>
              </div>
            </div>
          </div>
          <div class="pt-5">
            <hr />
          </div>
        </div>
      </div>
    </div>

    <div
      class="flex flex-col w-[800px] min-h-[500px] bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700 ml-10"
    >
      <div class="flex justify-center">
        <router-link to="infrastructures">
          <h2
            class="text-2xl font-semibold flex justify-center text-purple-700 hover:text-purple-500 capitalize"
          >
            {{ infrastructures.length }} infrastructure
            <span v-if="infrastructures.length > 1" class="lowercase">s</span>
          </h2>
        </router-link>
      </div>

      <div class="pt-10">
        <div class="my-7" v-for="infrastructure in infrastructures" :key="infrastructure.name">
          <router-link
            :to="{ name: 'infrastructuredetails', params: { name: infrastructure.name } }"
          >
            <span
              class="text-base font-normal leading-tight dark:text-gray-400 capitalize text-purple-700 hover:font-medium"
              >{{ infrastructure.name }}</span
            >
          </router-link>

          <div class="flex justify-between">
            <span class="lowercase"> {{ infrastructure.description }} </span>

            <div class="flex justify-end">
              <div v-for="tag in infrastructure.tags" :key="tag" class="px-1">
                <span class="p-2 bg-purple-700 rounded-md text-white">#{{ tag }}</span>
              </div>
            </div>
          </div>
          <div class="pt-4">
            <hr />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
