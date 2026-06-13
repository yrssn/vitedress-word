<template>
  <div class="page-container h-full flex flex-col">
    <div class="page-header">
      <h1 class="page-title">{{ isEdit ? '编辑文档' : '新建文档' }}</h1>
      <div class="flex gap-2">
        <el-button @click="$router.back()">返回</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </div>
    </div>

    <el-card class="flex-1 flex flex-col">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" class="mb-4">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="文档标题" prop="title">
              <el-input v-model="form.title" placeholder="请输入文档标题" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="所属位置" prop="location">
              <el-cascader
                v-model="categoryValue"
                :options="categoryOptions"
                :props="{ expandTrigger: 'hover', checkStrictly: true }"
                placeholder="选择文档类型（可选分类）"
                class="w-full"
                @change="onCategoryChange"
              />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="排序" prop="order">
              <el-input-number v-model="form.order" :min="0" :max="9999" class="w-full" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <div class="flex-1 min-h-0">
        <MdEditor
          v-model="form.content"
          :theme="'light'"
          :preview="true"
          style="height: calc(100vh - 280px)"
          @onUploadImg="onUploadImg"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { getDocTypes, getCategories, getDocument, createDocument, updateDocument, uploadFile } from '../api'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const saving = ref(false)
const docTypes = ref([])
const categories = ref([])
const categoryValue = ref([])

const isEdit = computed(() => !!route.params.id)

const form = ref({
  title: '',
  content: '# 文档标题\n\n开始编写您的文档内容...',
  category_id: null,
  doc_type_id: null,
  order: 0
})

const rules = {
  title: [{ required: true, message: '请输入文档标题', trigger: 'blur' }],
  location: [{
    validator: (rule, value, callback) => {
      if (!categoryValue.value || categoryValue.value.length === 0) {
        callback(new Error('请选择文档类型'))
      } else {
        callback()
      }
    },
    trigger: 'change'
  }]
}

const categoryOptions = computed(() => {
  if (!Array.isArray(categories.value) || !Array.isArray(docTypes.value)) {
    return []
  }
  const groups = {}
  categories.value.forEach(cat => {
    const typeId = cat.doc_type_id
    if (!typeId) return
    if (!groups[typeId]) {
      const typeInfo = docTypes.value.find(t => t.id === typeId)
      groups[typeId] = {
        value: typeId,
        label: typeInfo?.name || '未知类型',
        children: []
      }
    }
    groups[typeId].children.push({
      value: cat.id,
      label: cat.name
    })
  })
  // 包含没有分类的文档类型
  docTypes.value.forEach(dt => {
    if (!groups[dt.id]) {
      groups[dt.id] = {
        value: dt.id,
        label: dt.name,
        children: []
      }
    }
  })
  return Object.values(groups)
})

const onCategoryChange = (value) => {
  if (value && value.length === 2) {
    // 选了文档类型 + 分类
    form.value.category_id = value[1]
    form.value.doc_type_id = null
  } else if (value && value.length === 1) {
    // 只选了文档类型（独立文档，无分类）
    form.value.category_id = null
    form.value.doc_type_id = value[0]
  }
}

const onUploadImg = async (files, callback) => {
  const results = []
  for (const file of files) {
    try {
      const res = await uploadFile(file)
      results.push({
        url: res.data.url,
        alt: file.name,
        title: file.name
      })
    } catch (e) {
      ElMessage.error(`上传失败: ${file.name}`)
    }
  }
  callback(results)
}

const handleSave = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (isEdit.value) {
      await updateDocument(route.params.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await createDocument(form.value)
      ElMessage.success('创建成功')
      router.push('/documents')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const [typesRes, catsRes] = await Promise.all([getDocTypes(), getCategories()])
    docTypes.value = Array.isArray(typesRes.data) ? typesRes.data : []
    categories.value = Array.isArray(catsRes.data) ? catsRes.data : []
  } catch (e) {
    console.error('加载数据失败', e)
    docTypes.value = []
    categories.value = []
  }

  if (isEdit.value) {
    try {
      const res = await getDocument(route.params.id)
      form.value = res.data
      // 设置级联选择器的值
      if (form.value.category_id) {
        const cat = categories.value.find(c => c.id === form.value.category_id)
        if (cat) {
          categoryValue.value = [cat.doc_type_id, cat.id]
        }
      } else if (form.value.doc_type_id) {
        categoryValue.value = [form.value.doc_type_id]
      }
    } catch (e) {
      ElMessage.error('加载文档失败')
      router.push('/documents')
    }
  }
})
</script>
