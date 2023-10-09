<script setup lang="ts">
// import {ref, onMounted } from 'vue'
// import {useConfig } from '../plugins/config-plugin' 

// const {config} = useConfig();

</script>

<template>

    <section>
        <h1 class="text-5xl font-medium flex justify-center py-20">Overview of your database</h1>
    </section>

    <div class="cards flex justify-around">
        <div class="datacener_card w-full max-w-sm p-4 bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700">
            <h2 class="text-2xl font-semibold flex justify-center">??? Datacenters</h2>
            <ul role="list" class="space-y-5 my-7">
                <li class="flex space-x-3 items-center">
                    <span class="text-base font-normal leading-tight text-gray-500 dark:text-gray-400">Paris, freecooling tier2</span>
                </li>
            </ul>
            <button type="button" class="text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-200 dark:focus:ring-blue-900 font-medium rounded-lg text-sm px-5 py-2.5 inline-flex justify-center w-full text-center">
                Choose plan</button>
        </div>
    
        <div class="infrastructure_card">
            <div class="datacener_card w-full max-w-sm p-4 bg-white border border-gray-200 rounded-lg shadow sm:p-8 dark:bg-gray-800 dark:border-gray-700">
                <h2 class="text-2xl font-semibold flex justify-center">??? Infrastructures</h2>
                <ul role="list" class="space-y-5 my-7">
                    <li class="flex space-x-3 items-center">
                        <span class="text-base font-normal leading-tight text-gray-500 dark:text-gray-400">Mercury, Mercury HPC cluster</span>
                    </li>
                </ul>
                <button type="button" class="text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-200 dark:focus:ring-blue-900 font-medium rounded-lg text-sm px-5 py-2.5 inline-flex justify-center w-full text-center">
                    Choose plan</button>
            </div>
        </div>
    </div>




</template>
