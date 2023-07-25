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
          <h2>{{datacenters.length}} Datacenters</h2>
          <ul>
            <li v-for="datacenter in datacenters" :key="datacenter.id">
              {{datacenter.name}}, {{ datacenter.tags.join(' ') }}
            </li>
          </ul>
        </div>

        <div class="infrastructures">
          <h2>{{ infrastructures.length }} Infrastructures</h2>
          <ul>
            <li v-for="infrastructure in infrastructures" :key="infrastructure.id">
              {{ infrastructure.name }}, {{ infrastructure.tags.join(' ') }}
  
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
      infrastructures: []
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      try {
        const datacentersResponse = await axios.get('http://localhost:5000/api/datacenters');
        this.datacenters = datacentersResponse.data;

        const infrastructuresResponse = await axios.get('http://localhost:5000/api/infrastructures');
        this.infrastructures = infrastructuresResponse.data;
      } catch (error){
        this.error = 'Error fetching data';
        console.error(error)
      }
    },
  },
};



</script>
    
    <style scoped>
    
    /* Style of the section with the img in the background */ 
    .slider{
      position: relative;
      background-image: url('../assets/racks_black.jpg');
      background-size: cover;
      background-position: center;
      height: 250px;
    }
  
    /* Style to center the title in the middle of the img */
  .slider .main-title{
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
  }
  
  /* Style of the pseudo element to add the filter to the img */
  .slider .overlay::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(128, 50, 241, 0.2);
  }
  
  .slider h1{
    color: white;
    z-index: 1;
  }

  .cards {
    display: flex;
    justify-content: space-around;
    margin: 2% 0% 0% 0%
    
  }
    </style>
     