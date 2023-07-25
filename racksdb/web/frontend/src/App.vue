<template>
  <!-- La balise HeaderPage permet d'insérer le composant dans l'entièreté de l'application -->
<HeaderPage />

</template>


<script>
// Importation du composant HeaderPage pour ensuite l'insérer dans l'application
import HeaderPage from './components/HeaderPage.vue'

export default {
  name: 'App',
  components: {
    HeaderPage
  }
}
</script>

<style scoped>
  .header{
    margin: 0% 1% 1% 1%;
  }
</style>

