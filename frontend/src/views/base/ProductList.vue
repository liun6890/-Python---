<template>
  <div class="page-container">
    <el-card shadow="hover" class="search-card">
      <el-form :inline="true" @submit.prevent class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="keyword" placeholder="SKU/名称" clearable @keyup.enter="fetchList">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="fetchList">
            <el-icon class="el-icon--left"><Search /></el-icon>查询
          </el-button>
          <el-button @click="resetSearch">
            <el-icon class="el-icon--left"><Refresh /></el-icon>重置
          </el-button>
          <el-button type="success" plain @click="openCreate">
            <el-icon class="el-icon--left"><Plus /></el-icon>新增商品
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="table-card">
      <el-table :data="list" v-loading="loading" style="width: 100%" stripe border highlight-current-row>
        <el-table-column prop="sku_code" label="SKU编码" min-width="120" show-overflow-tooltip />
        <el-table-column prop="spu_name" label="商品名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" min-width="120" />
        <el-table-column prop="unit" label="单位" min-width="80" align="center" />
        <el-table-column prop="safety_stock" label="安全库存" min-width="100" align="right" />
        <el-table-column prop="barcode" label="条码" min-width="140" show-overflow-tooltip />
        <el-table-column prop="is_active" label="状态" min-width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_active" type="success" effect="dark">上架</el-tag>
            <el-tag v-else type="info" effect="dark">下架</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="160" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openEdit(row)">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button link type="danger" size="small" @click="removeItem(row)">
              <el-icon><Delete /></el-icon>删除
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" destroy-on-close>
      <el-form :model="form" label-width="100px" class="product-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="SKU编码" required>
              <el-input v-model="form.sku_code" placeholder="请输入SKU" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="商品名称" required>
              <el-input v-model="form.spu_name" placeholder="请输入名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分类">
              <el-input v-model="form.category" placeholder="例如：电子产品" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位">
              <el-input v-model="form.unit" placeholder="例如：个、箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="安全库存">
              <el-input-number v-model="form.safety_stock" :min="0" style="width: 100%" controls-position="right" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="条码">
              <el-input v-model="form.barcode" placeholder="请输入条形码" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="状态">
              <el-switch v-model="form.is_active" active-text="上架" inactive-text="下架" inline-prompt />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveItem">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Edit, Delete } from '@element-plus/icons-vue'
import request from '../../utils/request'

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const keyword = ref('')

const dialogVisible = ref(false)
const form = reactive({
  id: null,
  sku_code: '',
  spu_name: '',
  category: '',
  unit: '',
  safety_stock: 0,
  barcode: '',
  is_active: true,
})

const dialogTitle = computed(() => (form.id ? '编辑商品' : '新增商品'))

const fetchList = async () => {
  loading.value = true
  try {
    const res = await request({
      url: '/products',
      method: 'get',
      params: {
        page: page.value,
        pageSize: pageSize.value,
        keyword: keyword.value,
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
    sku_code: '',
    spu_name: '',
    category: '',
    unit: '',
    safety_stock: 0,
    barcode: '',
    is_active: true,
  })
  dialogVisible.value = true
}

const openEdit = (row) => {
  Object.assign(form, row)
  dialogVisible.value = true
}

const saveItem = async () => {
  const payload = { ...form }
  if (payload.id) {
    await request({ url: '/products', method: 'put', data: payload })
    ElMessage.success('更新成功')
  } else {
    await request({ url: '/products', method: 'post', data: payload })
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  fetchList()
}

const removeItem = async (row) => {
  await ElMessageBox.confirm('确认删除该商品吗？', '提示', { type: 'warning' })
  await request({ url: '/products', method: 'delete', data: { id: row.id } })
  ElMessage.success('删除成功')
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

.product-form {
  :deep(.el-form-item) {
    margin-bottom: 18px;
  }
}
</style>
