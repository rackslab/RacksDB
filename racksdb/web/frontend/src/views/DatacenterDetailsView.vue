<template>
    <div class="datacenter-details">
        <div class="search">
            <h1>Datacenters</h1>

            <input id="myInput" type="text" v-model="input" placeholder="Search a datacenter" v-on:keyup="searchDatacenter()"/>

            <ul id="myUL" v-show="showList">
                <router-link v-for="datacenter in datacenters" :key="datacenter.name" :to="getDatacenterDetailsRoute(datacenter.name)">
                <li>{{datacenter.name}}</li></router-link>
            </ul> 
        </div>
              
        <div v-if="selectedDatacenter" class="details-table">
            <h2>{{ selectedDatacenter.name }} Datacenter :</h2>

            <table class="table table-bordered">
                <thead>
                    <tr>
                    <th scope="col">Name</th>
                    <th scope="col">Depth</th>
                    <th scope="col">Width</th>
                    <th scope="col">Number of racks</th>
                    <th scope="col">Access to the room</th>
                    </tr>
                </thead>

                <tbody>
                    <tr>
                    <td class="room">{{ selectedDatacenter.room_name}}</td>
                    <td>{{ selectedDatacenter.room_depth / 1000}}m</td>
                    <td>{{ selectedDatacenter.room_width / 1000 }}m</td>
                    <td>{{ selectedDatacenter.nb_rack }}</td>
                    <td>
                        <router-link :to="getRoomRoute(selectedDatacenter.room_name)">
                        <button type="button" class="btn btn-primary">SEE THE ROOM</button></router-link>
                    </td>
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
            fillRate:[],
            showList: false,
            selectedDatacenter: null,
        };
    },

    watch: {
        datacenterName(newValue) {
            this.show(newValue)
        }
    },

    mounted() {
        this.fetchData();
    },

    methods: {
        async fetchData() {
            try {
                const response = await axios.get('http://localhost:5000/api/datacenterDetails');
                this.datacenters = response.data.datacenters;
                this.racks = response.data.racks;

                this.show(this.datacenterName);

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

        show(datacenterName) {
            this.selectedDatacenter = this.datacenters.find(datacenter => datacenter.name === datacenterName);
        },

        getDatacenterDetailsRoute(datacenterName) {
            return `/datacenters/${encodeURIComponent(datacenterName)}`
        },

        getRoomRoute(datacenterRoom){
            return`/datacenters/${encodeURIComponent(this.datacenterName)}/${encodeURIComponent(datacenterRoom)}`
        },
    }
}
 
  </script>
  
  <style scoped src="../assets/css/DatacenterDetailsView.css">
  </style>
  