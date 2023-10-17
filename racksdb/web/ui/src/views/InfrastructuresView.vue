<script setup lang="ts">
import { useHttp } from '@/plugins/http';
import { ref, onMounted } from 'vue'
import type { Ref } from 'vue'
import SearchBarView from '@/components/SearchBarView.vue';

var infrastructures: Ref<Array<Infrastructure>> = ref([])
const http = useHttp()

async function getInfrastructure(){
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
}
</script>

<template>
    <SearchBarView 
        v-if="infrastructures.length"
        viewTitle="Infrastructure View"    
        searchedItem="infrastructure" 
        :items="infrastructures"
    />
</template>