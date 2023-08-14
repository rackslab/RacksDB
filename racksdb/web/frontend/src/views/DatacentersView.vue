<template>
  <div class="datacenters">
    <div class="search">
      <h1>Datacenters</h1>

      <input id="myInput" type="text" v-model="input" placeholder="Search a datacenter" v-on:keyup="searchDatacenter()"/>

      <ul id="myUL" v-show="showList">
        <router-link v-for="datacenter in datacenters" :key="datacenter.name" :to="getDatacenterDetailsRoute(datacenter.name)">
          <li @click="showResult($event)">{{datacenter.name}}</li></router-link>
      </ul> 

    </div>

      <div v-if="selectedDatacenter">
        <h2>{{ selectedDatacenter.name }}</h2>

        <table class="table table-bordered">
          <thead>
            <tr>
              <th scope="col">Name</th>
              <th scope="col">Depth</th>
              <th scope="col">width</th>
              <th scope="col">Number of racks</th>
              <th scope="col"> Access to the room</th>
            </tr>
          </thead>

          <tbody>
            <tr>
              <th scope="row">{{ selectedDatacenter.room_name}}</th>
              <td>{{ selectedDatacenterc }}</td>
              <td>{{ selectedDatacenter.room_width }}</td>
              <td>{{ selectedDatacenter.nb_rack }}</td>
              <td><button type="button" class="btn btn-primary" @click="showRoom()">SEE THE ROOM</button></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="show-room" v-if="selectedDatacenter">
        <h2>{{ selectedDatacenter.name }} Room {{ selectedDatacenter.room_name }}</h2>

        <table class="table table-bordered">
          <thead>
            <tr>
              <th scope="col">Name</th>
              <th scope="col">Fill rate</th>
              <th scope="col">List of infrastructures</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="rack in racks" :key="rack.name">
              <td> {{ rack.rack_name }}</td>
              <td>Hello1</td>
              <td>{{ rack.infrastructure_name || 'N/A' }}</td>
            </tr>
            </tbody>
        </table>

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

    // This method get the selection of the user (event) and put the result of the query in a variable
    showResult(datacenterName) {
      this.selectedDatacenter = this.datacenters.find(datacenter => datacenter.name === datacenterName);
      this.$router.push({ name: 'datacenterdetails', params: { datacenterName: datacenterName } });
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
  