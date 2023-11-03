<script setup lang="ts">
import { useHttp } from '@/plugins/http';
import { ref, onMounted, inject } from 'vue'
import SearchBar from '@/components/SearchBar.vue';
import { injectionKey } from '@/plugins/runtimeConfiguration';
import type { Ref } from 'vue'
import type { Datacenter } from './DatacentersView.vue';

const datacenters: Ref<Array<Datacenter>> = ref([])
const datacenterDetails: Ref<Datacenter | undefined> = ref()
const racks: Ref<Array<Rack>> = ref([])
const rackDetails: Ref<Array<Rack>> = ref([])
const showFullImg = ref(false)
const http = useHttp()

function openImg(){
    showFullImg.value = !showFullImg.value
}

function listInfrastructures(){
    var rack = rackDetails.value[0].nodes
    for (let index = 0; index < rack.length; index++) {
        return rack[index].infrastructure
    }
}

async function getRacks(){
    try {
        const resp = await http.get('racks')
        racks.value = resp.data as Rack[]
        rackDetails.value = racks.value.filter((rack) => rack.room === props.datacenterRoom)
        console.log(rackDetails.value)
    } catch (error) {
        console.error('Erreur lors de la récupératuon des données des datacenters', error)
    }
}

async function getDatacenters(){
    try {
        const resp = await http.get('datacenters')
        datacenters.value = resp.data as Datacenter[]
        datacenterDetails.value = datacenters.value.filter((datacenter) => datacenter.name === props.name)[0]
    } catch (error) {
        console.error('Erreur lors de la récupératuon des données des datacenters', error)
    }
}

onMounted(() => {
    getDatacenters()
    getRacks()
})

const props = defineProps({
    name: String,
    datacenterRoom: String,
})

interface Rack {
    room: String,
    name: String,
    nodes: [{
        infrastructure: String,
    }]
}
</script>

<template>

    <SearchBar 
        v-if="datacenters.length"
        viewTitle="Datacenter Room"    
        searchedItem="datacenter" 
        :items="datacenters"
    />

    <img :src="`${inject(injectionKey)!.api_server}/draw/room/${ props.datacenterRoom }.svg`" alt="" @click="openImg()" class="h-96 max-w-500 mx-auto p-10">
    
    <div v-show="showFullImg" class="fixed top-0 left-0 flex flex-col items-center justify-center w-screen h-screen bg-gray-300 bg-opacity-50 dark:bg-gray-900 dark:bg-opacity-50 backdrop-blur-md z-50">
        <img :src="`${inject(injectionKey)!.api_server}/draw/room/${ props.datacenterRoom }.svg`" alt="" @click="openImg()" class="h-screen max-w-full bg-white" >

    </div>
    
    <table v-if="datacenterDetails" class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
        <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
            <tr>
                <th scope="col" class="px-6 py-3">Name</th>
                <th scope="col" class="px-6 py-3">Fill rate</th>
                <th scope="col" class="px-6 py-3">List of infrastructures</th>
            </tr>
        </thead>

        <template v-for="room in datacenterDetails.rooms" :key="room">
            <template v-for="row in room.rows" :key="row">
                <template v-for="rack in row.racks" :key="rack">
                    <tbody>
                        <tr>
                            <td>{{ rack.name }}</td>
                            <td>{{ (rack.fillrate * 100).toFixed(0) }}%</td>
                            <td>{{ listInfrastructures()}}</td>
                        </tr>
                    </tbody>  
                </template>
            </template>
        </template>
    </table>
</template>