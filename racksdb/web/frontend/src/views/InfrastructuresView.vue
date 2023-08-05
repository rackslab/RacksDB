<template>
    <div class="infrastructures">
      <h1>Infrastructures</h1>

      <!-- Search zone -->
      <input id="myInput" type="text" v-model="input" placeholder="Search an infrastructure" v-on:keyup="searchInfrastructure()"/>

      <ul id="myUL" v-show="showList">
        <li v-for="infrastructure in infrastructures" :key="infrastructure.name" @click="showSearchResult($event)">{{infrastructure.name}}</li>
      </ul>

      <!-- Cards of the infrastructure -->
      <div class="cards" v-if="selectedInfrastructure">
          <div class="card" v-for="item in showResultSelection()" :key="item">
            <ul>
              <li><span class="name">{{ item.rack_name }}</span></li>
              <li><span class="type">Pas encore trouvé</span></li>
              <li>{{ item.name }}</li>
              <li @click="showPopup(item.id)">{{ item.id }}</li>
            </ul>
        </div>
      </div>

      <!-- Popup -->
      <div v-if="showPopupFlag" class="popup">
        <div class="pop-inner">
          <div class="details" v-for="e in node_equipments" :key="e">
            <!-- content of the popup will go here-->
          </div>
            <button class="popup-close" @click="hidePopup">Close popup</button>
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
      nodes: [],
      storages: [],
      networks: [],
      node_equipments: [],
      showList: false,
      selectedInfrastructure: null,
      showPopupFlag: false,
      popupItemId: null,
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
        this.nodes = response.data.nodes;
        this.storages = response.data.storages;
        this.networks = response.data.networks;

        const response2 = await axios.get('http://localhost:5000/api/infrastructuresEquipments');
        this.node_equipments = response2.data.node_equipments;

      } catch (error){
        this.error = 'Error fetching data';
        console.error(error)
      }
    },

    // This method recovers the elements of the template and loop through all the items
    // and hide those who don't match the search query
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

    // This method get the selection of the user (event) and put the result of the query in a variable
    showSearchResult(event) {
      const userSelection = event.target.textContent;
      this.selectedInfrastructure = this.infrastructures.find(infrastructure => infrastructure.name === userSelection);
    },

    // if a infrastructure is selected, this method will merge all the data of this infrastructure in one variable
    showResultSelection(){
      if(this.selectedInfrastructure){
        const filteredNodes = this.nodes.filter(node => node.infrastructure_name === this.selectedInfrastructure.name);
        const filteredStorages = this.storages.filter(storage => storage.infrastructure_name === this.selectedInfrastructure.name);
        const filteredNetworks = this.networks.filter(network => network.infrastructure_name === this.selectedInfrastructure.name);

        const mergedData = filteredNodes.concat(filteredStorages, filteredNetworks);

        return mergedData;
      }
    },

    showPopup(itemId) {
      this.showPopupFlag = true; // afficher le pop up
      this.popupItemId = itemId; // Stock l'id de l'élément cliqué
    },

    hidePopup() {
      this.showPopupFlag = false;
      this.popupItemId = null;
    },

  },
}; 
</script>
  
<style scoped src="../assets/css/InfrastructureView.css">

</style>
  