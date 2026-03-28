import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown } from 'lucide-react';
import Layout from '@/components/layout/Layout';
import api from '@/lib/api';
import { POPULAR_TICKERS, fmt } from '@/lib/utils';

export default function InsiderPage() {
  const [ticker, setTicker] = useState('AAPL');
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<'all' | 'Purchase' | 'Sale'>('all');

  const load = async (t: string) => {
    setLoading(true);
    try { const res = await api.getInsider(t.toUpperCase()); setData(res?.data || []); }
    catch {} finally { setLoading(false); }
  };

  useEffect(() => { load(ticker); }, []);

  const filtered = filter === 'all' ? data : data.filter(d => d.action === filter);
  const buys = data.filter(d => d.action === 'Purchase').length;
  const sells = data.filter(d => d.action === 'Sale').length;
  const buyRatio = data.length > 0 ? Math.round((buys / data.length) * 100) : 0;

  return (
    <>
      <Head><title>内幕交易监控 — Q-Alpha</title></Head>
      <Layout title="内幕交易监控">
        <div className="p-4 md:p-6 space-y-5 max-w-screen-xl mx-auto">
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-2xl font-display font-bold text-white">
              内幕 <span className="text-q-green">交易监控</span>
            </h1>
            <p className="text-q-muted text-sm mt-1">
              依据 SEC Form 4 文件追踪公司高管、董事及大股东的买卖动向 · 每小时更新
            </p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label: '交易记录总数', value: data.length, color: 'text-q-blue' },
              { label: '买入笔数', value: buys, color: 'text-q-green' },
              { label: '卖出笔数', value: sells, color: 'text-q-red' },
              { label: '买入占比', value: `${buyRatio}%`, color: buyRatio >= 60 ? 'text-q-green' : 'text-q-amber' },
            ].map((s, i) => (
              <div key={i} className="glass-card p-3">
                <div className="text-[10px] text-q-muted mb-1">{s.label}</div>
                <div className={`text-2xl font-display font-bold ${s.color}`}>{s.value}</div>
              </div>
            ))}
          </div>

          <div className="flex flex-wrap gap-3 items-center">
            <div className="flex gap-1.5 flex-wrap">
              {POPULAR_TICKERS.slice(0, 8).map(t => (
                <button key={t} onClick={() => { setTicker(t); load(t); }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all ${ticker === t ? 'bg-q-green/20 text-q-green border border-q-green/30' : 'bg-q-card border border-q-border text-q-muted hover:text-q-text'}`}>
                  {t}
                </button>
              ))}
            </div>
            <div className="flex-1" />
            <div className="flex gap-1">
              {[{ key: 'all', label: '全部' }, { key: 'Purchase', label: '仅买入' }, { key: 'Sale', label: '仅卖出' }].map(f => (
                <button key={f.key} onClick={() => setFilter(f.key as any)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${filter === f.key ? (f.key === 'Purchase' ? 'bg-q-green/20 text-q-green border border-q-green/30' : f.key === 'Sale' ? 'bg-q-red/20 text-q-red border border-q-red/30' : 'bg-q-blue/20 text-q-blue border border-q-blue/30') : 'bg-q-card border border-q-border text-q-muted hover:text-q-text'}`}>
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          <div className="glass-card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-q-border bg-q-surface/60">
                    {['内幕人员', '职务', '股票代码', '交易类型', '股数', '均价', '交易总额', '日期'].map(h => (
                      <th key={h} className="text-left py-3 px-4 text-[10px] font-mono font-semibold text-q-muted uppercase tracking-wider">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {loading ? [...Array(8)].map((_, i) => (
                    <tr key={i} className="border-b border-q-border/20">
                      {[...Array(8)].map((_, j) => (
                        <td key={j} className="py-3 px-4"><div className="h-3 rounded bg-q-border/40 animate-pulse" style={{ width: `${40 + Math.random() * 50}%` }} /></td>
                      ))}
                    </tr>
                  )) : filtered.map((row, i) => (
                    <motion.tr key={i} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.04 }}
                      className="border-b border-q-border/20 hover:bg-q-border/10 transition-colors">
                      <td className="py-3 px-4 font-semibold text-xs text-q-text">{row.insider_name}</td>
                      <td className="py-3 px-4 text-xs text-q-muted">{row.role}</td>
                      <td className="py-3 px-4">
                        <Link href={`/stock/${row.ticker}`}>
                          <span className="font-mono font-bold text-xs text-q-blue hover:underline cursor-pointer">${row.ticker}</span>
                        </Link>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`tag text-[10px] ${row.action === 'Purchase' ? 'tag-buy' : row.action === 'Sale' ? 'tag-sell' : 'tag-hold'}`}>
                          {row.action === 'Purchase' ? '▲ 买入' : row.action === 'Sale' ? '▼ 卖出' : '行权'}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-xs text-q-dim">{row.shares?.toLocaleString()}</td>
                      <td className="py-3 px-4 font-mono text-xs text-q-dim">${fmt(row.price)}</td>
                      <td className="py-3 px-4 font-mono text-xs font-semibold text-q-text">{row.amount}</td>
                      <td className="py-3 px-4 font-mono text-[11px] text-q-muted">{row.date}</td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
}
