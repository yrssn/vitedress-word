import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 文档类型管理
export const getDocTypes = () => api.get('/doc-types')
export const getDocType = (id) => api.get(`/doc-types/${id}`)
export const createDocType = (data) => api.post('/doc-types', data)
export const updateDocType = (id, data) => api.put(`/doc-types/${id}`, data)
export const deleteDocType = (id) => api.delete(`/doc-types/${id}`)

// 分类管理
export const getCategories = (docTypeId) => api.get('/categories', { params: { doc_type_id: docTypeId } })
export const getCategory = (id) => api.get(`/categories/${id}`)
export const createCategory = (data) => api.post('/categories', data)
export const updateCategory = (id, data) => api.put(`/categories/${id}`, data)
export const deleteCategory = (id) => api.delete(`/categories/${id}`)

// 文档管理
export const getDocuments = (categoryId) => api.get('/documents', { params: { category_id: categoryId } })
export const getDocument = (id) => api.get(`/documents/${id}`)
export const createDocument = (data) => api.post('/documents', data)
export const createDocumentsBatch = (documents) => api.post('/documents/batch', { documents })
export const updateDocument = (id, data) => api.put(`/documents/${id}`, data)
export const deleteDocument = (id) => api.delete(`/documents/${id}`)

// VitePress生成
export const generateDocs = () => api.post('/generate')

// 文件上传
export const uploadFile = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export default api
