<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">生成 & 发布文档</h1>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="font-bold">生成文档</span>
          </template>
          <div class="text-center py-8">
            <el-icon :size="64" class="text-blue-500 mb-4"><Document /></el-icon>
            <p class="text-gray-600 mb-6">
              生成VitePress Markdown文件，<br>
              可用于本地预览。
            </p>
            <el-button type="primary" size="large" @click="handleGenerate" :loading="generating">
              <el-icon><Document /></el-icon>
              生成Markdown文件
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="font-bold">构建 & 发布</span>
          </template>
          <div class="text-center py-8">
            <el-icon :size="64" class="text-green-500 mb-4"><Upload /></el-icon>
            <p class="text-gray-600 mb-6">
              生成文档并构建为静态站点，<br>
              构建完成后可直接在线访问。
            </p>
            <el-button type="success" size="large" @click="handleBuild" :loading="building">
              <el-icon><Upload /></el-icon>
              构建并发布
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 结果展示 -->
    <el-card class="mt-6" v-if="result">
      <template #header>
        <span class="font-bold">{{ buildResult ? '构建结果' : '生成结果' }}</span>
      </template>
      <el-alert :type="buildResult ? 'success' : 'info'" :closable="false" class="mb-4">
        <template #title>
          <span class="font-bold">{{ result.message }}</span>
        </template>
      </el-alert>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="文档类型">{{ result.doc_types_count }} 个</el-descriptions-item>
        <el-descriptions-item label="分类数量">{{ result.categories_count }} 个</el-descriptions-item>
        <el-descriptions-item label="文档数量">{{ result.documents_count }} 个</el-descriptions-item>
        <el-descriptions-item v-if="buildResult" label="输出目录">{{ result.dist_dir }}</el-descriptions-item>
      </el-descriptions>
      <div v-if="buildResult" class="mt-4">
        <el-alert type="success" :closable="false">
          文档站点已构建完成，可通过 docs 服务访问。
        </el-alert>
      </div>
    </el-card>

    <el-card class="mt-6">
      <template #header>
        <span class="font-bold">使用说明</span>
      </template>
      <el-steps :active="3" align-center>
        <el-step title="创建分类" description="在分类管理中创建文档分类" />
        <el-step title="编写文档" description="在文档管理中编写Markdown文档" />
        <el-step title="生成文档" description="点击生成按钮生成VitePress文件" />
        <el-step title="构建发布" description="点击构建发布，生成静态站点" />
      </el-steps>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { generateDocs, buildDocs } from '../api'

const generating = ref(false)
const building = ref(false)
const result = ref(null)
const buildResult = ref(false)

const handleGenerate = async () => {
  generating.value = true
  buildResult.value = false
  try {
    const res = await generateDocs()
    result.value = res.data
    ElMessage.success('文档生成成功')
  } catch (e) {
    ElMessage.error('生成失败：' + (e.response?.data?.detail || e.message))
  } finally {
    generating.value = false
  }
}

const handleBuild = async () => {
  building.value = true
  buildResult.value = false
  try {
    const res = await buildDocs()
    result.value = res.data
    buildResult.value = true
    ElMessage.success('文档构建发布成功')
  } catch (e) {
    ElMessage.error('构建失败：' + (e.response?.data?.detail || e.message))
  } finally {
    building.value = false
  }
}
</script>
