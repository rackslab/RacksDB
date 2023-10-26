<script setup lang="ts">
import { ref } from 'vue'
import type { Ref, PropType } from 'vue'
import type { Infrastructure, NodeEquipment, NetworkEquipment, StorageEquipment } from '@/views/InfrastructureDetailsView.vue'

var showPopUp = ref(false)
var popUpContent: Ref<NodeEquipment | NetworkEquipment | StorageEquipment | undefined > = ref()


    
const props = defineProps({
    rack: String,
    equipment: {
        type: String,
        required: true,
    },
    name: {
        type: String,
        required: true
    },
    id: String,
    infrastructure: {
        type: Object as PropType<Infrastructure>,
        required: true
    }
})
        
function popUp(name: string, equipment: "nodes" | "storage" | "network"){
    if(showPopUp.value){
        showPopUp.value = !showPopUp.value
    } else {
            var layout = props.infrastructure.layout

            for(var y=0; y < layout.length; y++){
                var result = layout[y][equipment].find(item => item.name === name)
                if (result){
                    popUpContent.value = result
                    break
                }
            }
        showPopUp.value = true      
    }
}

function closePopUp(){
    showPopUp.value = !showPopUp.value
}

</script>

<template>

<div class="w-full max-w-lg pt-32 px-32">
    <div class="w-60 p-6 bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700 transition-transform hover:scale-105">
        <h2 class="text-2xl font-semibold flex justify-center text-purple-700 capitalize"> {{ rack }} </h2>
            <h3 class="flex justify-center text-purple-700 capitalize">{{ equipment }}</h3>
                    
                <ul role="list" class="space-y-5 my-7">
                    <li class="flex space-x-3 items-center">
                        <span class="text-base font-normal leading-tight  dark:text-gray-400 capitalize text-purple-700">{{ name }}</span>
                    </li>                                
                                    
                    <li class="flex space-x-3 items-center">
                        <span class="text-base font-normal leading-tight  dark:text-gray-400 capitalize text-purple-700 cursor-pointer" @click="popUp(name, equipment)">{{ id }}</span>
                    </li>
                </ul>
    </div>

    <div v-if="showPopUp && popUpContent" class="fixed top-0 left-0 flex flex-col items-center justify-center w-screen h-screen bg-gray-300 bg-opacity-50 dark:bg-gray-900 dark:bg-opacity-50 backdrop-blur-md z-50">
        <div class="w-full max-w-md p-4 bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700">
            <div v-if="'cpu' in popUpContent['type']" >
                <p class="font-medium">ID: {{ popUpContent.type.id }}</p>
                <p>Model: {{ popUpContent.type.model }}</p>
                <p>Height: {{ popUpContent.type.height }}</p>
                <p>Width: {{ popUpContent.type.width }}</p>
                <p>Specs: {{ popUpContent.type.specs }}</p>
    
                <p class="font-medium">CPU:</p>
                <p>Sockets: {{ popUpContent.type.cpu.sockets }}</p>
                <p>Model: {{ popUpContent.type.cpu.model }}</p>
                <p>Specs: {{ popUpContent.type.cpu.specs }}</p>
                <p>Cores: {{ popUpContent.type.cpu.cores }}</p>
    
                <p class="font-medium">RAM:</p>
                <p>Dimm: {{ popUpContent.type.ram.dimm }}</p>
                <p>Size: {{ popUpContent.type.ram.size / (1024**3) }}GB</p>
            </div>
    
            <div v-else-if="'disks' in popUpContent['type']">
                <p>ID: {{ popUpContent.type.id }}</p>
                <p>Model: {{ popUpContent.type.model }}</p>
                <p>Height: {{ popUpContent.type.height }}</p>
                <p>Disks:</p>
                <p>Type: {{ popUpContent.type.disks.type }}</p>
                <p>Size: {{ popUpContent.type.disks.size }}</p>
                <p>Model: {{ popUpContent.type.disks.model }}</p>
                <p>Number: {{ popUpContent.type.disks.number }}</p>
    
            </div>

            <div v-else-if="'netifs' in popUpContent['type']">
                <p>ID: {{ popUpContent.type.id }}</p>
                <p>Model: {{ popUpContent.type.model }}</p>
                <p>Height: {{ popUpContent.type.height }}</p>
                <p>Width: {{  popUpContent.type.width }}</p>
                <p>Netif:</p>
                <p>Type: {{ popUpContent.type.netifs.type }}</p>
                <p>Bandwidth: {{ popUpContent.type.netifs.bandwidth }}</p>
                <p>Number: {{ popUpContent.type.netifs.number }}</p>
    
            </div>

            <button type="button" @click="closePopUp()" class="py-2.5 px-5 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700">close</button>
        </div>
    </div>

    

</div>
</template>