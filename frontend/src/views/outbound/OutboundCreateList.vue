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
          <el-button type="success" @click="openCreate">新增出库单</el-button>
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
                <el-table-column label="商品SKU" min-width="200">
                  <template #default="{ row: item }">
                    {{ getProductNameDisplay(item.product_sku) }}
                  </template>
                </el-table-column>
                <el-table-column prop="quantity" label="数量" width="100" />
              </el-table>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="order_no" label="出库单号" min-width="160" />
        <el-table-column prop="customer_name" label="客户" min-width="140" />
        <el-table-column label="出库仓库" min-width="140">
          <template #default="{ row }">
            {{ getWarehouseName(row.warehouse_code) }}
          </template>
        </el-table-column>
        <el-table-column prop="planned_date" label="计划发货" min-width="120" />
        <el-table-column prop="reject_reason" label="驳回原因" min-width="160" />
        <el-table-column prop="status" label="状态" min-width="110">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openEdit(row)">编辑</el-button>
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
      <el-form :model="form" label-width="90px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="出库单号">
              <el-input v-model="form.order_no" placeholder="自动生成" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="客户">
              <el-select v-model="form.customer_name" filterable placeholder="选择客户" style="width: 100%">
                <el-option
                  v-for="c in customerList"
                  :key="c.code"
                  :label="c.name"
                  :value="c.name"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出库仓库">
              <el-select v-model="form.warehouse_code" filterable placeholder="选择仓库" style="width: 100%">
                <el-option
                  v-for="w in warehouseList"
                  :key="w.code"
                  :label="w.name + ' (' + w.code + ')'"
                  :value="w.code"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计划发货">
              <el-date-picker v-model="form.planned_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width: 100%">
                <el-option v-for="s in statuses" :key="s" :label="s" :value="s" />
              </el-select>
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
          <el-button type="primary" link size="small" style="float: right" @click="addItem">+ 添加商品</el-button>
        </div>
        
        <el-table :data="form.items" border style="width: 100%" size="small">
          <el-table-column label="商品SKU" min-width="180">
            <template #default="{ row }">
              <el-select v-model="row.product_sku" filterable placeholder="选择商品" style="width: 100%">
                <el-option
                  v-for="item in productList"
                  :key="item.product_sku"
                  :label="item.spu_name + ' (' + item.product_sku + ') [可用:' + item.available_qty + '] '"
                  :value="item.product_sku"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="数量" width="220">
            <template #default="{ row }">
              <el-input-number 
                v-model="row.quantity" 
                :min="1" 
                :max="getProductAvailable(row.product_sku)"
                style="width: 110px"
              />
              <span style="margin-left: 5px; font-size: 12px; color: #999;">
                (最大: {{ getProductAvailable(row.product_sku) }})
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" align="center">
            <template #default="{ $index }">
              <el-button type="danger" link @click="removeItem($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveItem">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../../utils/request'

const statuses = ['草稿', '待审核', '已审核', '待拣货', '已发货', '已完成', '已驳回', '已取消']

const list = ref([])
const productList = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const keyword = ref('')
const status = ref(null)

const dialogVisible = ref(false)
const form = reactive({
  id: null,
  order_no: '',
  customer_name: '',
  planned_date: '',
  status: '草稿',
  remark: '',
  reject_reason: '',
  items: []
})

const dialogTitle = computed(() => (form.id ? '编辑出库单' : '新增出库单'))

const statusTag = (s) => {
  if (s === '草稿') return ''
  if (s === '待审核') return 'warning'
  if (s === '已审核') return 'success'
  if (s === '待拣货') return 'info'
  if (s === '已发货') return 'primary'
  if (s === '已完成') return 'success'
  if (s === '已驳回') return 'danger'
  if (s === '已取消') return 'danger'
  return ''
}

const fetchProducts = async () => {
  // Only fetch products that have inventory in the selected warehouse
  const wh = form.warehouse_code
  if (!wh) {
    productList.value = []
    return
  }
  
  const res = await request({
    url: '/inventory/items',
    params: {
      pageSize: 200,
      warehouse_code: wh
    }
  })
  
  // Aggregate inventory by SKU
  const invMap = {}
  const list = res.data?.list || []
  list.forEach(item => {
    if (!invMap[item.product_sku]) {
      invMap[item.product_sku] = {
        product_sku: item.product_sku,
        available_qty: 0,
        spu_name: item.product_sku // Fallback name
      }
    }
    invMap[item.product_sku].available_qty += (item.available_qty || 0)
  })
  
  // Fetch product details for names
  const pMap = {}
  allProducts.value.forEach(p => pMap[p.sku_code] = p.spu_name)
  
  productList.value = Object.values(invMap).map(i => ({
    ...i,
    spu_name: pMap[i.product_sku] || i.product_sku
  })).filter(i => i.available_qty > 0)
}

// Watch warehouse change to reload products
watch(() => form.warehouse_code, () => {
  form.items = [] // Clear items when warehouse changes
  fetchProducts()
})

const getWarehouseName = (code) => {
  if (!code) return '-'
  const w = warehouseList.value.find(i => i.code === code)
  return w ? `${w.name} (${code})` : code
}

const getProductName = (sku) => {
  // Try to find in loaded productList
  let p = productList.value.find(i => i.product_sku === sku)
  if (p) return `${p.spu_name} (${sku})`
  // If not found (e.g. warehouse filter), fallback to simple sku
  return sku
}

// Need to fetch ALL products to display names correctly in the list, 
// not just the ones in the selected warehouse (which is for the form)
const allProducts = ref([])
const fetchAllProducts = async () => {
  try {
    const res = await request({ url: '/products', params: { pageSize: 200 } })
    allProducts.value = res.data?.list || []
  } catch { allProducts.value = [] }
}
// Override getProductName to use allProducts
const getProductNameDisplay = (sku) => {
  const p = allProducts.value.find(i => i.sku_code === sku)
  return p ? `${p.spu_name} (${sku})` : sku
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

const openCreate = () => {
  Object.assign(form, {
    id: null,
    order_no: '',   // 由后端生成，保存后显示
    customer_name: '',
    planned_date: new Date().toISOString().slice(0,10),
    status: '草稿',
    remark: '',
    reject_reason: '',
    items: []
  })
  dialogVisible.value = true
}

const openEdit = (row) => {
  const data = JSON.parse(JSON.stringify(row))
  Object.assign(form, {
    id: data.id,
    order_no: data.order_no,
    customer_name: data.customer_name,
    planned_date: data.planned_date,
    status: data.status,
    remark: data.remark,
    reject_reason: data.reject_reason,
    items: data.items || []
  })
  dialogVisible.value = true
}

const addItem = () => {
  form.items.push({
    product_sku: '',
    quantity: 1
  })
}

const removeItem = (index) => {
  form.items.splice(index, 1)
}

const getProductAvailable = (sku) => {
  if (!sku) return 99999999
  const item = productList.value.find(p => p.product_sku === sku)
  return item ? (item.available_qty || 0) : 0
}

const canSubmit = (row) => ['草稿', '已驳回'].includes(row.status)

const saveItem = async () => {
  try {
    const payload = { ...form }
    if (payload.id) {
      await request({ url: '/outbound/orders', method: 'put', data: payload })
      ElMessage.success('更新成功')
    } else {
      const res = await request({ url: '/outbound/orders', method: 'post', data: payload })
      if (res.data?.order_no) {
        ElMessage.success(`创建成功，单号：${res.data.order_no}`)
      } else {
        ElMessage.success('创建成功')
      }
    }
    dialogVisible.value = false
    fetchList()
  } catch {
    // 错误已由拦截器弹出
  }
}

const submitOrder = async (row) => {
  await request({ url: '/outbound/orders', method: 'put', data: { id: row.id, action: 'submit' } })
  ElMessage.success('提交成功')
  fetchList()
}

const cancelOrder = async (row) => {
  await ElMessageBox.confirm('确认取消该出库单吗？', '提示', { type: 'warning' })
  await request({ url: '/outbound/orders', method: 'put', data: { id: row.id, action: 'cancel' } })
  ElMessage.success('已取消')
  fetchList()
}

const customerList = ref([])
const warehouseList = ref([])

const fetchCustomers = async () => {
  try {
    const res = await request({ url: '/customers', params: { pageSize: 200 } })
    customerList.value = res.data?.list || []
  } catch { customerList.value = [] }
}

const fetchWarehouses = async () => {
  try {
    const res = await request({ url: '/warehouses', params: { pageSize: 200 } })
    warehouseList.value = res.data?.list || []
  } catch { warehouseList.value = [] }
}

onMounted(() => {
  fetchList()
  // fetchProducts() // This depends on warehouse selection, so don't call it here or call it with empty
  fetchAllProducts()
  fetchCustomers()
  fetchWarehouses()
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
