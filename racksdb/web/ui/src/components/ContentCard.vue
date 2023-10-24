<script setup lang="ts">
import { ref } from 'vue'
import type { Ref } from 'vue'
import type { Infrastructure, NodeEquipment, NetworkEquipment, StorageEquipment } from './InfrastructureCards.vue';

var showPopUp = ref(false)
var popUpContent: Ref<NodeEquipment | NetworkEquipment | StorageEquipment | undefined > = ref()


    
const props = defineProps({
    rack: String,
    tag: String,
    name: {
        type: String,
        required: true
    },
    id: String,
    items: {
        type: Array<Infrastructure>,
            default() {
                return []
            }
    }
})
        
function popUp(name: string){
    if(showPopUp.value){
        showPopUp.value = !showPopUp.value
    } else {
        for(var i=0; i < props.items.length; i++){
            var layout = props.items[i].layout

            for(var y=0; y < layout.length; y++){
                if (layout[y].nodes.find(node => node.name === name)){
                    popUpContent.value = layout[y].nodes.find(node => node.name === name)
                    break
                } 



            }

        }
        showPopUp.value = true      


    }
}


</script>

<template>

<div class="flex justify-around pt-32 px-32" @click="popUp(name)">
    <div class="w-full max-w-sm p-4 bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700">
        <h2 class="text-2xl font-semibold flex justify-center text-purple-700 capitalize"> {{ rack }} </h2>
            <h3 class="flex justify-center text-purple-700 capitalize">{{ tag }}</h3>
                    
                <ul role="list" class="space-y-5 my-7">
                    <li class="flex space-x-3 items-center">
                        <span class="text-base font-normal leading-tight  dark:text-gray-400 capitalize text-purple-700">{{ name }}</span>
                    </li>                                
                                    
                    <li class="flex space-x-3 items-center">
                        <span class="text-base font-normal leading-tight  dark:text-gray-400 capitalize text-purple-700">{{ id }}</span>
                    </li>
                </ul>
    </div>

    <div v-if="showPopUp && popUpContent">
        <div v-if="'cpu' in popUpContent['type']">
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
            <p>{{ popUpContent.name}}</p>

        </div>
        
    </div>

    

</div>
</template>