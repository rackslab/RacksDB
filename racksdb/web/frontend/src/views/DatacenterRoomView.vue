<template>
    <div class="datacenter-room">

        <div class="search">
            <h1>Datacenters</h1>

            <input id="myInput" type="text" v-model="input" placeholder="Search a datacenter" v-on:keyup="searchDatacenter()"/>

            <ul id="myUL" v-show="showList">
                <router-link v-for="datacenter in datacenters" :key="datacenter.name" :to="getDatacenterDetailsRoute(datacenter.name)">
                <li>{{datacenter.name}}</li></router-link>
            </ul> 

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
                <tr v-for="rack in getRack()" :key="rack.name">
                <td> {{ rack.rack_name }}</td>
                <td>N/A</td>
                <td> {{ getInfrastructure(rack.rack_name).join(', ') || '/'}}</td>
                </tr>
                </tbody>
            </table>
        </div>

    </div>
  </template>
  
  <script>
import axios from 'axios';

  export default {
    name: 'DatacenterDetailsView',
    props: ['datacenterRoom', 'datacenterName'],

    data() {
        return {
            datacenters: [],
            infrastructures: [],
            racks: [],
            showList: false,
            selectedDatacenter: null,
        };
    },


    mounted() {
        this.fetchData();

    },

    methods: {
        async fetchData() {
            try {
                const response = await axios.get('http://localhost:5000/api/datacenterroom');
                this.datacenters = response.data.datacenters;
                this.infrastructures = response.data.infrastructures;
                this.racks = response.data.racks;

                this.show(this.datacenterRoom);

            } catch (error) {
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
            this.selectedDatacenter == null
            return `/datacenters/${encodeURIComponent(datacenterName)}`
        },

        show(datacenterRoom) {
            this.selectedDatacenter = this.datacenters.find(datacenter => datacenter.room_name === datacenterRoom);
            console.log('ici' + this.selectedDatacenter.name)
        },

        getRack(){
            const filteredRack = this.racks.filter(rack => rack.datacenter_name === this.selectedDatacenter.name)

            return filteredRack
        },

        getInfrastructure(rack){
            const filteredInfrastructure = this.infrastructures.filter(infrastructure => infrastructure.rack_name === rack)
            .map(infrastructure => infrastructure.name);


            return filteredInfrastructure
        }


    }
  }
 
  </script>
  
  <style scoped src="../assets/css/DatacenterRoomView.css">
  </style>
  