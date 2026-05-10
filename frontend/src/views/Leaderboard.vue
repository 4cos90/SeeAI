<template>
  <div class="leaderboard-container">
    <h2 class="title">积分榜单</h2>
    <el-table
      v-loading="loading"
      :data="tableData"
      stripe
      border
      style="width: 100%"
    >
      <el-table-column prop="rank" label="排名" width="80" align="center" />
      <el-table-column prop="name" label="姓名" min-width="120" />
      <el-table-column prop="department" label="部门" min-width="150" />
      <el-table-column prop="score" label="积分" width="100" align="center" />
      <el-table-column prop="updateTime" label="更新时间" width="180" />
    </el-table>
    <el-empty v-if="!loading && tableData.length === 0" description="暂无数据" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getLeaderboard } from '../api'

const loading = ref(false)
const tableData = ref([])

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getLeaderboard()
    if (res.code === 0 && res.data) {
      tableData.value = res.data.items || []
    }
  } catch (error) {
    console.error('Failed to fetch leaderboard:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.leaderboard-container {
  padding: 20px;
}
.title {
  text-align: center;
  margin-bottom: 24px;
  color: #303133;
}
</style>
