<template>
  <div class="page-container">
    <el-tabs v-model="activeTab" class="stocktaking-tabs" type="border-card">
      <el-tab-pane label="实时库存盘点" name="current">
        <template #label>
          <span class="custom-tabs-label">
            <el-icon><List /></el-icon>
            <span>实时库存盘点</span>
          </span>
        </template>
        <div class="tab-content">
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
              <el-table-column prop="quantity" label="当前库存" min-width="120" align="right">
                <template #default="{ row }">
                  <span class="font-bold">{{ row.quantity }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right" align="center">
                <template #default="{ row }">
                  <el-button type="primary" size="small" @click="startStocktaking(row)">
                    <el-icon class="el-icon--left"><Edit /></el-icon>盘点
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
      </el-tab-pane>

      <el-tab-pane label="盘点历史记录" name="history">
        <template #label>
          <span class="custom-tabs-label">
            <el-icon><Timer /></el-icon>
            <span>盘点历史记录</span>
          </span>
        </template>
        <div class="tab-content">
          <el-card shadow="hover" class="table-card">
            <el-table :data="historyList" v-loading="historyLoading" style="width: 100%" stripe border>
              <el-table-column prop="product_sku" label="SKU" min-width="140" show-overflow-tooltip />
              <el-table-column prop="warehouse_code" label="仓库" min-width="120" />
              <el-table-column prop="location_code" label="库位" min-width="120" />
              <el-table-column prop="quantity_before" label="盘点前" min-width="100" align="right" />
              <el-table-column prop="quantity_after" label="盘点后" min-width="100" align="right" />
              <el-table-column prop="diff_qty" label="差异" min-width="90" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.diff_qty === 0 ? 'success' : row.diff_qty > 0 ? 'warning' : 'danger'" effect="dark">
                    {{ row.diff_qty > 0 ? '+' + row.diff_qty : row.diff_qty }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="reason" label="差异原因" min-width="150" show-overflow-tooltip />
              <el-table-column prop="created_at" label="盘点时间" min-width="160" sortable />
            </el-table>
            <div class="pager">
              <el-pagination
                background
                layout="total, sizes, prev, pager, next, jumper"
                :total="historyTotal"
                :page-sizes="[10, 20, 50]"
                :page-size="historyPageSize"
                :current-page="historyPage"
                @current-change="changeHistoryPage"
                @size-change="changeHistorySize"
              />
            </div>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="dialogVisible" title="库存盘点" width="500px" destroy-on-close>
      <el-form :model="form" label-width="100px" class="stocktaking-form">
        <el-descriptions :column="1" border size="small" class="mb-4">
          <el-descriptions-item label="仓库">{{ form.warehouse_code }}</el-descriptions-item>
          <el-descriptions-item label="SKU">{{ form.product_sku }}</el-descriptions-item>
          <el-descriptions-item label="库位">{{ form.location_code }}</el-descriptions-item>
          <el-descriptions-item label="账面数量">
            <span class="font-bold">{{ currentSystemQty }}</span>
          </el-descriptions-item>
        </el-descriptions>
        
        <el-form-item label="实盘数量" required>
          <el-input-number v-model="form.actual_qty" :min="0" style="width: 100%" controls-position="right" />
        </el-form-item>
        
        <el-form-item label="差异原因" v-if="isDiff" required>
          <el-input v-model="form.reason" placeholder="实盘与账面不符，请说明原因" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveItem">确认盘点</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, List, Timer, Edit, House } from '@element-plus/icons-vue'
import request from '../../utils/request'

const activeTab = ref('current')

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const filters = reactive({
  product_sku: '',
  warehouse_code: '',
})

// History variables
const historyList = ref([])
const historyLoading = ref(false)
const historyPage = ref(1)
const historyPageSize = ref(10)
const historyTotal = ref(0)

const dialogVisible = ref(false)
const form = reactive({
  id: null,
  product_sku: '',
  warehouse_code: '',
  location_code: '',
  actual_qty: 0,
  reason: ''
})

// Remove warehouseOptions, productOptions, locationOptions since we fetch items directly
// const warehouseOptions = ref([])
// const productOptions = ref([])
// const locationOptions = ref([])
const currentSystemQty = ref(0)

const isDiff = computed(() => {
  return form.actual_qty !== currentSystemQty.value
})

const fetchList = async () => {
  loading.value = true
  try {
    // Change API to fetch inventory items instead of stocktaking history
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

const fetchHistoryList = async () => {
  historyLoading.value = true
  try {
    const res = await request({
      url: '/inventory/stocktaking',
      method: 'get',
      params: {
        page: historyPage.value,
        pageSize: historyPageSize.value,
      },
    })
    historyList.value = res.data?.list || []
    historyTotal.value = res.data?.total || 0
  } finally {
    historyLoading.value = false
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

const changeHistoryPage = (p) => {
  historyPage.value = p
  fetchHistoryList()
}

const changeHistorySize = (s) => {
  historyPageSize.value = s
  historyPage.value = 1
  fetchHistoryList()
}

// Change openCreate logic to remove direct create button usage if needed
// Or repurpose it to select item first? The requirement says "Show items then click button"
// So maybe "openCreate" is not needed in toolbar anymore?
// Let's keep it but maybe it should redirect to inventory query or pop up a selection dialog?
// For now, let's focus on the row action.

const startStocktaking = (row) => {
  Object.assign(form, {
    id: null, // Stocktaking record is new
    product_sku: row.product_sku,
    warehouse_code: row.warehouse_code,
    location_code: row.location_code,
    actual_qty: row.quantity, // Default to current qty
    reason: ''
  })
  currentSystemQty.value = row.quantity
  dialogVisible.value = true
}

// Remove openCreate, openEdit, loadOptions, onWarehouseChange, onSkuChange, onLocationChange, updateLocationOptions
// As they are no longer needed for the dialog which is now read-only for selection

const openCreate = () => {
  // Optional: If user still wants to create from scratch, we might need the old logic.
  // But per requirement "Show items -> Click start stocktaking", the flow is row-based.
  ElMessage.info('请在下方列表中选择库存项进行盘点')
}

// ... (keep saveItem)

const saveItem = async () => {
  if (isDiff.value && !form.reason) {
    ElMessage.warning('存在盘点差异，请填写差异原因')
    return
  }

  const payload = { ...form }
  // Only create is allowed
  await request({ url: '/inventory/stocktaking', method: 'post', data: payload })
  ElMessage.success('盘点完成')
  
  dialogVisible.value = false
  fetchList()
  fetchHistoryList() // Refresh history
}

const removeItem = async (row) => {
  // Remove implementation or keep for admin cleanup?
  // Logic updated to forbid delete in list view to keep history trace
}

onMounted(() => {
  fetchList()
  fetchHistoryList()
})
</script>

<style scoped lang="scss">
.page-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stocktaking-tabs {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0,21,41,0.08);
  
  :deep(.el-tabs__content) {
    padding: 20px;
  }
}

.custom-tabs-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.search-card {
  border: none;
  border-radius: 8px;
  margin-bottom: 16px;

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

.font-bold {
  font-weight: bold;
}

.mb-4 {
  margin-bottom: 16px;
}

.stocktaking-form {
  padding: 0 10px;
}
</style>
