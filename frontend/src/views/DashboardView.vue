<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <div class="welcome-card">
          <div class="welcome-header">
            <el-avatar :size="64" :src="user?.avatar || 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'" />
            <div class="welcome-text">
              <h2>欢迎回来，{{ user?.name }}</h2>
              <p class="role-badge">{{ user?.role?.toUpperCase() }}</p>
            </div>
          </div>
          <div class="date-display">
            <p>{{ currentDate }}</p>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 管理员/经理 概览 -->
    <div v-if="['admin', 'manager'].includes(user?.role)" class="stats-section">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-blue">
                <el-icon><Box /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-label">今日入库量</div>
                <div class="stat-value">{{ stats.inbound_today ?? '-' }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-green">
                <el-icon><SoldOut /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-label">今日出库量</div>
                <div class="stat-value">{{ stats.outbound_today ?? '-' }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bg-orange">
                <el-icon><Goods /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-label">在售商品 SKU</div>
                <div class="stat-value">{{ stats.sku_count ?? '-' }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="chart-row">
        <el-col :span="24">
          <el-card shadow="hover" class="chart-card">
            <template #header>
              <div class="chart-header">
                <span>近7天业务趋势</span>
              </div>
            </template>
            <div ref="chartRef" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="chart-row">
        <el-col :span="24">
          <el-card shadow="hover" class="chart-card">
            <template #header>
              <div class="chart-header">
                <span>库存分布分析</span>
                <div class="chart-filters">
                  <el-select 
                    v-model="pieFilter.warehouse_code" 
                    placeholder="按仓库查看" 
                    clearable 
                    style="width: 180px" 
                    @change="onWarehouseChange"
                  >
                    <el-option
                      v-for="item in warehouseOptions"
                      :key="item.code"
                      :label="item.name"
                      :value="item.code"
                    />
                  </el-select>
                  
                  <span class="filter-separator">或</span>

                  <el-select
                    v-model="pieFilter.product_sku"
                    placeholder="按商品查看分布"
                    clearable
                    filterable
                    remote
                    :remote-method="remoteSearchProducts"
                    :loading="productSearchLoading"
                    style="width: 220px"
                    @change="onProductChange"
                  >
                    <el-option
                      v-for="item in productOptions"
                      :key="item.sku_code"
                      :label="`${item.spu_name} (${item.sku_code})`"
                      :value="item.sku_code"
                    />
                  </el-select>
                  <el-button type="primary" link @click="updatePieChart" style="margin-left: 10px;">刷新</el-button>
                </div>
              </div>
            </template>
            <div ref="pieChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 操作员 任务列表 -->
    <div v-if="['operator'].includes(user?.role)" class="task-section">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover" header="待处理入库任务">
            <el-table :data="inboundTasks" style="width: 100%" stripe>
              <el-table-column prop="id" label="单号" width="140" />
              <el-table-column prop="supplier" label="供应商" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag type="warning" effect="plain">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <el-button link type="primary" size="small" @click="$router.push('/inbound')">处理</el-button>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover" header="待处理拣货任务">
            <el-table :data="pickingTasks" style="width: 100%" stripe>
              <el-table-column prop="id" label="单号" width="140" />
              <el-table-column prop="customer" label="客户" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag type="danger" effect="plain">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <el-button link type="primary" size="small" @click="$router.push('/outbound')">处理</el-button>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 查询员/Viewer -->
    <div v-if="['viewer'].includes(user?.role)" class="viewer-section">
      <el-card shadow="hover" header="系统公告">
        <div class="notice-content">
          <p>欢迎使用智仓通 WMS 系统。</p>
          <p>您当前权限为：<el-tag>访客</el-tag></p>
          <p>请联系管理员分配更多权限。</p>
        </div>
      </el-card>
    </div>

  </div>
</template>

<script setup>
import { computed, ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useAuthStore } from '../stores/auth'
import { Box, SoldOut, Goods } from '@element-plus/icons-vue'
import request from '../utils/request'
import * as echarts from 'echarts'

const authStore = useAuthStore()
const user = computed(() => authStore.user)
const currentDate = new Date().toLocaleDateString('zh-CN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })

const stats = ref({
  inbound_today: null,
  outbound_today: null,
  sku_count: null,
  trend_7d: []
})
const inboundTasks = ref([])
const pickingTasks = ref([])

const chartRef = ref(null)
const pieChartRef = ref(null)
let myChart = null
let pieChart = null

const pieFilter = ref({
  warehouse_code: '',
  product_sku: ''
})
const warehouseOptions = ref([])
const productOptions = ref([])
const productSearchLoading = ref(false)

const onWarehouseChange = (val) => {
  if (val) {
    pieFilter.value.product_sku = ''
  }
  updatePieChart()
}

const onProductChange = (val) => {
  if (val) {
    pieFilter.value.warehouse_code = ''
  }
  updatePieChart()
}

const remoteSearchProducts = async (query) => {
  productSearchLoading.value = true
  try {
    const res = await request({
      url: '/products',
      method: 'get',
      params: { keyword: query, pageSize: 20 }
    })
    productOptions.value = res.data?.list || []
  } catch {
    productOptions.value = []
  } finally {
    productSearchLoading.value = false
  }
}

const initChart = () => {
  if (chartRef.value) {
    myChart = echarts.init(chartRef.value)
  }
  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
  }
}

const updatePieChart = async () => {
  try {
    const res = await request({
      url: '/dashboard/inventory-pie',
      method: 'get',
      params: pieFilter.value
    })
    const data = res.data || []
    
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        type: 'scroll'
      },
      series: [
        {
          name: '库存分布',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 20,
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: data
        }
      ]
    }
    pieChart?.setOption(option)
  } catch (e) {
    console.error(e)
  }
}

const updateChart = () => {
  if (!stats.value.trend_7d || stats.value.trend_7d.length === 0) return

  const dates = stats.value.trend_7d.map(item => item.date)
  const inboundData = stats.value.trend_7d.map(item => item.inbound)
  const outboundData = stats.value.trend_7d.map(item => item.outbound)

  const option = {
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
        itemStyle: { color: '#409EFF' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        }
      },
      {
        name: '出库',
        type: 'line',
        smooth: true,
        data: outboundData,
        itemStyle: { color: '#67C23A' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
          ])
        }
      }
    ]
  }
  myChart?.setOption(option)
}

const loadStats = async () => {
  // 用 allSettled 避免单个接口失败导致整页白屏
  const [resStats, resWh, resProd] = await Promise.allSettled([
    request({ url: '/dashboard/stats', method: 'get' }),
    request({ url: '/warehouses', method: 'get', params: { pageSize: 100 } }),
    request({ url: '/products', method: 'get', params: { pageSize: 50 } })
  ])

  if (resStats.status === 'fulfilled') {
    stats.value = resStats.value.data || {}
    inboundTasks.value = resStats.value.data?.inbound_tasks || []
    pickingTasks.value = resStats.value.data?.picking_tasks || []
  }
  if (resWh.status === 'fulfilled') {
    warehouseOptions.value = resWh.value.data?.list || []
  }
  if (resProd.status === 'fulfilled') {
    productOptions.value = resProd.value.data?.list || []
  }

  if (['admin', 'manager'].includes(user.value?.role)) {
    nextTick(() => {
      initChart()
      updateChart()
      updatePieChart()
    })
  }
}

const handleResize = () => {
  myChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
  loadStats()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  myChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped lang="scss">
.dashboard-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);

  .welcome-card {
    background: #fff;
    padding: 24px;
    margin-bottom: 24px;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);

    .welcome-header {
      display: flex;
      align-items: center;
      gap: 20px;

      .welcome-text {
        h2 {
          margin: 0 0 8px;
          font-size: 20px;
          color: #303133;
        }
        .role-badge {
          display: inline-block;
          background: #ecf5ff;
          color: #409eff;
          padding: 2px 10px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: bold;
          margin: 0;
        }
      }
    }
    
    .date-display {
      color: #909399;
      font-size: 14px;
    }
  }

  .stat-card {
    margin-bottom: 20px;
    border: none;
    border-radius: 8px;
    transition: all 0.3s;
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }

    .stat-content {
      display: flex;
      align-items: center;
    }

    .stat-icon {
      width: 56px;
      height: 56px;
      border-radius: 16px;
      display: flex;
      justify-content: center;
      align-items: center;
      margin-right: 20px;
      
      .el-icon {
        font-size: 28px;
        color: #fff;
      }

      &.bg-blue { background: linear-gradient(135deg, #409EFF, #79bbff); }
      &.bg-green { background: linear-gradient(135deg, #67C23A, #95d475); }
      &.bg-orange { background: linear-gradient(135deg, #E6A23C, #f3d19e); }
    }

    .stat-info {
      .stat-label {
        font-size: 14px;
        color: #909399;
        margin-bottom: 4px;
      }
      .stat-value {
        font-size: 28px;
        font-weight: bold;
        color: #303133;
      }
    }
  }

  .chart-card {
    border: none;
    border-radius: 8px;
    
    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: bold;
      font-size: 16px;
      color: #303133;
    }

    .chart-filters {
      display: flex;
      align-items: center;
      
      .filter-separator {
        margin: 0 10px;
        color: #909399;
        font-size: 14px;
      }
    }

    .chart-container {
      height: 400px;
      width: 100%;
    }
  }

  .task-section, .viewer-section {
    margin-top: 20px;
  }
  
  .notice-content {
    text-align: center;
    padding: 40px;
    color: #606266;
    
    p {
      margin: 10px 0;
    }
  }
}
</style>
