<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()

function isRouteActive(name: String) {
  return route.meta.entry == name
}
</script>

<template>
  <header class="flex justify-between items-center p-4 px-20">
    <div>
      <router-link :to="{ name: 'home' }"
        ><img alt="Rackslab logo" src="/assets/racksdb_logo.svg" class="h-32 w-32"
      /></router-link>
    </div>

    <nav class="space-x-4">
      <router-link :to="{ name: 'home' }">
        <span :class="[ isRouteActive('home') && 'text-purple-700 font-medium']">Home</span>
      </router-link>

      <router-link :to="{ name: 'datacenters' }">
        <span :class="[ isRouteActive('datacenters') && 'text-purple-700 font-medium']">Datacenters</span>
      </router-link>

      <router-link :to="{ name: 'infrastructures' }">
        <span :class="[ isRouteActive('infrastructures') && 'text-purple-700 font-medium']">Infrastructures</span>

      </router-link>
    </nav>
  </header>
</template>
