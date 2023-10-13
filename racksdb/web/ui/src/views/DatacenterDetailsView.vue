<script setup lang="ts">
import { useHttp } from '@/plugins/http';
import { ref, onMounted } from 'vue'
import type { Ref } from 'vue'

const http = useHttp()
const datacenters: Ref<Array<Datacenter>> = ref([])
const racks: Ref<Array<Rack>> = ref([])
const infrastructures: Ref<Array<Infrastructure>> = ref([])
var showList =  ref(true)
const input = ref('')
var selectedRack: Ref<Rack | undefined> = ref(undefined)
var selectedinfrastucture: Ref<Infrastructure | undefined> = ref(undefined)


const props = defineProps({
    datacenterName: String
})


async function getInfrastructures(){
    try{
        const resp = await http.get('infrastructures')
        infrastructures.value = resp.data as Infrastructure[]
        selectedinfrastucture.value = infrastructures.value.find(infrastructure => infrastructure.rack === selectedRack.value?.name);
    } catch (error) {
       console.error('erreur', error)
    }
}

async function getRacks(){
    try{
        const resp = await http.get('racks')
        racks.value = resp.data as Rack[]
        selectedRack.value = racks.value.find(rack => rack.datacenter === props.datacenterName);
    } catch (error) {
        console.error('erreur', error)
    }
}

async function getDatacenters(){
    try {
        const resp = await http.get('datacenters')
        datacenters.value = resp.data as Datacenter[]
    } catch (error) {
        console.error('Erreur lors de la récupératuon des données des datacenters', error)
    }
}

function getDatacenterDetailsRoute(datacenterName: string) {
    return `/datacenters/${encodeURIComponent(datacenterName)}`
}

function searchDatacenter() {
  const filter = input.value.toUpperCase();
  const li = document.getElementsByTagName('li')

  for (var i = 0; i < li.length; i++) {
      var txtValue = li[i].textContent || li[i].innerText;
      console.log(txtValue)
      console.log('.........')

      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        li[i].style.display = "";
      } else {
        li[i].style.display = "none";
      }
    }
    showList.value = input.value.trim() !=='';
};


onMounted(() => {
    getDatacenters()
    getRacks()
    getInfrastructures()
})

export interface Datacenter {
  name: string
  tags: any
  show: boolean
}

export interface Infrastructure {
    rack: string
}

export interface Rack {
    name: string
    datacenter: string
    room: string
    type : {
        width: number
        depth: number
    }
    row: string
}

</script>

<template>

    <div>
        <h1 class="text-5xl font-medium flex justify-center py-20 capitalize">Datacenter Details</h1>

        <div class="mx-60">
            <label for="search" class="mb-2 text-sm font-medium text-gray-900 sr-only dark:text-white">Search</label>
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                        <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 20">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"/>
                        </svg>
                    </div>
                    <input type="text" id="myInput" v-model="input" @input="searchDatacenter" class="block w-full p-4 pl-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="Search a datacenter" required>
                    <button type="submit" class="text-white absolute right-2.5 bottom-2.5 bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-4 py-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">Search</button>
                </div>
        </div>

        <ul id="myUL" v-show="showList" class="flex justify-center">
            <router-link v-for="datacenter in datacenters" :key="datacenter.name" :to="getDatacenterDetailsRoute(datacenter.name)">
              <li class="capitalize">{{datacenter.name}}</li></router-link>
        </ul> 
      
    </div>

    
<div class="relative overflow-x-auto py-20">
    <h2 class="text-3xl font-medium flex justify-center capitalize py-16">{{ selectedRack?.datacenter }} Datacenter</h2>
    <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
        <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
            <tr>
                <th scope="col" class="px-6 py-3">
                    Name
                </th>
                <th scope="col" class="px-6 py-3">
                    Depth
                </th>
                <th scope="col" class="px-6 py-3">
                    Width
                </th>
                <th scope="col" class="px-6 py-3">
                    Number of racks
                </th>
                <th scope="col">
                    Access to the room
                </th>
            </tr>
        </thead>

        <tbody>
            <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">
                    {{ selectedRack?.room }}
                </th>
                <td class="px-6 py-4">
                    {{ selectedRack?.type.depth }}
                </td>
                <td class="px-6 py-4">
                    {{ selectedRack?.type.width }}
                </td>
                <td class="px-6 py-4">
                    {{  selectedinfrastucture?.rack}}
                </td>
            </tr>
            <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">
                    Microsoft Surface Pro
                </th>
                <td class="px-6 py-4">
                    White
                </td>
                <td class="px-6 py-4">
                    Laptop PC
                </td>
                <td class="px-6 py-4">
                    $1999
                </td>
            </tr>
            <tr class="bg-white dark:bg-gray-800">
                <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">
                    Magic Mouse 2
                </th>
                <td class="px-6 py-4">
                    Black
                </td>
                <td class="px-6 py-4">
                    Accessories
                </td>
                <td class="px-6 py-4">
                    $99
                </td>
            </tr>
        </tbody>
    </table>
</div>

</template>