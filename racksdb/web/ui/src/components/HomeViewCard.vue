<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
defineProps({
  title: {
    type: String,
    required: true
  },
  route: {
    type: String,
    required: true
  },
  body: {
    type: String,
    required: true
  },
  complement: {
    type: String,
    required: true
  },
  array: {
    type: Array,
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
      <router-link :to="route">
        <h2 class="text-2xl font-semibold flex justify-center text-purple-700 capitalize">
          {{ title }}
          <span v-if="array.length > 1" class="lowercase">s</span>
        </h2>
      </router-link>

      <ul role="list" class="space-y-5 my-7">
        <li class="flex space-x-3 items-center">
          <router-link :to="{ name: title + 'details', params: { name: body } }">
            <span
              class="text-base font-normal leading-tight dark:text-gray-400 capitalize text-purple-700"
              >{{ body }},</span
            >
          </router-link>
          <span class="lowercase italic text-gray-500"> {{ complement }} </span>
        </li>
      </ul>
    </div>
  </div>
</template>
