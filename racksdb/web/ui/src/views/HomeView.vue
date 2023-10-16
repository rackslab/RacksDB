<script setup lang="ts">
import { useHttp } from '@/plugins/http';
import { ref, onMounted} from 'vue'
import type { Ref } from 'vue'
import BannerHomeView from '../components/BannerHomeView.vue';
import CardsHomeView from '@/components/CardsHomeView.vue';

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

    <BannerHomeView />


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
            :complement=infrastructure.description
            :array=infrastructures
        />

    </div>

</template>
