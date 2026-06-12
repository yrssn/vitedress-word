# 文档发布系统

基于 Vue + FastAPI + VitePress 的文档发布系统，支持批量编写各种类型的文档（进销存、财务系统、人力资源、客户关系等）。

## 项目结构

```
vitepress-system/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── main.py       # API入口
│   │   ├── models.py     # 数据模型
│   │   ├── database.py   # 数据库操作
│   │   └── vitepress.py  # VitePress生成
│   ├── data/             # JSON数据存储
│   └── requirements.txt
├── frontend/         # Vue 前端管理界面
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── api/          # API调用
│   │   └── router/       # 路由配置
│   └── package.json
└── docs/             # VitePress 文档目录
    ├── .vitepress/
    │   └── config.mts
    └── index.md
```

## 快速开始

### 1. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 3. 访问管理界面

打开浏览器访问 http://localhost:3000

### 4. 预览VitePress文档

在管理界面生成文档后：

```bash
cd docs
npm install
npm run dev
```

## 功能说明

### 分类管理
- 支持多种文档类型：进销存、财务系统、人力资源、客户关系、其他
- 每个类型下可创建多个分类
- 分类支持图标和描述

### 文档管理
- Markdown编辑器，支持实时预览
- 文档归属于分类
- 支持排序功能
- 批量创建文档

### VitePress生成
- 一键生成VitePress文档结构
- 自动生成导航和侧边栏配置
- 支持本地搜索

## API文档

启动后端后访问 http://localhost:8000/docs 查看Swagger API文档。

## 技术栈

- **前端**: Vue 3 + Element Plus + TailwindCSS + md-editor-v3
- **后端**: Python FastAPI
- **文档**: VitePress
