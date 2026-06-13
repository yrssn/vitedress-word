# 文档发布系统

基于 Vue + FastAPI + VitePress 的文档发布系统，支持批量编写各种类型的文档（进销存、财务系统、人力资源、客户关系等）。

## 项目结构

```
vitedress-word/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── main.py       # API入口
│   │   ├── auth.py       # JWT认证
│   │   ├── models.py     # 数据模型
│   │   ├── database.py   # 数据库操作
│   │   └── vitepress.py  # VitePress生成 & 构建
│   ├── data/             # JSON数据存储
│   └── requirements.txt
├── frontend/         # Vue 前端管理界面
│   ├── src/
│   │   ├── views/        # 页面组件（含登录页）
│   │   ├── api/          # API调用（含认证）
│   │   └── router/       # 路由配置（含守卫）
│   └── package.json
├── docs/             # VitePress 文档目录
├── docker/           # Docker 辅助配置
│   └── docs/nginx.conf
└── docker-compose.yml
```

## Docker 部署（推荐）

```bash
docker-compose up -d --build
```

| 服务 | 地址 | 说明 |
|------|------|------|
| 管理后台 | http://localhost:9280 | Vue 管理界面 |
| 后端 API | http://localhost:8013/docs | Swagger 文档 |
| 文档站点 | http://localhost:9281 | VitePress 构建产物 |

默认管理员：`admin / admin123`

## 本地开发

### 1. 启动后端

```bash
cd backend
pip install -r requirements.txt
python run.py
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 3. 访问管理界面

打开浏览器访问 http://localhost:3001，使用 `admin / admin123` 登录。

## 功能说明

### 用户认证
- JWT Token 认证
- 登录 / 注册
- 路由守卫，未登录自动跳转
- 首次启动自动创建默认管理员

### 分类管理
- 支持多种文档类型：进销存、财务系统、人力资源、客户关系、其他
- 每个类型下可创建多个分类
- 分类支持图标和描述

### 文档管理
- Markdown编辑器，支持实时预览
- 文档归属于分类
- 支持排序功能
- 批量创建文档

### VitePress 生成 & 发布
- 一键生成VitePress文档结构
- 一键构建并发布为静态站点
- 自动生成导航和侧边栏配置
- 支持本地搜索

## API文档

启动后端后访问 http://localhost:8013/docs 查看Swagger API文档。

## 技术栈

- **前端**: Vue 3 + Element Plus + TailwindCSS + md-editor-v3
- **后端**: Python FastAPI + JWT + bcrypt
- **文档**: VitePress
- **部署**: Docker + Nginx
