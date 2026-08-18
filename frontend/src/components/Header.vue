<template>
  <el-header class="header">
    <div class="header-left">
      <el-icon class="fold-unfold" @click="toggle">
        <component :is="isCollapse ? 'Expand' : 'Fold'"></component>
      </el-icon>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentRouteName">{{ currentRouteName }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    
    <div class="header-right">
      <el-tooltip content="刷新" placement="bottom">
        <el-icon class="op-icon" @click="onRefresh"><RefreshRight /></el-icon>
      </el-tooltip>
      <el-tooltip content="全屏" placement="bottom">
        <el-icon class="op-icon" @click="toggleFullscreen"><FullScreen /></el-icon>
      </el-tooltip>
      <el-tooltip content="设置" placement="bottom">
        <el-icon class="op-icon" @click="settingsVisible = true"><Setting /></el-icon>
      </el-tooltip>
      <el-dropdown @command="handleCommand">
        <span class="el-dropdown-link">
          <el-avatar :size="32" :src="userAvatar" />
          <span class="username">{{ username }}</span>
          <el-icon class="el-icon--right"><arrow-down /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人中心</el-dropdown-item>
            <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
    <el-drawer v-model="settingsVisible" title="个性化设置" size="30%">
      <div style="padding: 10px; color: #666;">此处保留设置入口，按需扩展。</div>
    </el-drawer>
  </el-header>
  </template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ArrowDown, RefreshRight, FullScreen, Setting, Fold, Expand } from '@element-plus/icons-vue'

const props = defineProps({
  isCollapse: {
    type: Boolean,
    default: false
  }
})
const emit = defineEmits(['toggle-collapse', 'refresh'])
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const currentRouteName = computed(() => route.meta.title || route.name)
const username = computed(() => authStore.user?.username || '用户')
const userAvatar = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'

const settingsVisible = ref(false)
const isFullscreen = ref(false)

const toggle = () => emit('toggle-collapse')
const onRefresh = () => emit('refresh')
const toggleFullscreen = async () => {
  try {
    if (!isFullscreen.value) {
      await document.documentElement.requestFullscreen()
      isFullscreen.value = true
    } else {
      await document.exitFullscreen()
      isFullscreen.value = false
    }
  } catch {}
}

const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.logout()
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped lang="scss">
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: $base-nav-bar-height;
  background: $base-color-white;
  box-shadow: $base-box-shadow;
  padding: 0 $base-padding;
  
  .fold-unfold {
    font-size: 18px;
    color: $base-color-gray;
    cursor: pointer;
    margin-right: 12px;
  }
  .op-icon {
    margin: 0 10px;
    color: rgba(0,0,0,0.65);
    cursor: pointer;
    transition: all 0.3s;
    &:hover {
      color: $base-color-default;
      transform: rotate(90deg);
    }
  }
  .header-right {
    .el-dropdown-link {
      cursor: pointer;
      display: flex;
      align-items: center;
      
      .username {
        margin-left: 8px;
        margin-right: 4px;
        font-size: 14px;
      }
    }
  }
}
</style>
