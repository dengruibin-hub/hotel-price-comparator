# 酒店价格比价器

比较同一家酒店在 **去哪儿、智行、高德** 的价格。

> 当前版本是 MVP：三家平台先使用模拟数据，重点把“统一查询条件 → 标准化价格 → 最低价比较”的流程跑通。真实平台数据接入将在后续通过官方或授权接口完成。

## 当前功能

- FastAPI 后端
- `/health` 健康检查
- `/api/compare` 酒店价格比价接口
- 三个平台 Provider 接口骨架
- 统一价格数据结构
- 最低价、最高价、节省金额计算
- 基础自动化测试

## 项目结构

```text
hotel-price-comparator/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── models/
│   │   └── schemas.py
│   ├── providers/
│   │   ├── base.py
│   │   ├── qunar/provider.py
│   │   ├── zhixing/provider.py
│   │   └── amap/provider.py
│   └── services/
│       └── comparator.py
└── tests/
    └── test_comparator.py
```

## 本地运行

```bash
cd backend
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn main:app --reload
```

打开：`http://127.0.0.1:8000/docs`

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

返回结果会包含三家平台的模拟价格，以及最低价平台。

## 测试

```bash
cd backend
pytest ../tests -q
```

## 后续路线

1. 完成前端搜索页面和比价卡片
2. 增加酒店标准化与跨平台酒店匹配
3. 增加 PostgreSQL 数据库
4. 增加价格历史记录和价格监控
5. 根据平台官方/授权接口接入真实价格
6. 增加 GitHub Actions 定时任务
