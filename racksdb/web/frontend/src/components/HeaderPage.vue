<template>
    <div class="header">
      <nav class="navbar navbar-expand-lg">
        <div class="container-fluid">
          <a class="navbar-brand" href="#">
            <img src="../assets/racksdb_logo.svg" alt="Logo Racksdb" width="100" height="100">
          </a>
  
          <!-- Ajouter la classe navbar-toggler ici pour activer le menu burger -->
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
            aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
          </button>
  
          <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
            <ul class="navbar-nav">
              <router-link to="/" class="nav-link active" aria-current="page"><li class="nav-item">Home</li></router-link>
              <router-link to="/datacenters" class="nav-link"><li class="nav-item">Datacenters</li></router-link>
              <router-link to="/infrastructures" class="nav-link"><li class="nav-item">Infrastructures</li></router-link>
            </ul>
          </div>
        </div>
      </nav>
      <router-view/>
    </div>
</template>
  

  
<script>

export default {
  name: 'HeaderPage'
}

</script>
  
<style scoped>

  .header{
    margin: 0% 1% 1% 1%;
  }
 
  </style>
  