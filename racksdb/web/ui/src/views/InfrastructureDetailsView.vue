<script setup lang="ts">
import { useHttp } from '@/plugins/http';
import { ref, onMounted } from 'vue'
import type { Ref } from 'vue'
import SearchBarView from '@/components/SearchBarView.vue';
import InfrastructureCards from '@/components/InfrastructureCards.vue';

const http = useHttp()
var infrastructures: Ref<Array<Infrastructure>> = ref([])
var infrastructureDetails: Ref<Array<Infrastructure>> = ref([])


async function getInfrastructure(){
    try {
        const resp = await http.get('infrastructures')
        infrastructures.value = resp.data as Infrastructure[]
        infrastructureDetails.value = infrastructures.value.filter((infrastructure) => infrastructure.name === props.name)
    } catch (error) {
        console.error('Error during infrastructure data recovery', error)
    }
}

onMounted(() => {
    getInfrastructure()
})

export interface Infrastructure {
  name: string
  layout: [{
    rack: string

    nodes: [{
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
                dim: number
                size: number
            }
            storage: [{
                type: string
                model: string
                size: number
            }]
            netifs: [{
                type: string
                bandwidth: number
            }]
        }
        rack: string
        name: string
        slot: number
    }]

    network: [{
        type: {
            id: string
            model: string
            height: number
            width: number
            netifs:[{
                type: string
                bandwidth: number
                number: number

            }]
        }
        tags: []
        rack: string
        name: string
        slot: number
    }]

    storage: [{
        type: {
            id: string
            model: string
            height: number
            width: number
            disks: [{
                type: string
                size: number
                model: string
                number: number
            }]
        }
        tags: []
        rack: string
        name: string
        slot: number

    }]

}]
}

const props = defineProps({
    name: String
})
</script>

<template>
    <SearchBarView 
    v-if="infrastructures.length"
        viewTitle="Infrastructure Details"    
        searchedItem="infrastructure" 
        :items="infrastructures"
    />

    <h2 class="text-3xl font-medium flex justify-center capitalize py-16">{{ name }} Infrastructure</h2>

    <InfrastructureCards v-if="infrastructures.length" :items="infrastructures" searchItem="nodes" />
    <InfrastructureCards v-if="infrastructures.length" :items="infrastructures" searchItem="storage" />
    <InfrastructureCards v-if="infrastructures.length" :items="infrastructures" searchItem="network" />


</template>