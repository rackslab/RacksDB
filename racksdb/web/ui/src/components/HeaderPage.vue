<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { RouterLink, RouterView, useRouter } from 'vue-router'

const router = useRouter()

function isRouteActive(routePath: string) {
  return router.currentRoute.value.path === routePath
}

function isDatacentersRouteActive() {
  return router.currentRoute.value.path.startsWith('/datacenters')
}

function isInfrastructuresRouteActive() {
  return router.currentRoute.value.path.startsWith('/infrastructures')
}
</script>

<template>
  <header class="flex justify-between items-center p-4 px-20">
    <div>
      <router-link to="/"
        ><img alt="Rackslab logo" src="/assets/racksdb_logo.svg" class="h-32 w-32"
      /></router-link>
    </div>

    <nav class="space-x-4">
      <router-link to="/">
        <span v-if="isRouteActive('/')" class="text-purple-700 font-medium">Home</span>
        <span v-else>Home</span>
      </router-link>

      <router-link to="/datacenters">
        <span v-if="isDatacentersRouteActive()" class="text-purple-700 font-medium"
          >Datacenters</span
        >
        <span v-else>Datacenters</span>
      </router-link>

      <router-link to="/infrastructures">
        <span v-if="isInfrastructuresRouteActive()" class="text-purple-700 font-medium"
          >Infrastructures</span
        >
        <span v-else>Infrastructures</span>
      </router-link>
    </nav>
  </header>
  <RouterView />
</template>
