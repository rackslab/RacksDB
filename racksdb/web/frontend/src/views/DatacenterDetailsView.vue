<template>
    <div class="datacenter-details">
              
        <div v-if="selectedDatacenter" class="details-table">
            <h2>{{ selectedDatacenter.name }} Datacenter :</h2>

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
                    <td>{{ selectedDatacenter.room_name}}</td>
                    <td>{{ selectedDatacenter.room_depth }}</td>
                    <td>{{ selectedDatacenter.room_width }}</td>
                    <td>{{ selectedDatacenter.nb_rack }}</td>
                    <td><router-link :to="getRoomRoute(selectedDatacenter.room_name)"><button type="button" class="btn btn-primary">SEE THE ROOM</button></router-link></td>
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

        getRoomRoute(datacenterRoom){
            return`/datacenters/${encodeURIComponent(this.datacenterName)}/${encodeURIComponent(datacenterRoom)}`
        }
    }
  }
 
  </script>
  
  <style scoped src="../assets/css/DatacenterDetailsView.css">
  </style>
  