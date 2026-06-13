<template>
  <div class="login-wrapper">
    <!-- 左侧品牌区 -->
    <div class="login-brand">
      <div class="brand-content">
        <el-icon :size="64" class="brand-icon"><Document /></el-icon>
        <h1 class="brand-title">文档发布系统</h1>
        <p class="brand-desc">
          基于 VitePress 的企业级文档管理平台<br>
          统一管理、一键生成、快速发布
        </p>
        <div class="brand-features">
          <div class="feature-item">
            <el-icon><Folder /></el-icon>
            <span>多类型文档分类管理</span>
          </div>
          <div class="feature-item">
            <el-icon><Edit /></el-icon>
            <span>Markdown 在线编辑</span>
          </div>
          <div class="feature-item">
            <el-icon><Upload /></el-icon>
            <span>一键构建发布静态站点</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧登录表单 -->
    <div class="login-form-area">
      <div class="login-form-wrapper">
        <h2 class="form-title">欢迎登录</h2>
        <p class="form-subtitle">请输入您的账号信息</p>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          size="large"
          @submit.prevent="handleLogin"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              prefix-icon="User"
            />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-button
            type="primary"
            size="large"
            class="w-full mt-2"
            :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '../api'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await login(form)
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('username', res.data.username)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
}

/* 左侧品牌区 */
.login-brand {
  flex: 1;
  background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 50%, #3b7dd8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: #fff;
}

.brand-content {
  max-width: 400px;
}

.brand-icon {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 24px;
}

.brand-title {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 16px;
  letter-spacing: 2px;
}

.brand-desc {
  font-size: 16px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 48px;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  color: rgba(255, 255, 255, 0.85);
}

.feature-item .el-icon {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.7);
}

/* 右侧表单区 */
.login-form-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  padding: 60px;
}

.login-form-wrapper {
  width: 100%;
  max-width: 380px;
}

.form-title {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.form-subtitle {
  font-size: 14px;
  color: #909399;
  margin-bottom: 36px;
}
</style>
