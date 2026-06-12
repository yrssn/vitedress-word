<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">生成VitePress文档</h1>
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
              点击下方按钮，将所有文档生成为VitePress格式，<br>
              生成后可以使用VitePress预览或构建静态站点。
            </p>
            <el-button type="primary" size="large" @click="handleGenerate" :loading="generating">
              <el-icon><Upload /></el-icon>
              生成VitePress文档
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="font-bold">生成结果</span>
          </template>
          <div v-if="result" class="space-y-4">
            <el-alert type="success" :closable="false">
              <template #title>
                <span class="font-bold">文档生成成功！</span>
              </template>
            </el-alert>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="文档目录">{{ result.docs_dir }}</el-descriptions-item>
              <el-descriptions-item label="分类数量">{{ result.categories_count }}</el-descriptions-item>
              <el-descriptions-item label="文档数量">{{ result.documents_count }}</el-descriptions-item>
            </el-descriptions>
            <div class="bg-gray-100 p-4 rounded">
              <p class="text-sm text-gray-600 mb-2">预览命令：</p>
              <code class="text-sm">cd docs && npx vitepress dev</code>
            </div>
            <div class="bg-gray-100 p-4 rounded">
              <p class="text-sm text-gray-600 mb-2">构建命令：</p>
              <code class="text-sm">cd docs && npx vitepress build</code>
            </div>
          </div>
          <el-empty v-else description="尚未生成文档" />
        </el-card>
      </el-col>
    </el-row>

    <el-card class="mt-6">
      <template #header>
        <span class="font-bold">使用说明</span>
      </template>
      <el-steps :active="3" align-center>
        <el-step title="创建分类" description="在分类管理中创建文档分类" />
        <el-step title="编写文档" description="在文档管理中编写Markdown文档" />
        <el-step title="生成文档" description="点击生成按钮生成VitePress文件" />
        <el-step title="预览/发布" description="使用VitePress预览或构建发布" />
      </el-steps>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { generateDocs } from '../api'

const generating = ref(false)
const result = ref(null)

const handleGenerate = async () => {
  generating.value = true
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
</script>
