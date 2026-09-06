'use client';

import { useState } from 'react';

const platformNames = { qunar: '去哪儿', zhixing: '智行', amap: '高德' };

export default function Home() {
  const [form, setForm] = useState({
    hotel_name: '上海外滩某酒店',
    check_in: '2026-10-10',
    check_out: '2026-10-12',
    guests: 2,
    rooms: 1,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  function update(key, value) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function compare() {
    setLoading(true);
    setError('');
    try {
      const response = await fetch('/api/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, guests: Number(form.guests), rooms: Number(form.rooms) }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || '比价失败');
      setResult(data);
    } catch (err) {
      setError(err.message || '无法连接后端，请确认 FastAPI 正在运行。');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <section className="hero">
        <div className="eyebrow">HOTEL PRICE COMPARATOR · MVP</div>
        <h1>同一家酒店，<span>哪里更便宜？</span></h1>
        <p>一次查询，对比去哪儿、智行、高德的房价。</p>
      </section>

      <section className="search-card">
        <label className="full">酒店名称<input value={form.hotel_name} onChange={(e) => update('hotel_name', e.target.value)} placeholder="输入酒店名称" /></label>
        <label>入住日期<input type="date" value={form.check_in} onChange={(e) => update('check_in', e.target.value)} /></label>
        <label>退房日期<input type="date" value={form.check_out} onChange={(e) => update('check_out', e.target.value)} /></label>
        <label>入住人数<input type="number" min="1" value={form.guests} onChange={(e) => update('guests', e.target.value)} /></label>
        <label>房间数<input type="number" min="1" value={form.rooms} onChange={(e) => update('rooms', e.target.value)} /></label>
        <button onClick={compare} disabled={loading}>{loading ? '正在比价…' : '开始比价'}</button>
      </section>

      {error && <div className="error">{error}</div>}

      {result && (
        <section className="results">
          <div className="summary">
            <div><small>比价结果</small><h2>{result.hotel_name}</h2><p>{result.check_in} → {result.check_out} · {result.guests} 人 · {result.rooms} 间</p></div>
            <div className="saving"><small>最高可省</small><strong>¥{result.savings}</strong></div>
          </div>
          <div className="cards">
            {result.prices.map((item) => {
              const lowest = item.price === result.lowest_price;
              return (
                <article className={`price-card ${lowest ? 'lowest' : ''}`} key={item.source}>
                  {lowest && <div className="badge">最低价</div>}
                  <div className="platform">{platformNames[item.source] || item.source}</div>
                  <h3>{item.room_name}</h3>
                  <div className="price">¥{item.price}<small>/间</small></div>
                  <div className="features"><span>{item.breakfast ? '✓ 含早餐' : '× 不含早餐'}</span><span>{item.cancelable ? '✓ 免费取消' : '× 不可取消'}</span></div>
                </article>
              );
            })}
          </div>
          <div className="note">当前为 MVP 模拟价格。后续将接入官方或授权数据源，并增加酒店跨平台匹配。</div>
        </section>
      )}
    </main>
  );
}
