<template>
  <div class="page-container">
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
        <el-table-column prop="location_code" label="库位" min-width="120">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.location_code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="可用库存" min-width="100" align="right">
          <template #default="{ row }">
            <el-tag :type="row.available_qty > 0 ? 'success' : 'danger'" effect="dark">{{ row.available_qty }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="120" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openTransfer(row)">
              <el-icon class="el-icon--left"><Switch /></el-icon>调拨
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

    <el-dialog v-model="dialogVisible" title="库存调拨" width="600px" destroy-on-close>
      <el-form :model="form" label-width="100px" class="transfer-form">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-divider content-position="left">源信息</el-divider>
          </el-col>
          <el-col :span="12">
            <el-form-item label="SKU">
              <el-input :value="form.product_sku" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="可用数量">
              <el-input :value="form.max_qty" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="源仓库">
              <el-input :value="form.from_wh" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="源库位">
              <el-input :value="form.from_location" disabled />
            </el-form-item>
          </el-col>
          
          <el-col :span="24">
            <el-divider content-position="left">目标信息</el-divider>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="目标仓库" required>
              <el-select v-model="form.to_wh" placeholder="请选择目标仓库" filterable style="width: 100%">
                <el-option
                  v-for="item in warehouseOptions"
                  :key="item.code"
                  :label="item.name + ' (' + item.code + ')'"
                  :value="item.code"
                  :disabled="item.code === form.from_wh"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="目标库位">
              <el-input v-model="form.to_location" placeholder="可选，默认自动分配" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="调拨数量" required>
              <el-input-number v-model="form.quantity" :min="1" :max="form.max_qty" style="width: 100%" controls-position="right" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveItem">确认调拨</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, House, Switch } from '@element-plus/icons-vue'
import request from '../../utils/request'

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const filters = reactive({
  product_sku: '',
  warehouse_code: '',
})

const dialogVisible = ref(false)
const form = reactive({
  id: null,
  product_sku: '',
  from_wh: '',
  from_location: '',
  to_wh: '',
  to_location: '',
  quantity: 0,
  max_qty: 0
})

const warehouseOptions = ref([])
// const productOptions = ref([]) // Not needed as we select from row

const loadOptions = async () => {
  // Load warehouses
  const resWh = await request({ url: '/warehouses', method: 'get', params: { pageSize: 100 } })
  warehouseOptions.value = resWh.data?.list || []
}

// const dialogTitle = computed(() => (form.id ? '编辑调拨' : '新增调拨'))

const fetchList = async () => {
  loading.value = true
  try {
    // Change to fetch inventory items directly
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

const openCreate = () => {
  // Logic changed: redirect user to select row
  ElMessage.info('请在下方列表中选择库存项进行调拨')
}

const openTransfer = (row) => {
  if (row.available_qty <= 0) {
    ElMessage.warning('该库存项无可用数量，无法调拨')
    return
  }
  
  Object.assign(form, {
    id: null,
    product_sku: row.product_sku,
    from_wh: row.warehouse_code,
    from_location: row.location_code,
    to_wh: '',
    to_location: '',
    quantity: 1,
    max_qty: row.available_qty
  })
  loadOptions()
  dialogVisible.value = true
}

const saveItem = async () => {
  if (!form.to_wh) {
    ElMessage.warning('请选择目标仓库')
    return
  }
  if (form.from_wh === form.to_wh && form.from_location === form.to_location) {
    ElMessage.warning('目标位置不能与源位置相同')
    return
  }

  const payload = { ...form }
  // Only create is allowed
  await request({ url: '/inventory/transfer', method: 'post', data: payload })
  ElMessage.success('调拨成功')
  
  dialogVisible.value = false
  fetchList()
}

const removeItem = async (row) => {
  // Remove implementation
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
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.transfer-form {
  :deep(.el-form-item) {
    margin-bottom: 18px;
  }
}
</style>
