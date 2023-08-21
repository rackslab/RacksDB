<template>
    <div class="infrastructure-details">

      <div class="search">
        <h1>Infrastructures</h1>
  
        <input id="myInput" type="text" v-model="input" placeholder="Search an infrastructure" v-on:keyup="searchInfrastructure()"/>
  
        <ul id="myUL" v-show="showList">
          <router-link v-for="infrastructure in infrastructures" :key="infrastructure.name" :to="getInfrastructureDetailsRoute(infrastructure.name)"><li>{{infrastructure.name}}</li></router-link>
        </ul>
      </div>

      <h2 class="infrastructure-name">{{ infrastructureName }}</h2>

      <div class="cards" v-if="selectedInfrastructure">
          <div class="card" v-for="item in showResultSelection()" :key="item">
            <ul>
              <li><span class="name">{{ item.rack_name }}</span></li>
              <li><span class="type">{{ item.type }}</span></li>
              <li>{{ item.name }}</li>
              <li @click="openModal(item.id, item.type)" class="equipment">{{ item.id }}</li>
            </ul>
          </div>
      </div>

      <div v-if="showPopupFlag" class="modal">
        <div class="modal-content">

          <h2>{{ selectedItemId }} details :</h2>

          <div v-if="selectedEquipment" class="details">
            <div v-if="selectedItemType === 'node'">
              <ul>
                <div class="section1">
                  <li><span class="property">ID:</span> {{ selectedEquipment.node_id }}</li>
                  <li><span class="property">Model:</span>  {{ selectedEquipment.node_model }}</li>
                  <li><span class="property">Height:</span> {{ selectedEquipment.node_height }}u</li>
                  <li><span class="property">Width:</span> {{ selectedEquipment.node_width }}</li>
                  <li><span class="property">Specs:</span> {{ selectedEquipment.node_specs }}</li>
                </div>

                <div class="section2">
                  <li><span class="property">CPU:</span></li>
                  <div class="section2a">
                    <li><span class="property">Sockets:</span> {{ selectedEquipment.node_cpu_socket }}</li>
                    <li><span class="property">Model:</span> {{ selectedEquipment.node_cpu_model }}</li>
                    <li><span class="property">Specs:</span> {{ selectedEquipment.node_cpu_specs }}</li>
                    <li><span class="property">Cores:</span> {{ selectedEquipment.node_cpu_cores }}</li>
                  </div>
                </div>

                <div class="section3">
                  <li><span class="property">RAM:</span></li>
                  <div class="section3a">
                    <li><span class="property">Dimm:</span> {{ selectedEquipment.node_ram_dimm }}</li>
                    <li><span class="property">Size:</span> {{ selectedEquipment.node_ram_size }}GB</li>
                  </div>
                </div>
              </ul>
            </div>

            <div v-else-if="selectedItemType === 'storage'">
              <ul>
                <div class="section1">
                  <li><span class="property">ID:</span> {{ selectedEquipment.storage_id }}</li>
                  <li><span class="property">Model:</span> {{ selectedEquipment.storage_model }}</li>
                  <li><span class="property">Height:</span> {{ selectedEquipment.storage_height }}u</li>
                </div>

                <div class="section2">
                  <li><span class="property">Disks:</span></li>
                  <div class="section2a">
                    <li><span class="property">Type:</span> {{ selectedEquipment.disk_type }}</li>
                    <li><span class="property">Size:</span> {{ selectedEquipment.disk_size }}</li>
                    <li><span class="property">Model:</span> {{ selectedEquipment.disk_model }}</li>
                    <li><span class="property">Number:</span> {{ selectedEquipment.disk_number }}</li>
                  </div>

                </div>
              </ul>
            </div>

            <div v-else-if="selectedItemType === 'network'">
              <ul>
                <div class="section1">
                  <li><span class="property">ID:</span> {{ selectedEquipment.network_id }}</li>
                  <li><span class="property">Model:</span> {{ selectedEquipment.network_model }}</li>
                  <li><span class="property">Height:</span> {{ selectedEquipment.network_height }}u</li>
                  <li><span class="property">Width:</span> {{ selectedEquipment.network_width }}u</li>
                </div>
                
                <div class="section2">
                  <li><span class="property">Netifs:</span></li>
                  <div class="section2a">
                    <li><span class="property">Type:</span> {{ selectedEquipment.netif_type }}</li>
                    <li><span class="property">Bandwidth:</span> {{ selectedEquipment.netif_bandwidth }}</li>
                    <li><span class="property">Number:</span> {{ selectedEquipment.netif_number }}</li>
                  </div>
                </div>
              </ul>
            </div>
          </div>

          <button @click="closeModal">Close</button>
        </div>
      </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    name:'InfrastructureDetailsView',
    props: ['infrastructureName'],

  data() {
    return {
      infrastructures: [],
      nodes: [],
      storages: [],
      networks: [],
      node_equipments: [],
      network_equipments: [],
      storage_equipments: [],
      showList: false,
      selectedInfrastructure: null,
      selectedEquipment: null,
      showPopupFlag: false,
      selectedItemId: null,
      selectedItemType: null,
    };
  },

  watch: {
        infrastructureName(newValue) {
            this.show(newValue)
        }
    },

  mounted() {
    this.fetchData();
  },

  methods: {
    async fetchData() {
      try {
        const response = await axios.get('http://localhost:5000/api/infrastructureDetails');
        this.infrastructures = response.data.infrastructures;
        this.nodes = response.data.nodes;
        this.storages = response.data.storages;
        this.networks = response.data.networks;
        this.node_equipments = response.data.node_equipments;
        this.storage_equipments = response.data.storage_equipments;
        this.network_equipments = response.data.network_equipments;

        this.show(this.infrastructureName);

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

    show(infrastructureName) {
        this.selectedInfrastructure = this.infrastructures.find(infrastructure => infrastructure.name === infrastructureName);
    },

    showResultSelection(){
      if(this.selectedInfrastructure){
        const filteredNodes = this.nodes.filter(node => node.infrastructure_name === this.selectedInfrastructure.name).map(node => ({ ...node, type: 'node'}));
        const filteredStorages = this.storages.filter(storage => storage.infrastructure_name === this.selectedInfrastructure.name).map(storage => ({ ...storage, type: 'storage'}));
        const filteredNetworks = this.networks.filter(network => network.infrastructure_name === this.selectedInfrastructure.name).map(network => ({ ...network, type: 'network'}));

        const mergedData = filteredNodes.concat(filteredStorages, filteredNetworks);
        
        return mergedData;
      }
    },

    getEquipmentDetails(itemId, itemType){
      if(itemType ==='node') {
        const node = this.node_equipments.find(equipment => equipment.node_id === itemId)
        return node

      } else if (itemType ==='storage') {
        const storage = this.storage_equipments.find(equipment => equipment.storage_id === itemId)
        return storage

      } else {
        const network = this.network_equipments.find(equipment => equipment.network_id === itemId)
        return network
      }
    },

    openModal(itemId, itemType) {
      this.showPopupFlag = true;
      this.selectedItemId = itemId;
      this.selectedItemType = itemType
      this.selectedEquipment = this.getEquipmentDetails(itemId, itemType);
    },

    closeModal(){
      this.showPopupFlag = false;
    },
  },
}; 
</script>
  
<style scoped src="../assets/css/InfrastructureDetailsView.css">

</style>
  