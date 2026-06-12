<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">文档管理</h1>
      <div class="flex gap-2">
        <el-button type="success" @click="$router.push('/documents/edit')">
          <el-icon><Plus /></el-icon>
          新建文档
        </el-button>
      </div>
    </div>

    <el-card>
      <div class="flex gap-4 mb-4">
        <el-select v-model="filterDocType" placeholder="文档类型" clearable @change="onFilterChange" class="w-40">
          <el-option v-for="type in docTypes" :key="type.value" :label="type.label" :value="type.value" />
        </el-select>
        <el-select v-model="filterCategory" placeholder="选择分类" clearable @change="loadDocuments" class="w-48">
          <el-option v-for="cat in filteredCategories" :key="cat.id" :label="cat.name" :value="cat.id" />
        </el-select>
        <el-input v-model="searchText" placeholder="搜索文档标题" clearable class="w-60" @input="onSearch">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
      </div>

      <el-table :data="filteredDocuments" v-loading="loading" stripe>
        <el-table-column prop="title" label="文档标题" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="$router.push(`/documents/edit/${row.id}`)">{{ row.title }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="category_id" label="所属分类" width="150">
          <template #default="{ row }">
            <el-tag>{{ getCategoryName(row.category_id) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="order" label="排序" width="80" align="center" />
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="$router.push(`/documents/edit/${row.id}`)">编辑</el-button>
            <el-popconfirm title="确定删除该文档？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getDocTypes, getCategories, getDocuments, deleteDocument } from '../api'

const loading = ref(false)
const docTypes = ref([])
const categories = ref([])
const documents = ref([])
const filterDocType = ref('')
const filterCategory = ref('')
const searchText = ref('')

const filteredCategories = computed(() => {
  if (!filterDocType.value) return categories.value
  return categories.value.filter(c => c.doc_type === filterDocType.value)
})

const filteredDocuments = computed(() => {
  let docs = documents.value
  if (searchText.value) {
    docs = docs.filter(d => d.title.toLowerCase().includes(searchText.value.toLowerCase()))
  }
  return docs
})

const getCategoryName = (id) => {
  const cat = categories.value.find(c => c.id === id)
  return cat?.name || id
}

const formatDate = (date) => {
  return new Date(date).toLocaleString('zh-CN')
}

const onFilterChange = () => {
  filterCategory.value = ''
  loadDocuments()
}

const onSearch = () => {
  // 搜索由computed属性处理
}

const loadDocuments = async () => {
  loading.value = true
  try {
    const res = await getDocuments(filterCategory.value || undefined)
    documents.value = res.data
  } catch (e) {
    ElMessage.error('加载文档失败')
  } finally {
    loading.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await deleteDocument(id)
    ElMessage.success('删除成功')
    loadDocuments()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(async () => {
  const [typesRes, catsRes] = await Promise.all([getDocTypes(), getCategories()])
  docTypes.value = typesRes.data
  categories.value = catsRes.data
  loadDocuments()
})
</script>
