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
              <li @click="openModal(item.id)">{{ item.id }}</li>
            </ul>
          </div>
      </div>

      <!-- Modal -->
    <div v-if="showPopupFlag" class="modal">
      <div class="modal-content">
        <!-- Affichez ici les détails de la modal en utilisant `selectedItemId` -->
        <h2>Modal Content for ID: {{ selectedItemId }}</h2>

        <div v-if="selectedEquipment">
          <ul>
            <li>ID: {{ selectedEquipment.node_id }}</li>
            <li>Model: {{ selectedEquipment.node_model }}</li>
            <li>Height: {{ selectedEquipment.node_height }}u</li>
            <li>Width: {{ selectedEquipment.node_width }}</li>
            <li>Specs: {{ selectedEquipment.node_specs }}</li>
            
            <!-- Specific for nodes-->
            <li>CPU:</li>
            <li>Sockets: {{ selectedEquipment.node_cpu_socket }}</li>
            <li>Model: {{ selectedEquipment.node_cpu_model }}</li>
            <li>Specs: {{ selectedEquipment.node_cpu_specs }}</li>
            <li>Cores: {{ selectedEquipment.node_cpu_cores }}</li>
            <li>RAM:</li>
            <li>Dimm: {{ selectedEquipment.node_ram_dimm }}</li>
            <li>Size: {{ selectedEquipment.node_ram_size }}GB</li>


          </ul>
        </div>
    
        <!-- ... Autres informations liées à l'élément sélectionné ... -->
        <button @click="closeModal">Close</button>
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
      selectedEquipment: null,
      showPopupFlag: false,
      selectedItemId: null,
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

        console.log(response.data);

        const response2 = await axios.get('http://localhost:5000/api/equipments');
        this.node_equipments = response2.data.node_equipments;

        console.log("je retourne ça :" + response2.data);

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

    getEquipmentDetails(itemId){
      return this.node_equipments.find(equipment => equipment.node_id === itemId)
    },

    openModal(itemId) {
      this.showPopupFlag = true;
      this.selectedItemId = itemId;
      this.selectedEquipment = this.getEquipmentDetails(itemId);
    },

    closeModal(){
      this.showPopupFlag = false;
    },

  },
}; 
</script>
  
<style scoped src="../assets/css/InfrastructureView.css">

</style>
  