<template>
    <div class="datacenter-details">
              
        
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
    name: 'DatacenterDetailsView',
    props: ['datacenterName'],

    data() {
        return {
            datacenters: [],
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
                const response = await axios.get('http://localhost:5000/api/datacenters');
                this.datacenters = response.data.datacenters;
                this.racks = response.data.racks;

                this.show(this.datacenterName);

            } catch (error) {
                this.error = 'Error fetching data';
                console.error(error)
            }
        },

        show(datacenterName) {
            this.selectedDatacenter = this.datacenters.find(datacenter => datacenter.name === datacenterName);
            console.log(this.selectedDatacenter)
        },
    }
  }
 
  </script>
  
  <style scoped src="../assets/css/DatacenterDetailsView.css">
  </style>
  