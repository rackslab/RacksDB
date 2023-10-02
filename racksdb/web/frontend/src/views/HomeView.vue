<template>
    <div class="home">

      <section class="slider">
        <div class="overlay"></div>
          <div class="main-title">
            <h1>Overview of your database</h1>
          </div>
      </section>

      <div class="cards">
        <div class="datacenters">
          <router-link to="/datacenters"><h2 class="title_card">{{datacenters.length}} Datacenters</h2></router-link> 
          
            <ul>
              <li v-for="datacenter in datacenters" :key="datacenter.id">
                <router-link :to="getDatacenterDetailsRoute(datacenter.name)"><span class="name">{{datacenter.name}}</span></router-link> 
                  <span class="description">, {{ datacenter.tags.join(' ') }}</span>
              </li>
            </ul>
        </div>

        <div class="infrastructures">
          <router-link to="/infrastructures"><h2 class="title_card">{{ infrastructures.length }} Infrastructures</h2></router-link>

            <ul>
              <li v-for="infrastructure in infrastructures" :key="infrastructure.id">
                <router-link :to="getInfrastructureDetailsRoute(infrastructure.name)"><span class="name">{{infrastructure.name}}</span></router-link>
                  <span class="description">, {{ infrastructure.tags.join(' ') }}</span>
              </li>
            </ul>
        </div>

      </div>
    </div>
</template>
    
<script>
import axios from 'axios';

export default {
  data() {
    return {
      datacenters: [],
      infrastructures: [],
    };
  },

  mounted() {
    this.fetchData();
  },

  methods: {
    async fetchData() {
      try {
        const response = await axios.get('http://localhost:5000/api/homeview');
        this.datacenters = response.data.datacenters;
        this.infrastructures = response.data.infrastructures

      } catch (error){
        this.error = 'Error fetching data';
        console.error(error)
      }
    },

    getDatacenterDetailsRoute(datacenterName) {
      return `/datacenters/${encodeURIComponent(datacenterName)}`
    },

    getInfrastructureDetailsRoute(infrastructureName) {
      return `/infrastructures/${encodeURIComponent(infrastructureName)}`
    },
  },
};
</script>

<style scoped src="../assets/css/HomeView.css">
</style>
     