<template>
  <el-aside :style="{ width: isCollapse ? styleVars.leftMin : styleVars.leftFull }" class="sidebar" :class="{ 'is-collapse': isCollapse }">
    <div class="sidebar-header">
      <el-icon :size="24" :color="styleVars.colorDefault"><Box /></el-icon>
      <span v-if="!isCollapse" class="sidebar-title">智仓通 WMS</span>
    </div>
    
    <el-menu
      :default-active="activeMenu"
      class="el-menu-vertical"
      :collapse="isCollapse"
      :background-color="styleVars.menuBg"
      :text-color="styleVars.menuText"
      :active-text-color="styleVars.menuActiveText"
      router
    >
      <el-menu-item index="/dashboard">
        <el-icon><DataBoard /></el-icon>
        <template #title>工作台</template>
      </el-menu-item>

      <!-- 基础数据 (Admin, Manager) -->
      <el-sub-menu index="/base" v-if="hasPermission(['admin', 'manager'])">
        <template #title>
          <el-icon><Setting /></el-icon>
          <span>基础数据</span>
        </template>
        <el-menu-item index="/base/products">商品管理</el-menu-item>
        <el-menu-item index="/base/warehouses">仓库管理</el-menu-item>
        <el-menu-item index="/base/suppliers">供应商管理</el-menu-item>
        <el-menu-item index="/base/customers">客户管理</el-menu-item>
      </el-sub-menu>

      <!-- 入库管理 (Admin, Manager, Operator) -->
      <el-sub-menu index="/inbound" v-if="hasPermission(['admin', 'manager', 'operator'])">
        <template #title>
          <el-icon><Download /></el-icon>
          <span>入库管理</span>
        </template>
        <el-menu-item index="/inbound/overview" v-if="hasPermission(['admin', 'manager', 'operator'])">入库总览</el-menu-item>
        <el-menu-item index="/inbound/create" v-if="hasPermission(['admin', 'manager'])">入库申请</el-menu-item>
        <el-menu-item index="/inbound/audit" v-if="hasPermission(['admin', 'manager'])">入库审核</el-menu-item>
        <el-menu-item index="/inbound/execute" v-if="hasPermission(['admin', 'operator'])">收货上架</el-menu-item>
      </el-sub-menu>

      <!-- 出库管理 (Admin, Manager, Operator) -->
      <el-sub-menu index="/outbound" v-if="hasPermission(['admin', 'manager', 'operator'])">
        <template #title>
          <el-icon><Upload /></el-icon>
          <span>出库管理</span>
        </template>
        <el-menu-item index="/outbound/overview" v-if="hasPermission(['admin', 'manager', 'viewer'])">出库总览</el-menu-item>
        <el-menu-item index="/outbound/create" v-if="hasPermission(['admin', 'manager'])">出库申请</el-menu-item>
        <el-menu-item index="/outbound/audit" v-if="hasPermission(['admin', 'manager'])">出库审核</el-menu-item>
        <el-menu-item index="/outbound/picking" v-if="hasPermission(['admin', 'operator'])">拣货发货</el-menu-item>
      </el-sub-menu>

      <!-- 库存管理 (All) -->
      <el-sub-menu index="/inventory">
        <template #title>
          <el-icon><Goods /></el-icon>
          <span>库存管理</span>
        </template>
        <el-menu-item index="/inventory/query">库存查询</el-menu-item>
        <el-menu-item index="/inventory/stocktaking" v-if="hasPermission(['admin', 'manager', 'operator'])">库存盘点</el-menu-item>
        <el-menu-item index="/inventory/transfer" v-if="hasPermission(['admin', 'manager'])">库存调拨</el-menu-item>
        <el-menu-item index="/inventory/warning" v-if="hasPermission(['admin', 'manager'])">库存预警</el-menu-item>
      </el-sub-menu>

      <!-- 报表中心 (Admin, Manager, Viewer) -->
      <el-sub-menu index="/reports" v-if="hasPermission(['admin', 'manager', 'viewer'])">
        <template #title>
          <el-icon><TrendCharts /></el-icon>
          <span>报表中心</span>
        </template>
        <el-menu-item index="/reports/dashboard">数据大屏</el-menu-item>
        <el-menu-item index="/reports/daily">出入库日报</el-menu-item>
      </el-sub-menu>

      <!-- 系统管理 (Admin) -->
      <el-sub-menu index="/system" v-if="hasPermission(['admin'])">
        <template #title>
          <el-icon><Tools /></el-icon>
          <span>系统管理</span>
        </template>
        <el-menu-item index="/system/users">用户管理</el-menu-item>
        <!-- <el-menu-item index="/system/roles">角色管理</el-menu-item> -->
        <el-menu-item index="/system/logs">操作日志</el-menu-item>
      </el-sub-menu>

      <!-- 个人中心 (All) -->
      <el-menu-item index="/profile">
        <el-icon><User /></el-icon>
        <template #title>个人中心</template>
      </el-menu-item>
    </el-menu>
  </el-aside>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { 
  Box, 
  DataBoard, 
  Setting, 
  Download, 
  Upload, 
  Goods, 
  TrendCharts, 
  Tools, 
  User
} from '@element-plus/icons-vue'

const props = defineProps({
  isCollapse: {
    type: Boolean,
    default: false
  }
})

const route = useRoute()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)
// 样式变量映射
const styleVars = {
  leftFull: '256px',
  leftMin: '64px',
  menuBg: '#001529',
  menuText: 'hsla(0,0%,100%,.95)',
  menuActiveText: '#fff',
  colorDefault: '#1890ff'
}

// Helper to check permissions
const hasPermission = (roles) => {
  return authStore.hasPermission(roles)
}
</script>

<style scoped lang="scss">
.sidebar {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 1001;
  height: 100vh;
  background-color: $base-menu-background;
  overflow-x: hidden;
  transition: width 0.3s;
  box-shadow: 2px 0 6px rgba(0, 21, 41, 0.35);
  
  .sidebar-header {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(255, 255, 255, 0.04);
    color: $base-title-color;
    
    .sidebar-title {
      margin-left: 10px;
      font-weight: bold;
      font-size: 18px;
    }
  }
  
  .el-menu-vertical {
    border-right: none;
    :deep(.el-menu-item),
    :deep(.el-submenu__title) {
      height: $base-menu-item-height;
      line-height: $base-menu-item-height;
    }
  }
}
</style>
