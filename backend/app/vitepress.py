import os
import json
import shutil
import aiofiles
from typing import List, Dict
from .database import db

# 优先使用环境变量 DOCS_DIR（容器里设为 /app/docs，vitepress 也装在这里）；
# 本地开发回退到相对仓库的 docs 目录。
DOCS_DIR = os.environ.get("DOCS_DIR") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docs"
)
# 上传图片的源目录（后端运行时通过 /uploads 静态挂载），与 main.py 的 UPLOAD_DIR 一致
UPLOAD_DIR = os.environ.get("UPLOAD_DIR") or os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "uploads"
)


def sync_uploads_to_public():
    """把上传的图片同步到 docs/public/uploads，
    使得 vitepress build 后静态站点也能通过 /uploads/xxx 访问到图片。"""
    if not os.path.isdir(UPLOAD_DIR):
        return
    public_uploads = os.path.join(DOCS_DIR, "public", "uploads")
    os.makedirs(public_uploads, exist_ok=True)
    for name in os.listdir(UPLOAD_DIR):
        src = os.path.join(UPLOAD_DIR, name)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(public_uploads, name))


async def generate_vitepress_files():
    """生成VitePress文档文件"""
    # 确保docs目录存在
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(os.path.join(DOCS_DIR, ".vitepress"), exist_ok=True)

    # 同步上传图片到 public 目录，保证构建产物包含图片
    sync_uploads_to_public()
    
    # 获取动态文档类型
    doc_types_list = await db.get_doc_types()
    categories = await db.get_categories()
    documents = await db.get_documents()
    
    # 按分类组织文档
    docs_by_category: Dict[str, List[dict]] = {}
    for doc in documents:
        cat_id = doc.get('category_id')
        if cat_id not in docs_by_category:
            docs_by_category[cat_id] = []
        docs_by_category[cat_id].append(doc)
    
    # 生成侧边栏配置
    sidebar = {}
    nav = []
    
    # 按文档类型ID分组分类
    cats_by_type: Dict[str, List[dict]] = {}
    for cat in categories:
        type_id = cat.get('doc_type_id', '')
        if type_id not in cats_by_type:
            cats_by_type[type_id] = []
        cats_by_type[type_id].append(cat)
    
    # 创建文档类型ID到信息的映射
    doc_type_map = {dt['id']: dt for dt in doc_types_list}
    
    for doc_type in doc_types_list:
        type_id = doc_type['id']
        type_value = doc_type.get('value', type_id)
        type_label = doc_type.get('name', type_value)
        type_path = f"/{type_value}/"
        cats = cats_by_type.get(type_id, [])
        
        # 创建文档类型目录
        type_dir = os.path.join(DOCS_DIR, type_value)
        os.makedirs(type_dir, exist_ok=True)
        
        # 生成该类型的index.md
        index_content = f"# {type_label}\n\n"
        for cat in cats:
            index_content += f"## {cat['name']}\n\n"
            if cat.get('description'):
                index_content += f"{cat['description']}\n\n"
            
            cat_docs = docs_by_category.get(cat['id'], [])
            for doc in sorted(cat_docs, key=lambda x: x.get('order', 0)):
                index_content += f"- [{doc['title']}](./{cat['id']}/{doc['slug']}.md)\n"
            index_content += "\n"
        
        async with aiofiles.open(os.path.join(type_dir, "index.md"), 'w', encoding='utf-8') as f:
            await f.write(index_content)
        
        # 侧边栏项
        sidebar_items = []
        
        for cat in cats:
            cat_dir = os.path.join(type_dir, cat['id'])
            os.makedirs(cat_dir, exist_ok=True)
            
            cat_docs = docs_by_category.get(cat['id'], [])
            doc_items = []
            
            for doc in sorted(cat_docs, key=lambda x: x.get('order', 0)):
                # 生成文档文件
                doc_path = os.path.join(cat_dir, f"{doc['slug']}.md")
                async with aiofiles.open(doc_path, 'w', encoding='utf-8') as f:
                    await f.write(doc['content'])
                
                doc_items.append({
                    'text': doc['title'],
                    'link': f"{type_path}{cat['id']}/{doc['slug']}"
                })
            
            if doc_items:
                sidebar_items.append({
                    'text': cat['name'],
                    'collapsed': False,
                    'items': doc_items
                })
        
        if sidebar_items:
            sidebar[type_path] = sidebar_items
            nav.append({
                'text': type_label,
                'link': type_path
            })
    
    # 生成VitePress配置
    config = {
        'title': '文档中心',
        'description': '企业文档管理系统',
        # 上传的图片以 /uploads/ 绝对路径引用，由后端运行时提供。
        # 构建时禁止把绝对路径资源当作模块解析，否则 Rollup 会报错。
        'vue': {
            'template': {
                'transformAssetUrls': {
                    'includeAbsolute': False
                }
            }
        },
        'themeConfig': {
            'nav': nav if nav else [{'text': '首页', 'link': '/'}],
            'sidebar': sidebar,
            'socialLinks': [],
            'search': {
                'provider': 'local'
            }
        }
    }
    
    config_content = f"""import {{ defineConfig }} from 'vitepress'

export default defineConfig({json.dumps(config, ensure_ascii=False, indent=2)})
"""
    
    async with aiofiles.open(os.path.join(DOCS_DIR, ".vitepress", "config.mts"), 'w', encoding='utf-8') as f:
        await f.write(config_content)
    
    # 生成首页（动态生成features）
    first_type_link = f"/{doc_types_list[0]['value']}/" if doc_types_list else "/"
    
    features_yaml = ""
    for dt in doc_types_list:
        features_yaml += f"""  - title: {dt['name']}
    details: {dt.get('description') or dt['name'] + '相关文档'}
    link: /{dt['value']}/
"""
    
    index_content = f"""---
layout: home
hero:
  name: "文档中心"
  text: "企业文档管理系统"
  tagline: 统一管理各类业务文档
  actions:
    - theme: brand
      text: 开始阅读
      link: {first_type_link}
features:
{features_yaml}---
"""
    
    async with aiofiles.open(os.path.join(DOCS_DIR, "index.md"), 'w', encoding='utf-8') as f:
        await f.write(index_content)
    
    return {
        'docs_dir': DOCS_DIR,
        'doc_types_count': len(doc_types_list),
        'categories_count': len(categories),
        'documents_count': len(documents)
    }
