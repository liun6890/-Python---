<template>
  <div class="page-container">
    <el-card shadow="hover" class="search-card">
      <el-form :inline="true" class="search-form" @submit.prevent>
        <el-form-item label="关键词">
          <el-input v-model="keyword" placeholder="入库单号/供应商" clearable @keyup.enter="fetchList">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="status" clearable filterable placeholder="全部" style="width: 160px">
            <el-option v-for="s in statuses" :key="s" :label="s" :value="s" />
          </el-select>
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
        <el-table-column prop="order_no" label="入库单号" min-width="160" show-overflow-tooltip />
        <el-table-column prop="warehouse_code" label="入库仓库" min-width="120" />
        <el-table-column prop="supplier_name" label="供应商" min-width="140" show-overflow-tooltip />
        <el-table-column prop="planned_date" label="预计到货" min-width="120" sortable />
        <el-table-column label="阶段" min-width="120">
          <template #default="{ row }">
            <el-tag type="info" effect="plain">{{ stageLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" effect="dark">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="计划数" width="90" align="right">
          <template #default="{ row }">
            {{ sumQty(row.items, 'quantity') }}
          </template>
        </el-table-column>
        <el-table-column label="实收数" width="90" align="right">
          <template #default="{ row }">
            <span :class="{'text-success': sumQty(row.items, 'received_qty') > 0}">
              {{ sumQty(row.items, 'received_qty') }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="上架数" width="90" align="right">
          <template #default="{ row }">
             <span :class="{'text-primary': sumQty(row.items, 'putaway_qty') > 0}">
              {{ sumQty(row.items, 'putaway_qty') }}
             </span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="140" show-overflow-tooltip />
        <el-table-column label="操作" width="160" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openDetails(row)">
              <el-icon><Document /></el-icon>详情
            </el-button>
            <el-button link type="info" size="small" @click="openLogs(row)">
              <el-icon><Memo /></el-icon>日志
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

    <el-dialog v-model="detailsVisible" title="入库单详情" width="800px" destroy-on-close>
      <el-descriptions border :column="2" class="mb-4">
        <el-descriptions-item label="入库单号">{{ currentOrder.order_no }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ currentOrder.supplier_name }}</el-descriptions-item>
        <el-descriptions-item label="入库仓库">{{ currentOrder.warehouse_code }}</el-descriptions-item>
        <el-descriptions-item label="预计到货">{{ currentOrder.planned_date }}</el-descriptions-item>
        <el-descriptions-item label="当前状态">
          <el-tag :type="statusTag(currentOrder.status)">{{ currentOrder.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentOrder.remark || '-' }}</el-descriptions-item>
        <el-descriptions-item v-if="currentOrder.reject_reason" label="驳回原因" :span="2">
          <span class="text-danger">{{ currentOrder.reject_reason }}</span>
        </el-descriptions-item>
      </el-descriptions>
      
      <div class="section-title">商品明细</div>
      <el-table :data="currentOrder.items || []" border size="small" stripe>
        <el-table-column prop="product_sku" label="商品SKU" />
        <el-table-column prop="quantity" label="计划数量" width="100" align="right" />
        <el-table-column prop="received_qty" label="实收数量" width="100" align="right" />
        <el-table-column prop="putaway_qty" label="上架数量" width="100" align="right" />
        <el-table-column prop="location_code" label="库位" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="detailsVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="logsVisible" title="操作日志" width="700px">
      <el-table :data="logList" border size="small" v-loading="logLoading" stripe>
        <el-table-column prop="created_at" label="时间" width="160" />
        <el-table-column prop="operator" label="操作人" width="100" />
        <el-table-column prop="action" label="动作" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detail" label="详情" show-overflow-tooltip />
      </el-table>
      <template #footer>
        <el-button @click="logsVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search, Refresh, Document, Memo } from '@element-plus/icons-vue'
import request from '../../utils/request'

const statuses = ['草稿', '待审核', '已审核', '已收货', '已完成', '已驳回', '已取消']

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const keyword = ref('')
const status = ref(null)

const detailsVisible = ref(false)
const currentOrder = ref({})
const logsVisible = ref(false)
const logList = ref([])
const logLoading = ref(false)

const openDetails = (row) => {
  currentOrder.value = row
  detailsVisible.value = true
}

const openLogs = async (row) => {
  logsVisible.value = true
  logLoading.value = true
  try {
    const res = await request({
      url: '/system/logs',
      method: 'get',
      params: { detail: row.order_no, action: '入库', pageSize: 100 }
    })
    logList.value = res.data?.list || []
  } finally {
    logLoading.value = false
  }
}

const statusTag = (s) => {
  if (s === '草稿') return ''
  if (s === '待审核') return 'warning'
  if (s === '已审核') return 'success'
  if (s === '已收货') return 'info'
  if (s === '已完成') return 'success'
  if (s === '已驳回') return 'danger'
  if (s === '已取消') return 'danger'
  return ''
}

const stageLabel = (s) => {
  if (['草稿', '待审核', '已驳回'].includes(s)) return '入库申请'
  if (['已审核'].includes(s)) return '入库审核'
  if (['已收货'].includes(s)) return '收货上架'
  if (['已完成'].includes(s)) return '已完成'
  if (['已取消'].includes(s)) return '已取消'
  return '入库申请'
}

const sumQty = (items, key) => {
  if (!Array.isArray(items)) return 0
  return items.reduce((acc, cur) => acc + (Number(cur[key]) || 0), 0)
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

.text-success {
  color: var(--el-color-success);
  font-weight: bold;
}

.text-primary {
  color: var(--el-color-primary);
  font-weight: bold;
}

.text-danger {
  color: var(--el-color-danger);
}

.mb-4 {
  margin-bottom: 16px;
}

.section-title {
  font-weight: bold;
  font-size: 16px;
  margin: 16px 0 8px;
  border-left: 4px solid var(--el-color-primary);
  padding-left: 8px;
}
</style>
