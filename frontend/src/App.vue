<template>
  <div id="app">
    <div class="app-main">
      <Leaderboard />
    </div>
  </div>
</template>

<script setup>
import Leaderboard from './views/Leaderboard.vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
#app {
  min-height: 100vh;
}
.app-header {
  background: white;
  color: #3da742;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 15px 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.app-header h1 {
  font-size: 24px;
  font-weight: 700;
}
.app-main {
  padding: 0;
}
</style>
