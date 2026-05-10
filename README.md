# SeeAI 积分榜单系统

基于 Vue + ElementUI + FastAPI + Docker 的积分榜单展示系统。

## 技术栈

- **前端**: Vue 3 + ElementPlus + Vite + Nginx
- **后端**: FastAPI + Uvicorn + httpx
- **部署**: Docker + Docker Compose
- **数据源**: 飞书开放平台 API

## 项目结构

```
SeeAI/
├── frontend/          # Vue 前端项目
│   ├── src/          # 源代码
│   ├── nginx.conf    # Nginx 配置
│   └── Dockerfile    # 前端镜像构建
├── backend/           # FastAPI 后端项目
│   ├── app/          # 应用代码
│   └── Dockerfile    # 后端镜像构建
├── docker-compose.yml
└── .env.example      # 环境变量示例
```

## 快速开始

### 1. 配置环境变量

复制 `.env.example` 为 `.env` 并填入飞书应用的凭证：

```bash
cp .env.example .env
```

### 2. 启动服务（Docker）

```bash
docker-compose up --build
```

访问 `http://localhost` 查看前端页面。

### 3. 本地开发

**后端：**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**前端：**
```bash
cd frontend
npm install
npm run dev
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `GET /api/health` | 健康检查 | 返回 `{"status": "ok"}` |
| `GET /api/leaderboard` | 获取积分榜单 | 返回积分数据列表 |

## 飞书 API 配置

1. 登录 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 `App ID` 和 `App Secret`
4. 配置应用权限（根据实际数据源配置）
5. 将凭证填入 `.env` 文件
