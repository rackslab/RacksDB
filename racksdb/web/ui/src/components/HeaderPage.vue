<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'

</script>

<template>
    <header class="flex justify-between items-center p-4">
        <div>
            <router-link to="/"><img alt="Rackslab logo" src="/assets/racksdb_logo.svg" class="h-32 w-32"/></router-link>
        </div>

        <nav class="space-x-4">
            <router-link to="/">Home</router-link>
            <router-link to="/datacenters">Datacenters</router-link>
            <router-link to="/infrastructures">Infrastructures</router-link>
        </nav>
    </header>
    <RouterView />
</template>