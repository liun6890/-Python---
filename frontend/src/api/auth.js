import request from '../utils/request'

// Mock implementation switch
const USE_MOCK = false

// 模拟 API
export function login(data) {
  if (USE_MOCK) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const { username, password } = data
        let role = 'viewer'
        if (username.includes('admin')) role = 'admin'
        else if (username.includes('manager')) role = 'manager'
        else if (username.includes('operator')) role = 'operator'

        if (password === '123456') {
          resolve({
            code: 200,
            message: 'success',
            data: {
              token: 'mock-jwt-token-' + Date.now(),
              user: {
                id: 1,
                username,
                role,
                name: username.charAt(0).toUpperCase() + username.slice(1),
                avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
              }
            }
          })
        } else {
          // Simulate error response structure
          // In axios interceptor, we might catch this if it was a real 400 status
          // But here we resolve with a non-200 code
          resolve({
            code: 400,
            message: '用户名或密码错误 (默认密码: 123456)'
          })
        }
      }, 800)
    })
  }
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

export function logout() {
  if (USE_MOCK) {
    return Promise.resolve({
      code: 200,
      message: 'success'
    })
  }
  return request({
    url: '/auth/logout',
    method: 'post'
  })
}

export function getUserInfo() {
  if (USE_MOCK) {
    // This would typically use the token to look up the user
    return Promise.resolve({
      code: 200,
      data: {
        // Mock data
      }
    })
  }
  return request({
    url: '/auth/profile',
    method: 'get'
  })
}
