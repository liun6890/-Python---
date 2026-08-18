<template>
  <div class="dashboard-container">
    <!-- KPI Cards -->
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="6" v-for="(item, index) in kpiCards" :key="index">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-content">
            <div class="kpi-icon" :style="{ backgroundColor: item.color }">
              <el-icon size="24" color="#fff">
                <component :is="item.icon" />
              </el-icon>
            </div>
            <div class="kpi-info">
              <div class="kpi-label">{{ item.label }}</div>
              <div class="kpi-value">{{ item.value }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="14">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="chart-header">
              <span>近7天出入库趋势</span>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="chart-header">
              <span>库存商品 Top10 (按数量)</span>
            </div>
          </template>
          <div ref="topChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, computed } from 'vue'
import request from '../../utils/request'
import * as echarts from 'echarts'
import {
  Box,
  TopRight,
  BottomRight,
  Files
} from '@element-plus/icons-vue'

const stats = ref({})
const trendChartRef = ref(null)
const topChartRef = ref(null)
let trendChart = null
let topChart = null

// KPI Cards Configuration
const kpiCards = computed(() => [
  {
    label: '今日入库量',
    value: stats.value.kpi?.inbound_today ?? '-',
    icon: 'BottomRight',
    color: '#67C23A' // Success Green
  },
  {
    label: '今日出库量',
    value: stats.value.kpi?.outbound_today ?? '-',
    icon: 'TopRight',
    color: '#F56C6C' // Danger Red
  },
  {
    label: '库存总件数',
    value: stats.value.kpi?.inventory_amount?.toLocaleString() ?? '-',
    icon: 'Box',
    color: '#409EFF' // Primary Blue
  },
  {
    label: '在售商品 SKU',
    value: stats.value.kpi?.sku_count ?? '-',
    icon: 'Files',
    color: '#E6A23C' // Warning Orange
  }
])

const initCharts = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
  }
  if (topChartRef.value) {
    topChart = echarts.init(topChartRef.value)
  }
}

const updateCharts = () => {
  if (!stats.value) return

  // 1. Trend Chart (Line)
  const trendData = stats.value.trend_7d || []
  const dates = trendData.map(item => item.date)
  const inboundData = trendData.map(item => item.inbound)
  const outboundData = trendData.map(item => item.outbound)

  const trendOption = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['入库', '出库'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '入库',
        type: 'line',
        smooth: true,
        data: inboundData,
        itemStyle: { color: '#67C23A' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
          ])
        }
      },
      {
        name: '出库',
        type: 'line',
        smooth: true,
        data: outboundData,
        itemStyle: { color: '#F56C6C' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
            { offset: 1, color: 'rgba(245, 108, 108, 0.05)' }
          ])
        }
      }
    ]
  }
  trendChart?.setOption(trendOption)

  // 2. Top 10 Chart (Bar)
  const topData = stats.value.top10 || []
  // Sort descending just in case, though backend should handle it
  // Take top 10
  const topNames = topData.map(item => item.name)
  const topQtys = topData.map(item => item.qty)

  const topOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value'
    },
    yAxis: {
      type: 'category',
      data: topNames,
      inverse: true // Highest on top
    },
    series: [
      {
        name: '库存数量',
        type: 'bar',
        data: topQtys,
        itemStyle: {
          color: '#409EFF',
          borderRadius: [0, 4, 4, 0] // Rounded corners on right
        },
        label: {
          show: true,
          position: 'right'
        }
      }
    ]
  }
  topChart?.setOption(topOption)
}

const loadData = async () => {
  try {
    const res = await request.get('/reports/dashboard')
    stats.value = res.data || {}
    nextTick(() => {
      updateCharts()
    })
  } catch {
    // 静默失败，图表保持空白
  }
}

const handleResize = () => {
  trendChart?.resize()
  topChart?.resize()
}

onMounted(() => {
  initCharts()
  loadData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  topChart?.dispose()
})
</script>

<style scoped lang="scss">
.dashboard-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.kpi-card {
  margin-bottom: 20px;
  border: none;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .kpi-content {
    display: flex;
    align-items: center;
  }

  .kpi-icon {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-right: 16px;
  }

  .kpi-info {
    display: flex;
    flex-direction: column;

    .kpi-label {
      font-size: 14px;
      color: #909399;
      margin-bottom: 4px;
    }

    .kpi-value {
      font-size: 24px;
      font-weight: bold;
      color: #303133;
    }
  }
}

.chart-row {
  margin-top: 20px;
}

.chart-card {
  border: none;
  margin-bottom: 20px;

  .chart-header {
    font-weight: bold;
    font-size: 16px;
    color: #303133;
  }

  .chart-container {
    height: 350px;
    width: 100%;
  }
}
</style>
