<template>
  <div class="login-container">
    <el-card class="login-card" shadow="always">
      <div class="text-center mb-8">
        <el-icon :size="48" class="text-blue-500 mb-4"><Document /></el-icon>
        <h1 class="text-2xl font-bold text-gray-800">文档发布系统</h1>
        <p class="text-gray-500 mt-2">请登录以继续</p>
      </div>

      <el-tabs v-model="activeTab" class="mb-4">
        <el-tab-pane label="登录" name="login" />
        <el-tab-pane label="注册" name="register" />
      </el-tabs>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleSubmit"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleSubmit"
          />
        </el-form-item>

        <el-button
          type="primary"
          size="large"
          class="w-full"
          :loading="loading"
          @click="handleSubmit"
        >
          {{ activeTab === 'login' ? '登 录' : '注 册' }}
        </el-button>
      </el-form>

      <div class="text-center mt-4 text-sm text-gray-400">
        默认账号：admin / admin123
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login, register } from '../api'

const router = useRouter()
const formRef = ref(null)
const activeTab = ref('login')
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const api = activeTab.value === 'login' ? login : register
    const res = await api(form)
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('username', res.data.username)
    ElMessage.success(activeTab.value === 'login' ? '登录成功' : '注册成功')
    router.push('/')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 420px;
  padding: 20px;
  border-radius: 12px;
}
</style>
