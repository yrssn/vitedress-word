from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========== 文档类型模型 ==========

class DocTypeBase(BaseModel):
    """文档类型基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="类型名称，如：进销存系统")
    value: str = Field(..., min_length=1, max_length=50, description="类型标识，如：inventory")
    description: Optional[str] = Field(None, max_length=200, description="类型描述")
    icon: Optional[str] = Field(None, description="图标")
    order: int = Field(default=0, description="排序")


class DocTypeCreate(DocTypeBase):
    """创建文档类型"""
    pass


class DocTypeUpdate(BaseModel):
    """更新文档类型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    icon: Optional[str] = None
    order: Optional[int] = None


class DocType(DocTypeBase):
    """文档类型完整模型"""
    id: str
    created_at: datetime
    updated_at: datetime


# ========== 分类模型 ==========

class CategoryBase(BaseModel):
    """分类基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="分类名称")
    doc_type_id: str = Field(..., description="所属文档类型ID")
    description: Optional[str] = Field(None, max_length=500, description="分类描述")
    icon: Optional[str] = Field(None, description="分类图标")


class CategoryCreate(CategoryBase):
    """创建分类"""
    pass


class CategoryUpdate(BaseModel):
    """更新分类"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = None


class Category(CategoryBase):
    """分类完整模型"""
    id: str
    created_at: datetime
    updated_at: datetime
    doc_count: int = 0
    doc_type_name: Optional[str] = None  # 关联的文档类型名称


class DocumentBase(BaseModel):
    """文档基础模型"""
    title: str = Field(..., min_length=1, max_length=200, description="文档标题")
    content: str = Field(..., description="Markdown内容")
    category_id: str = Field(..., description="所属分类ID")
    order: int = Field(default=0, description="排序顺序")


class DocumentCreate(DocumentBase):
    """创建文档"""
    pass


class DocumentUpdate(BaseModel):
    """更新文档"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    category_id: Optional[str] = None
    order: Optional[int] = None


class Document(DocumentBase):
    """文档完整模型"""
    id: str
    slug: str  # URL友好的标识符
    created_at: datetime
    updated_at: datetime


class BatchDocumentCreate(BaseModel):
    """批量创建文档"""
    documents: List[DocumentCreate]


