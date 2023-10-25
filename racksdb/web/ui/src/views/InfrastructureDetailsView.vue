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

var showContentRack = ref(false)
var text = ref()
var rackDetails: Ref<Array<Infrastructure>> = ref([])


function showRack(rack: string){
    showContentRack.value = true
    text.value= rack


    for (let index = 0; index < infrastructureDetails.value.length; index++) {
        const element = infrastructureDetails.value[index];
        for (let y = 0; y < infrastructureDetails.value[index].layout.length; y++) {
            const element = infrastructureDetails.value[index].layout[y].rack;
            console.log(element)    
        }
        
    }


    //console.log(rackDetails.value)

}


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
        <div class="flex justify-center" v-for="infrastructure in infrastructures" :key="infrastructure.name">
            <div v-for="rack in infrastructure.layout" :key="rack.rack">
                <button @click="showRack(rack.rack)" type="button" class="py-2.5 px-5 mr-2 mb-2 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700">
                    {{rack.rack}}</button>
            </div>
        </div>

        <div v-show="showContentRack">
            {{ text }}
            <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
                <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                    <tr>
                        <th scope="col" class="px-6 py-3">Name</th>
                        <th scope="col" class="px-6 py-3">Equipment</th>
                        <th scope="col" class="px-6 py-3">ID</th>
                    </tr>
                </thead>

                <tbody>
                    <tr>
                        <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">Un nom</th>
                        <td class="px-6 py-4">un equipement</td>
                        <td class="px-6 py-4">un ID</td>
                    </tr>
                </tbody>
            </table>

        </div>

    </div>

</template>