import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Users, BarChart2, Zap, ArrowUpRight, Activity, Globe, RefreshCw } from 'lucide-react';
import Layout from '@/components/layout/Layout';
import TickerTape from '@/components/dashboard/TickerTape';
import StockSearch from '@/components/common/StockSearch';
import api from '@/lib/api';
import { fmt, fmtPct, partyBg, scoreColor, scoreLabel } from '@/lib/utils';

const fadeUp = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0, transition: { duration: 0.4 } } };
const stagger = { hidden: {}, show: { transition: { staggerChildren: 0.07 } } };

export default function Dashboard() {
  const [popular, setPopular] = useState<any[]>([]);
  const [news, setNews] = useState<any[]>([]);
  const [trades, setTrades] = useState<any[]>([]);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [ts, setTs] = useState('');

  const loadAll = async () => {
    try {
      const [pop, nws, ctr] = await Promise.allSettled([
        api.getPopular(), api.getNews(), api.getCongressTrading(),
      ]);
      if (pop.status === 'fulfilled') setPopular(pop.value?.data || []);
      if (nws.status === 'fulfilled') setNews(nws.value?.data || []);
      if (ctr.status === 'fulfilled') setTrades(ctr.value?.data || []);
      setTs(new Date().toLocaleTimeString('zh-CN', { hour12: false }));
    } catch {}
    setLoading(false); setRefreshing(false);
  };

  useEffect(() => { loadAll(); const id = setInterval(loadAll, 30000); return () => clearInterval(id); }, []);
  useEffect(() => {
    if (!popular.length) return;
    api.analyzeStock(popular[0]?.ticker || 'AAPL').then(r => setAnalysis(r?.data)).catch(() => {});
  }, [popular]);

  const catMap: Record<string, { bg: string; text: string }> = {
    Congress: { bg: 'bg-blue-500/15', text: 'text-blue-400' },
    Insider:  { bg: 'bg-q-green/15', text: 'text-q-green' },
    Whale:    { bg: 'bg-q-purple/15', text: 'text-q-purple' },
    Analyst:  { bg: 'bg-q-amber/15', text: 'text-q-amber' },
    Lobbying: { bg: 'bg-orange-500/15', text: 'text-orange-400' },
    SEC:      { bg: 'bg-q-blue/10', text: 'text-q-blue' },
    Contract: { bg: 'bg-pink-500/15', text: 'text-pink-400' },
  };
  const catLabel: Record<string, string> = {
    Congress:'国会', Insider:'内幕', Whale:'鲸鱼', Analyst:'分析师', Lobbying:'游说', SEC:'SEC', Contract:'合同'
  };

  return (
    <>
      <Head><title>数据仪表盘 — Q-Alpha 量化智能平台</title></Head>
      <Layout title="数据仪表盘">
        <TickerTape />
        <div className="p-4 md:p-6 space-y-5 max-w-screen-2xl mx-auto">

          {/* 标题区 */}
          <motion.div variants={stagger} initial="hidden" animate="show" className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <motion.div variants={fadeUp}>
              <h1 className="text-2xl md:text-3xl font-display font-bold text-white tracking-tight">
                市场 <span className="text-neon-blue">智能中心</span>
              </h1>
              <p className="text-q-muted text-sm mt-0.5">
                AI 驱动的量化金融数据聚合平台
                {ts && <span className="ml-2 text-q-muted/50 font-mono text-xs">· 更新于 {ts}</span>}
              </p>
            </motion.div>
            <motion.div variants={fadeUp} className="flex items-center gap-2">
              <StockSearch className="w-64" />
              <button onClick={() => { setRefreshing(true); loadAll(); }} disabled={refreshing}
                className="btn-primary flex items-center gap-2">
                <RefreshCw size={13} className={refreshing ? 'animate-spin' : ''} />
                <span className="hidden sm:inline">刷新数据</span>
              </button>
            </motion.div>
          </motion.div>

          {/* 统计卡片 */}
          <motion.div variants={stagger} initial="hidden" animate="show" className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label: '追踪股票数量', value: '500+', icon: TrendingUp, color: 'text-q-blue', glow: 'glow-blue' },
              { label: '国会交易记录', value: `${trades.length}+`, icon: Users, color: 'text-q-amber' },
              { label: '数据来源接入', value: '12个', icon: Globe, color: 'text-q-green' },
              { label: 'AI 分析引擎', value: '实时', icon: Zap, color: 'text-q-purple' },
            ].map((s, i) => (
              <motion.div key={i} variants={fadeUp} className={`glass-card p-4 ${s.glow || ''}`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-q-muted">{s.label}</span>
                  <s.icon size={14} className={s.color} />
                </div>
                <div className={`text-2xl font-display font-bold ${s.color}`}>{s.value}</div>
              </motion.div>
            ))}
          </motion.div>

          {/* 主内容 */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* 热门股票 */}
            <motion.div className="lg:col-span-2" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
              <div className="glass-card p-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Activity size={15} className="text-q-blue" />
                    <span className="font-display font-semibold text-q-text">热门股票行情</span>
                  </div>
                  <Link href="/search" className="text-xs text-q-blue hover:text-q-blue/80 transition-colors flex items-center gap-1">
                    查看全部 <ArrowUpRight size={11} />
                  </Link>
                </div>
                {loading ? (
                  <div className="space-y-3">{[...Array(6)].map((_, i) => <div key={i} className="h-14 rounded-lg bg-q-border/30 animate-pulse" />)}</div>
                ) : (
                  <div className="space-y-1">
                    {popular.map((stock, i) => {
                      const pos = stock.change_pct >= 0;
                      return (
                        <Link key={stock.ticker} href={`/stock/${stock.ticker}`}>
                          <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-q-border/20 transition-all cursor-pointer group">
                            <span className="text-[11px] font-mono text-q-muted/50 w-4 flex-shrink-0">{i + 1}</span>
                            <div className="w-8 h-8 rounded-lg flex items-center justify-center text-[10px] font-bold font-mono flex-shrink-0" style={{ background: '#00d4ff11', color: '#00d4ff', border: '1px solid #00d4ff22' }}>
                              {stock.ticker?.slice(0, 2)}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-baseline gap-2">
                                <span className="font-mono font-bold text-sm text-q-text">{stock.ticker}</span>
                                <span className="text-xs text-q-muted truncate hidden sm:block">{stock.name}</span>
                              </div>
                            </div>
                            <div className="text-right flex-shrink-0">
                              <div className="font-mono font-semibold text-sm text-q-text">${fmt(stock.price)}</div>
                              <div className={`font-mono text-xs flex items-center gap-0.5 justify-end ${pos ? 'text-q-green' : 'text-q-red'}`}>
                                {pos ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
                                {fmtPct(stock.change_pct)}
                              </div>
                            </div>
                            <ArrowUpRight size={13} className="text-q-muted/30 group-hover:text-q-blue transition-colors flex-shrink-0" />
                          </div>
                        </Link>
                      );
                    })}
                  </div>
                )}
              </div>
            </motion.div>

            {/* 右侧栏 */}
            <div className="space-y-4">
              {/* AI 快速信号 */}
              {analysis && (
                <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }} className="glass-card p-4 glow-blue">
                  <div className="flex items-center gap-2 mb-3">
                    <Zap size={14} className="text-q-blue" />
                    <span className="font-display font-semibold text-sm">AI 快速信号</span>
                    <span className="text-[10px] text-q-muted ml-auto font-mono">{analysis.ticker}</span>
                  </div>
                  <div className="flex items-center gap-4 mb-3">
                    <div className="relative w-16 h-16">
                      <svg viewBox="0 0 64 64" className="w-full h-full -rotate-90">
                        <circle cx="32" cy="32" r="26" fill="none" stroke="#1a2a4a" strokeWidth="5" />
                        <circle cx="32" cy="32" r="26" fill="none" stroke={scoreColor(analysis.score)} strokeWidth="5" strokeLinecap="round"
                          strokeDasharray={`${2 * Math.PI * 26}`}
                          strokeDashoffset={`${2 * Math.PI * 26 * (1 - analysis.score / 100)}`}
                          style={{ filter: `drop-shadow(0 0 4px ${scoreColor(analysis.score)}88)` }} />
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="font-mono font-bold text-sm" style={{ color: scoreColor(analysis.score) }}>{analysis.score}</span>
                      </div>
                    </div>
                    <div>
                      <div className={`text-lg font-bold font-display ${analysis.rating === 'BUY' ? 'text-q-green' : analysis.rating === 'SELL' ? 'text-q-red' : 'text-q-amber'}`}>
                        {analysis.rating === 'BUY' ? '买入' : analysis.rating === 'SELL' ? '卖出' : '持有'}
                      </div>
                      <div className="text-xs text-q-muted">{scoreLabel(analysis.score)}</div>
                    </div>
                  </div>
                  <div className="text-[11px] text-q-dim leading-relaxed line-clamp-3"
                    dangerouslySetInnerHTML={{ __html: analysis.explanation?.replace(/\*\*(.+?)\*\*/g, '<strong style="color:#00d4ff">$1</strong>') || '' }} />
                  <Link href="/ai-analysis" className="mt-3 flex items-center gap-1 text-xs text-q-blue hover:underline">
                    查看完整分析 <ArrowUpRight size={11} />
                  </Link>
                </motion.div>
              )}

              {/* 资讯动态 */}
              <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.25 }} className="glass-card p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-q-red animate-pulse" />
                    <span className="font-display font-semibold text-sm">实时资讯</span>
                  </div>
                </div>
                <div className="space-y-2.5 max-h-72 overflow-y-auto">
                  {news.map((item, i) => {
                    const c = catMap[item.category] || { bg: 'bg-q-border/30', text: 'text-q-muted' };
                    return (
                      <div key={i} className="flex items-start gap-2.5 group cursor-pointer hover:bg-q-border/10 rounded-lg p-1.5 -mx-1.5 transition-colors">
                        <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded flex-shrink-0 mt-0.5 ${c.bg} ${c.text}`}>
                          {catLabel[item.category] || item.category}
                        </span>
                        <div>
                          <p className="text-[11px] text-q-dim leading-snug group-hover:text-q-text transition-colors line-clamp-2">{item.title}</p>
                          <span className="text-[10px] text-q-muted/50 font-mono">{item.time}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </motion.div>
            </div>
          </div>

          {/* 国会交易速览 */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass-card p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Users size={15} className="text-q-amber" />
                <span className="font-display font-semibold">国会股票交易动态</span>
                <span className="text-[10px] text-q-muted font-mono">STOCK 法案披露</span>
              </div>
              <Link href="/congress-trading" className="text-xs text-q-blue hover:underline flex items-center gap-1">
                查看完整仪表盘 <ArrowUpRight size={11} />
              </Link>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-q-border/50">
                    {['议员姓名', '股票代码', '交易类型', '交易金额', '披露日期', '党派'].map(h => (
                      <th key={h} className="text-left py-2 px-3 text-[10px] font-mono font-semibold text-q-muted uppercase tracking-wider">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {trades.slice(0, 6).map((trade, i) => (
                    <tr key={i} className="border-b border-q-border/20 hover:bg-q-border/10 transition-colors">
                      <td className="py-2.5 px-3 font-medium text-xs text-q-text">{trade.politician}</td>
                      <td className="py-2.5 px-3"><span className="font-mono font-bold text-xs text-q-blue">${trade.ticker}</span></td>
                      <td className="py-2.5 px-3">
                        <span className={`tag text-[10px] ${trade.action === 'Purchase' ? 'tag-buy' : 'tag-sell'}`}>
                          {trade.action === 'Purchase' ? '▲ 买入' : '▼ 卖出'}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 font-mono text-xs text-q-dim">{trade.amount}</td>
                      <td className="py-2.5 px-3 font-mono text-[11px] text-q-muted">{trade.date}</td>
                      <td className="py-2.5 px-3">
                        <span className={`tag text-[10px] ${partyBg(trade.party)}`}>
                          {trade.party?.includes('Dem') ? '民主党' : '共和党'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>

        </div>
      </Layout>
    </>
  );
}
