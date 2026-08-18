<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <el-icon :size="40" color="#409EFF"><Box /></el-icon>
        <h2 class="title">智仓通 SmartWMS</h2>
        <p class="subtitle">专业的仓储物流管理系统</p>
      </div>
      
      <el-form 
        ref="loginFormRef"
        :model="loginForm"
        :rules="rules"
        class="login-form"
        label-position="top"
        size="large"
      >
        <el-form-item prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="用户名 (admin/manager/operator)"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="密码 (默认: 123456)"
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="loading" 
            class="login-btn" 
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
        
        <div class="login-tips">
          <p>测试账号说明:</p>
          <div class="tips-grid">
            <div class="tip-item"><el-tag size="small" type="danger">admin</el-tag> 超级管理员</div>
            <div class="tip-item"><el-tag size="small" type="warning">manager</el-tag> 仓库经理</div>
            <div class="tip-item"><el-tag size="small" type="success">operator</el-tag> 库管员</div>
            <div class="tip-item"><el-tag size="small" type="info">viewer</el-tag> 查询员</div>
          </div>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import { User, Lock, Box } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const loginFormRef = ref(null)

const loginForm = reactive({
  username: '',
  password: ''
})

const loading = ref(false)

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await authStore.login(loginForm.username, loginForm.password)
        ElMessage.success('登录成功')
        router.push('/')
      } catch (error) {
        // Error is handled by request interceptor or here
        // If it's a string, show it, otherwise it might be an Error object
        const msg = error.message || '登录失败'
        // Avoid duplicate messages if interceptor already showed one
        if (!document.querySelector('.el-message')) {
           ElMessage.error(msg)
        }
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #2d3a4b;
  background-image: linear-gradient(135deg, #2d3a4b 0%, #1c2630 100%);
  position: relative;
  overflow: hidden;
  
  // Animated background circles
  &::before, &::after {
    content: '';
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    z-index: 0;
  }
  
  &::before {
    width: 400px;
    height: 400px;
    background: rgba(64, 158, 255, 0.1);
    top: -100px;
    left: -100px;
    animation: float 10s infinite ease-in-out;
  }
  
  &::after {
    width: 300px;
    height: 300px;
    background: rgba(103, 194, 58, 0.1);
    bottom: -50px;
    right: -50px;
    animation: float 15s infinite ease-in-out reverse;
  }
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, 30px); }
}

.login-box {
  position: relative;
  width: 90%;
  max-width: 420px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  z-index: 1;
  backdrop-filter: blur(10px);
  transition: transform 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 35px;
  
  .title {
    margin: 15px 0 8px;
    font-size: 26px;
    color: #303133;
    font-weight: 700;
    letter-spacing: 1px;
  }
  
  .subtitle {
    margin: 0;
    color: #909399;
    font-size: 14px;
  }
}

.login-btn {
  width: 100%;
  font-weight: 600;
  letter-spacing: 2px;
  height: 44px;
  font-size: 16px;
  background: linear-gradient(90deg, #409EFF 0%, #3a8ee6 100%);
  border: none;
  
  &:hover {
    background: linear-gradient(90deg, #66b1ff 0%, #409EFF 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  }
}

.login-tips {
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px dashed #dcdfe6;
  
  p {
    margin: 0 0 12px;
    font-size: 13px;
    color: #606266;
    font-weight: 500;
  }
  
  .tips-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    
    .tip-item {
      display: flex;
      align-items: center;
      font-size: 12px;
      color: #606266;
      
      .el-tag {
        margin-right: 8px;
        width: 65px;
        text-align: center;
        border-radius: 4px;
      }
    }
  }
}

// Mobile Adaptation
@media (max-width: 480px) {
  .login-box {
    padding: 30px 20px;
  }
  
  .tips-grid {
    grid-template-columns: 1fr !important;
  }
}
</style>
