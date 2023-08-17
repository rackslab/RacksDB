<template>
    <div class="header">
      <nav class="navbar navbar-expand-lg">
        <div class="container-fluid">

            <!-- Left part of the navbar : clickable logo -->
            <a class="navbar-brand" href="/">
              <img class="img" src="../assets/racksdb_logo.svg" alt="Logo Racksdb">
            </a>
  
          <!-- Lateral menu for small screen -->
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
            aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
          </button>
  
          <!-- Right part of the navbar : different pages of the site -->
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
    // Checks whether the current route path matches the specified path
    isRouteActive(routePath) {
      return this.$route.path === routePath;
    },
    // Checks whether the current route path begins with '/datacenters'.
    isDatacentersRouteActive() {
      return this.$route.path.startsWith('/datacenters');
    },
    // Checks whether the current route path begins with '/infrastructures'.
    isInfrastructuresRouteActive(){
      return this.$route.path.startsWith('/infrastructures')
    }
  }
}
</script>
  
<style scoped src="../assets/css/HeaderPage.css">
</style>
  
