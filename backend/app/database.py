import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import uuid
import re
import aiofiles
import asyncio

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DOC_TYPES_FILE = os.path.join(DATA_DIR, "doc_types.json")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")
DOCUMENTS_FILE = os.path.join(DATA_DIR, "documents.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)


def generate_id() -> str:
    """生成唯一ID"""
    return str(uuid.uuid4())[:8]


def generate_slug(title: str) -> str:
    """生成URL友好的slug"""
    # 移除特殊字符，保留中文、字母、数字
    slug = re.sub(r'[^\w\u4e00-\u9fff-]', '-', title.lower())
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug or generate_id()


def datetime_serializer(obj):
    """JSON序列化datetime"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def datetime_deserializer(data: dict) -> dict:
    """反序列化datetime字段"""
    for key in ['created_at', 'updated_at']:
        if key in data and isinstance(data[key], str):
            data[key] = datetime.fromisoformat(data[key])
    return data


class Database:
    """简单的JSON文件数据库"""
    
    def __init__(self):
        self._lock = asyncio.Lock()
        self._init_files()
    
    def _init_files(self):
        """初始化数据文件"""
        if not os.path.exists(DOC_TYPES_FILE):
            with open(DOC_TYPES_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
        if not os.path.exists(CATEGORIES_FILE):
            with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
        if not os.path.exists(DOCUMENTS_FILE):
            with open(DOCUMENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    async def init_default_admin(self):
        """首次启动时创建默认管理员账号"""
        users = await self._read_file(USERS_FILE)
        if not users:
            from .auth import get_password_hash
            now = datetime.now()
            admin = {
                'id': generate_id(),
                'username': os.getenv('DEFAULT_ADMIN_USER', 'admin'),
                'password_hash': get_password_hash(os.getenv('DEFAULT_ADMIN_PASS', 'admin123')),
                'created_at': now,
                'updated_at': now
            }
            users.append(admin)
            await self._write_file(USERS_FILE, users)

    # ========== 用户操作 ==========

    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """根据用户名查找用户"""
        users = await self._read_file(USERS_FILE)
        for user in users:
            if user['username'] == username:
                return user
        return None

    async def create_user(self, data: dict) -> dict:
        """创建用户"""
        async with self._lock:
            users = await self._read_file(USERS_FILE)
            for u in users:
                if u['username'] == data['username']:
                    raise ValueError("用户名已存在")
            now = datetime.now()
            user = {
                'id': generate_id(),
                'username': data['username'],
                'password_hash': data['password_hash'],
                'created_at': now,
                'updated_at': now
            }
            users.append(user)
            await self._write_file(USERS_FILE, users)
            return user

    async def _read_file(self, filepath: str) -> List[dict]:
        """读取JSON文件"""
        async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
            content = await f.read()
            data = json.loads(content)
            return [datetime_deserializer(item) for item in data]
    
    async def _write_file(self, filepath: str, data: List[dict]):
        """写入JSON文件"""
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2, default=datetime_serializer))
    
    # ========== 文档类型操作 ==========
    
    async def get_doc_types(self) -> List[dict]:
        """获取所有文档类型"""
        doc_types = await self._read_file(DOC_TYPES_FILE)
        return sorted(doc_types, key=lambda x: x.get('order', 0))
    
    async def get_doc_type(self, doc_type_id: str) -> Optional[dict]:
        """获取单个文档类型"""
        doc_types = await self._read_file(DOC_TYPES_FILE)
        for dt in doc_types:
            if dt['id'] == doc_type_id:
                return dt
        return None
    
    async def create_doc_type(self, data: dict) -> dict:
        """创建文档类型"""
        async with self._lock:
            doc_types = await self._read_file(DOC_TYPES_FILE)
            now = datetime.now()
            doc_type = {
                'id': generate_id(),
                **data,
                'created_at': now,
                'updated_at': now
            }
            doc_types.append(doc_type)
            await self._write_file(DOC_TYPES_FILE, doc_types)
            return doc_type
    
    async def update_doc_type(self, doc_type_id: str, data: dict) -> Optional[dict]:
        """更新文档类型"""
        async with self._lock:
            doc_types = await self._read_file(DOC_TYPES_FILE)
            for i, dt in enumerate(doc_types):
                if dt['id'] == doc_type_id:
                    for key, value in data.items():
                        if value is not None:
                            dt[key] = value
                    dt['updated_at'] = datetime.now()
                    doc_types[i] = dt
                    await self._write_file(DOC_TYPES_FILE, doc_types)
                    return dt
            return None
    
    async def delete_doc_type(self, doc_type_id: str) -> bool:
        """删除文档类型（同时删除该类型下的所有分类和文档）"""
        async with self._lock:
            doc_types = await self._read_file(DOC_TYPES_FILE)
            new_doc_types = [dt for dt in doc_types if dt['id'] != doc_type_id]
            if len(new_doc_types) == len(doc_types):
                return False
            await self._write_file(DOC_TYPES_FILE, new_doc_types)
            
            # 删除该类型下的所有分类
            categories = await self._read_file(CATEGORIES_FILE)
            cat_ids_to_delete = [c['id'] for c in categories if c.get('doc_type_id') == doc_type_id]
            new_categories = [c for c in categories if c.get('doc_type_id') != doc_type_id]
            await self._write_file(CATEGORIES_FILE, new_categories)
            
            # 删除这些分类下的所有文档
            if cat_ids_to_delete:
                documents = await self._read_file(DOCUMENTS_FILE)
                new_documents = [d for d in documents if d.get('category_id') not in cat_ids_to_delete]
                await self._write_file(DOCUMENTS_FILE, new_documents)
            return True
    
    # ========== 分类操作 ==========
    
    async def get_categories(self, doc_type_id: Optional[str] = None) -> List[dict]:
        """获取所有分类"""
        categories = await self._read_file(CATEGORIES_FILE)
        if doc_type_id:
            categories = [c for c in categories if c.get('doc_type_id') == doc_type_id]
        # 计算每个分类的文档数量，并获取文档类型名称
        documents = await self._read_file(DOCUMENTS_FILE)
        doc_types = await self._read_file(DOC_TYPES_FILE)
        doc_type_map = {dt['id']: dt['name'] for dt in doc_types}
        for cat in categories:
            cat['doc_count'] = len([d for d in documents if d.get('category_id') == cat['id']])
            cat['doc_type_name'] = doc_type_map.get(cat.get('doc_type_id'), '')
        return categories
    
    async def get_category(self, category_id: str) -> Optional[dict]:
        """获取单个分类"""
        categories = await self._read_file(CATEGORIES_FILE)
        for cat in categories:
            if cat['id'] == category_id:
                documents = await self._read_file(DOCUMENTS_FILE)
                cat['doc_count'] = len([d for d in documents if d.get('category_id') == cat['id']])
                return cat
        return None
    
    async def create_category(self, data: dict) -> dict:
        """创建分类"""
        async with self._lock:
            categories = await self._read_file(CATEGORIES_FILE)
            now = datetime.now()
            category = {
                'id': generate_id(),
                **data,
                'created_at': now,
                'updated_at': now,
                'doc_count': 0
            }
            categories.append(category)
            await self._write_file(CATEGORIES_FILE, categories)
            return category
    
    async def update_category(self, category_id: str, data: dict) -> Optional[dict]:
        """更新分类"""
        async with self._lock:
            categories = await self._read_file(CATEGORIES_FILE)
            for i, cat in enumerate(categories):
                if cat['id'] == category_id:
                    for key, value in data.items():
                        if value is not None:
                            cat[key] = value
                    cat['updated_at'] = datetime.now()
                    categories[i] = cat
                    await self._write_file(CATEGORIES_FILE, categories)
                    return cat
            return None
    
    async def delete_category(self, category_id: str) -> bool:
        """删除分类（同时删除该分类下的所有文档）"""
        async with self._lock:
            categories = await self._read_file(CATEGORIES_FILE)
            new_categories = [c for c in categories if c['id'] != category_id]
            if len(new_categories) == len(categories):
                return False
            await self._write_file(CATEGORIES_FILE, new_categories)
            
            # 删除该分类下的所有文档
            documents = await self._read_file(DOCUMENTS_FILE)
            new_documents = [d for d in documents if d.get('category_id') != category_id]
            await self._write_file(DOCUMENTS_FILE, new_documents)
            return True
    
    # ========== 文档操作 ==========
    
    async def get_documents(self, category_id: Optional[str] = None) -> List[dict]:
        """获取所有文档"""
        documents = await self._read_file(DOCUMENTS_FILE)
        if category_id:
            documents = [d for d in documents if d.get('category_id') == category_id]
        return sorted(documents, key=lambda x: x.get('order', 0))
    
    async def get_document(self, document_id: str) -> Optional[dict]:
        """获取单个文档"""
        documents = await self._read_file(DOCUMENTS_FILE)
        for doc in documents:
            if doc['id'] == document_id:
                return doc
        return None
    
    async def create_document(self, data: dict) -> dict:
        """创建文档"""
        async with self._lock:
            documents = await self._read_file(DOCUMENTS_FILE)
            now = datetime.now()
            document = {
                'id': generate_id(),
                'slug': generate_slug(data['title']),
                **data,
                'created_at': now,
                'updated_at': now
            }
            documents.append(document)
            await self._write_file(DOCUMENTS_FILE, documents)
            return document
    
    async def create_documents_batch(self, docs_data: List[dict]) -> List[dict]:
        """批量创建文档"""
        async with self._lock:
            documents = await self._read_file(DOCUMENTS_FILE)
            now = datetime.now()
            new_docs = []
            for data in docs_data:
                document = {
                    'id': generate_id(),
                    'slug': generate_slug(data['title']),
                    **data,
                    'created_at': now,
                    'updated_at': now
                }
                new_docs.append(document)
                documents.append(document)
            await self._write_file(DOCUMENTS_FILE, documents)
            return new_docs
    
    async def update_document(self, document_id: str, data: dict) -> Optional[dict]:
        """更新文档"""
        async with self._lock:
            documents = await self._read_file(DOCUMENTS_FILE)
            for i, doc in enumerate(documents):
                if doc['id'] == document_id:
                    for key, value in data.items():
                        if value is not None:
                            doc[key] = value
                    if 'title' in data and data['title']:
                        doc['slug'] = generate_slug(data['title'])
                    doc['updated_at'] = datetime.now()
                    documents[i] = doc
                    await self._write_file(DOCUMENTS_FILE, documents)
                    return doc
            return None
    
    async def delete_document(self, document_id: str) -> bool:
        """删除文档"""
        async with self._lock:
            documents = await self._read_file(DOCUMENTS_FILE)
            new_documents = [d for d in documents if d['id'] != document_id]
            if len(new_documents) == len(documents):
                return False
            await self._write_file(DOCUMENTS_FILE, new_documents)
            return True


# 全局数据库实例
db = Database()
