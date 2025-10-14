<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT -->

<script setup lang="ts">
import { ChevronRightIcon } from '@heroicons/vue/24/outline'
import { useRoute } from 'vue-router'

const route = useRoute()

const props = defineProps({
  infrastructureName: String,
  datacenterName: String,
  datacenterRoom: String
})
</script>

<template>
  <div class="flex items-center px-20 py-10">
    <router-link :to="{ name: 'home' }"
      ><img alt="Rackslab logo" src="/assets/racksdb_logo.png" class="h-32 w-32"
    /></router-link>

    <div v-if="route.meta.entry == 'datacenters'" class="flex items-center">
      <div class="px-5">
        <ChevronRightIcon class="h-4 w-4" />
      </div>
      <router-link :to="{ name: 'datacenters' }"
        ><span class="text-xl text-black hover:text-purple-700 hover:underline"
          >Datacenters</span
        ></router-link
      >

      <div v-if="route.name == 'datacenterdetails'" class="flex items-center">
        <div class="px-5">
          <ChevronRightIcon class="h-4 w-4" />
        </div>
        <router-link :to="{ name: 'datacenterdetails', params: { name: props.datacenterName } }"
          ><span class="capitalize text-xl text-black hover:text-purple-700 hover:underline">{{
            props.datacenterName
          }}</span></router-link
        >
      </div>

      <div v-if="route.name == 'datacenterroom'" class="flex items-center">
        <div class="px-5">
          <ChevronRightIcon class="h-4 w-4" />
        </div>
        <router-link :to="{ name: 'datacenterdetails', params: { name: props.datacenterName } }"
          ><span class="capitalize text-xl text-black hover:text-purple-700 hover:underline">{{
            props.datacenterName
          }}</span></router-link
        >
        <div class="px-5">
          <ChevronRightIcon class="h-4 w-4" />
        </div>

        <router-link :to="{ name: 'datacenterdetails', params: { name: props.datacenterRoom } }"
          ><span class="capitalize text-xl text-black hover:text-purple-700 hover:underline">{{
            props.datacenterRoom
          }}</span></router-link
        >
      </div>
    </div>

    <div v-if="route.meta.entry == 'infrastructures'" class="flex items-center">
      <div class="px-5">
        <ChevronRightIcon class="h-4 w-4" />
      </div>
      <router-link :to="{ name: 'infrastructures' }"
        ><span class="text-xl text-black hover:text-purple-700 hover:underline"
          >Infrastructures</span
        ></router-link
      >

      <div v-if="route.name == 'infrastructuredetails'" class="flex items-center">
        <div class="px-5">
          <ChevronRightIcon class="h-4 w-4" />
        </div>
        <router-link
          :to="{ name: 'infrastructuredetails', params: { name: props.infrastructureName } }"
          ><span class="capitalize text-xl text-black hover:text-purple-700 hover:underline">{{
            props.infrastructureName
          }}</span></router-link
        >
      </div>
    </div>
  </div>
</template>
