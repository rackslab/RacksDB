<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Ref } from 'vue'

const input = ref('')
const matchingItems: Ref<Array<Item>> = ref([])

// This function filters items by name based on the user input value
function search() {
  matchingItems.value = props.items.filter((item) => item.name.includes(input.value))
}

// Use the hook onMounted to insert data from the prop in a variabe when the component is initialized
onMounted(() => {
  matchingItems.value = props.items
})

export interface Item {
  name: string
}

const props = defineProps({
  searchedItem: String,
  viewTitle: String,
  items: {
    type: Array<Item>,
    default() {
      return []
    }
  }
})
</script>

<template>
  <div>
    <h1 class="text-5xl font-medium flex justify-center py-20">{{ viewTitle }}</h1>
    <div class="mx-60">
      <label for="search" class="mb-2 text-sm font-medium text-gray-900 sr-only dark:text-white"
        >Search</label
      >
      <div class="relative">
        <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
          <svg
            class="w-4 h-4 text-gray-500 dark:text-gray-400"
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 20 20"
          >
            <path
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"
            />
          </svg>
        </div>
        <input
          type="text"
          id="myInput"
          v-model="input"
          v-on:keyup="search()"
          class="block w-full p-4 pl-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          :placeholder="`Search a ${viewTitle}`"
          required
        />
        <button
          type="submit"
          class="text-white absolute right-2.5 bottom-2.5 bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-4 py-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
        >
          Search
        </button>
      </div>
    </div>

    <ul id="myUL" v-for="item in matchingItems" :key="item.name" class="flex justify-center">
      <router-link :to="{ name: searchedItem + 'details', params: { name: item.name } }">
        <li class="capitalize">{{ item.name }}</li>
      </router-link>
    </ul>
  </div>
</template>
