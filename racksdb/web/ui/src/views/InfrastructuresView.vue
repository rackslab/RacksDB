<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { ref, onMounted } from 'vue'
import SearchBar from '@/components/SearchBar.vue'
import type { Ref } from 'vue'

const infrastructures: Ref<Array<Infrastructure>> = ref([])
const http = useHttp()

async function getInfrastructure() {
  try {
    const resp = await http.get('infrastructures')
    infrastructures.value = resp.data as Infrastructure[]
  } catch (error) {
    console.error('Error during infrastructure data recovery', error)
  }
}

onMounted(() => {
  getInfrastructure()
})

export interface Infrastructure {
  name: string
  description: string
  layout: [
    {
      rack: string
      nodes: [NodeEquipment]
      network: [NetworkEquipment]
      storage: [StorageEquipment]
    }
  ]
}

export interface NodeEquipment {
  type: {
    id: string
    model: string
    height: number
    width: number
    specs: string
    cpu: {
      sockets: number
      model: string
      specs: string
      cores: number
    }
    ram: {
      dimm: number
      size: number
    }
    storage: [
      {
        type: string
        model: string
        size: number
      }
    ]
    netifs: [
      {
        type: string
        bandwidth: number
      }
    ]
  }
  rack: string
  name: string
  slot: number
}

export interface NetworkEquipment {
  type: {
    id: string
    model: string
    height: number
    width: number
    netifs: [
      {
        type: string
        bandwidth: number
        number: number
      }
    ]
  }
  tags: []
  rack: string
  name: string
  slot: number
}

export interface StorageEquipment {
  type: {
    id: string
    model: string
    height: number
    width: number
    disks: [
      {
        type: string
        size: number
        model: string
        number: number
      }
    ]
  }
  tags: []
  rack: string
  name: string
  slot: number
}
</script>

<template>
  <SearchBar
    v-if="infrastructures.length"
    viewTitle="Infrastructure View"
    searchedItem="infrastructure"
    :items="infrastructures"
  />
</template>
