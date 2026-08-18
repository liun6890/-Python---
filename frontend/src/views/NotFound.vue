<template>
  <div class="not-found-container">
    <div class="content">
      <h1 class="code">404</h1>
      <h2 class="desc">抱歉，您访问的页面不存在</h2>
      <el-button type="primary" size="large" @click="$router.push('/')">
        返回首页
      </el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
  
  .content {
    text-align: center;
    
    .code {
      font-size: 120px;
      margin: 0;
      color: #409EFF;
      font-weight: bold;
      line-height: 1.2;
    }
    
    .desc {
      font-size: 24px;
      color: #606266;
      margin: 20px 0 40px;
    }
  }
}
</style>
