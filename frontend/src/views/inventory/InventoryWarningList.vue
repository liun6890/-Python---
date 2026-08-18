<template>
  <div class="page-container">
    <el-alert
      v-if="total > 0"
      :title="`当前有 ${total} 个库存项低于安全库存，请及时补货！`"
      type="warning"
      show-icon
      class="warning-alert"
    />

    <el-card shadow="hover" class="search-card">
      <el-form :inline="true" :model="filters" class="search-form" @submit.prevent>
        <el-form-item label="SKU">
          <el-input v-model="filters.product_sku" placeholder="请输入SKU" clearable @keyup.enter="fetchList">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item label="仓库">
          <el-input v-model="filters.warehouse_code" placeholder="请输入仓库编码" clearable @keyup.enter="fetchList">
            <template #prefix><el-icon><House /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="fetchList">
            <el-icon class="el-icon--left"><Search /></el-icon>查询
          </el-button>
          <el-button @click="resetSearch">
            <el-icon class="el-icon--left"><Refresh /></el-icon>重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="table-card">
      <el-table :data="list" v-loading="loading" style="width: 100%" stripe border highlight-current-row>
        <el-table-column prop="product_sku" label="SKU" min-width="140" show-overflow-tooltip />
        <el-table-column prop="warehouse_code" label="仓库" min-width="120" />
        <el-table-column prop="quantity" label="总库存" min-width="100" align="right" />
        <el-table-column prop="locked_qty" label="锁定数量" min-width="100" align="right" />
        <el-table-column prop="available_qty" label="可用库存" min-width="100" align="right">
          <template #default="{ row }">
            <span class="text-danger font-bold">{{ row.available_qty }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="safety_stock" label="安全库存" min-width="100" align="right" />
        <el-table-column prop="shortage" label="缺口数量" min-width="100" align="right">
          <template #default="{ row }">
            <el-tag type="danger" effect="dark">{{ row.shortage }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="120" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="createPurchase(row)">
              <el-icon class="el-icon--left"><ShoppingCart /></el-icon>一键补货
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pager">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          :page-sizes="[10, 20, 50]"
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
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Refresh, House, ShoppingCart } from '@element-plus/icons-vue'
import request from '../../utils/request'

const router = useRouter()
const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const filters = reactive({
  product_sku: '',
  warehouse_code: '',
})

const createPurchase = (row) => {
  router.push({
    path: '/inbound/create',
    query: {
      product_sku: row.product_sku,
      warehouse_code: row.warehouse_code,
      quantity: row.shortage
    }
  })
}

const fetchList = async () => {
  loading.value = true
  try {
    const res = await request({
      url: '/inventory/warning',
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

.warning-alert {
  margin-bottom: 8px;
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
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.text-danger {
  color: var(--el-color-danger);
}

.font-bold {
  font-weight: bold;
}
</style>
