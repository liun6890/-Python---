import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { login as loginApi, logout as logoutApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user')) || null)
  const token = ref(localStorage.getItem('token') || null)

  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role)

  function login(username, password) {
    return new Promise((resolve, reject) => {
      loginApi({ username, password })
        .then(response => {
          if (response.code === 200) {
            const { data } = response
            
            // Assuming response structure: { data: { user: {...}, token: '...' } }
            // Adapt if your API structure is different
            // Based on api/auth.js mock:
            // resolve({ code: 200, data: { token: '...', user: {...} } })
            
            const userData = data.user
            const accessToken = data.token

            // role 由后端返回，不在前端推断
            if (!userData.role) {
                userData.role = 'viewer'
            }

            user.value = userData
            token.value = accessToken

            localStorage.setItem('user', JSON.stringify(userData))
            localStorage.setItem('token', accessToken)
            resolve(userData)
          } else {
            reject(new Error(response.message || 'Login failed'))
          }
        })
        .catch(error => {
          reject(error)
        })
    })
  }

  function logout() {
    return new Promise((resolve) => {
      // Call API logout but always clear local state
      logoutApi().finally(() => {
        user.value = null
        token.value = null
        localStorage.removeItem('user')
        localStorage.removeItem('token')
        // Force reload to clear any memory state
        window.location.href = '/login'
        resolve()
      })
    })
  }

  function hasPermission(requiredRoles) {
    if (!user.value) return false
    if (user.value.role === 'admin') return true // Admin has all permissions
    if (!requiredRoles || requiredRoles.length === 0) return true
    return requiredRoles.includes(user.value.role)
  }

  return {
    user,
    token,
    isAuthenticated,
    userRole,
    login,
    logout,
    hasPermission
  }
})
