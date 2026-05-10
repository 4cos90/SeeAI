<template>
  <div class="leaderboard-page">
    <div class="particles" id="particles"></div>

    <div class="header">
      <div class="decorative-element"></div>
      <h1>积分排行榜</h1>
      <div class="selector-group">
        <el-select v-model="selectedYear" placeholder="选择年份" size="large" @change="handleYearChange">
          <el-option v-for="year in availableYears" :key="year" :label="year + '年'" :value="year" />
        </el-select>
        <el-select v-model="selectedMonth" placeholder="选择月份" size="large" @change="handleMonthChange">
          <el-option v-for="month in availableMonths" :key="month" :label="month" :value="month" />
        </el-select>
      </div>
      <p>激励创新与协作学习 | Inspiring Innovation &amp; Collaborative Learning</p>
    </div>

    <div class="container">
      <table class="ranking-table">
        <thead>
          <tr>
            <th>排名</th>
            <th>参与者</th>
            <th>积分</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in filteredData" :key="index"
            :class="{ 'top-3': index < 3, [`rank-${index + 1}`]: index < 3 }">
            <td>
              <div class="rank">{{ index + 1 }}</div>
              <div class="participant-name">{{ item.executor }}</div>
            </td>
            <td>{{ item.executor }}</td>
            <td>
              <div class="score">{{ item.total_score }}</div>
            </td>
          </tr>
        </tbody>
      </table>
      <el-empty v-if="!loading && filteredData.length === 0" description="暂无数据" />
    </div>

    <div class="footer">
      <p>数据更新于 {{ currentDate }} | 最终解释权归SeeAI平台所有</p>
      <p>tipes：</p>
      <p>Question:哪些动作是有效积分的？</p>
      <p>Anwser:比如参加活动或提出有建设性的意见建议，或执行社区发放任务都可以获得积分</p>
      <p> 参加活动视本次活动中角色得分不同，如果是观众得保底1分，作为嘉宾出席得6分</p>
      <p> 关于提出社区建议，被采纳得6分，自行提出建议并执行完成得12分</p>
      <p> 完成社区发放的小任务得6分</p>
      <p> 具体参考SeeAI积分规则文档：https://docs.qq.com/doc/DR2tFeVNHYXdPb0pX</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { getLeaderboard } from '../api'

const loading = ref(false)
const tableData = ref([])
const selectedYear = ref('')
const selectedMonth = ref('')

const currentDate = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
})

const availableYears = computed(() => {
  const years = new Set(tableData.value.map(item => item.year).filter(year => year))
  return Array.from(years).sort()
})

const availableMonths = computed(() => {
  let filtered = tableData.value
  if (selectedYear.value) {
    filtered = tableData.value.filter(item => item.year === selectedYear.value)
  }
  const months = new Set(filtered.map(item => item.month))
  return Array.from(months).sort()
})

const filteredData = computed(() => {
  let result = tableData.value
  
  if (selectedYear.value) {
    result = result.filter(item => item.year === selectedYear.value)
  }
  
  if (selectedMonth.value) {
    result = result.filter(item => item.month === selectedMonth.value)
  }
  
  return result
})

const handleYearChange = () => {
  console.log('Selected year:', selectedYear.value)
}

const handleMonthChange = () => {
  console.log('Selected month:', selectedMonth.value)
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getLeaderboard()
    if (res.code === 0 && res.data) {
      tableData.value = res.data.records || []
      
      const now = new Date()
      const currentYear = now.getFullYear().toString()
      const currentMonth = (now.getMonth() + 1).toString().padStart(2, '0')
      
      if (tableData.value.length > 0) {
        if (availableYears.value.includes(currentYear)) {
          selectedYear.value = currentYear
        } else if (availableYears.value.length > 0) {
          selectedYear.value = availableYears.value[availableYears.value.length - 1]
        }
        
        if (availableMonths.value.length > 0) {
          const currentMonthStr = availableMonths.value.find(m => 
            m.includes(`-${currentMonth}`) || m.includes(`年${currentMonth}`)
          )
          if (currentMonthStr) {
            selectedMonth.value = currentMonthStr
          } else {
            selectedMonth.value = availableMonths.value[availableMonths.value.length - 1]
          }
        }
      }
    }
  } catch (error) {
    console.error('Failed to fetch leaderboard:', error)
  } finally {
    loading.value = false
    nextTick(() => {
      createParticles()
    })
  }
}

const createParticles = () => {
  const particlesContainer = document.getElementById('particles')
  if (!particlesContainer) return

  particlesContainer.innerHTML = ''
  const particleCount = 30

  for (let i = 0; i < particleCount; i++) {
    const particle = document.createElement('div')
    particle.classList.add('particle')

    const size = Math.random() * 80 + 20
    const posX = Math.random() * 100
    const posY = Math.random() * 100

    particle.style.width = `${size}px`
    particle.style.height = `${size}px`
    particle.style.left = `${posX}%`
    particle.style.top = `${posY}%`

    const animationDuration = Math.random() * 20 + 10
    particle.style.animation = `float ${animationDuration}s infinite ease-in-out`
    particle.style.animationDelay = `${Math.random() * 5}s`

    particlesContainer.appendChild(particle)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.leaderboard-page {
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: linear-gradient(135deg, #f0f9f0 0%, #e6f5e6 100%);
  color: rgb(62, 62, 62);
  min-height: 100vh;
  padding: 40px 20px;
  position: relative;
  overflow-x: hidden;
}

.particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  overflow: hidden;
}

.particle {
  position: absolute;
  background: linear-gradient(45deg, #00d100, #3da742);
  border-radius: 50%;
  opacity: 0.1;
}

.header {
  text-align: center;
  padding: 30px 0;
  margin-bottom: 30px;
  position: relative;
  z-index: 2;
}

.decorative-element {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 100px;
  height: 100px;
  background: linear-gradient(45deg, #00d100, #3da742);
  clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
  opacity: 0.15;
}

.header h1 {
  color: #3da742;
  font-size: 3.5rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 10px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.selector-group {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.selector-group .el-select {
  width: 180px;
}

.selector-group :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(61, 167, 66, 0.1);
}

.selector-group :deep(.el-input__inner) {
  color: #3da742;
  font-weight: 600;
  font-size: 1.2rem;
}

.header p {
  color: rgb(160, 160, 160);
  font-size: 1.2rem;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

.container {
  max-width: 900px;
  margin: 0 auto 30px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 15px 40px rgba(0, 100, 0, 0.12);
  overflow: hidden;
  position: relative;
  z-index: 2;
}

.ranking-table {
  width: 100%;
  border-collapse: collapse;
}

.ranking-table thead {
  background: linear-gradient(to right, #00d100, #3da742);
  color: white;
}

.ranking-table th {
  padding: 20px 15px;
  text-align: center;
  font-weight: 600;
  font-size: 1.2rem;
}

.ranking-table th:first-child {
  border-top-left-radius: 20px;
}

.ranking-table th:last-child {
  border-top-right-radius: 20px;
}

.ranking-table tbody tr {
  border-bottom: 1px solid rgba(114, 188, 106, 0.2);
  transition: all 0.3s ease;
}

.ranking-table tbody tr:hover {
  background-color: rgba(114, 188, 106, 0.05);
}

.ranking-table td {
  padding: 18px 15px;
  font-size: 1.1rem;
  font-weight: 500;
  text-align: center;
}

.ranking-table td:first-child {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.rank {
  font-weight: 700;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(61, 167, 66, 0.1);
  color: #3da742;
}

.participant-name {
  font-weight: 600;
  color: #303133;
}

.top-3 .rank {
  color: white;
}

.rank-1 .rank {
  background: linear-gradient(135deg, #ffd700, #ffa500);
}

.rank-2 .rank {
  background: linear-gradient(135deg, #c0c0c0, #a0a0a0);
}

.rank-3 .rank {
  background: linear-gradient(135deg, #cd7f32, #a56a2b);
}

.score {
  display: inline-block;
  padding: 8px 18px;
  border-radius: 30px;
  background: linear-gradient(90deg, #00d100, #3da742);
  color: white;
  font-weight: 700;
  min-width: 80px;
  text-align: center;
  box-shadow: 0 4px 10px rgba(0, 209, 0, 0.25);
}

.top-3 .score {
  box-shadow: 0 4px 15px rgba(0, 209, 0, 0.4);
  padding: 10px 20px;
  font-size: 1.2rem;
}

.footer {
  text-align: center;
  padding: 25px 0;
  color: rgb(160, 160, 160);
  font-size: 1rem;
  position: relative;
  z-index: 2;
  background: rgba(249, 249, 249, 0.8);
  border-top: 1px solid rgba(114, 188, 106, 0.1);
}

@keyframes float {
  0% {
    transform: translateY(0px);
  }

  50% {
    transform: translateY(-10px);
  }

  100% {
    transform: translateY(0px);
  }
}

@media (max-width: 768px) {
  .leaderboard-page {
    padding: 20px 10px;
  }

  .header h1 {
    font-size: 2.5rem;
  }

  .selector-group {
    flex-direction: column;
    gap: 10px;
  }

  .selector-group .el-select {
    width: 100%;
    max-width: 250px;
  }

  .ranking-table th {
    padding: 15px 10px;
    font-size: 1rem;
  }

  .ranking-table td {
    padding: 15px 10px;
    font-size: 1rem;
  }
}
</style>
