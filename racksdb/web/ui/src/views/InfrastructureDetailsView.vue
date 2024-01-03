<!--Copyright (c) 2022-2024 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { useRacksDBAPI } from '@/composables/RacksDBAPI'
import { ref, onMounted, watch } from 'vue'
import InfrastructureTable from '@/components/InfrastructureTable.vue'
import type { Ref } from 'vue'
import type { Infrastructure } from '@/composables/RacksDBAPI'
import { Dialog, DialogPanel } from '@headlessui/vue'
import BreadCrumbs from '@/components/BreadCrumbs.vue'

const http = useHttp()
const racksDBAPI = useRacksDBAPI(http)
const infrastructureDetails: Ref<Infrastructure | undefined> = ref()
const blobURL = ref()
const showImg = ref(false)

function toggleImageModal() {
  if (showImg.value) {
    showImg.value = false
  } else {
    showImg.value = true
  }
}

async function getInfrastructureImg() {
  try {
    const myBlob = await racksDBAPI.infrastructureImageSvg(props.name)
    blobURL.value = URL.createObjectURL(myBlob)
  } catch (error) {
    console.error(`Error getting ${props.name}: ` + error)
  }
}

async function getInfrastructures() {
  infrastructureDetails.value = (await racksDBAPI.infrastructures()).filter(
    (infrastructure) => infrastructure.name === props.name
  )[0]
}

onMounted(() => {
  getInfrastructures()
  getInfrastructureImg()
})

// Using watch to trigger getDatacenter() when the value of props.name change
watch(
  () => props.name,
  () => {
    getInfrastructures()
    getInfrastructureImg()
  }
)

const props = defineProps({
  name: {
    type: String,
    required: true
  }
})
</script>

<template>
  <BreadCrumbs :infrastructureName="props.name" />
  <div class="pb-10">
    <img
      v-if="blobURL"
      @click="toggleImageModal()"
      :src="blobURL"
      class="h-96 max-w-500 mx-auto p-10 border-2 border-gray-100 border-opacity-10 transition-transform transform duration-300 hover:scale-105 hover:border-purple-50 cursor-pointer shadow-2xl"
      :alt="`Small image of the infrastructure ${props.name}`"
    />
  </div>

  <Dialog
    :open="showImg"
    @close="toggleImageModal"
    class="fixed top-0 left-0 flex flex-col items-center justify-center w-screen h-screen bg-gray-300 bg-opacity-50 dark:bg-gray-900 dark:bg-opacity-50 backdrop-blur-md z-50"
  >
    <DialogPanel
      class="h-[90vh] flex flex-col items-center justify-center max-w-4xl bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700"
    >
      <img
        v-if="blobURL"
        :src="blobURL"
        class="h-full max-w-full border border-gray-300"
        :alt="`Big image of the infrastructure ${props.name}`"
      />

      <div class="pt-5">
        <button
          type="button"
          @click="toggleImageModal"
          class="py-2.5 px-5 text-sm font-medium text-white focus:outline-none bg-purple-700 rounded-lg border"
        >
          close
        </button>
      </div>
    </DialogPanel>
  </Dialog>

  <div class="pb-10">
    <InfrastructureTable
      v-if="infrastructureDetails"
      :infrastructureDetails="infrastructureDetails"
    />
  </div>
</template>
