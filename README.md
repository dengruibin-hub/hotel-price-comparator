# 酒店价格比价器

比较同一家酒店在 **去哪儿、智行、高德** 的价格。

> 当前版本是 MVP：三家平台先使用模拟数据，重点把“统一查询条件 → 酒店标准化/匹配 → 标准化价格 → 最低价比较”的流程跑通。真实平台数据接入将在后续通过官方或授权接口完成。

## 当前功能

- FastAPI 后端
- `/health` 健康检查
- `/api/compare` 酒店价格比价接口
- 去哪儿、智行、高德 Provider 接口骨架
- 统一价格数据结构
- 最低价、最高价、节省金额计算
- Next.js 前端搜索页面
- 三家平台价格卡片与最低价高亮
- 酒店名称、地址、电话、经纬度标准化
- 跨平台酒店匹配评分 `match_score`
- PostgreSQL 数据库 Schema
- 基础自动化测试

## 第三阶段：酒店标准化与跨平台匹配

比价之前必须先确认三家平台展示的是同一家物理酒店。项目现在引入 canonical hotel（标准酒店）和 `HotelCandidate`（平台候选酒店）两个概念。

匹配 MVP 会综合以下信号：

1. 酒店名称相似度
2. 地址相似度
3. 经纬度距离
4. 电话号码是否一致

最终输出 `matched` 和 `match_score`。因此不会因为“酒店名称刚好相同”就直接判定为同一家。

## 数据库设计

`database/schema.sql` 使用 PostgreSQL 定义三张核心表：

- `hotels`：标准酒店信息
- `hotel_sources`：标准酒店与去哪儿/智行/高德酒店 ID 的映射，并保存 `match_score`
- `price_snapshots`：每次价格查询的历史快照，包括房型、房价、税费、服务费、最终价格、早餐、取消政策和查询时间

数据库 Schema 已先落地，当前 MVP 不要求本地必须安装 PostgreSQL。

## 项目结构

```text
hotel-price-comparator/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── models/
│   │   ├── hotel.py
│   │   └── schemas.py
│   ├── providers/
│   └── services/
│       ├── comparator.py
│       ├── normalizer.py
│       └── hotel_matcher.py
├── database/
│   └── schema.sql
├── frontend/
│   ├── app/
│   │   ├── page.js
│   │   ├── layout.js
│   │   └── globals.css
│   ├── next.config.mjs
│   ├── package.json
│   └── README.md
└── tests/
    ├── test_comparator.py
    └── test_hotel_matcher.py
```

## 本地运行

### 1. 启动后端

```bash
cd backend
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\\Scripts\\Activate.ps1

pip install -r requirements.txt
uvicorn main:app --reload
```

后端文档：`http://127.0.0.1:8000/docs`

### 2. 启动前端

新开一个终端：

```bash
cd frontend
npm install
npm run dev
```

然后打开：`http://localhost:3000`

前端会将 `/api/compare` 代理到本地 FastAPI。

## API 示例

### POST `/api/compare`

```json
{
  "hotel_name": "上海外滩某酒店",
  "check_in": "2026-10-10",
  "check_out": "2026-10-12",
  "guests": 2,
  "rooms": 1
}
```

## 测试

```bash
cd backend
pytest ../tests -q
```

## 开发路线

- [x] 后端比价 MVP
- [x] 前端搜索与价格展示
- [x] 酒店标准化与跨平台酒店匹配 MVP
- [x] PostgreSQL 数据库 Schema
- [ ] 将酒店匹配接入实际搜索流程
- [ ] 价格历史记录和价格监控
- [ ] 根据平台官方/授权接口接入真实价格
- [ ] GitHub Actions 定时任务
