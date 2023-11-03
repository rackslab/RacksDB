<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { ref, onMounted} from 'vue'
import CardsHomeView from '@/components/CardsHomeView.vue'
import type { Ref } from 'vue'
import type { Datacenter } from './DatacentersView.vue'
import type { Infrastructure } from './InfrastructuresView.vue'

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

onMounted(() => {
    getDatacenters()
    getInfrastructures()
})
</script>

<template>
    <section class="relative w-screen bg-cover bg-center h-72 mt-6" style="background-image: url('/assets/racks_black.jpg');">
        <div class="absolute top-0 left-0 w-full h-72 bg-purple-700 bg-opacity-20"></div>
            <div class="flex justify-center items-center w-full h-full text-white">
                <h1 class="text-5xl font-medium flex justify-center py-20 z-10">Overview of your database</h1>
            </div>
    </section>

    <div class="flex justify-around pt-32 px-32">
        <CardsHomeView 
            v-for="datacenter in datacenters" 
            :key="datacenter.name" 
            title="datacenter" 
            route="datacenters"
            :body=datacenter.name 
            :complement=datacenter.tags
            :array=datacenters
        />
    
        <CardsHomeView 
            v-for="infrastructure in infrastructures" 
            :key="infrastructure.name" 
            title="infrastructure" 
            route="infrastructures"
            :body=infrastructure.name 
            :complement=infrastructure.name
            :array=infrastructures
        />

    </div>
</template>
