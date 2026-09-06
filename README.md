# Hotel Price Comparator

比较同一家酒店在去哪儿、智行、高德的价格，并记录历史价格、趋势和目标价提醒。

## 当前能力

- 三平台标准化酒店候选匹配
- 统一价格结构与最低价比较
- PostgreSQL 酒店、平台映射和价格快照
- 历史价格趋势 API
- 目标价降价提醒 API
- GitHub Actions 自动检查骨架
- Docker Compose 一键启动 PostgreSQL、FastAPI 和 Next.js
- GitHub Actions CI：后端 pytest + 前端 production build

## 本地启动

### Docker

```bash
cp .env.example .env
docker compose up --build
```

- 前端：http://localhost:3000
- 后端：http://localhost:8000/health
- PostgreSQL：localhost:5432

PostgreSQL 官方镜像会在首次初始化空数据目录时执行 `/docker-entrypoint-initdb.d` 下的 SQL 文件，因此本项目把 schema 和 migration 挂载到初始化目录。生产环境不要使用默认密码。

### 手动启动

后端：

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

前端：

```bash
cd frontend
npm install
npm run dev
```

## CI

每次 push 到 `main` 或提交 Pull Request 时，GitHub Actions 会运行：

- Python 3.12 + pytest
- Node 20 + `npm ci` + `npm run build`

## 数据接入原则

目前平台价格仍是 MVP 模拟数据。真实去哪儿、智行、高德数据应优先通过官方或获得授权的接口接入，不绕过验证码、登录限制或反爬风控。

## 下一步

1. 修正并验证生产数据库 migration 顺序
2. 接入真实授权数据源
3. 增加通知渠道（邮件/企业微信等）
4. 完善酒店跨平台匹配与人工确认
5. 增加生产部署与监控
