<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Ref } from 'vue'
import ContentCard from './ContentCard.vue';


var infrastructureDetails: Ref<Array<Infrastructure>> = ref([])
    
const props = defineProps({
    cardTitle: String,
    searchItem: String,
    items: {
        type: Array<Infrastructure>,
            default() {
                return []
            }
    }
})

export interface Infrastructure {
  name: string
  layout: [{
    rack: string

    nodes: [{
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
                dim: number
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
    }]

    network: [{
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
    }]

    storage: [{
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

    }]

}]
}

onMounted(() => {
    infrastructureDetails.value = props.items
})


</script>

<template>
    <div v-for="infrastructure in infrastructureDetails" :key="infrastructure.name">
        <div v-for="rack in infrastructure.layout" :key="rack.rack">
            <div v-if="searchItem === 'nodes'">
                <div v-for="item in rack.nodes" :key="item.name">
                    <ContentCard :rack="item.rack" tag="node" :name="item.name" :id="item.type.id"/>
                </div>
            </div>
            
            <div v-else-if="searchItem === 'storage'">
                <div v-for="item in rack.storage" :key="item.name">
                    <ContentCard :rack="item.rack" tag="storage" :name="item.name" :id="item.type.id"/>
                </div>
                
            </div>
            <div v-else>
                <div v-for="item in rack.network" :key="item.name">
                    <ContentCard :rack="item.rack" tag="network" :name="item.name" :id="item.type.id"/>
                </div>

            </div>
        </div>
    </div>

</template>