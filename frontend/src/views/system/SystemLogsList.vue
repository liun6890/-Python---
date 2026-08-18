<template>
  <div class="page-container">
    <el-card shadow="hover" class="search-card">
      <el-form :inline="true" :model="filters" class="search-form" @submit.prevent>
        <el-form-item label="操作人">
          <el-input v-model="filters.operator" placeholder="请输入操作人" clearable @keyup.enter="fetchList">
            <template #prefix><el-icon><User /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item label="动作">
          <el-input v-model="filters.action" placeholder="请输入动作" clearable @keyup.enter="fetchList">
            <template #prefix><el-icon><Operation /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item label="详情">
          <el-input v-model="filters.detail" placeholder="请输入详情关键词" clearable @keyup.enter="fetchList">
            <template #prefix><el-icon><Document /></el-icon></template>
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
        <el-table-column prop="operator" label="操作人" min-width="120">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="24" icon="UserFilled" class="mr-2" />
              <span>{{ row.operator }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="动作" min-width="140">
          <template #default="{ row }">
            <el-tag effect="plain">{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detail" label="详情" min-width="300" show-overflow-tooltip />
        <el-table-column prop="created_at" label="时间" min-width="180" sortable />
      </el-table>
      <div class="pager">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
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
import { Search, Refresh, User, Operation, Document } from '@element-plus/icons-vue'
import request from '../../utils/request'

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const filters = reactive({
  operator: '',
  action: '',
  detail: ''
})

const fetchList = async () => {
  loading.value = true
  try {
    const res = await request({
      url: '/system/logs',
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
  filters.operator = ''
  filters.action = ''
  filters.detail = ''
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

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
