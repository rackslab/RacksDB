<!--Copyright (c) 2022-2024 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Combobox,
  ComboboxInput,
  ComboboxOption,
  ComboboxOptions,
  ComboboxLabel,
  ComboboxButton,
  Dialog,
  DialogPanel,
  TransitionChild,
  TransitionRoot
} from '@headlessui/vue'
import { XMarkIcon, ChevronUpDownIcon, CheckIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  showSlider: Boolean,
  racks: {
    type: Array<string>,
    required: true
  },
  equipmentCategories: {
    type: Array<string>,
    required: true
  },
  equipmentTypes: {
    type: Array<string>,
    required: true
  },
  tags: {
    type: Array<string>,
    required: true
  }
})

defineEmits(['toggleSlider'])
const selectedRacks = defineModel<Array<string>>('selectedRacks', { required: true })
const selectedEquipmentTypes = defineModel<Array<string>>('selectedEquipmentTypes', {
  required: true
})
const selectedCategories = defineModel<Array<string>>('selectedCategories')
const selectedTags = defineModel<Array<string>>('selectedTags')
const inputEquipmentName = defineModel<string>('inputEquipmentName')
const queryRacks = ref('')
const queryEquipmentTypes = ref('')
const filteredRacks = computed(() =>
  queryRacks.value === ''
    ? props.racks
    : props.racks.filter((rack) =>
        rack
          .toLowerCase()
          .replace(/\s+/g, '')
          .includes(queryRacks.value.toLowerCase().replace(/\s+/g, ''))
      )
)
const filteredEquipmentTypes = computed(() =>
  queryEquipmentTypes.value === ''
    ? props.equipmentTypes
    : props.equipmentTypes.filter((equipmentType) =>
        equipmentType
          .toLowerCase()
          .replace(/\s+/g, '')
          .includes(queryEquipmentTypes.value.toLowerCase().replace(/\s+/g, ''))
      )
)
</script>

<template>
  <TransitionRoot as="template" :show="showSlider">
    <Dialog as="div" class="relative z-10" @close="$emit('toggleSlider')">
      <TransitionChild
        as="template"
        enter="ease-in-out duration-500"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in-out duration-500"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-hidden">
        <div class="absolute inset-0 overflow-hidden">
          <div class="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
            <TransitionChild
              as="template"
              enter="transform transition ease-in-out duration-500 sm:duration-700"
              enter-from="translate-x-full"
              enter-to="translate-x-0"
              leave="transform transition ease-in-out duration-500 sm:duration-700"
              leave-from="translate-x-0"
              leave-to="translate-x-full"
            >
              <DialogPanel class="pointer-events-auto relative w-screen max-w-md">
                <TransitionChild
                  as="template"
                  enter="ease-in-out duration-500"
                  enter-from="opacity-0"
                  enter-to="opacity-100"
                  leave="ease-in-out duration-500"
                  leave-from="opacity-100"
                  leave-to="opacity-0"
                >
                  <div class="absolute left-0 top-0 -ml-8 flex pr-2 pt-4 sm:-ml-10 sm:pr-4">
                    <button
                      type="button"
                      class="relative rounded-md text-gray-300 hover:text-white focus:outline-none focus:ring-2 focus:ring-white"
                      @close="$emit('toggleSlider')"
                    >
                      <span @click="$emit('toggleSlider')" class="absolute -inset-2.5" />
                      <span class="sr-only">Close panel</span>
                      <XMarkIcon class="h-6 w-6" />
                    </button>
                  </div>
                </TransitionChild>
                <div class="flex h-full flex-col overflow-y-scroll bg-white py-6 shadow-xl">
                  <div class="relative flex-1 px-4 sm:px-6">
                    <!-- Racks -->
                    <Combobox as="div" v-model="selectedRacks" multiple class="px-4 py-6">
                      <ComboboxLabel class="text-xl flex items-center"
                        ><span
                          class="w-3 h-3 bg-orange-700 rounded-full mr-2"
                        />Racks</ComboboxLabel
                      >

                      <div
                        class="pt-3 relative w-full cursor-default rounded-lg bg-white text-left shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-white/75 focus-visible:ring-offset-2 focus-visible:ring-offset-teal-300 sm:text-sm"
                      >
                        <ComboboxInput
                          class="w-96 capitalize focus:border-purple-700 focus:outline-none border-2 border-solid rounded-md bg-white py-1.5 pl-3 pr-10 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-purple-600 sm:text-sm sm:leading-6"
                          :placeholder="selectedRacks.join(', ')"
                          @change="queryRacks = $event.target.value"
                        />
                        <ComboboxButton class="pt-3 absolute inset-y-0 right-0 flex items-center">
                          <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
                        </ComboboxButton>
                      </div>
                      <transition
                        enter-active-class="transition duration-100 ease-out"
                        enter-from-class="transform scale-95 opacity-0"
                        enter-to-class="transform scale-100 opacity-100"
                        leave-active-class="transition duration-75 ease-out"
                        leave-from-class="transform scale-100 opacity-100"
                        leave-to-class="transform scale-95 opacity-0"
                      >
                        <ComboboxOptions
                          class="w-96 mt-1 max-h-60 overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm"
                        >
                          <ComboboxOption
                            v-for="rack in filteredRacks"
                            :key="rack"
                            :value="rack"
                            v-slot="{ active, selected }"
                          >
                            <li
                              :class="[
                                'relative cursor-default select-none py-2 pl-3 pr-9',
                                active ? 'bg-purple-600 text-white' : 'text-gray-900'
                              ]"
                            >
                              <span
                                :class="['block truncate capitalize', selected && 'font-semibold']"
                              >
                                {{ rack }}
                              </span>

                              <span
                                v-if="selected"
                                :class="[
                                  'absolute inset-y-0 right-0 flex items-center pr-4',
                                  active ? 'text-white' : 'text-purple-600'
                                ]"
                              >
                                <CheckIcon class="h-5 w-5" aria-hidden="true" />
                              </span>
                            </li>
                          </ComboboxOption>
                        </ComboboxOptions>
                      </transition>
                    </Combobox>

                    <!-- Equipment category -->
                    <div class="px-4 flex flex-col">
                      <label for="equipment-category" class="text-xl pb-3 flex items-center"
                        ><span class="w-3 h-3 bg-yellow-500 rounded-full mr-2" />Equipment
                        category</label
                      >
                      <div
                        v-for="equipmentCategory in props.equipmentCategories"
                        :key="equipmentCategory"
                      >
                        <input
                          :id="`category-${equipmentCategory}`"
                          :name="`category-${equipmentCategory}`"
                          type="checkbox"
                          :value="equipmentCategory"
                          v-model="selectedCategories"
                          class="h-4 w-4 rounded border-gray-300 text-purple-700 focus:ring-purple-700"
                        />
                        <label :for="`category-${equipmentCategory}`" class="pl-2 capitalize">{{
                          equipmentCategory
                        }}</label>
                      </div>
                    </div>

                    <!-- Equipment types -->
                    <Combobox as="div" v-model="selectedEquipmentTypes" multiple class="px-4 pt-6">
                      <ComboboxLabel class="text-xl flex items-center"
                        ><span class="w-3 h-3 bg-green-700 rounded-full mr-2" />Equipment
                        Types</ComboboxLabel
                      >

                      <div
                        class="pt-3 relative w-full cursor-default rounded-lg bg-white text-left shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-white/75 focus-visible:ring-offset-2 focus-visible:ring-offset-teal-300 sm:text-sm"
                      >
                        <ComboboxInput
                          class="w-96 capitalize focus:border-purple-700 focus:outline-none border-2 border-solid rounded-md bg-white py-1.5 pl-3 pr-10 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-purple-600 sm:text-sm sm:leading-6"
                          :placeholder="selectedEquipmentTypes.join(', ')"
                          @change="queryEquipmentTypes = $event.target.value"
                        />
                        <ComboboxButton class="pt-3 absolute inset-y-0 right-0 flex items-center">
                          <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
                        </ComboboxButton>
                      </div>
                      <transition
                        enter-active-class="transition duration-100 ease-out"
                        enter-from-class="transform scale-95 opacity-0"
                        enter-to-class="transform scale-100 opacity-100"
                        leave-active-class="transition duration-75 ease-out"
                        leave-from-class="transform scale-100 opacity-100"
                        leave-to-class="transform scale-95 opacity-0"
                      >
                        <ComboboxOptions
                          class="w-96 mt-1 max-h-60 overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm"
                        >
                          <ComboboxOption
                            v-for="equipment in filteredEquipmentTypes"
                            :key="equipment"
                            :value="equipment"
                            v-slot="{ active, selected }"
                          >
                            <li
                              :class="[
                                'relative cursor-default select-none py-2 pl-3 pr-9',
                                active ? 'bg-purple-600 text-white' : 'text-gray-900'
                              ]"
                            >
                              <span
                                :class="['block truncate capitalize', selected && 'font-semibold']"
                              >
                                {{ equipment }}
                              </span>

                              <span
                                v-if="selected"
                                :class="[
                                  'absolute inset-y-0 right-0 flex items-center pr-4',
                                  active ? 'text-white' : 'text-purple-600'
                                ]"
                              >
                                <CheckIcon class="h-5 w-5" aria-hidden="true" />
                              </span>
                            </li>
                          </ComboboxOption>
                        </ComboboxOptions>
                      </transition>
                    </Combobox>

                    <!-- Tags -->
                    <div class="px-4 pt-6 flex flex-col">
                      <label for="tags" class="text-xl pb-3 flex items-center"
                        ><span class="w-3 h-3 bg-purple-700 rounded-full mr-2" />Tags</label
                      >
                      <div v-for="tag in props.tags" :key="tag">
                        <input
                          :id="tag"
                          :name="tag"
                          type="checkbox"
                          :value="tag"
                          v-model="selectedTags"
                          class="h-4 w-4 rounded border-gray-300 text-purple-700 focus:ring-purple-700"
                        />
                        <label :for="tag" class="pl-2 capitalize">{{ tag }}</label>
                      </div>
                    </div>

                    <!-- Equipment name -->
                    <div class="px-4 pt-6 flex flex-col">
                      <label for="equipment-name" class="text-xl pb-3 flex items-center"
                        ><span class="w-3 h-3 bg-blue-700 rounded-full mr-2" />Equipment name</label
                      >
                      <input
                        type="text"
                        v-model="inputEquipmentName"
                        class="w-96 rounded-md focus:border-purple-700 focus:outline-none border-2 border-solid bg-white py-1.5 pl-3 pr-10 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 sm:text-sm sm:leading-6"
                        placeholder="Filter by equipment name"
                        required
                      />
                    </div>
                  </div>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>
