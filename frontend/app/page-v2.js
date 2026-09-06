'use client';

import { useState } from 'react';

const platformNames = { qunar: '去哪儿', zhixing: '智行', amap: '高德' };

export default function PriceDashboard() {
  const [form, setForm] = useState({ hotel_name: '上海外滩某酒店', check_in: '2026-10-10', check_out: '2026-10-12', guests: 2, rooms: 1 });
  const [result, setResult] = useState(null);
  const [trend, setTrend] = useState(null);
  const [targetPrice, setTargetPrice] = useState('550');
  const [alertCreated, setAlertCreated] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  function update(key, value) { setForm((current) => ({ ...current, [key]: value })); }

  async function compare() {
    setLoading(true); setError(''); setAlertCreated(false);
    try {
      const response = await fetch('/api/compare', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...form, guests: Number(form.guests), rooms: Number(form.rooms) }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || '比价失败');
      setResult(data); setTrend(null);
      if (data.hotel_db_id) {
        const params = new URLSearchParams({ hotel_id: data.hotel_db_id, check_in: data.check_in, check_out: data.check_out, guests: data.guests, rooms: data.rooms, days: 30 });
        const trendResponse = await fetch(`/api/price-trend?${params}`);
        if (trendResponse.ok) setTrend(await trendResponse.json());
      }
    } catch (err) { setError(err.message || '无法连接后端，请确认 FastAPI 正在运行。'); }
    finally { setLoading(false); }
  }

  async function createAlert() {
    if (!result?.hotel_db_id) return;
    setError('');
    try {
      const response = await fetch('/api/price-alerts', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ hotel_id: result.hotel_db_id, check_in: result.check_in, check_out: result.check_out, guests: result.guests, rooms: result.rooms, target_price: Number(targetPrice), currency: 'CNY' }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || '提醒创建失败');
      setAlertCreated(true);
    } catch (err) { setError(err.message || '提醒创建失败'); }
  }

  return (
    <main className="page">
      <section className="hero"><div className="eyebrow">HOTEL PRICE COMPARATOR · MVP</div><h1>同一家酒店，<span>哪里更便宜？</span></h1><p>一次查询，对比去哪儿、智行、高德的房价。</p></section>
      <section className="search-card">
        <label className="full">酒店名称<input value={form.hotel_name} onChange={(e) => update('hotel_name', e.target.value)} placeholder="输入酒店名称" /></label>
        <label>入住日期<input type="date" value={form.check_in} onChange={(e) => update('check_in', e.target.value)} /></label>
        <label>退房日期<input type="date" value={form.check_out} onChange={(e) => update('check_out', e.target.value)} /></label>
        <label>入住人数<input type="number" min="1" value={form.guests} onChange={(e) => update('guests', e.target.value)} /></label>
        <label>房间数<input type="number" min="1" value={form.rooms} onChange={(e) => update('rooms', e.target.value)} /></label>
        <button onClick={compare} disabled={loading}>{loading ? '正在比价…' : '开始比价'}</button>
      </section>
      {error && <div className="error">{error}</div>}
      {result && <section className="results">
        <div className="summary"><div><small>比价结果</small><h2>{result.hotel_name}</h2><p>{result.check_in} → {result.check_out} · {result.guests} 人 · {result.rooms} 间</p></div><div className="saving"><small>最高可省</small><strong>¥{result.savings}</strong></div></div>
        <div className="match-info">跨平台匹配度 <strong>{Math.round(result.match_score * 100)}%</strong> · 已匹配：{result.matched_sources.map((source) => platformNames[source] || source).join('、')}</div>
        <div className="cards">{result.prices.map((item) => { const lowest = item.price === result.lowest_price; return <article className={`price-card ${lowest ? 'lowest' : ''}`} key={item.source}>{lowest && <div className="badge">最低价</div>}<div className="platform">{platformNames[item.source] || item.source}</div><h3>{item.room_name}</h3><div className="price">¥{item.price}<small>/间</small></div><div className="features"><span>{item.breakfast ? '✓ 含早餐' : '× 不含早餐'}</span><span>{item.cancelable ? '✓ 免费取消' : '× 不可取消'}</span></div></article>; })}</div>
        <div className="insights-grid">
          <section className="panel"><div className="panel-head"><div><small>PRICE HISTORY</small><h3>历史价格趋势</h3></div><span className="pill">近 30 天</span></div>{trend?.points?.length ? <div className="trend-list">{trend.points.map((point, index) => <div className="trend-row" key={`${point.checked_at}-${index}`}><span>{new Date(point.checked_at).toLocaleDateString()}</span><b>¥{point.lowest ?? '—'}</b><span>{point.qunar != null ? `去哪儿 ¥${point.qunar}` : ''}</span><span>{point.zhixing != null ? `智行 ¥${point.zhixing}` : ''}</span><span>{point.amap != null ? `高德 ¥${point.amap}` : ''}</span></div>)}</div> : <div className="empty-trend">配置 DATABASE_URL 后，每次比价会自动保存快照并显示历史趋势。</div>}</section>
          <section className="panel alert-panel"><div><small>PRICE ALERT</small><h3>降价提醒</h3><p>当最终价格低于你的目标价时，记录触发时间。</p></div><div className="alert-form"><label>目标价格<input type="number" min="0" value={targetPrice} onChange={(e) => setTargetPrice(e.target.value)} /></label><button onClick={createAlert} disabled={!result?.hotel_db_id}>设置提醒</button></div>{!result?.hotel_db_id && <div className="alert-hint">需要启用 PostgreSQL 后才能建立持久化提醒。</div>}{alertCreated && <div className="success">✓ 降价提醒已创建</div>}</section>
        </div>
        <div className="note">当前为 MVP 模拟价格。真实平台数据将在后续通过官方或授权接口接入。</div>
      </section>}
    </main>
  );
}
