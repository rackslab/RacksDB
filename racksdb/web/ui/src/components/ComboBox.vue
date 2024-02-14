<!--Copyright (c) 2022-2024 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { ref, computed, watchEffect, onMounted } from 'vue'
import type { PropType } from 'vue'
import type { Ref } from 'vue'
import { useRouter } from 'vue-router'
import type { Datacenter, Infrastructure } from '@/composables/RacksDBAPI'
import {
  Combobox,
  ComboboxInput,
  ComboboxOption,
  ComboboxOptions,
  ComboboxLabel
} from '@headlessui/vue'
import { CheckIcon } from '@heroicons/vue/24/outline'

const selectedItem: Ref<string | undefined> = ref()
const router = useRouter()
const input = ref('')
const inputComponent: Ref<typeof ComboboxInput | null> = ref(null)
const filteredItems = computed(() =>
  input.value === ''
    ? props.items
    : props.items.filter((item) => {
        return item.name.toLocaleLowerCase().includes(input.value.toLocaleLowerCase())
      })
)

function goToItem(item: string) {
  router.push({
    name: props.itemType + 'details',
    params: { name: item }
  })
}

const props = defineProps({
  itemType: {
    type: String as PropType<'datacenter' | 'infrastructure'>,
    required: true
  },
  items: {
    type: Array<Datacenter | Infrastructure>,
    default: []
  }
})

/*
 * Watch selected item in combobox to redirect to item view as soon as user
 * selects an entry in the list.
 */
watchEffect(() => {
  if (selectedItem.value) {
    goToItem(selectedItem.value)
  }
})

onMounted(() => {
  /*
   * Give focus to ComboboxInputElement when component is loaded.
   *
   * This is not stated in Headless UI documentation but ComboboxInput
   * component exposes an el attribute which is a ref on the child input
   * HTML element. This can be use to set focus on this element.
   */
  inputComponent.value?.el.focus()
})
</script>

<template>
  <div class="flex justify-center items-center pt-10">
    <Combobox as="div" v-model="selectedItem" class="p-4 px-20">
      <div class="relative mt-2">
        <div class="flex flex-col">
          <ComboboxLabel class="flex justify-center text-3xl pb-4">
            <span
              >Select
              {{ itemType == 'infrastructure' ? 'an': 'a' }}
              {{ itemType }}</span
            >
          </ComboboxLabel>
          <ComboboxInput
            ref="inputComponent"
            class="w-96 focus:border-purple-700 focus:outline-none border-2 border-solid rounded-md bg-white py-1.5 pl-3 pr-10 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-purple-600 sm:text-sm sm:leading-6"
            :placeholder="`Type to filter the list of ${itemType}s`"
            @change="input = $event.target.value"
          />
        </div>

        <ComboboxOptions
          static
          v-if="filteredItems.length > 0"
          class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm"
        >
          <ComboboxOption
            v-for="item in filteredItems"
            :key="item.name"
            :value="item.name"
            v-slot="{ active, selected }"
          >
            <li
              :class="[
                'relative cursor-default select-none py-2 pl-3 pr-9',
                active ? 'bg-purple-600 text-white' : 'text-gray-900'
              ]"
              @click="goToItem(item.name)"
            >
              <span :class="['block truncate capitalize', selected && 'font-semibold']">
                {{ item.name }}
              </span>

              <span
                v-if="selected"
                :class="[
                  'absolute inset-y-0 right-0 flex items-center pr-4',
                  active ? 'text-white' : 'text-indigo-600'
                ]"
              >
                <CheckIcon class="h-5 w-5" aria-hidden="true" />
              </span>
            </li>
          </ComboboxOption>
        </ComboboxOptions>
      </div>
    </Combobox>
  </div>
</template>
