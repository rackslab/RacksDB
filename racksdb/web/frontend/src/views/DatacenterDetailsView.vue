<template>
    <div class="datacenter-details">

        <p>{{ show() }}</p>
        <button @click="show()">hello</button>

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

            } catch (error) {
                this.error = 'Error fetching data';
                console.error(error)
            }
        },

        show(){
            this.selectedDatacenter = this.datacenters.find(datacenter => datacenter.name === this.datacenterName)
            console.log(this.selectedDatacenter)
        },
    }
  }
 
  </script>
  
  <style scoped>
  </style>
  