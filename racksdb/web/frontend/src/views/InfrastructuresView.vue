<template>
    <div class="infrastructures">
      <h1>Infrastructures</h1>

      <input id="myInput" type="text" v-model="input" placeholder="Search an infrastructure" v-on:keyup="searchInfrastructure()"/>

      <ul id="myUL" v-show="showList">
        <li v-for="infrastructure in infrastructures" :key="infrastructure.name" @click="showSearchResult($event)">{{infrastructure.name}}</li>
      </ul>

      <div class="cards" v-if="selectedInfrastructure">


          <div class="card" v-for="rack in showResultSelection()" :key="rack">
            <ul>
              <li><span class="name">{{ rack.rack_name }}</span></li>
              <li><span class="type">Pas encore trouvé</span></li>
              <li>{{ rack.node_name }}</li>
              <li>{{ rack.node_id }}</li>
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
      infrastructures: [],
      racks: [],
      showList: false,
      selectedInfrastructure: null,
    };
  },
  mounted() {
    this.fetchData();
  },

  methods: {
    async fetchData() {
      try {
        const response = await axios.get('http://localhost:5000/api/infrastructures');
        this.infrastructures = response.data.infrastructures;
        this.racks = response.data.racks;

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

    showSearchResult(event) {
      const userSelection = event.target.textContent;
      this.selectedInfrastructure = this.infrastructures.find(infrastructure => infrastructure.name === userSelection);
    },

    showResultSelection(){
      if(this.selectedInfrastructure){
        return this.racks.filter(rack => rack.infrastructure_name === this.selectedInfrastructure.name)
      }
    }



  },
}; 

</script>
  

<style scoped src="../assets/css/InfrastructureView.css">

</style>
  