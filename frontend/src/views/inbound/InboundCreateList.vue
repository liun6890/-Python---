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
          <el-button type="success" @click="openCreate">新增入库单</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <el-table :data="list" v-loading="loading" style="width: 100%">
        <el-table-column prop="order_no" label="入库单号" min-width="160" />
        <el-table-column prop="supplier_name" label="供应商" min-width="140" />
        <el-table-column prop="planned_date" label="预计到货" min-width="120" />
        <el-table-column prop="reject_reason" label="驳回原因" min-width="160" />
        <el-table-column prop="status" label="状态" min-width="110">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openDetails(row)">详情</el-button>
            <el-button link type="primary" size="small" :disabled="!canEdit(row)" @click="openEdit(row)">编辑</el-button>
            <el-button link type="warning" size="small" :disabled="!canSubmit(row)" @click="submitOrder(row)">
              提交
            </el-button>
            <el-button link type="danger" size="small" :disabled="row.status === '已取消'" @click="cancelOrder(row)">
              取消
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px">
      <el-form :model="form" label-width="90px" :disabled="isDetails">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="入库单号">
              <el-input v-model="form.order_no" placeholder="保存后自动生成" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商">
              <el-select v-model="form.supplier_name" filterable placeholder="选择供应商" style="width: 100%">
                <el-option
                  v-for="item in supplierList"
                  :key="item.name"
                  :label="item.name"
                  :value="item.name"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入库仓库">
              <el-select v-model="form.warehouse_code" filterable placeholder="选择仓库" style="width: 100%">
                <el-option
                  v-for="item in warehouseList"
                  :key="item.code"
                  :label="item.name + ' (' + item.code + ')'"
                  :value="item.code"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预计到货">
              <el-date-picker v-model="form.planned_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="当前状态">
              <el-tag :type="statusTag(form.status)">{{ form.status }}</el-tag>
            </el-form-item>
          </el-col>
          <el-col :span="24" v-if="form.reject_reason">
            <el-form-item label="驳回原因">
              <el-alert :title="form.reject_reason" type="error" :closable="false" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input v-model="form.remark" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
        </el-row>

        <div style="margin-bottom: 10px; font-weight: bold; border-bottom: 1px solid #eee; padding-bottom: 5px;">
          <span>商品明细</span>
          <el-button v-if="!isDetails" type="primary" link size="small" style="float: right" @click="addItem">+ 添加商品</el-button>
        </div>
        
        <el-table :data="form.items" border style="width: 100%" size="small">
          <el-table-column label="商品SKU" min-width="180">
            <template #default="{ row }">
              <el-select v-model="row.product_sku" filterable placeholder="选择商品" style="width: 100%">
                <el-option
                  v-for="item in productList"
                  :key="item.sku_code"
                  :label="item.spu_name + ' (' + item.sku_code + ')'"
                  :value="item.sku_code"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="数量" width="150">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="1" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column v-if="!isDetails" label="操作" width="80" align="center">
            <template #default="{ $index }">
              <el-button type="danger" link @click="removeItem($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ isDetails ? '关闭' : '取消' }}</el-button>
        <el-button v-if="!isDetails" type="primary" @click="saveItem">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../../utils/request'

const route = useRoute()
const statuses = ['草稿', '待审核', '已审核', '已收货', '已完成', '已驳回', '已取消']

const list = ref([])
const productList = ref([])
const supplierList = ref([])
const warehouseList = ref([])
const loading = ref(false)
const isDetails = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const keyword = ref('')
const status = ref(null)

const dialogVisible = ref(false)
const form = reactive({
  id: null,
  order_no: '',
  supplier_name: '',
  warehouse_code: '',
  planned_date: '',
  status: '草稿',
  remark: '',
  reject_reason: '',
  items: []
})

const dialogTitle = computed(() => {
  if (isDetails.value) return '入库单详情'
  return form.id ? '编辑入库单' : '新增入库单'
})

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

const fetchProducts = async () => {
  try {
    const res = await request({ url: '/products', method: 'get', params: { page: 1, pageSize: 200 } })
    productList.value = res.data?.list || []
  } catch { productList.value = [] }
}

const fetchSuppliers = async () => {
  try {
    const res = await request({ url: '/suppliers', method: 'get', params: { page: 1, pageSize: 200 } })
    supplierList.value = res.data?.list || []
  } catch { supplierList.value = [] }
}

const fetchWarehouses = async () => {
  try {
    const res = await request({ url: '/warehouses', method: 'get', params: { page: 1, pageSize: 200 } })
    warehouseList.value = res.data?.list || []
  } catch { warehouseList.value = [] }
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

const openCreate = () => {
  isDetails.value = false
  Object.assign(form, {
    id: null,
    order_no: '',       // 由后端生成，保存后显示
    supplier_name: '',
    warehouse_code: '',
    planned_date: new Date().toISOString().slice(0, 10),
    status: '草稿',
    remark: '',
    reject_reason: '',
    items: []
  })
  dialogVisible.value = true
}

const openEdit = (row) => {
  isDetails.value = false
  // Deep copy to avoid reference issues, especially with items array
  const data = JSON.parse(JSON.stringify(row))
  Object.assign(form, {
    id: data.id,
    order_no: data.order_no,
    supplier_name: data.supplier_name,
    warehouse_code: data.warehouse_code,
    planned_date: data.planned_date,
    status: data.status,
    remark: data.remark,
    reject_reason: data.reject_reason,
    items: data.items || []
  })
  dialogVisible.value = true
}

const openDetails = (row) => {
  isDetails.value = true
  const data = JSON.parse(JSON.stringify(row))
  Object.assign(form, {
    id: data.id,
    order_no: data.order_no,
    supplier_name: data.supplier_name,
    warehouse_code: data.warehouse_code,
    planned_date: data.planned_date,
    status: data.status,
    remark: data.remark,
    reject_reason: data.reject_reason,
    items: data.items || []
  })
  dialogVisible.value = true
}

const canEdit = (row) => ['草稿', '已驳回'].includes(row.status)

const addItem = () => {
  form.items.push({
    product_sku: '',
    quantity: 1
  })
}

const removeItem = (index) => {
  form.items.splice(index, 1)
}

const canSubmit = (row) => ['草稿', '已驳回'].includes(row.status)

const saveItem = async () => {
  try {
    const payload = { ...form }
    if (payload.id) {
      await request({ url: '/inbound/orders', method: 'put', data: payload })
      ElMessage.success('更新成功')
    } else {
      const res = await request({ url: '/inbound/orders', method: 'post', data: payload })
      // 回显后端生成的单号
      if (res.data?.order_no) {
        ElMessage.success(`创建成功，单号：${res.data.order_no}`)
      } else {
        ElMessage.success('创建成功')
      }
    }
    dialogVisible.value = false
    fetchList()
  } catch {
    // 错误已由 request 拦截器弹出，此处不重复提示
  }
}

const submitOrder = async (row) => {
  await request({ url: '/inbound/orders', method: 'put', data: { id: row.id, action: 'submit' } })
  ElMessage.success('提交成功')
  fetchList()
}

const cancelOrder = async (row) => {
  await ElMessageBox.confirm('确认取消该入库单吗？', '提示', { type: 'warning' })
  await request({ url: '/inbound/orders', method: 'put', data: { id: row.id, action: 'cancel' } })
  ElMessage.success('已取消')
  fetchList()
}

onMounted(() => {
  fetchList()
  fetchProducts()
  fetchSuppliers()
  fetchWarehouses()

  // 从告警页跳转带参打开创建弹窗
  if (route.query.product_sku && route.query.warehouse_code) {
    openCreate()
    form.warehouse_code = String(route.query.warehouse_code).slice(0, 50)
    if (route.query.quantity) {
      const qty = Math.max(1, Math.min(99999, parseInt(route.query.quantity) || 1))
      form.items = [{
        product_sku: String(route.query.product_sku).slice(0, 50),
        quantity: qty
      }]
    }
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
