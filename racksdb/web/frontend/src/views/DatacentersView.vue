<template>
<div class="datacenters">
    <h1>Datacenters</h1>

    <div class="search-filter">
        <input type="text" v-model="search" placeholder="Search a datacenter"/>
        
        <div class="item-datacenter" v-for="datacenter in datacenters" :key="datacenter">
            <a href="#">{{ datacenter.name }}</a>
        </div>

    </div>

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
filteredList() {
    if (this.search){
        return this.datacenters.filter((datacenter) =>
        datacenter.toLocaleLowerCase().includes(this.search))
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
  