<template>
  <div class="page-container">
    <el-card shadow="never" class="toolbar">
      <el-form :inline="true" @submit.prevent>
        <el-form-item label="关键词">
          <el-input v-model="keyword" placeholder="入库单号/供应商" clearable @keyup.enter="fetchList" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="status" clearable placeholder="全部" style="width: 160px">
            <el-option v-for="s in statuses" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchList">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <el-table :data="list" v-loading="loading" style="width: 100%">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div style="padding: 10px 20px; background-color: #f8f9fa;">
              <h4>商品明细</h4>
              <el-table :data="row.items || []" border size="small">
                <el-table-column prop="product_sku" label="商品SKU" />
                <el-table-column prop="quantity" label="计划数量" width="100" />
                <el-table-column prop="received_qty" label="实收数量" width="100" />
                <el-table-column prop="putaway_qty" label="上架数量" width="100" />
                <el-table-column prop="location_code" label="库位" width="120" />
              </el-table>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="order_no" label="入库单号" min-width="160" />
        <el-table-column prop="warehouse_code" label="入库仓库" min-width="120" />
        <el-table-column prop="supplier_name" label="供应商" min-width="140" />
        <el-table-column prop="planned_date" label="预计到货" min-width="120" />
        <el-table-column prop="status" label="状态" min-width="110">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openDetails(row)">详情</el-button>
            <el-button link type="warning" size="small" :disabled="!canReceive(row)" @click="openReceive(row)">
              收货
            </el-button>
            <el-button link type="success" size="small" :disabled="!canPutaway(row)" @click="openPutaway(row)">
              上架
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pager">
        <el-pagination
          layout="total, prev, pager, next, sizes"
          :total="total"
          :page-size="pageSize"
          :current-page="page"
          @current-change="changePage"
          @size-change="changeSize"
        />
      </div>
    </el-card>

    <el-dialog v-model="detailsVisible" title="入库单详情" width="800px">
      <el-descriptions border :column="2">
        <el-descriptions-item label="入库单号">{{ currentOrder.order_no }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ currentOrder.supplier_name }}</el-descriptions-item>
        <el-descriptions-item label="入库仓库">{{ currentOrder.warehouse_code }}</el-descriptions-item>
        <el-descriptions-item label="预计到货">{{ currentOrder.planned_date }}</el-descriptions-item>
        <el-descriptions-item label="当前状态">
          <el-tag :type="statusTag(currentOrder.status)">{{ currentOrder.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentOrder.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <h4 style="margin-top: 20px;">商品明细</h4>
      <el-table :data="currentOrder.items || []" border size="small">
        <el-table-column prop="product_sku" label="商品SKU" />
        <el-table-column prop="quantity" label="计划数量" width="90" />
        <el-table-column prop="received_qty" label="实收数量" width="90" />
        <el-table-column prop="putaway_qty" label="上架数量" width="90" />
        <el-table-column prop="location_code" label="库位" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="detailsVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="receiveVisible" title="收货" width="900px">
      <el-table :data="receiveItems" border size="small">
        <el-table-column prop="product_sku" label="商品SKU" min-width="120" />
        <el-table-column prop="quantity" label="计划数量" width="90" />
        <el-table-column label="实收数量" width="140">
          <template #default="{ row }">
            <el-input-number v-model="row.received_qty" :min="0" :max="row.quantity" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="完成状态" width="120">
           <template #default="{ row }">
             <el-select v-model="row.completion_status" size="small">
               <el-option label="部分收货" value="partial" />
               <el-option label="已完成" value="completed" />
             </el-select>
           </template>
        </el-table-column>
        <el-table-column label="差异原因" min-width="150">
          <template #default="{ row }">
            <el-input v-model="row.reason" placeholder="如实收与计划不符请说明" size="small" />
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 10px; color: #e6a23c; font-size: 12px;">
        <el-icon><Warning /></el-icon> 注意：选择“已完成”后该条目将无法再次收货。若需分批收货，请选择“部分收货”。
      </div>
      <template #footer>
        <el-button @click="receiveVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReceive">确认收货</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="putawayVisible" title="上架" width="1000px">
      <el-table :data="putawayItems" border size="small">
        <el-table-column prop="product_sku" label="商品SKU" min-width="120" />
        <el-table-column prop="received_qty" label="实收" width="70" />
        <el-table-column label="已上架" width="70">
          <template #default="{ row }">
             {{ row.original_putaway_qty }}
          </template>
        </el-table-column>
        <el-table-column label="本次上架" width="140">
          <template #default="{ row }">
            <el-input-number v-model="row.putaway_qty" :min="row.original_putaway_qty" :max="row.received_qty" style="width: 100%" />
          </template>
        </el-table-column>
        <el-table-column label="库位" width="150">
          <template #default="{ row }">
            <el-select
              v-model="row.location_code"
              filterable
              allow-create
              default-first-option
              placeholder="选择库位"
              style="width: 100%"
              @change="updatePutawayPreview(row)"
            >
              <el-option
                v-for="loc in row.location_options || []"
                :key="loc"
                :label="loc"
                :value="loc"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="完成状态" width="110">
           <template #default="{ row }">
             <el-select v-model="row.completion_status" size="small">
               <el-option label="部分上架" value="partial" />
               <el-option label="已完成" value="completed" />
             </el-select>
           </template>
        </el-table-column>
        <el-table-column label="差异原因" min-width="140">
          <template #default="{ row }">
            <el-input v-model="row.reason" placeholder="说明原因" size="small" />
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 10px; color: #e6a23c; font-size: 12px;">
        <el-icon><Warning /></el-icon> 注意：选择“已完成”后该条目将无法再次上架。若需分批上架，请选择“部分上架”。
      </div>

      <div v-if="hasAllocationPreview" style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 4px;">
        <div style="font-weight: bold; margin-bottom: 10px; color: #409eff; display: flex; align-items: center;">
          <el-icon style="margin-right: 5px;"><InfoFilled /></el-icon>
          上架方案预览 (单库位上限: 100)
        </div>
        <el-table :data="allocationPreview" size="small" border stripe>
          <el-table-column prop="product_sku" label="商品SKU" width="180" />
          <el-table-column prop="location_code" label="分配库位" />
          <el-table-column prop="quantity" label="上架数量" width="100" />
        </el-table>
        <div style="margin-top: 10px; font-size: 12px; color: #909399;">
          * 系统检测到大批量上架，已根据库位余量自动规划分层存储方案。
        </div>
      </div>

      <template #footer>
        <el-button @click="putawayVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPutaway">确认上架</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled, Warning } from '@element-plus/icons-vue'
import request from '../../utils/request'

const statuses = ['已审核', '部分收货', '已收货', '部分上架', '已完成', '已驳回', '已取消']

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const keyword = ref('')
const status = ref(null)

const statusTag = (s) => {
  if (s === '已审核') return 'warning'
  if (s === '部分收货') return 'primary'
  if (s === '已收货') return 'info'
  if (s === '部分上架') return 'primary'
  if (s === '已完成') return 'success'
  return ''
}

const canReceive = (row) => ['已审核', '部分收货'].includes(row.status)
const canPutaway = (row) => ['已收货', '部分上架'].includes(row.status) || (row.status === '部分收货' && (row.items || []).some(i => i.received_qty > 0))

const detailsVisible = ref(false)
const receiveVisible = ref(false)
const putawayVisible = ref(false)
const currentOrder = ref({})
const currentOrderId = ref(null)
const receiveItems = ref([])
const putawayItems = ref([])
const currentWarehouseCode = ref('')
const allocationPreview = ref([])

const hasAllocationPreview = computed(() => allocationPreview.value.length > 0)

const updatePutawayPreview = async () => {
  const batchItems = []
  
  for (const item of putawayItems.value) {
    // Only preview the *increment*, not the total
    const increment = item.putaway_qty - item.original_putaway_qty
    if (increment > 0) {
      batchItems.push({
        warehouse_code: currentWarehouseCode.value,
        product_sku: item.product_sku,
        quantity: increment,
        location_code: item.location_code
      })
    }
  }
  
  if (batchItems.length === 0) {
    allocationPreview.value = []
    return
  }

  try {
    const res = await request({
      url: '/inbound/orders',
      method: 'get',
      params: {
        action: 'putaway_preview_batch',
        items: JSON.stringify(batchItems)
      }
    })
    allocationPreview.value = res.data?.allocations || []
  } catch (e) {
    console.error('Preview error', e)
  }
}

// Watch for changes in putaway items to update preview, but debounce or check if value actually changed meaningfully
let previewTimeout = null
watch(() => putawayItems.value, (newVal) => {
  if (previewTimeout) clearTimeout(previewTimeout)
  previewTimeout = setTimeout(() => {
    updatePutawayPreview()
  }, 500)
}, { deep: true })

const openDetails = (row) => {
  currentOrder.value = row
  detailsVisible.value = true
}

const fetchList = async () => {
  loading.value = true
  try {
    const res = await request({
      url: '/inbound/orders',
      method: 'get',
      params: {
        page: page.value,
        pageSize: pageSize.value,
        keyword: keyword.value,
        status: status.value || undefined,
      },
    })
    list.value = res.data?.list || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  keyword.value = ''
  status.value = null
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

const openReceive = (row) => {
  currentOrderId.value = row.id
  receiveItems.value = (row.items || []).map(i => {
    // Determine default completion status
    const isFull = (i.received_qty ?? 0) >= i.quantity
    return {
      id: i.id,
      product_sku: i.product_sku,
      quantity: i.quantity,
      received_qty: i.received_qty ?? 0,
      completion_status: isFull ? 'completed' : 'partial',
      reason: i.reason || ''
    }
  })
  receiveVisible.value = true
}

const submitReceive = async () => {
  await request({
    url: '/inbound/orders',
    method: 'put',
    data: {
      id: currentOrderId.value,
      action: 'receive',
      receive_items: receiveItems.value.map(i => ({ 
        id: i.id, 
        received_qty: i.received_qty,
        completion_status: i.completion_status,
        reason: i.reason
      }))
    }
  })
  ElMessage.success('已确认收货')
  receiveVisible.value = false
  fetchList()
}

const openPutaway = (row) => {
  currentOrderId.value = row.id
  currentWarehouseCode.value = row.warehouse_code || ''
  allocationPreview.value = [] // Reset preview when opening
  putawayItems.value = (row.items || []).map(i => {
    // If there are multiple locations, just take the first one as the starting point for input
    let startLoc = i.location_code || ''
    if (startLoc.includes(',')) {
      startLoc = startLoc.split(',')[0].trim()
    }
    
    // Determine default completion status
    const isFull = (i.putaway_qty ?? 0) >= (i.received_qty ?? 0)
    
    return {
      id: i.id,
      product_sku: i.product_sku,
      received_qty: i.received_qty ?? 0,
      original_putaway_qty: i.putaway_qty ?? 0,
      putaway_qty: i.putaway_qty ?? 0,
      location_code: startLoc,
      location_options: [],
      completion_status: isFull ? 'completed' : 'partial',
      reason: i.reason || ''
    }
  })
  loadLocationOptions()
  putawayVisible.value = true
}

const loadLocationOptions = async () => {
  const warehouseCode = currentWarehouseCode.value
  const tasks = putawayItems.value.map(async (row) => {
    const res = await request({
      url: '/inventory/items',
      method: 'get',
      params: {
        pageSize: 1000,
        product_sku: row.product_sku,
        warehouse_code: warehouseCode
      },
    })
    const invList = res.data?.list || []
    
    // Extract unique location codes, splitting comma-separated strings if they exist
    const locs = new Set()
    invList.forEach(i => {
      if (i.location_code) {
        i.location_code.split(',').forEach(c => {
          const trimmed = c.trim()
          if (trimmed) locs.add(trimmed)
        })
      }
    })
    
    // Also add the current row's location codes if any
    if (row.location_code) {
      row.location_code.split(',').forEach(c => {
        const trimmed = c.trim()
        if (trimmed) locs.add(trimmed)
      })
    }
    
    row.location_options = Array.from(locs)
  })
  await Promise.all(tasks)
}

const submitPutaway = async () => {
  await request({
    url: '/inbound/orders',
    method: 'put',
    data: {
      id: currentOrderId.value,
      action: 'putaway',
      putaway_items: putawayItems.value.map(i => ({
        id: i.id,
        putaway_qty: i.putaway_qty,
        location_code: i.location_code,
        completion_status: i.completion_status,
        reason: i.reason
      }))
    }
  })
  ElMessage.success('已确认上架')
  putawayVisible.value = false
  fetchList()
}

onMounted(() => {
  fetchList()
})

onBeforeUnmount(() => {
  if (previewTimeout) {
    clearTimeout(previewTimeout)
    previewTimeout = null
  }
})
</script>

<style scoped lang="scss">
.page-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  :deep(.el-form-item) {
    margin-bottom: 0;
  }
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
