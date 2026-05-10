<template>
  <div id="app">
    <el-container>
      <el-header class="header">
        <h1>SeeAI 积分管理系统</h1>
      </el-header>
      <el-main>
        <Leaderboard />
      </el-main>
    </el-container>
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
.header {
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}
.header h1 {
  font-size: 24px;
}
</style>
