<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">分类管理</h1>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        新建分类
      </el-button>
    </div>

    <el-card>
      <el-tabs v-model="activeTab" @tab-change="loadCategories">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane v-for="type in docTypes" :key="type.id" :label="type.name" :name="type.id" />
      </el-tabs>

      <el-table :data="categories" v-loading="loading" stripe>
        <el-table-column prop="name" label="分类名称" min-width="150">
          <template #default="{ row }">
            <div class="flex items-center">
              <el-icon v-if="row.icon" class="mr-2"><component :is="row.icon" /></el-icon>
              <span class="font-medium">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="doc_type_name" label="文档类型" width="150">
          <template #default="{ row }">
            <el-tag>{{ row.doc_type_name || '未知' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="doc_count" label="文档数" width="100" align="center" />
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除该分类？删除后该分类下的文档也会被删除" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑分类' : '新建分类'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="文档类型" prop="doc_type_id">
          <el-select v-model="form.doc_type_id" placeholder="请选择文档类型" :disabled="!!editingId" class="w-full">
            <el-option v-for="type in docTypes" :key="type.id" :label="type.name" :value="type.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入分类描述" />
        </el-form-item>
        <el-form-item label="图标" prop="icon">
          <el-input v-model="form.icon" placeholder="Element Plus图标名称，如 Document" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getDocTypes, getCategories, createCategory, updateCategory, deleteCategory } from '../api'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const activeTab = ref('all')
const docTypes = ref([])
const categories = ref([])
const editingId = ref(null)
const formRef = ref(null)

const form = ref({
  name: '',
  doc_type_id: '',
  description: '',
  icon: ''
})

const rules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
  doc_type_id: [{ required: true, message: '请选择文档类型', trigger: 'change' }]
}

const formatDate = (date) => {
  return new Date(date).toLocaleString('zh-CN')
}

const loadCategories = async () => {
  loading.value = true
  try {
    const docType = activeTab.value === 'all' ? undefined : activeTab.value
    const res = await getCategories(docType)
    categories.value = res.data
  } catch (e) {
    ElMessage.error('加载分类失败')
  } finally {
    loading.value = false
  }
}

const openDialog = (row = null) => {
  editingId.value = row?.id || null
  form.value = row ? { ...row } : { name: '', doc_type_id: '', description: '', icon: '' }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editingId.value) {
      await updateCategory(editingId.value, { name: form.value.name, description: form.value.description, icon: form.value.icon })
      ElMessage.success('更新成功')
    } else {
      await createCategory(form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadCategories()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await deleteCategory(id)
    ElMessage.success('删除成功')
    loadCategories()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(async () => {
  const res = await getDocTypes()
  docTypes.value = res.data
  loadCategories()
})
</script>
