<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">文档发布系统</h1>
    </div>
    
    <el-row :gutter="20" class="mb-6">
      <el-col :span="6" v-for="stat in stats" :key="stat.title">
        <el-card shadow="hover">
          <div class="flex items-center">
            <div class="w-12 h-12 rounded-lg flex items-center justify-center mr-4" :class="stat.bgColor">
              <el-icon :size="24" :class="stat.iconColor"><component :is="stat.icon" /></el-icon>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-800">{{ stat.value }}</div>
              <div class="text-sm text-gray-500">{{ stat.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-bold">文档类型分布</span>
            </div>
          </template>
          <div v-if="docTypes.length">
            <div v-for="type in docTypes" :key="type.id" class="flex items-center justify-between py-3 border-b last:border-b-0">
              <div class="flex items-center">
                <el-tag class="mr-3">{{ type.name }}</el-tag>
                <span class="text-gray-600">{{ type.description || '' }}</span>
              </div>
              <span class="text-gray-500">{{ getCategoryCount(type.id) }} 个分类</span>
            </div>
          </div>
          <el-empty v-else description="暂无数据" />
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-bold">快速操作</span>
            </div>
          </template>
          <div class="grid grid-cols-2 gap-4">
            <el-button type="primary" size="large" class="h-20" @click="$router.push('/categories')">
              <div class="text-center">
                <el-icon :size="24"><Folder /></el-icon>
                <div class="mt-2">管理分类</div>
              </div>
            </el-button>
            <el-button type="success" size="large" class="h-20" @click="$router.push('/documents/edit')">
              <div class="text-center">
                <el-icon :size="24"><DocumentAdd /></el-icon>
                <div class="mt-2">新建文档</div>
              </div>
            </el-button>
            <el-button type="warning" size="large" class="h-20" @click="$router.push('/documents')">
              <div class="text-center">
                <el-icon :size="24"><Document /></el-icon>
                <div class="mt-2">文档列表</div>
              </div>
            </el-button>
            <el-button type="danger" size="large" class="h-20" @click="$router.push('/generate')">
              <div class="text-center">
                <el-icon :size="24"><Upload /></el-icon>
                <div class="mt-2">生成VitePress</div>
              </div>
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getDocTypes, getCategories, getDocuments } from '../api'

const docTypes = ref([])
const categories = ref([])
const documents = ref([])

const stats = computed(() => [
  { title: '文档类型', value: docTypes.value.length, icon: 'Collection', bgColor: 'bg-blue-100', iconColor: 'text-blue-500' },
  { title: '分类数量', value: categories.value.length, icon: 'Folder', bgColor: 'bg-green-100', iconColor: 'text-green-500' },
  { title: '文档数量', value: documents.value.length, icon: 'Document', bgColor: 'bg-orange-100', iconColor: 'text-orange-500' },
  { title: '今日更新', value: getTodayCount(), icon: 'Calendar', bgColor: 'bg-purple-100', iconColor: 'text-purple-500' }
])

const getCategoryCount = (docTypeId) => {
  return categories.value.filter(c => c.doc_type_id === docTypeId).length
}

const getTodayCount = () => {
  const today = new Date().toDateString()
  return documents.value.filter(d => new Date(d.updated_at).toDateString() === today).length
}

onMounted(async () => {
  try {
    const [typesRes, catsRes, docsRes] = await Promise.all([
      getDocTypes(),
      getCategories(),
      getDocuments()
    ])
    docTypes.value = typesRes.data
    categories.value = catsRes.data
    documents.value = docsRes.data
  } catch (e) {
    console.error('加载数据失败', e)
  }
})
</script>
