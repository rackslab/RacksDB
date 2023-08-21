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
      datacenters: [],
      showList: true,
      selectedDatacenter: null,
    };
  },
  mounted() {
    this.fetchData();
  },

  methods: {
    async fetchData() {
      try {
        const response = await axios.get('http://localhost:5000/api/datacentersView');
        this.datacenters = response.data.datacenters;

      } catch (error){
        this.error = 'Error fetching data';
        console.error(error)
      }
    },

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

    getDatacenterDetailsRoute(datacenterName) {
      return `/datacenters/${encodeURIComponent(datacenterName)}`
    },
  },
}; 
</script>
  
<style scoped src="../assets/css/DatacenterView.css">
</style>
  