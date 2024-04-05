<!--Copyright (c) 2022-2024 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
const props = defineProps({
  infrastructures: {
    type: Array<string>,
    default: []
  }
})
</script>

<template>
  <template v-if="props.infrastructures.length > 0">
    <router-link
      v-for="(infrastructure, index) in props.infrastructures"
      :key="infrastructure"
      :to="{ name: 'infrastructuredetails', params: { name: infrastructure } }"
      class="font-bold hover:text-purple-700 capitalize"
    >
      {{ infrastructure }}
      <span v-if="index < props.infrastructures.length - 1">, </span>
    </router-link>
  </template>
  <template v-else>
    <span>-</span>
  </template>
</template>
