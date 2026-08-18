import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

let _isRedirectingToLogin = false

// 创建 axios 实例
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api', // url = base url + request url
  timeout: 5000 // request timeout
})

// request 拦截器
service.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么
    const authStore = useAuthStore()
    if (authStore.token) {
      // 让每个请求携带 token
      // ['Authorization'] 是自定义头部 key
      // 请根据实际情况修改
      config.headers['Authorization'] = `Bearer ${authStore.token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// response 拦截器
service.interceptors.response.use(
  /**
   * 如果你想要 HTTP 信息如头信息或状态
   * Please return  response => response
  */

  /**
   * 下面的注释为通过在 response 里，自定义 code 来标示请求状态
   * 当 code 返回如下情况则说明权限有问题，登出并返回到登录页
   * 如通过 xmlhttprequest 状态码标识 逻辑可写在下面 error 中
  */
  response => {
    const res = response.data

    // 如果是 mock 数据，可能没有 code 字段，直接返回
    // 实际项目中，通常约定 code !== 200 (或 0) 为错误
    if (res.code !== undefined && res.code !== 200) {
      ElMessage({
        message: res.message || 'Error',
        type: 'error',
        duration: 5 * 1000
      })

      // token 无效或过期，跳转登录页（防止重复触发）
      if (res.code === 50008 || res.code === 50012 || res.code === 50014 || res.code === 401) {
        if (!_isRedirectingToLogin) {
          _isRedirectingToLogin = true
          ElMessage.error('登录状态已失效，请重新登录')
          const authStore = useAuthStore()
          authStore.logout()
          // logout() 内部已跳转 /login，此处无需再操作
        }
      }
      return Promise.reject(new Error(res.message || 'Error'))
    } else {
      return res
    }
  },
  error => {
    const msg = error.response?.data?.message || error.message || '网络错误'
    ElMessage({
      message: msg,
      type: 'error',
      duration: 5 * 1000
    })
    return Promise.reject(error)
  }
)

export default service
