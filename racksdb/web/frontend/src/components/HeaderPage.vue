<template>
    <div class="header">
      <nav class="navbar navbar-expand-lg">
        
        <div class="container-fluid">
          <a class="navbar-brand" href="/">
            <img class="img" src="../assets/racksdb_logo.svg" alt="Logo Racksdb">
          </a>
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
            aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
          </button>
         
          <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
            <ul class="navbar-nav">
              <router-link to="/" exact class="nav-link" :class="{ 'active': isRouteActive('/') }"><li class="nav-item">Home</li></router-link>
              <router-link to="/datacenters" class="nav-link" :class="{ 'active': isDatacentersRouteActive() }"><li class="nav-item">Datacenters</li></router-link>
              <router-link to="/infrastructures" class="nav-link" :class="{ 'active': isInfrastructuresRouteActive() }"><li class="nav-item">Infrastructures</li></router-link>
            </ul>
          </div>
        </div>
      </nav>
      <router-view/>
    </div>
</template>
    
<script>
export default {
  name: 'HeaderPage',
  methods: {
    
    isRouteActive(routePath) {
      return this.$route.path === routePath;
    },

    isDatacentersRouteActive() {
      return this.$route.path.startsWith('/datacenters');
    },

    isInfrastructuresRouteActive(){
      return this.$route.path.startsWith('/infrastructures')
    }
  }
}
</script>
  
<style scoped src="../assets/css/HeaderPage.css">
</style>
  
