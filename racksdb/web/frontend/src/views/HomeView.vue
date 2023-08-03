<template>
    <div class="home">

      <!-- C'est la partie du site ou il y a la bannière (effet de superposition entre img, filtre couleur et texte)-->
      <section class="slider">
        <div class="overlay"></div>
        <div class="main-title">
          <h1>Overview of your database</h1>
        </div>
      </section>

      <!-- Les cartes qui affichent les informations de la base de données-->
      <div class="cards">

        <div class="datacenters">
          <h2 class="title_card">{{datacenters.length}} Datacenters</h2>
          <ul>
            <li v-for="datacenter in datacenters" :key="datacenter.id">
              <span class="name">{{datacenter.name}}</span> <span class="description">, {{ datacenter.tags.join(' ') }}</span>
            </li>
          </ul>
        </div>

        <div class="infrastructures">
          <h2 class="title_card">{{ infrastructures.length }} Infrastructures</h2>
          <ul>
            <li v-for="infrastructure in infrastructures" :key="infrastructure.id">
              <span class="name">{{infrastructure.name}}</span> <span class="description">, {{ infrastructure.tags.join(' ') }}</span>
            </li>
          </ul>
        </div>
      </div>

    </div>
</template>
    
<script>
// Axio est une librairie qui permet de faire des requêtes plus simplement et de se protéger des failles XSRF
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

  },
};

</script>

<style scoped src="../assets/css/HomeView.css">
</style>
     