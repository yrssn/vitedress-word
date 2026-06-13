<template>
  <el-config-provider :locale="zhCn">
    <!-- 登录页不显示侧边栏 -->
    <router-view v-if="isLoginPage" />

    <!-- 主布局 -->
    <el-container v-else class="h-screen">
      <el-aside width="220px" class="bg-slate-800">
        <div class="p-4 text-white text-xl font-bold border-b border-slate-700">
          <el-icon><Document /></el-icon>
          文档发布系统
        </div>
        <el-menu
          :default-active="activeMenu"
          class="border-none"
          background-color="#1e293b"
          text-color="#94a3b8"
          active-text-color="#fff"
          router
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/doc-types">
            <el-icon><Collection /></el-icon>
            <span>文档类型</span>
          </el-menu-item>
          <el-menu-item index="/categories">
            <el-icon><Folder /></el-icon>
            <span>分类管理</span>
          </el-menu-item>
          <el-menu-item index="/documents">
            <el-icon><Document /></el-icon>
            <span>文档管理</span>
          </el-menu-item>
          <el-menu-item index="/generate">
            <el-icon><Upload /></el-icon>
            <span>生成文档</span>
          </el-menu-item>
        </el-menu>

        <!-- 用户信息 & 退出 -->
        <div class="absolute bottom-0 left-0 w-[220px] p-4 border-t border-slate-700">
          <div class="flex items-center justify-between text-slate-400 text-sm">
            <span class="truncate">
              <el-icon><User /></el-icon>
              {{ username }}
            </span>
            <el-button type="danger" text size="small" @click="handleLogout">
              退出
            </el-button>
          </div>
        </div>
      </el-aside>
      <el-main class="bg-gray-50 p-0">
        <router-view />
      </el-main>
    </el-container>
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => route.path)
const isLoginPage = computed(() => route.path === '/login')
const username = computed(() => localStorage.getItem('username') || '')

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  router.push('/login')
}
</script>

<style>
.el-aside {
  height: 100vh;
  position: relative;
}
.el-menu {
  border-right: none !important;
}
</style>
