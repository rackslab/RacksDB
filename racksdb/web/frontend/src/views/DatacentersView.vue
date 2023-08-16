<template>
  <div class="datacenters">
    <div class="search">
      <h1>Datacenters</h1>

      <input id="myInput" type="text" v-model="input" placeholder="Search a datacenter" v-on:keyup="searchDatacenter()"/>

      <ul id="myUL" v-show="showList">
        <router-link v-for="datacenter in datacenters" :key="datacenter.name" :to="getDatacenterDetailsRoute(datacenter.name)">
          <li>{{datacenter.name}}</li></router-link>
      </ul> 
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      datacenters: [], // List of all the data for datacenters
      racks: [], // List of all the data for racks
      showList: true, // Hides the list of datacenters until the user write something
      selectedDatacenter: null, // The selection of the user will be in this variable
    };
  },
  mounted() {
    this.fetchData();
  },

  methods: {
    async fetchData() {
      try {
        const response = await axios.get('http://localhost:5000/api/datacenters');
        this.datacenters = response.data.datacenters;
        this.racks = response.data.racks

      } catch (error){
        this.error = 'Error fetching data';
        console.error(error)
      }
    },

    // This method recovers the elements of the template and loop through all the items
    // and hide those who don't match the search query
    searchDatacenter() {
    var input, filter, ul, li, i, txtValue;
    input = document.getElementById('myInput'); 
    filter = input.value.toUpperCase();
    ul = document.getElementById("myUL");
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

    // This method send the user to a dedicated page for the datacenter selected
    getDatacenterDetailsRoute(datacenterName) {
      return `/datacenters/${encodeURIComponent(datacenterName)}`
    },
    
  },
}; 
</script>
  
<style scoped src="../assets/css/DatacenterView.css">
</style>
  