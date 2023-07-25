<template>
<div class="datacenters">
    <h1>Datacenters</h1>

    <input id="myInput" type="text" v-model="input" placeholder="Search a datacenter" v-on:keyup="myFunction()"/>


    <ul id="myUL">
      <li v-for="datacenter in datacenters" :key="datacenter"><a href="#">{{datacenter.name}}</a></li>
    </ul>



</div>

</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      datacenters: [],
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

    myFunction() {
    // Declare variables
    var input, filter, ul, li, a, i, txtValue;
    input = document.getElementById('myInput');
    filter = input.value.toUpperCase();
    ul = document.getElementById("myUL");
    li = ul.getElementsByTagName('li');

    // Loop through all list items, and hide those who don't match the search query
    for (i = 0; i < li.length; i++) {
      a = li[i].getElementsByTagName("a")[0];
      txtValue = a.textContent || a.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        li[i].style.display = "";
      } else {
        li[i].style.display = "none";
      }
    }
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
  