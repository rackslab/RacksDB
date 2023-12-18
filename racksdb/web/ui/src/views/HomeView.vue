<!--Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import HomeViewCards from '@/components/HomeViewCards.vue'
</script>

<template>
  <section>
    <div class="flex justify-center items-center w-full h-full text-purple-700">
      <h1 class="text-5xl flex justify-center py-20 z-10 font-bold">Overview</h1>
    </div>
  </section>

  <div class="flex justify-around pt-32 px-32">
    <HomeViewCards />
  </div>
</template>
