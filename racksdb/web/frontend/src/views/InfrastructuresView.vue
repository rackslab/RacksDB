<template>
    <div class="infrastructures">
      <div class="search">
        <h1>Infrastructures</h1>
  
        <input id="myInput" type="text" v-model="input" placeholder="Search an infrastructure" v-on:keyup="searchInfrastructure()"/>
  
        <ul id="myUL" v-show="showList">
          <router-link v-for="infrastructure in infrastructures" :key="infrastructure.name" :to="getInfrastructureDetailsRoute(infrastructure.name)"><li>{{infrastructure.name}}</li></router-link>
        </ul>
      </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      infrastructures: [],
      showList: true,
    };
  },

  mounted() {
    this.fetchData();
  },

  methods: {
    async fetchData() {
      try {
        const response = await axios.get('http://localhost:5000/api/infrastructuresView');
        this.infrastructures = response.data.infrastructures;

      } catch (error){
        this.error = 'Error fetching data';
        console.error(error)
      }
    },

    searchInfrastructure() {
      var input, filter, ul, li, i, txtValue;

      input = document.getElementById('myInput')
      filter = input.value.toUpperCase();
      ul = document.getElementById('myUL');
      li = ul.getElementsByTagName('li');

      for (i = 0; i < li.length; i++) {
      txtValue = li[i].textContent || li[i].innerText;
      
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        li[i].style.display = "";
      } else {
        li[i].style.display = "none";
      }
    }
    this.showList = this.input.trim() !=='';
    },

    getInfrastructureDetailsRoute(infrastructureName) {
      return `/infrastructures/${encodeURIComponent(infrastructureName)}`
    },
  },
}; 
</script>
  
<style scoped src="../assets/css/InfrastructureView.css">
</style>
  