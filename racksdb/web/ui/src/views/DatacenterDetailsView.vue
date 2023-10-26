<script setup lang="ts">
import { useHttp } from '@/plugins/http';
import { ref, onMounted } from 'vue'
import type { Ref } from 'vue'
import SearchBarView from '@/components/SearchBarView.vue';


const http = useHttp()
var datacenters: Ref<Array<Datacenter>> = ref([])
var datacenterDetails: Ref<Array<Datacenter>> = ref([])
    
    async function getDatacenters(){
        try {
            const resp = await http.get('datacenters')
            datacenters.value = resp.data as Datacenter[]
            datacenterDetails.value = datacenters.value.filter((datacenter) => datacenter.name === props.name) as Datacenter[]
        } catch (error) {
            console.error('Erreur lors de la récupératuon des données des datacenters', error)
        }
    }    
    
    onMounted(() => {
        getDatacenters()
    })

    function roomNbRacks(room: DatacenterRoom) {
        return room.rows.reduce((result, row) => result + row.nbracks, 0)
    }
    
    interface Datacenter {
        name: string,
        rooms: Array<DatacenterRoom>
    }

    interface DatacenterRoom {
            name: string
            dimensions: {
                width: number
                depth: number
            }
            rows: [{
                nbracks: number
            }]       
    }
    
    const props = defineProps({
        name: String,
        
    })
</script>

<template>

    <SearchBarView 
        v-if="datacenters.length"
        viewTitle="Datacenter Details"    
        searchedItem="datacenter" 
        :items="datacenters"
    />

    
<div class="relative overflow-x-auto py-20">
    <h2 class="text-3xl font-medium flex justify-center capitalize py-16">{{ name }} Datacenter</h2>
    <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
        <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
            <tr>
                <th scope="col" class="px-6 py-3">
                    Name
                </th>
                <th scope="col" class="px-6 py-3">
                    Area (m²)
                </th>
                <th scope="col" class="px-6 py-3">
                    Number of racks
                </th>
                <th scope="col">
                    Access to the room
                </th>
            </tr>
        </thead>

        <tbody v-for="datacenter in datacenterDetails" :key="datacenter.name">
            <tr v-for="room in datacenter.rooms" :key="room.name" class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 text-black">
                <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">
                    <span>{{ room.name }} </span>
                </th>

                <td class="px-6 py-4">
                    <span class="text-black">{{ room.dimensions.width * room.dimensions.depth / 10**6 }}m²</span><br>
                    <div class="italic text-gray-500 text-xs">
                        width: {{ room.dimensions.width / 10**3 }}m<br>
                        depth: {{ room.dimensions.depth / 10**3}}m
                    </div>
                </td>

                <td class="px-6 py-4">
                    {{ roomNbRacks(room) }}
                </td>

                <td>
                    <router-link :to="{name: 'datacenterroom', params: {name: datacenter.name, datacenterRoom: room.name}}">
                        <button class="py-2.5 px-5 mr-2 mb-2 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700">
                            Access to the room</button>
                    </router-link>
                </td>
            </tr>

        </tbody>
    </table>
</div>

</template>