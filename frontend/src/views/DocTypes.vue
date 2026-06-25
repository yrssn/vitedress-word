<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">文档类型管理</h1>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        新建类型
      </el-button>
    </div>

    <el-card>
      <el-table :data="docTypes" v-loading="loading" stripe>
        <el-table-column prop="name" label="类型名称" min-width="150">
          <template #default="{ row }">
            <div class="flex items-center">
              <el-icon v-if="row.icon" class="mr-2"><component :is="row.icon" /></el-icon>
              <span class="font-medium">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="value" label="类型标识" width="150">
          <template #default="{ row }">
            <el-tag type="info">{{ row.value }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="order" label="排序" width="80" align="center" />
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除该类型？删除后该类型下的所有分类和文档也会被删除" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑文档类型' : '新建文档类型'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="类型名称" prop="name">
          <el-input v-model="form.name" placeholder="如：进销存系统" />
        </el-form-item>
        <el-form-item label="类型标识" prop="value">
          <el-input v-model="form.value" placeholder="如：inventory（英文小写）" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入类型描述" />
        </el-form-item>
        <el-form-item label="图标" prop="icon">
          <el-input v-model="form.icon" placeholder="Element Plus图标名称，如 Document" />
        </el-form-item>
        <el-form-item label="排序" prop="order">
          <el-input-number v-model="form.order" :min="-9999" :max="9999" />
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
import { getDocTypes, createDocType, updateDocType, deleteDocType } from '../api'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const docTypes = ref([])
const editingId = ref(null)
const formRef = ref(null)

const form = ref({
  name: '',
  value: '',
  description: '',
  icon: '',
  order: 0
})

const rules = {
  name: [{ required: true, message: '请输入类型名称', trigger: 'blur' }],
  value: [
    { required: true, message: '请输入类型标识', trigger: 'blur' },
    { pattern: /^[a-z][a-z0-9_]*$/, message: '只能使用小写字母、数字和下划线，且以字母开头', trigger: 'blur' }
  ]
}

const formatDate = (date) => {
  return new Date(date).toLocaleString('zh-CN')
}

const loadDocTypes = async () => {
  loading.value = true
  try {
    const res = await getDocTypes()
    console.log('doc-types response:', res.data)
    docTypes.value = Array.isArray(res.data) ? res.data : []
  } catch (e) {
    console.error('加载文档类型失败', e)
    ElMessage.error('加载文档类型失败')
    docTypes.value = []
  } finally {
    loading.value = false
  }
}

const openDialog = (row = null) => {
  editingId.value = row?.id || null
  form.value = row ? { ...row } : { name: '', value: '', description: '', icon: '', order: 0 }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editingId.value) {
      await updateDocType(editingId.value, { 
        name: form.value.name, 
        description: form.value.description, 
        icon: form.value.icon,
        order: form.value.order
      })
      ElMessage.success('更新成功')
    } else {
      await createDocType(form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadDocTypes()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await deleteDocType(id)
    ElMessage.success('删除成功')
    loadDocTypes()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadDocTypes()
})
</script>
