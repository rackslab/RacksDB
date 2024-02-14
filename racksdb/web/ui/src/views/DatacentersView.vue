<!--Copyright (c) 2022-2024 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later -->

<script setup lang="ts">
import { useHttp } from '@/plugins/http'
import { useRacksDBAPI } from '@/composables/RacksDBAPI'
import { ref, onMounted } from 'vue'
import type { Ref } from 'vue'
import type { Datacenter, DatacenterLocation } from '@/composables/RacksDBAPI'
import BreadCrumbs from '@/components/BreadCrumbs.vue'
import L from 'leaflet'
import ComboBox from '@/components/ComboBox.vue'
import { useRouter } from 'vue-router'

const http = useHttp()
const racksDBAPI = useRacksDBAPI(http)
const router = useRouter()
const datacenters: Ref<Array<Datacenter>> = ref([])
const mapContainer: Ref<HTMLDivElement | undefined> = ref()
const showMap: Ref<Boolean> = ref(true)

async function getDatacenters() {
  datacenters.value = await racksDBAPI.datacenters()
}

function datacentersMapConfig() {
  // Nothing to do if map element is not defined
  if (!mapContainer.value) {
    return
  }

  // Build array of defined locations
  const locations = datacenters.value
    .filter((datacenter) => datacenter.location)
    .map((datacenter) => datacenter.location as DatacenterLocation)

  // Stop if no location defined
  if (!locations.length) {
    showMap.value = false
    return
  }

  // Compute average longitude and latitude with defined locations
  const averageLongitude =
    locations.reduce((accumulator, location) => accumulator + location.longitude, 0) /
    locations.length
  const averageLatitude =
    locations.reduce((accumulator, location) => accumulator + location.latitude, 0) /
    locations.length

  // Configuration of the map
  const map = L.map(mapContainer.value).setView([averageLatitude, averageLongitude], 5)
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map)

  // Add a marker on a map if the datacenter has coordinates
  datacenters.value.forEach((datacenter) => {
    // Skip datacenter if location is not defined
    if (!datacenter.location) {
      return
    }

    const datacenterRoute = router.resolve({
      name: 'datacenterdetails',
      params: { name: datacenter.name }
    })

    const purpleIcon = L.icon({
      iconUrl: 'assets/racksdb-marker.svg',
      iconSize: [32, 32],
      iconAnchor: [16, 16],
      popupAnchor: [0, -32]
    })

    let marker = L.marker([datacenter.location.latitude, datacenter.location.longitude], {
      icon: purpleIcon
    }).addTo(map)
    marker.bindPopup(
      `<div class="text-center max-h-30">
        <a class="appearance-none" href="${datacenterRoute.fullPath}">
          <span class="text-sm font-semibold capitalize text-purple-700">${datacenter.name} datacenter</span>
        </a>

        <p>${datacenter.rooms.length} room(s)</p>
      </div>`
    )
  })
}

onMounted(async () => {
  await getDatacenters()
  datacentersMapConfig()
})
</script>

<style src="leaflet/dist/leaflet.css" />

<template>
  <BreadCrumbs />

  <ComboBox itemType="datacenter" :items="datacenters" class="pb-10" />

  <div v-if="showMap" class="flex justify-center py-20">
    <div ref="mapContainer" class="min-w-[75vw] h-96 shadow-2xl z-0"></div>
  </div>
</template>
