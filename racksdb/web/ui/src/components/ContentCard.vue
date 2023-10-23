<script setup lang="ts">
    
defineProps({
    rack: String,
    tag: String,
    name: String,
    id: String
})

</script>

<template>

<div class="flex justify-around pt-32 px-32 ">
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
</div>
</template>