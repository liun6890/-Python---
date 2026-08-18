<template>
  <div class="page-container">
    <el-card shadow="never" class="toolbar">
      <el-form :inline="true" @submit.prevent>
        <el-form-item label="关键词">
          <el-input v-model="keyword" placeholder="出库单号/客户" clearable @keyup.enter="fetchList" />
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
                <el-table-column prop="quantity" label="数量" width="100" />
              </el-table>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="order_no" label="出库单号" min-width="160" />
        <el-table-column prop="customer_name" label="客户" min-width="140" />
        <el-table-column prop="planned_date" label="计划发货" min-width="120" />
        <el-table-column prop="reject_reason" label="驳回原因" min-width="160" />
        <el-table-column prop="status" label="状态" min-width="110">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="success" size="small" :disabled="row.status !== '待审核'" @click="approve(row)">
              通过
            </el-button>
            <el-button link type="danger" size="small" :disabled="row.status !== '待审核'" @click="reject(row)">
              驳回
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../../utils/request'

const statuses = ['待审核', '已审核', '已驳回', '已取消']

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const keyword = ref('')
const status = ref(null)

const statusTag = (s) => {
  if (s === '待审核') return 'warning'
  if (s === '已审核') return 'success'
  if (s === '已驳回') return 'danger'
  if (s === '已取消') return 'info'
  return ''
}

const fetchList = async () => {
  loading.value = true
  try {
    const res = await request({
      url: '/outbound/orders',
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

const approve = async (row) => {
  await request({ url: '/outbound/orders', method: 'put', data: { id: row.id, action: 'approve' } })
  ElMessage.success('已通过')
  fetchList()
}

const reject = async (row) => {
  const { value } = await ElMessageBox.prompt('请输入驳回原因', '驳回', { confirmButtonText: '确认', cancelButtonText: '取消' })
  await request({ url: '/outbound/orders', method: 'put', data: { id: row.id, action: 'reject', reject_reason: value } })
  ElMessage.success('已驳回')
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
