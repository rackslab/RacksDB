<script setup lang="ts">
import { useHttp } from '@/plugins/http';
import { ref, onMounted } from 'vue'
import type { Ref } from 'vue'
import SearchBarView from '@/components/SearchBarView.vue';
import InfrastructureCards from '@/components/InfrastructureCards.vue';

const http = useHttp()
var infrastructures: Ref<Array<Infrastructure>> = ref([])
var infrastructureDetails: Ref<Array<Infrastructure>> = ref([])
var cardsView = ref(true)
var tableView = ref(false)


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

function choseView(){
    if(cardsView.value){
        cardsView.value = !cardsView.value
        tableView.value = !tableView.value 
    }else{
        tableView.value = !tableView.value
        cardsView.value = !cardsView.value
    }
}

export interface Infrastructure {
  name: string
  layout: [{
    rack: string

    nodes: [NodeEquipment]

    network: [NetworkEquipment]

    storage: [StorageEquipment]

}]
}

export interface NodeEquipment{
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
    
}

export interface NetworkEquipment{
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

}

export interface StorageEquipment{
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
    
    <div class="flex justify-end mr-36">
        <img @click="choseView()" src="/assets/cards.svg" alt="">
        <img @click="choseView()" src="/assets/table.svg" alt="">

    </div>

    <div v-show="cardsView">
        <InfrastructureCards v-if="infrastructures.length" :items="infrastructures" searchItem="nodes" />
        <InfrastructureCards v-if="infrastructures.length" :items="infrastructures" searchItem="storage" />
        <InfrastructureCards v-if="infrastructures.length" :items="infrastructures" searchItem="network" />
    </div>

    <div v-show="tableView">
        <h1>hello</h1>
    </div>

</template>