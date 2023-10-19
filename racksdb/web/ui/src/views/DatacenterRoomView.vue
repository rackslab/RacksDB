<script setup lang="ts">
import { useHttp } from '@/plugins/http';
import { ref, onMounted } from 'vue'
import type { Ref } from 'vue'
import SearchBarView from '@/components/SearchBarView.vue';

var datacenters: Ref<Array<Datacenter>> = ref([])
const http = useHttp()

async function getDatacenters(){
    try {
        const resp = await http.get('datacenters')
        datacenters.value = resp.data as Datacenter[]
    } catch (error) {
        console.error('Erreur lors de la récupératuon des données des datacenters', error)
    }
}

onMounted(() => {
    getDatacenters()
})

export interface Datacenter {
  name: string
}

</script>

<template>

    <SearchBarView 
        v-if="datacenters.length"
        viewTitle="Datacenter Room"    
        searchedItem="datacenter" 
        :items="datacenters"
    />

</template>