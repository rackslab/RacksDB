<script setup lang="ts">
import { useHttp } from '@/plugins/http';
import { ref, onMounted} from 'vue'
import type { Ref } from 'vue'


const http = useHttp()
const datacenters: Ref<Array<Datacenter>> = ref([])
const infrastructures: Ref<Array<Infrastructure>> = ref([])

async function getDatacenters(){
    try {
        const resp = await http.get('datacenters')
        datacenters.value = resp.data as Datacenter[]
    } catch (error) {
        console.error('Erreur lors de la récupératuon des données des datacenters', error)
    }
}

async function getInfrastructures(){
    try {
        const resp = await http.get('infrastructures')
        infrastructures.value = resp.data as Infrastructure[]
    } catch (error) {
        console.error('Erreur lors de la récupératuon des données des datacenters', error)
    }
}

function getDatacenterDetailsRoute(datacenterName: string){
    return `/datacenters/${encodeURIComponent(datacenterName)}`
}

function getInfrastructureDetailsRoute(infrastructureName: string){
    return `/infrastructures/${encodeURIComponent(infrastructureName)}`
}

onMounted(() => {
    getDatacenters()
    getInfrastructures()
})



export interface Datacenter {
  name: string
  tags: any
}

export interface Infrastructure {
  name: string
  description: string
}

</script>

<template>

    <section class="relative w-screen bg-cover bg-center h-72 mt-6" style="background-image: url('/assets/racks_black.jpg');">
        <div class="absolute top-0 left-0 w-full h-72 bg-purple-700 bg-opacity-20"></div>
        <div class="flex justify-center items-center w-full h-full text-white">
            <h1 class="text-5xl font-medium flex justify-center py-20 z-10">Overview of your database</h1>
        </div>
    </section>

    <div class="cards flex justify-around pt-32 px-32 ">
        <div v-for="datacenter in datacenters" :key="datacenter.name" class="datacenter_card w-full max-w-sm p-4 bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700">
            <router-link to="/datacenters">
                <h2 class="text-2xl font-semibold flex justify-center text-purple-700">{{ datacenters.length }} Datacenter
                    <span v-if="datacenters.length > 1">s</span>
                </h2>
            </router-link>

            <ul role="list" class="space-y-5 my-7">
                <li class="flex space-x-3 items-center">
                    <router-link :to="getDatacenterDetailsRoute(datacenter.name)">
                        <span class="text-base font-normal leading-tight  dark:text-gray-400 capitalize text-purple-700">{{ datacenter.name }},</span>
                    </router-link>
                    <span class="lowercase italic text-gray-500">{{ datacenter.tags.join(' ') }}</span>
                </li>
            </ul>
        </div>

        <div v-for="infrastructure in infrastructures" :key="infrastructure.name" class="datacener_card w-full max-w-sm p-4 bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700">
            <router-link to="/infrastructures">
                <h2 class="text-2xl font-semibold flex justify-center text-purple-700">{{ infrastructures.length }} Infrastructure
                    <span v-if="datacenters.length > 1">s</span>
                </h2>
            </router-link>

            <ul role="list" class="space-y-5 my-7">
                <li class="flex space-x-3 items-center">
                    <router-link :to="getInfrastructureDetailsRoute(infrastructure.name)">
                        <span class="text-base font-normal leading-tight  dark:text-gray-400 capitalize text-purple-700">{{ infrastructure.name }},</span>
                    </router-link>
                    <span class="lowercase italic text-gray-500">{{ infrastructure.description }}</span>
                </li>
            </ul>
        </div>
    
    </div>

</template>
