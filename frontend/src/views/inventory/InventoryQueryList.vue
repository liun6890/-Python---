<template>
  <div class="page-container">
    <el-card shadow="hover" class="search-card">
      <el-form :inline="true" :model="filters" class="search-form" @submit.prevent>
        <el-form-item label="SKU">
          <el-input v-model="filters.product_sku" placeholder="请输入SKU" clearable @keyup.enter="fetchList">
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="仓库">
          <el-input v-model="filters.warehouse_code" placeholder="请输入仓库编码" clearable @keyup.enter="fetchList">
            <template #prefix>
              <el-icon><House /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="库位">
          <el-input v-model="filters.location_code" placeholder="请输入库位编码" clearable @keyup.enter="fetchList">
            <template #prefix>
              <el-icon><Location /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="fetchList">
            <el-icon class="el-icon--left"><Search /></el-icon>查询
          </el-button>
          <el-button @click="resetSearch">
            <el-icon class="el-icon--left"><Refresh /></el-icon>重置
          </el-button>
          <el-button type="success" plain @click="exportData">
            <el-icon class="el-icon--left"><Download /></el-icon>导出
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="table-card">
      <template #header>
        <div class="card-header">
          <span>库存列表</span>
          <el-tag type="info" effect="plain">共 {{ total }} 条记录</el-tag>
        </div>
      </template>
      <el-table 
        :data="list" 
        v-loading="loading" 
        style="width: 100%" 
        :row-class-name="tableRowClassName"
        stripe
        border
        highlight-current-row
      >
        <el-table-column prop="product_sku" label="商品SKU" min-width="140" show-overflow-tooltip />
        <el-table-column prop="warehouse_code" label="仓库" min-width="120" />
        <el-table-column prop="location_code" label="库位" min-width="120">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.location_code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="库存总数" min-width="100" align="right" />
        <el-table-column prop="locked_qty" label="锁定数量" min-width="100" align="right">
          <template #default="{ row }">
            <span :class="{ 'text-danger': row.locked_qty > 0 }">{{ row.locked_qty }}</span>
          </template>
        </el-table-column>
        <el-table-column label="可用数量" min-width="100" align="right">
          <template #default="{ row }">
            <el-tag :type="row.available_qty > row.safety_stock ? 'success' : 'danger'" effect="dark">
              {{ row.available_qty }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="safety_stock" label="安全库存" min-width="100" align="right" />
        <el-table-column prop="batch_no" label="批次号" min-width="150" show-overflow-tooltip />
      </el-table>
      <div class="pager">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          :current-page="page"
          @current-change="changePage"
          @size-change="changeSize"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Download, House, Location } from '@element-plus/icons-vue'
import request from '../../utils/request'

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const filters = reactive({
  product_sku: '',
  warehouse_code: '',
  location_code: '',
})

const exportData = () => {
  ElMessage.success('导出任务已提交，请稍后在下载中心查看')
}

const tableRowClassName = ({ row }) => {
  if (row.available_qty <= row.safety_stock) {
    return 'warning-row'
  }
  return ''
}

const fetchList = async () => {
  loading.value = true
  try {
    const res = await request({
      url: '/inventory/items',
      method: 'get',
      params: {
        page: page.value,
        pageSize: pageSize.value,
        ...filters,
      },
    })
    list.value = res.data?.list || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  filters.product_sku = ''
  filters.warehouse_code = ''
  filters.location_code = ''
  page.value = 1
  fetchList()
}

const changePage = (p) => {
  page.value = p
  fetchList()
}

const changeSize = (s) => {
  pageSize.value = s
  page.value = 1
  fetchList()
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped lang="scss">
.page-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-card {
  border: none;
  border-radius: 8px;

  .search-form {
    :deep(.el-form-item) {
      margin-bottom: 0;
      margin-right: 16px;
      
      &:last-child {
        margin-right: 0;
      }
    }
  }
}

.table-card {
  border: none;
  border-radius: 8px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: bold;
    font-size: 16px;
  }
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.text-danger {
  color: var(--el-color-danger);
  font-weight: bold;
}

:deep(.el-table .warning-row) {
  --el-table-tr-bg-color: var(--el-color-warning-light-9);
}
</style>
