import React, { useState } from 'react';
import Head from 'next/head';
import { motion } from 'framer-motion';
import { Search, Users, TrendingUp, DollarSign, Award, Globe } from 'lucide-react';
import Layout from '@/components/layout/Layout';
import api from '@/lib/api';
import { partyBg, partyLabel, chamberLabel } from '@/lib/utils';

export default function PoliticiansPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selected, setSel] = useState<any>(null);
  const [detail, setDetail] = useState<any>(null);

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try { const res = await api.searchPolitician(query); setResults(res?.data || []); }
    catch {} finally { setLoading(false); }
  };

  const loadDetail = async (p: any) => {
    setSel(p);
    const [score, networth, trades, fund] = await Promise.allSettled([
      api.getInsiderScore(p.name), api.getNetWorth(p.name),
      api.getCongressTrading(p.name), api.getFundraising(p.name),
    ]);
    setDetail({
      score:   score.status === 'fulfilled' ? score.value?.data : null,
      networth: networth.status === 'fulfilled' ? networth.value?.data : null,
      trades:  trades.status === 'fulfilled' ? trades.value?.data : [],
      fund:    fund.status === 'fulfilled' ? fund.value?.data : null,
    });
  };

  const DEFAULT_POLI = [
    { name: 'Nancy Pelosi',           party: 'Democrat',   chamber: 'House',  state: 'CA', score: 94 },
    { name: 'Tommy Tuberville',       party: 'Republican', chamber: 'Senate', state: 'AL', score: 88 },
    { name: 'J.D. Vance',             party: 'Republican', chamber: 'Senate', state: 'OH', score: 85 },
    { name: 'Marjorie Taylor Greene', party: 'Republican', chamber: 'House',  state: 'GA', score: 78 },
    { name: 'Mark Warner',            party: 'Democrat',   chamber: 'Senate', state: 'VA', score: 71 },
    { name: 'Dan Goldman',            party: 'Democrat',   chamber: 'House',  state: 'NY', score: 65 },
    { name: 'Ro Khanna',              party: 'Democrat',   chamber: 'House',  state: 'CA', score: 72 },
    { name: 'Michael McCaul',         party: 'Republican', chamber: 'House',  state: 'TX', score: 80 },
  ];

  const displayList = results.length > 0 ? results : DEFAULT_POLI;

  return (
    <>
      <Head><title>政治人物查询 — Q-Alpha</title></Head>
      <Layout title="政治人物查询">
        <div className="p-4 md:p-6 space-y-5 max-w-screen-xl mx-auto">
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-2xl font-display font-bold text-white">
              政治人物 <span className="text-q-amber">情报中心</span>
            </h1>
            <p className="text-q-muted text-sm mt-1">查询美国国会议员的交易记录、净资产、DC 内幕评分及竞选筹款数据</p>
          </motion.div>

          <div className="flex gap-3 max-w-xl">
            <div className="flex items-center gap-2 flex-1 px-4 py-3 rounded-xl bg-q-card border border-q-border focus-within:border-q-blue/60 transition-all">
              <Search size={15} className="text-q-muted" />
              <input type="text" value={query} onChange={e => setQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && search()}
                placeholder="搜索议员姓名，例如：Pelosi、Vance..."
                className="flex-1 bg-transparent text-sm text-q-text placeholder:text-q-muted/50 outline-none" />
            </div>
            <button onClick={search} className="btn-primary px-6 text-sm">搜索</button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {displayList.map((p, i) => {
              const dem = p.party === 'Democrat';
              return (
                <motion.div key={p.name} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}>
                  <div onClick={() => loadDetail(p)}
                    className={`glass-card p-4 cursor-pointer transition-all hover:scale-[1.01] ${selected?.name === p.name ? 'glow-blue border-q-blue/40' : ''}`}>
                    <div className="flex items-center gap-3 mb-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${dem ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'}`}>
                        {p.name.split(' ').map((n: string) => n[0]).slice(0, 2).join('')}
                      </div>
                      <div className="min-w-0">
                        <div className="font-semibold text-xs text-q-text truncate">{p.name}</div>
                        <div className="text-[10px] text-q-muted">{chamberLabel(p.chamber)} · {p.state}</div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className={`tag text-[9px] ${partyBg(p.party)}`}>{partyLabel(p.party).slice(0, 3)}</span>
                      {p.score && (
                        <div className="flex items-center gap-1">
                          <Award size={10} className="text-q-blue" />
                          <span className="font-mono text-xs font-bold text-q-blue">{p.score}</span>
                          <span className="text-[9px] text-q-muted">内幕分</span>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {selected && detail && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5 glow-blue">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center text-base font-bold ${selected.party === 'Democrat' ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'}`}>
                    {selected.name.split(' ').map((n: string) => n[0]).slice(0, 2).join('')}
                  </div>
                  <div>
                    <h2 className="font-display font-bold text-lg text-q-text">{selected.name}</h2>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className={`tag text-[10px] ${partyBg(selected.party)}`}>{partyLabel(selected.party)}</span>
                      <span className="text-xs text-q-muted">{chamberLabel(selected.chamber)} · {selected.state}</span>
                    </div>
                  </div>
                </div>
                <button onClick={() => setSel(null)} className="text-q-muted hover:text-q-text text-xs">✕ 关闭</button>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-5">
                {[
                  { label: 'DC 内幕评分', value: detail.score?.dc_insider_score || '—', icon: Award, color: 'text-q-blue', sub: `535位中第#${detail.score?.rank || '?'}名` },
                  { label: '估算净资产', value: detail.networth ? `$${(detail.networth.estimated_net_worth / 1e6).toFixed(1)}M` : '—', icon: DollarSign, color: 'text-q-green', sub: '股票+房产' },
                  { label: '超额收益率', value: detail.score?.alpha ? `+${detail.score.alpha}%` : '—', icon: TrendingUp, color: 'text-q-amber', sub: '相对标普500' },
                  { label: '筹款总额', value: detail.fund?.total_raised || '—', icon: Users, color: 'text-q-purple', sub: '竞选筹款' },
                ].map((stat, i) => (
                  <div key={i} className="bg-q-surface rounded-xl p-3 border border-q-border">
                    <div className="flex items-center gap-1.5 mb-1">
                      <stat.icon size={12} className={stat.color} />
                      <span className="text-[10px] text-q-muted uppercase tracking-wide">{stat.label}</span>
                    </div>
                    <div className={`text-2xl font-display font-bold ${stat.color}`}>{stat.value}</div>
                    <div className="text-[10px] text-q-muted mt-0.5">{stat.sub}</div>
                  </div>
                ))}
              </div>

              {detail.trades?.length > 0 && (
                <div>
                  <div className="text-[10px] font-mono text-q-muted uppercase tracking-widest mb-3">近期股票交易</div>
                  <div className="space-y-2">
                    {detail.trades.slice(0, 5).map((trade: any, i: number) => (
                      <div key={i} className="flex items-center gap-3 p-2.5 rounded-lg bg-q-surface border border-q-border/40">
                        <span className={`tag text-[10px] ${trade.action === 'Purchase' ? 'tag-buy' : 'tag-sell'}`}>
                          {trade.action === 'Purchase' ? '买入' : '卖出'}
                        </span>
                        <span className="font-mono font-bold text-xs text-q-blue">${trade.ticker}</span>
                        <span className="text-xs text-q-muted flex-1">{trade.amount}</span>
                        <span className="font-mono text-[11px] text-q-muted">{trade.date}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </div>
      </Layout>
    </>
  );
}
