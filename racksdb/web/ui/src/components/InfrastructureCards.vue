<script setup lang="ts">
import type { PropType } from 'vue'
import ContentCard from './ContentCard.vue'
import type { Infrastructure } from '@/views/InfrastructureDetailsView.vue'

const props = defineProps({
    cardTitle: String,
    searchItem: String,
    infrastructure: {
        type: Object as PropType<Infrastructure>,
        required: true
    }
})

</script>

<template>
        <div v-for="rack in props.infrastructure.layout" :key="rack.rack" >
            <div v-if="searchItem === 'nodes'" class="flex justify-center px-0 flex-wrap">
                <div v-for="item in rack.nodes" :key="item.name">
                    <ContentCard :rack="item.rack" equipment="nodes" :name="item.name" :id="item.type.id" :infrastructure="props.infrastructure"/>
                </div>
            </div>
            
            <div v-else-if="searchItem === 'storage'" class="flex justify-center px-0 flex-wrap">
                <div v-for="item in rack.storage" :key="item.name">
                    <ContentCard :rack="item.rack" equipment="storage" :name="item.name" :id="item.type.id" :infrastructure="props.infrastructure"/>
                </div>
                
            </div>
            <div v-else class="flex justify-center px-0 flex-wrap">
                <div v-for="item in rack.network" :key="item.name">
                    <ContentCard :rack="item.rack" equipment="network" :name="item.name" :id="item.type.id" :infrastructure="props.infrastructure"/>
                </div>

            </div>
        </div>

</template>