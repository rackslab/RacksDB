<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Ref } from 'vue'


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
                    <div class="cards flex justify-around pt-32 px-32 ">
                        <div class="w-full max-w-sm p-4 bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700">
                                <h2 class="text-2xl font-semibold flex justify-center text-purple-700 capitalize"> {{ item.rack }} </h2>
                                <h3 class="flex justify-center text-purple-700 capitalize">Node</h3>
                    
                                <ul role="list" class="space-y-5 my-7">
                                    <li class="flex space-x-3 items-center">
                                        <span class="text-base font-normal leading-tight  dark:text-gray-400 capitalize text-purple-700">{{ item.name }}</span>
                                    </li>                                
                                    
                                    <li class="flex space-x-3 items-center">
                                        <span class="text-base font-normal leading-tight  dark:text-gray-400 capitalize text-purple-700">{{ item.type.id }}</span>
                                    </li>
                                </ul>
                        </div>
                    </div>
                </div>

            </div>
            <div v-else-if="searchItem === 'storage'">
                <div v-for="item in rack.storage" :key="item.name">
                    <div class="cards flex justify-around pt-32 px-32 ">
                        <div class="w-full max-w-sm p-4 bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700">
                                <h2 class="text-2xl font-semibold flex justify-center text-purple-700 capitalize"> {{ item.rack }} </h2>
                                <h3 class="flex justify-center text-purple-700 capitalize">{{ item.tags }}</h3>
                    
                                <ul role="list" class="space-y-5 my-7">
                                    <li class="flex space-x-3 items-center">
                                        <span class="text-base font-normal leading-tight  dark:text-gray-400 capitalize text-purple-700">{{ item.name }}</span>
                                    </li>                                
                                    
                                    <li class="flex space-x-3 items-center">
                                        <span class="text-base font-normal leading-tight  dark:text-gray-400 capitalize text-purple-700">{{ item.type.id }}</span>
                                    </li>
                                </ul>
                        </div>
                    </div>
                </div>

            </div>
            <div v-else>
                <div v-for="item in rack.network" :key="item.name">
                    <div class="cards flex justify-around pt-32 px-32 ">
                        <div class="w-full max-w-sm p-4 bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700">
                                <h2 class="text-2xl font-semibold flex justify-center text-purple-700 capitalize"> {{ item.rack }} </h2>
                                <h3 class="flex justify-center text-purple-700 capitalize">{{ item.tags }}</h3>
                    
                                <ul role="list" class="space-y-5 my-7">
                                    <li class="flex space-x-3 items-center">
                                        <span class="text-base font-normal leading-tight  dark:text-gray-400 capitalize text-purple-700">{{ item.name }}</span>
                                    </li>                                
                                    
                                    <li class="flex space-x-3 items-center">
                                        <span class="text-base font-normal leading-tight  dark:text-gray-400 capitalize text-purple-700">{{ item.type.id }}</span>
                                    </li>
                                </ul>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>
</template>