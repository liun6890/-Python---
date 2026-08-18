import NProgress from 'nprogress'
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginView from '../views/LoginView.vue'
import MainLayout from '../layouts/MainLayout.vue'

// NProgress Configuration
NProgress.configure({ showSpinner: false })

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: MainLayout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/DashboardView.vue'),
        meta: { title: '工作台', requiresAuth: true }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/ProfileView.vue'),
        meta: { title: '个人中心', requiresAuth: true }
      },
      // Base Data
      {
        path: 'base/products',
        name: 'ProductList',
        component: () => import('../views/base/ProductList.vue'),
        meta: { title: '商品管理', requiresAuth: true }
      },
      {
        path: 'base/warehouses',
        name: 'WarehouseList',
        component: () => import('../views/base/WarehouseList.vue'),
        meta: { title: '仓库管理', requiresAuth: true }
      },
      {
        path: 'base/suppliers',
        name: 'SupplierList',
        component: () => import('../views/base/SupplierList.vue'),
        meta: { title: '供应商管理', requiresAuth: true }
      },
      {
        path: 'base/customers',
        name: 'CustomerList',
        component: () => import('../views/base/CustomerList.vue'),
        meta: { title: '客户管理', requiresAuth: true }
      },
      // Inbound
      {
        path: 'inbound/overview',
        component: () => import('../views/inbound/InboundOverviewList.vue'),
        meta: { title: '入库总览', requiresAuth: true }
      },
      {
        path: 'inbound/create',
        component: () => import('../views/inbound/InboundCreateList.vue'),
        meta: { title: '入库申请', requiresAuth: true }
      },
      {
        path: 'inbound/audit',
        component: () => import('../views/inbound/InboundAuditList.vue'),
        meta: { title: '入库审核', requiresAuth: true }
      },
      {
        path: 'inbound/execute',
        component: () => import('../views/inbound/InboundExecuteList.vue'),
        meta: { title: '收货上架', requiresAuth: true }
      },
      // Outbound
      {
        path: 'outbound/overview',
        component: () => import('../views/outbound/OutboundOverviewList.vue'),
        meta: { title: '出库总览', requiresAuth: true }
      },
      {
        path: 'outbound/create',
        component: () => import('../views/outbound/OutboundCreateList.vue'),
        meta: { title: '出库申请', requiresAuth: true }
      },
      {
        path: 'outbound/audit',
        component: () => import('../views/outbound/OutboundAuditList.vue'),
        meta: { title: '出库审核', requiresAuth: true }
      },
      {
        path: 'outbound/picking',
        component: () => import('../views/outbound/OutboundPickingList.vue'),
        meta: { title: '拣货发货', requiresAuth: true }
      },
      // Inventory
      {
        path: 'inventory/query',
        component: () => import('../views/inventory/InventoryQueryList.vue'),
        meta: { title: '库存查询', requiresAuth: true }
      },
      {
        path: 'inventory/stocktaking',
        component: () => import('../views/inventory/InventoryStocktakingList.vue'),
        meta: { title: '库存盘点', requiresAuth: true }
      },
      {
        path: 'inventory/transfer',
        component: () => import('../views/inventory/InventoryTransferList.vue'),
        meta: { title: '库存调拨', requiresAuth: true }
      },
      {
        path: 'inventory/warning',
        component: () => import('../views/inventory/InventoryWarningList.vue'),
        meta: { title: '库存预警', requiresAuth: true }
      },
      // Reports
      {
        path: 'reports/dashboard',
        component: () => import('../views/reports/ReportsDashboardView.vue'),
        meta: { title: '数据大屏', requiresAuth: true }
      },
      {
        path: 'reports/daily',
        component: () => import('../views/reports/ReportsDailyView.vue'),
        meta: { title: '出入库日报', requiresAuth: true }
      },
      // System
      {
        path: 'system/users',
        component: () => import('../views/system/SystemUsersList.vue'),
        meta: { title: '用户管理', requiresAuth: true }
      },
      // Role management removed as per user request
      // {
      //   path: 'system/roles',
      //   component: () => import('../views/system/SystemRolesList.vue'),
      //   meta: { title: '角色管理', requiresAuth: true }
      // },
      {
        path: 'system/logs',
        component: () => import('../views/system/SystemLogsList.vue'),
        meta: { title: '操作日志', requiresAuth: true }
      }
    ]
  },
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: { title: '404' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  // Start progress bar
  NProgress.start()
  
  // Set page title
  document.title = to.meta.title ? `${to.meta.title} - 智仓通 WMS` : '智仓通 WMS'

  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

router.afterEach(() => {
  // Finish progress bar
  NProgress.done()
})

export default router
