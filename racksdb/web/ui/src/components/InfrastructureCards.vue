<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import InfrastructureContentCard from './InfrastructureContentCard.vue'
import type { PropType } from 'vue'
import type { Infrastructure } from '@/composables/RacksDBAPI'

const props = defineProps({
  cardTitle: String,
  searchItem: String,
  infrastructure: {
    type: Object as PropType<Infrastructure>,
    required: true
  }
})
</script>

<template>
  <div v-for="rack in props.infrastructure.layout" :key="rack.rack">
    <div v-if="searchItem === 'nodes'" class="flex flex-wrap justify-center">
      <div v-for="item in rack.nodes" :key="item.name">
        <InfrastructureContentCard
          :rack="item.rack"
          equipment="nodes"
          :name="item.name"
          :id="item.type.id"
          :infrastructure="props.infrastructure"
        />
      </div>
    </div>

    <div v-else-if="searchItem === 'storage'" class="flex flex-wrap justify-center">
      <div v-for="item in rack.storage" :key="item.name">
        <InfrastructureContentCard
          :rack="item.rack"
          equipment="storage"
          :name="item.name"
          :id="item.type.id"
          :infrastructure="props.infrastructure"
        />
      </div>
    </div>

    <div v-else class="flex flex-wrap justify-center">
      <div v-for="item in rack.network" :key="item.name">
        <InfrastructureContentCard
          :rack="item.rack"
          equipment="network"
          :name="item.name"
          :id="item.type.id"
          :infrastructure="props.infrastructure"
        />
      </div>
    </div>
  </div>
</template>
