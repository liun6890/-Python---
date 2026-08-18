<template>
  <div class="tabs-bar-container">
    <div class="tabs-content">
      <el-tabs
        type="card"
        v-model="activeTabsValue"
        @tab-click="tabClick"
        @tab-remove="removeTab"
      >
        <template v-for="item in visitedViews" :key="item.path">
          <el-tab-pane
            v-if="!item.meta?.isHide"
            type="card"
            :path="item.path"
            :label="item.title"
            :name="item.path"
            :closable="!item.affix"
          >
            <template #label>
              {{ item.title }}
            </template>
          </el-tab-pane>
        </template>
      </el-tabs>
    </div>
    <div class="tabs-action">
      <el-dropdown trigger="hover">
        <el-icon color="rgba(0, 0, 0, 0.65)" :size="20">
          <Menu />
        </el-icon>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="closeCurrentTab">
              <el-icon :size="14"><FolderRemove /></el-icon>
              关闭当前
            </el-dropdown-item>
            <el-dropdown-item @click="closeOtherTab">
              <el-icon :size="14"><Close /></el-icon>
              关闭其他
            </el-dropdown-item>
            <el-dropdown-item @click="closeAllTab">
              <el-icon :size="14"><FolderDelete /></el-icon>
              关闭所有
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Menu, FolderRemove, Close, FolderDelete } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const visitedViews = ref([])

const normalizeView = (r) => {
  const title = r.meta?.title || r.name || r.path
  const affix = r.path === '/dashboard'
  return {
    title,
    path: r.path.startsWith('/') ? r.path : `/${r.path}`,
    name: r.name,
    meta: r.meta || {},
    affix
  }
}

const addTags = () => {
  if (route.name === 'Login') return
  const view = normalizeView(route)
  if (!visitedViews.value.find(v => v.path === view.path)) {
    visitedViews.value.push(view)
  }
}

onMounted(() => {
  // 初始化固定首页
  if (!visitedViews.value.find(v => v.path === '/dashboard')) {
    visitedViews.value.push({ title: '工作台', path: '/dashboard', affix: true, meta: {} })
  }
  addTags()
})

watch(() => route.fullPath, () => addTags())

const activeTabsValue = computed({
  get: () => route.path,
  set: (val) => router.push(val)
})

const toLastView = (activePath) => {
  const idx = visitedViews.value.findIndex(v => v.path === activePath)
  const next = visitedViews.value[idx + 1] || visitedViews.value[idx - 1]
  if (next) router.push(next.path)
}

const tabClick = (tabItem) => {
  const path = tabItem.props.name
  router.push(path)
}
const isActive = (path) => path === route.path
const removeTab = (activeTabPath) => {
  const view = visitedViews.value.find(v => v.path === activeTabPath)
  if (view?.affix) return
  if (isActive(activeTabPath)) {
    toLastView(activeTabPath)
  }
  visitedViews.value = visitedViews.value.filter(v => v.path !== activeTabPath)
}

const closeCurrentTab = () => removeTab(route.path)
const closeOtherTab = () => {
  visitedViews.value = visitedViews.value.filter(v => v.affix || v.path === route.path)
}
const closeAllTab = () => {
  visitedViews.value = visitedViews.value.filter(v => v.affix)
  router.push('/dashboard')
}
</script>

<style scoped lang="scss">
@use '@/styles/tabs' as *;
</style>
