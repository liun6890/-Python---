<template>
  <div class="page-container">
    <el-card shadow="never" class="toolbar">
      <div class="toolbar-title">{{ config.title }}</div>
      <div class="toolbar-actions">
        <el-button v-if="!config.readOnly" type="success" @click="openCreate">新增</el-button>
      </div>
    </el-card>

    <el-card shadow="never">
      <el-table :data="list" v-loading="loading" style="width: 100%">
        <el-table-column
          v-for="col in config.columns"
          :key="col.prop"
          :prop="col.prop"
          :label="col.label"
          :min-width="col.minWidth || 120"
        >
          <template v-if="col.type === 'tag'" #default="{ row }">
            <el-tag :type="row[col.prop] ? 'success' : 'info'">
              {{ row[col.prop] ? col.activeText : col.inactiveText }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="!config.readOnly" label="操作" min-width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="removeItem(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px" v-if="!config.readOnly">
      <el-form :model="form" label-width="90px">
        <el-form-item v-for="field in config.fields" :key="field.prop" :label="field.label">
          <component
            :is="field.component"
            v-model="form[field.prop]"
            v-bind="field.props || {}"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveItem">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../utils/request'

const route = useRoute()

const configs = {
  '/base/warehouses': {
    title: '仓库管理',
    endpoint: '/warehouses',
    columns: [
      { prop: 'name', label: '仓库名称' },
      { prop: 'code', label: '仓库编码' },
      { prop: 'address', label: '地址' },
      { prop: 'contact', label: '联系人' },
      { prop: 'phone', label: '电话' },
      { prop: 'is_active', label: '状态', type: 'tag', activeText: '启用', inactiveText: '停用' },
    ],
    fields: [
      { prop: 'name', label: '仓库名称', component: 'el-input' },
      { prop: 'code', label: '仓库编码', component: 'el-input' },
      { prop: 'address', label: '地址', component: 'el-input' },
      { prop: 'contact', label: '联系人', component: 'el-input' },
      { prop: 'phone', label: '电话', component: 'el-input' },
      { prop: 'is_active', label: '状态', component: 'el-switch' },
    ],
  },
  '/base/suppliers': {
    title: '供应商管理',
    endpoint: '/suppliers',
    columns: [
      { prop: 'name', label: '供应商名称' },
      { prop: 'contact', label: '联系人' },
      { prop: 'phone', label: '电话' },
      { prop: 'rating', label: '评级' },
      { prop: 'is_active', label: '状态', type: 'tag', activeText: '启用', inactiveText: '停用' },
    ],
    fields: [
      { prop: 'name', label: '供应商名称', component: 'el-input' },
      { prop: 'contact', label: '联系人', component: 'el-input' },
      { prop: 'phone', label: '电话', component: 'el-input' },
      { prop: 'rating', label: '评级', component: 'el-input-number', props: { min: 0 } },
      { prop: 'is_active', label: '状态', component: 'el-switch' },
    ],
  },
  '/base/customers': {
    title: '客户管理',
    endpoint: '/customers',
    columns: [
      { prop: 'name', label: '客户名称' },
      { prop: 'contact', label: '联系人' },
      { prop: 'phone', label: '电话' },
      { prop: 'address', label: '地址' },
      { prop: 'credit_limit', label: '信用额度' },
    ],
    fields: [
      { prop: 'name', label: '客户名称', component: 'el-input' },
      { prop: 'contact', label: '联系人', component: 'el-input' },
      { prop: 'phone', label: '电话', component: 'el-input' },
      { prop: 'address', label: '地址', component: 'el-input' },
      { prop: 'credit_limit', label: '信用额度', component: 'el-input-number', props: { min: 0 } },
    ],
  },
  '/inbound/create': {
    title: '入库申请',
    endpoint: '/inbound/orders',
    columns: [
      { prop: 'order_no', label: '入库单号' },
      { prop: 'supplier_name', label: '供应商' },
      { prop: 'status', label: '状态' },
      { prop: 'planned_date', label: '预计到货' },
    ],
    fields: [
      { prop: 'order_no', label: '入库单号', component: 'el-input' },
      { prop: 'supplier_name', label: '供应商', component: 'el-input' },
      { prop: 'status', label: '状态', component: 'el-input' },
      { prop: 'planned_date', label: '预计到货', component: 'el-date-picker', props: { type: 'date', valueFormat: 'YYYY-MM-DD' } },
    ],
  },
  '/inbound/audit': {
    title: '入库审核',
    endpoint: '/inbound/orders',
    columns: [
      { prop: 'order_no', label: '入库单号' },
      { prop: 'supplier_name', label: '供应商' },
      { prop: 'status', label: '状态' },
    ],
    fields: [
      { prop: 'order_no', label: '入库单号', component: 'el-input' },
      { prop: 'supplier_name', label: '供应商', component: 'el-input' },
      { prop: 'status', label: '状态', component: 'el-input' },
    ],
  },
  '/inbound/execute': {
    title: '收货上架',
    endpoint: '/inbound/orders',
    columns: [
      { prop: 'order_no', label: '入库单号' },
      { prop: 'supplier_name', label: '供应商' },
      { prop: 'status', label: '状态' },
    ],
    fields: [
      { prop: 'order_no', label: '入库单号', component: 'el-input' },
      { prop: 'supplier_name', label: '供应商', component: 'el-input' },
      { prop: 'status', label: '状态', component: 'el-input' },
    ],
  },
  '/outbound/create': {
    title: '出库申请',
    endpoint: '/outbound/orders',
    columns: [
      { prop: 'order_no', label: '出库单号' },
      { prop: 'customer_name', label: '客户' },
      { prop: 'status', label: '状态' },
      { prop: 'planned_date', label: '计划发货' },
    ],
    fields: [
      { prop: 'order_no', label: '出库单号', component: 'el-input' },
      { prop: 'customer_name', label: '客户', component: 'el-input' },
      { prop: 'status', label: '状态', component: 'el-input' },
      { prop: 'planned_date', label: '计划发货', component: 'el-date-picker', props: { type: 'date', valueFormat: 'YYYY-MM-DD' } },
    ],
  },
  '/outbound/audit': {
    title: '出库审核',
    endpoint: '/outbound/orders',
    columns: [
      { prop: 'order_no', label: '出库单号' },
      { prop: 'customer_name', label: '客户' },
      { prop: 'status', label: '状态' },
    ],
    fields: [
      { prop: 'order_no', label: '出库单号', component: 'el-input' },
      { prop: 'customer_name', label: '客户', component: 'el-input' },
      { prop: 'status', label: '状态', component: 'el-input' },
    ],
  },
  '/outbound/picking': {
    title: '拣货发货',
    endpoint: '/outbound/orders',
    columns: [
      { prop: 'order_no', label: '出库单号' },
      { prop: 'customer_name', label: '客户' },
      { prop: 'status', label: '状态' },
    ],
    fields: [
      { prop: 'order_no', label: '出库单号', component: 'el-input' },
      { prop: 'customer_name', label: '客户', component: 'el-input' },
      { prop: 'status', label: '状态', component: 'el-input' },
    ],
  },
  '/inventory/query': {
    title: '库存查询',
    endpoint: '/inventory/items',
    columns: [
      { prop: 'product_sku', label: 'SKU' },
      { prop: 'warehouse_code', label: '仓库' },
      { prop: 'location_code', label: '库位' },
      { prop: 'quantity', label: '数量' },
      { prop: 'locked_qty', label: '锁定量' },
      { prop: 'batch_no', label: '批次号' },
    ],
    fields: [
      { prop: 'product_sku', label: 'SKU', component: 'el-input' },
      { prop: 'warehouse_code', label: '仓库', component: 'el-input' },
      { prop: 'location_code', label: '库位', component: 'el-input' },
      { prop: 'quantity', label: '数量', component: 'el-input-number', props: { min: 0 } },
      { prop: 'locked_qty', label: '锁定量', component: 'el-input-number', props: { min: 0 } },
      { prop: 'batch_no', label: '批次号', component: 'el-input' },
    ],
  },
  '/inventory/stocktaking': {
    title: '库存盘点',
    endpoint: '/inventory/stocktaking',
    columns: [
      { prop: 'product_sku', label: 'SKU' },
      { prop: 'warehouse_code', label: '仓库' },
      { prop: 'location_code', label: '库位' },
      { prop: 'quantity', label: '数量' },
    ],
    fields: [
      { prop: 'product_sku', label: 'SKU', component: 'el-input' },
      { prop: 'warehouse_code', label: '仓库', component: 'el-input' },
      { prop: 'location_code', label: '库位', component: 'el-input' },
      { prop: 'quantity', label: '数量', component: 'el-input-number', props: { min: 0 } },
    ],
  },
  '/inventory/transfer': {
    title: '库存调拨',
    endpoint: '/inventory/transfer',
    columns: [
      { prop: 'product_sku', label: 'SKU' },
      { prop: 'warehouse_code', label: '仓库' },
      { prop: 'location_code', label: '库位' },
      { prop: 'quantity', label: '数量' },
    ],
    fields: [
      { prop: 'product_sku', label: 'SKU', component: 'el-input' },
      { prop: 'warehouse_code', label: '仓库', component: 'el-input' },
      { prop: 'location_code', label: '库位', component: 'el-input' },
      { prop: 'quantity', label: '数量', component: 'el-input-number', props: { min: 0 } },
    ],
  },
  '/inventory/warning': {
    title: '库存预警',
    endpoint: '/inventory/warning',
    readOnly: true,
    columns: [
      { prop: 'product_sku', label: 'SKU' },
      { prop: 'warehouse_code', label: '仓库' },
      { prop: 'quantity', label: '数量' },
    ],
    fields: [],
  },
  '/system/users': {
    title: '用户管理',
    endpoint: '/system/users',
    columns: [
      { prop: 'username', label: '账号' },
      { prop: 'name', label: '姓名' },
      { prop: 'role', label: '角色' },
    ],
    fields: [
      { prop: 'username', label: '账号', component: 'el-input' },
      { prop: 'name', label: '姓名', component: 'el-input' },
      { prop: 'role', label: '角色', component: 'el-input' },
      { prop: 'avatar', label: '头像', component: 'el-input' },
    ],
  },
  '/system/roles': {
    title: '角色管理',
    endpoint: '/system/roles',
    columns: [
      { prop: 'name', label: '角色名' },
    ],
    fields: [
      { prop: 'name', label: '角色名', component: 'el-input' },
    ],
  },
  '/system/logs': {
    title: '操作日志',
    endpoint: '/system/logs',
    readOnly: true,
    columns: [
      { prop: 'operator', label: '操作人' },
      { prop: 'action', label: '动作' },
      { prop: 'created_at', label: '时间' },
    ],
    fields: [],
  },
}

const config = computed(() => configs[route.path] || { title: route.meta.title || '列表', endpoint: '', columns: [], fields: [], readOnly: true })

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const dialogVisible = ref(false)
const form = reactive({})
const dialogTitle = computed(() => (form.id ? `编辑${config.value.title}` : `新增${config.value.title}`))

const initForm = () => {
  Object.keys(form).forEach(k => delete form[k])
  config.value.fields.forEach(f => {
    form[f.prop] = f.component === 'el-switch' ? true : ''
  })
  form.id = null
}

const fetchList = async () => {
  if (!config.value.endpoint) return
  loading.value = true
  try {
    const res = await request({
      url: config.value.endpoint,
      method: 'get',
      params: { page: page.value, pageSize: pageSize.value },
    })
    list.value = res.data?.list || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
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
  initForm()
  dialogVisible.value = true
}

const openEdit = (row) => {
  initForm()
  Object.assign(form, row)
  dialogVisible.value = true
}

const saveItem = async () => {
  const payload = { ...form }
  if (payload.id) {
    await request({ url: config.value.endpoint, method: 'put', data: payload })
    ElMessage.success('更新成功')
  } else {
    await request({ url: config.value.endpoint, method: 'post', data: payload })
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  fetchList()
}

const removeItem = async (row) => {
  await ElMessageBox.confirm('确认删除该记录吗？', '提示', { type: 'warning' })
  await request({ url: config.value.endpoint, method: 'delete', data: { id: row.id } })
  ElMessage.success('删除成功')
  fetchList()
}

watch(() => route.path, () => {
  page.value = 1
  fetchList()
}, { immediate: true })
</script>

<style scoped lang="scss">
.page-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-title {
  font-size: 16px;
  font-weight: 600;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
