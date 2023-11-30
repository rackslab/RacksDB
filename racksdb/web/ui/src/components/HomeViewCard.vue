<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import type { Datacenter } from '@/composables/RacksDBAPI'
import type { Infrastructure } from '@/composables/RacksDBAPI'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  route: {
    type: String,
    required: true
  },
  nbItem: {
    type: Number,
    required: true
  },
  datacentersArray: {
    type: Array<Datacenter>,
    default() {
      return []
    }
  },
  infrastructuresArray: {
    type: Array<Infrastructure>,
    default() {
      return []
    }
  }
})
</script>

<template>
  <div class="cards flex justify-around pt-32 px-32">
    <div
      class="w-full max-w-sm p-4 bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700"
    >
      <div v-if="$props.title == 'infrastructure'">
        <router-link :to="route">
          <h2 class="text-2xl font-semibold flex justify-center text-purple-700 capitalize">
            {{ props.title }}
            <span v-if="nbItem > 1" class="lowercase">s</span>
          </h2>
        </router-link>

        <ul
          role="list"
          class="space-y-5 my-7"
          v-for="infrastrucutre in infrastructuresArray"
          :key="infrastrucutre.name"
        >
          <li class="flex space-x-3 items-center">
            <router-link
              :to="{ name: props.title + 'details', params: { name: infrastrucutre.name } }"
            >
              <span
                class="text-base font-normal leading-tight dark:text-gray-400 capitalize text-purple-700"
                >{{ infrastrucutre.name }},</span
              >
            </router-link>
            <span class="lowercase italic text-gray-500"> {{ infrastrucutre.description }} </span>
          </li>
        </ul>
      </div>

      <div v-if="$props.title == 'datacenter'">
        <router-link :to="route">
          <h2 class="text-2xl font-semibold flex justify-center text-purple-700 capitalize">
            {{ props.title }}
            <span v-if="nbItem > 1" class="lowercase">s</span>
          </h2>
        </router-link>

        <ul
          role="list"
          class="space-y-5 my-7"
          v-for="datacenter in datacentersArray"
          :key="datacenter.name"
        >
          <li class="flex space-x-3 items-center">
            <router-link :to="{ name: props.title + 'details', params: { name: datacenter.name } }">
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
  </div>
</template>
