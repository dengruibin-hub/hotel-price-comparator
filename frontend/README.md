# 前端

这是酒店价格比价器的 Next.js 前端 MVP。

## 运行

```bash
cd frontend
npm install
npm run dev
```

然后打开 `http://localhost:3000`。

前端会把 `/api/compare` 请求代理到本地 FastAPI：`http://127.0.0.1:8000`。

因此需要同时运行后端：

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
