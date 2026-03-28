import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { motion } from 'framer-motion';
import { Users, TrendingUp, TrendingDown, Search, Award, BarChart2, DollarSign } from 'lucide-react';
import Layout from '@/components/layout/Layout';
import api from '@/lib/api';
import { partyBg } from '@/lib/utils';

const POLITICIANS = [
  { name: 'Nancy Pelosi', party: 'Democrat', chamber: 'House', state: 'CA', score: 94 },
  { name: 'Tommy Tuberville', party: 'Republican', chamber: 'Senate', state: 'AL', score: 88 },
  { name: 'Marjorie Taylor Greene', party: 'Republican', chamber: 'House', state: 'GA', score: 78 },
  { name: 'J.D. Vance', party: 'Republican', chamber: 'Senate', state: 'OH', score: 85 },
  { name: 'Mark Warner', party: 'Democrat', chamber: 'Senate', state: 'VA', score: 71 },
  { name: 'Dan Goldman', party: 'Democrat', chamber: 'House', state: 'NY', score: 65 },
];

export default function CongressTradingPage() {
  const [trades, setTrades] = useState<any[]>([]);
  const [filter, setFilter] = useState('');
  const [partyFilter, setParty] = useState<'all' | 'Democrat' | 'Republican'>('all');
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<string | null>(null);
  const [detailData, setDetail] = useState<any>(null);

  useEffect(() => {
    api.getCongressTrading().then(r => { setTrades(r?.data || []); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const loadDetail = async (name: string) => {
    setSelected(name);
    const [tradesR, scoreR, networthR] = await Promise.allSettled([
      api.getCongressTrading(name), api.getInsiderScore(name), api.getNetWorth(name),
    ]);
    setDetail({
      trades: tradesR.status === 'fulfilled' ? tradesR.value?.data : [],
      score: scoreR.status === 'fulfilled' ? scoreR.value?.data : null,
      networth: networthR.status === 'fulfilled' ? networthR.value?.data : null,
    });
  };

  const filtered = trades.filter(t => {
    const matchName = !filter || t.politician?.toLowerCase().includes(filter.toLowerCase()) || t.ticker?.includes(filter.toUpperCase());
    const matchParty = partyFilter === 'all' || t.party === partyFilter;
    return matchName && matchParty;
  });

  const chamberLabel = (c: string) => c === 'House' ? '众议院' : '参议院';
  const partyLabel = (p: string) => p.includes('Dem') ? '民主党' : '共和党';

  return (
    <>
      <Head><title>国会股票交易 — Q-Alpha</title></Head>
      <Layout title="国会股票交易">
        <div className="p-4 md:p-6 space-y-5 max-w-screen-2xl mx-auto">

          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-2xl font-display font-bold text-white">
              国会 <span className="text-q-amber">股票交易</span> 披露
            </h1>
            <p className="text-q-muted text-sm mt-1">
              根据《STOCK 法案》，美国国会议员须在 45 天内公开披露股票交易记录 · 每小时更新
            </p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label: '交易记录总数', value: trades.length.toString(), icon: TrendingUp, color: 'text-q-amber' },
              { label: '活跃交易议员', value: POLITICIANS.length.toString(), icon: Users, color: 'text-q-blue' },
              { label: '买入记录', value: trades.filter(t => t.action === 'Purchase').length.toString(), icon: TrendingUp, color: 'text-q-green' },
              { label: '卖出记录', value: trades.filter(t => t.action === 'Sale').length.toString(), icon: TrendingDown, color: 'text-q-red' },
            ].map((s, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }} className="glass-card p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] text-q-muted">{s.label}</span>
                  <s.icon size={13} className={s.color} />
                </div>
                <div className={`text-2xl font-display font-bold ${s.color}`}>{s.value}</div>
              </motion.div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-5">
            {/* 议员侧边栏 */}
            <div className="space-y-2">
              <div className="text-[10px] font-mono text-q-muted uppercase tracking-widest mb-2 px-1">热门追踪议员</div>
              {POLITICIANS.map(p => (
                <div key={p.name} onClick={() => loadDetail(p.name)}
                  className={`glass-card p-3 cursor-pointer transition-all hover:scale-[1.01] ${selected === p.name ? 'glow-blue border-q-blue/40' : ''}`}>
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold ${p.party === 'Democrat' ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'}`}>
                      {p.name.split(' ').map(n => n[0]).slice(0, 2).join('')}
                    </div>
                    <div className="min-w-0">
                      <div className="text-xs font-semibold text-q-text truncate">{p.name}</div>
                      <div className="flex items-center gap-1.5 mt-0.5">
                        <span className={`tag text-[9px] ${partyBg(p.party)}`}>{partyLabel(p.party)}</span>
                        <span className="text-[10px] text-q-muted">{chamberLabel(p.chamber)} · {p.state}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* 主交易表 */}
            <div className="lg:col-span-3 space-y-4">
              <div className="flex items-center gap-3 flex-wrap">
                <div className="flex items-center gap-2 flex-1 min-w-[200px] px-3 py-2 rounded-lg bg-q-card border border-q-border">
                  <Search size={13} className="text-q-muted flex-shrink-0" />
                  <input type="text" value={filter} onChange={e => setFilter(e.target.value)}
                    placeholder="按议员姓名或股票代码筛选…"
                    className="bg-transparent text-xs text-q-text placeholder:text-q-muted/50 outline-none flex-1 font-mono" />
                </div>
                <div className="flex gap-1">
                  {[{ id: 'all', label: '全部' }, { id: 'Democrat', label: '民主党' }, { id: 'Republican', label: '共和党' }].map(p => (
                    <button key={p.id} onClick={() => setParty(p.id as any)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${partyFilter === p.id
                        ? p.id === 'all' ? 'bg-q-blue/20 text-q-blue border border-q-blue/30' : p.id === 'Democrat' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' : 'bg-red-500/20 text-red-400 border border-red-500/30'
                        : 'text-q-muted bg-q-card border border-q-border hover:border-q-border/80'}`}>
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="glass-card overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-q-border bg-q-surface/60">
                        {['议员', '党派', '股票代码', '交易类型', '交易金额', '披露日期'].map(h => (
                          <th key={h} className="text-left py-3 px-4 text-[10px] font-mono font-semibold text-q-muted uppercase tracking-wider">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {loading ? [...Array(8)].map((_, i) => (
                        <tr key={i} className="border-b border-q-border/20">
                          {[...Array(6)].map((_, j) => <td key={j} className="py-3 px-4"><div className="h-3 rounded bg-q-border/40 animate-pulse" /></td>)}
                        </tr>
                      )) : filtered.map((trade, i) => (
                        <motion.tr key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.03 }}
                          className="border-b border-q-border/20 hover:bg-q-border/10 transition-colors">
                          <td className="py-3 px-4">
                            <button onClick={() => loadDetail(trade.politician)} className="font-medium text-xs text-q-text hover:text-q-blue transition-colors text-left">{trade.politician}</button>
                          </td>
                          <td className="py-3 px-4">
                            <span className={`tag text-[9px] ${partyBg(trade.party)}`}>{partyLabel(trade.party)}</span>
                          </td>
                          <td className="py-3 px-4"><span className="font-mono font-bold text-xs text-q-blue">${trade.ticker}</span></td>
                          <td className="py-3 px-4">
                            <span className={`tag text-[10px] ${trade.action === 'Purchase' ? 'tag-buy' : 'tag-sell'}`}>
                              {trade.action === 'Purchase' ? '▲ 买入' : '▼ 卖出'}
                            </span>
                          </td>
                          <td className="py-3 px-4 font-mono text-xs text-q-dim">{trade.amount}</td>
                          <td className="py-3 px-4 font-mono text-[11px] text-q-muted">{trade.date}</td>
                        </motion.tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* 议员详情面板 */}
              {selected && detailData && (
                <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-4 glow-blue">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-display font-semibold text-q-text">{selected} — 详细数据</h3>
                    <button onClick={() => setSelected(null)} className="text-q-muted hover:text-q-text text-xs">✕ 关闭</button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {detailData.score && (
                      <div className="bg-q-surface rounded-xl p-4 border border-q-border">
                        <div className="text-[10px] text-q-muted uppercase tracking-widest mb-2">DC 内幕评分</div>
                        <div className="text-4xl font-display font-black text-q-blue">{detailData.score.dc_insider_score}</div>
                        <div className="text-xs text-q-muted mt-1">全国第 #{detailData.score.rank} / 535</div>
                        <div className="mt-2">
                          <div className="text-[10px] text-q-muted">跑赢大盘</div>
                          <div className="text-sm font-mono font-semibold text-q-green">+{detailData.score.alpha}% vs 标普500</div>
                        </div>
                      </div>
                    )}
                    {detailData.networth && (
                      <div className="bg-q-surface rounded-xl p-4 border border-q-border">
                        <div className="text-[10px] text-q-muted uppercase tracking-widest mb-2">估算净资产</div>
                        <div className="text-2xl font-display font-bold text-q-text">${(detailData.networth.estimated_net_worth / 1e6).toFixed(1)}M</div>
                        <div className="mt-2 space-y-1">
                          <div className="flex justify-between text-xs"><span className="text-q-muted">股票持仓</span><span className="font-mono">${(detailData.networth.stock_holdings / 1e6).toFixed(1)}M</span></div>
                          <div className="flex justify-between text-xs"><span className="text-q-muted">房地产</span><span className="font-mono">${(detailData.networth.real_estate / 1e6).toFixed(1)}M</span></div>
                        </div>
                      </div>
                    )}
                    <div className="bg-q-surface rounded-xl p-4 border border-q-border">
                      <div className="text-[10px] text-q-muted uppercase tracking-widest mb-2">近期交易</div>
                      <div className="text-4xl font-display font-bold text-q-amber">{detailData.trades?.length || 0}</div>
                      <div className="text-xs text-q-muted mt-1">本期披露笔数</div>
                      {detailData.score && (
                        <div className="mt-2">
                          <div className="text-[10px] text-q-muted">交易胜率</div>
                          <div className="text-sm font-mono font-semibold text-q-green">{detailData.score.trading_performance || 'N/A'}</div>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
}
