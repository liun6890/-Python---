<template>
  <el-card shadow="never" header="出入库日报">
    <el-table :data="list" v-loading="loading" style="width: 100%">
      <el-table-column prop="date" label="日期" />
      <el-table-column prop="inbound" label="入库量" />
      <el-table-column prop="outbound" label="出库量" />
    </el-table>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '../../utils/request'

const list = ref([])
const loading = ref(false)

const load = async () => {
  loading.value = true
  try {
    const res = await request({ url: '/reports/daily', method: 'get' })
    list.value = res.data?.list || []
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
