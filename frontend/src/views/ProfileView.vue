<template>
  <el-card shadow="never">
    <div class="profile">
      <el-avatar :size="80" :src="user?.avatar" />
      <div class="info">
        <div class="name">{{ user?.name || user?.username }}</div>
        <div class="meta">角色：{{ user?.role || '-' }}</div>
        <div class="meta">账号：{{ user?.username || '-' }}</div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const user = computed(() => authStore.user)
</script>

<style scoped lang="scss">
.profile {
  display: flex;
  align-items: center;
  gap: 16px;
}
.name {
  font-size: 18px;
  font-weight: 600;
}
.meta {
  color: #666;
  margin-top: 4px;
}
</style>
