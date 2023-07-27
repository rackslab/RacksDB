<template>
  <div class="datacenters">
      <h1>Datacenters</h1>

      <input id="myInput" type="text" v-model="input" placeholder="Search a datacenter" v-on:keyup="searchDatacenter()"/>

      <ul id="myUL" v-show="showList">
        <li v-for="datacenter in datacenters" :key="datacenter" @click="showResult($event)">{{datacenter.name}}</li>
      </ul>

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
              <td>{{ selectedDatacenter.room_depth }}</td>
              <td>{{ selectedDatacenter.room_width }}</td>
              <td>{{ selectedDatacenter.nb_rack }}</td>
              <td><button type="button" class="btn btn-primary">SEE THE ROOM</button></td>
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
      datacenters: [], // liste de tous les datacenters qui sont dans la BDD.
      showList: false, // Cette propriété permet de ne pas afficher la liste des datacenters (elle s'affiche uniquement quand il commence à taper quelque chose)
      selectedDatacenter: null, // cette propriété permet d'afficher le contenu demandé par l'utilisateur lors de la recherche
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
      } catch (error){
        this.error = 'Error fetching data';
        console.error(error)
      }
    },

    searchDatacenter() {
    // Declare variables
    var input, filter, ul, li, i, txtValue;
    input = document.getElementById('myInput'); 
    filter = input.value.toUpperCase();
    ul = document.getElementById("myUL");
    li = ul.getElementsByTagName('li');

    // Loop through all list items, and hide those who don't match the search query
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

  showResult(event){
    // On récupère la sélection de l'utilisateur .target permet de récupérer la référence dom de l'élément
    // .textContent permet lui de prendre uniquement le texte.
    const userSelection = event.target.textContent;

    this.selectedDatacenter = this.datacenters.find(datacenter => datacenter.name === userSelection);
  }
  },
}; 
</script>
  
<style scoped>
.datacenters{
    display: flex;
    flex-direction: column;
    align-items: center;
}
</style>
  