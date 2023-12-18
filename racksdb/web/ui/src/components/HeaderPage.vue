<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

function isRouteActive(name: String) {
  return route.meta.entry == name
}
</script>

<template>
  <header class="flex justify-end items-center px-20 py-16 w-1/2 top-0 right-0 absolute">
    <nav class="space-x-4 pt-10">
      <router-link :to="{ name: 'home' }">
        <span :class="[isRouteActive('home') && 'text-purple-700 font-medium']">Home</span>
      </router-link>

      <router-link :to="{ name: 'datacenters' }">
        <span :class="[isRouteActive('datacenters') && 'text-purple-700 font-medium']"
          >Datacenters</span
        >
      </router-link>

      <router-link :to="{ name: 'infrastructures' }">
        <span :class="[isRouteActive('infrastructures') && 'text-purple-700 font-medium']"
          >Infrastructures</span
        >
      </router-link>
    </nav>
  </header>
</template>
