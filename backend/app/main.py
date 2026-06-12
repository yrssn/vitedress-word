import os
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional

from .models import (
    Category, CategoryCreate, CategoryUpdate,
    Document, DocumentCreate, DocumentUpdate, BatchDocumentCreate,
    DocType, DocTypeCreate, DocTypeUpdate
)
from .database import db
from .vitepress import generate_vitepress_files

app = FastAPI(
    title="文档发布系统 API",
    description="基于VitePress的文档管理系统后端API",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 文档类型管理 ==========

@app.get("/api/doc-types", response_model=List[DocType], tags=["文档类型"])
async def get_doc_types():
    """获取所有文档类型"""
    return await db.get_doc_types()


@app.get("/api/doc-types/{doc_type_id}", response_model=DocType, tags=["文档类型"])
async def get_doc_type(doc_type_id: str):
    """获取单个文档类型"""
    doc_type = await db.get_doc_type(doc_type_id)
    if not doc_type:
        raise HTTPException(status_code=404, detail="文档类型不存在")
    return doc_type


@app.post("/api/doc-types", response_model=DocType, tags=["文档类型"])
async def create_doc_type(data: DocTypeCreate):
    """创建文档类型"""
    return await db.create_doc_type(data.model_dump())


@app.put("/api/doc-types/{doc_type_id}", response_model=DocType, tags=["文档类型"])
async def update_doc_type(doc_type_id: str, data: DocTypeUpdate):
    """更新文档类型"""
    doc_type = await db.update_doc_type(doc_type_id, data.model_dump(exclude_unset=True))
    if not doc_type:
        raise HTTPException(status_code=404, detail="文档类型不存在")
    return doc_type


@app.delete("/api/doc-types/{doc_type_id}", tags=["文档类型"])
async def delete_doc_type(doc_type_id: str):
    """删除文档类型（同时删除该类型下的所有分类和文档）"""
    success = await db.delete_doc_type(doc_type_id)
    if not success:
        raise HTTPException(status_code=404, detail="文档类型不存在")
    return {"message": "删除成功"}


# ========== 分类管理 ==========

@app.get("/api/categories", response_model=List[Category], tags=["分类管理"])
async def get_categories(doc_type_id: Optional[str] = None):
    """获取所有分类，可按文档类型ID筛选"""
    return await db.get_categories(doc_type_id)


@app.get("/api/categories/{category_id}", response_model=Category, tags=["分类管理"])
async def get_category(category_id: str):
    """获取单个分类"""
    category = await db.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


@app.post("/api/categories", response_model=Category, tags=["分类管理"])
async def create_category(data: CategoryCreate):
    """创建分类"""
    return await db.create_category(data.model_dump())


@app.put("/api/categories/{category_id}", response_model=Category, tags=["分类管理"])
async def update_category(category_id: str, data: CategoryUpdate):
    """更新分类"""
    category = await db.update_category(category_id, data.model_dump(exclude_unset=True))
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


@app.delete("/api/categories/{category_id}", tags=["分类管理"])
async def delete_category(category_id: str):
    """删除分类（同时删除该分类下的所有文档）"""
    success = await db.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="分类不存在")
    return {"message": "删除成功"}


# ========== 文档管理 ==========

@app.get("/api/documents", response_model=List[Document], tags=["文档管理"])
async def get_documents(category_id: Optional[str] = None):
    """获取所有文档，可按分类筛选"""
    return await db.get_documents(category_id)


@app.get("/api/documents/{document_id}", response_model=Document, tags=["文档管理"])
async def get_document(document_id: str):
    """获取单个文档"""
    document = await db.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    return document


@app.post("/api/documents", response_model=Document, tags=["文档管理"])
async def create_document(data: DocumentCreate):
    """创建文档"""
    # 验证分类是否存在
    category = await db.get_category(data.category_id)
    if not category:
        raise HTTPException(status_code=400, detail="分类不存在")
    return await db.create_document(data.model_dump())


@app.post("/api/documents/batch", response_model=List[Document], tags=["文档管理"])
async def create_documents_batch(data: BatchDocumentCreate):
    """批量创建文档"""
    # 验证所有分类是否存在
    category_ids = set(doc.category_id for doc in data.documents)
    for cat_id in category_ids:
        category = await db.get_category(cat_id)
        if not category:
            raise HTTPException(status_code=400, detail=f"分类 {cat_id} 不存在")
    
    return await db.create_documents_batch([doc.model_dump() for doc in data.documents])


@app.put("/api/documents/{document_id}", response_model=Document, tags=["文档管理"])
async def update_document(document_id: str, data: DocumentUpdate):
    """更新文档"""
    if data.category_id:
        category = await db.get_category(data.category_id)
        if not category:
            raise HTTPException(status_code=400, detail="分类不存在")
    
    document = await db.update_document(document_id, data.model_dump(exclude_unset=True))
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    return document


@app.delete("/api/documents/{document_id}", tags=["文档管理"])
async def delete_document(document_id: str):
    """删除文档"""
    success = await db.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="文档不存在")
    return {"message": "删除成功"}


# ========== VitePress生成 ==========

@app.post("/api/generate", tags=["VitePress"])
async def generate_docs():
    """生成VitePress文档文件"""
    result = await generate_vitepress_files()
    return {
        "message": "文档生成成功",
        **result
    }


@app.get("/api/health", tags=["系统"])
async def health_check():
    """健康检查"""
    return {"status": "ok"}


# ========== 文件上传 ==========

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.ico'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@app.post("/api/upload", tags=["文件上传"])
async def upload_file(file: UploadFile = File(...)):
    """上传文件（图片）"""
    # 检查文件扩展名
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext}")
    
    # 读取文件内容
    content = await file.read()
    
    # 检查文件大小
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过10MB限制")
    
    # 生成唯一文件名
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    
    # 保存文件
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # 返回文件URL
    return {
        "url": f"/uploads/{unique_name}",
        "filename": file.filename
    }
