import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, TrendingDown, BarChart2, Bot, FileText, Users, Zap, Download, ExternalLink } from 'lucide-react';
import Layout from '@/components/layout/Layout';
import CandlestickChart from '@/components/charts/CandlestickChart';
import AIScoreCard from '@/components/ai/AIScoreCard';
import StockSearch from '@/components/common/StockSearch';
import api from '@/lib/api';
import { fmt, fmtCompact, fmtPct, ratingBg, scoreColor } from '@/lib/utils';

const TABS = [
  { id: 'overview',    label: '行情概览', icon: BarChart2 },
  { id: 'ai',         label: 'AI 分析',  icon: Bot },
  { id: 'insider',    label: '内幕交易', icon: Users },
  { id: 'whales',     label: '大资金',   icon: BarChart2 },
  { id: 'financials', label: '财务数据', icon: FileText },
  { id: 'sec',        label: 'SEC 文件', icon: FileText },
];

export default function StockPage() {
  const router = useRouter();
  const ticker = (router.query.ticker as string || '').toUpperCase();
  const [activeTab, setActiveTab] = useState('overview');
  const [timeframe, setTimeframe] = useState('3mo');
  const [price, setPrice]         = useState<any>(null);
  const [info, setInfo]           = useState<any>(null);
  const [candles, setCandles]     = useState<any>(null);
  const [analysis, setAnalysis]   = useState<any>(null);
  const [insider, setInsider]     = useState<any[]>([]);
  const [whales, setWhales]       = useState<any[]>([]);
  const [analyst, setAnalyst]     = useState<any[]>([]);
  const [sec, setSec]             = useState<any[]>([]);
  const [revenue, setRevenue]     = useState<any>(null);
  const [risk, setRisk]           = useState<any[]>([]);
  const [loading, setLoading]     = useState(true);
  const [sourceMeta, setSourceMeta] = useState<Record<string, any>>({});

  const setMeta = (key: string, meta: any) => {
    if (!meta) return;
    setSourceMeta(prev => ({ ...prev, [key]: meta }));
  };

  useEffect(() => {
    if (!ticker) return;
    setLoading(true);
    Promise.allSettled([
      api.getStockPrice(ticker).then(r => { setPrice(r?.data); setMeta('price', r?.meta); }),
      api.getStockInfo(ticker).then(r => { setInfo(r?.data); setMeta('info', r?.meta); }),
      api.getStockCandles(ticker, timeframe).then(r => { setCandles(r?.data); setMeta('candles', r?.meta); }),
    ]).finally(() => setLoading(false));
    api.getInsider(ticker).then(r => { setInsider(r?.data || []); setMeta('insider', r?.meta); }).catch(() => {});
    api.getWhales(ticker).then(r => { setWhales(r?.data || []); setMeta('whales', r?.meta); }).catch(() => {});
    api.getAnalyst(ticker).then(r => { setAnalyst(r?.data || []); setMeta('analyst', r?.meta); }).catch(() => {});
    api.getSECFilings(ticker).then(r => { setSec(r?.data || []); setMeta('sec', r?.meta); }).catch(() => {});
    api.getRevenue(ticker).then(r => { setRevenue(r?.data); setMeta('revenue', r?.meta); }).catch(() => {});
    api.getRisk(ticker).then(r => { setRisk(r?.data || []); setMeta('risk', r?.meta); }).catch(() => {});
  }, [ticker]);

  useEffect(() => {
    if (!ticker) return;
    api.getStockCandles(ticker, timeframe).then(r => { setCandles(r?.data); setMeta('candles', r?.meta); }).catch(() => {});
  }, [timeframe, ticker]);

  useEffect(() => {
    if (!ticker || activeTab !== 'ai' || analysis) return;
    api.analyzeStock(ticker).then(r => { setAnalysis(r?.data); setMeta('ai', r?.meta); }).catch(() => {});
  }, [activeTab, ticker]);

  const pos = price && price.change_pct >= 0;
  if (!ticker) return null;

  const ratingCN = (r: string) => r === 'Buy' || r === 'Strong Buy' ? '买入' : r === 'Sell' || r === 'Strong Sell' ? '卖出' : '持有';
  const actionCN = (a: string) => a === 'Purchase' ? '买入' : a === 'Sale' ? '卖出' : '行权';

  return (
    <>
      <Head><title>${ticker} 股票分析 — Q-Alpha</title></Head>
      <Layout title={`$${ticker} 股票详情`}>
        <div className="p-4 md:p-6 space-y-5 max-w-screen-2xl mx-auto">
          <div className="flex items-center gap-3">
            <StockSearch className="max-w-xs" onSelect={t => router.push(`/stock/${t}`)} />
            <div className="flex-1" />
            <a href={api.getReportUrl(ticker, 'html')} target="_blank" className="btn-primary flex items-center gap-1.5 text-xs">
              <Download size={13} /> 下载报告
            </a>
          </div>

          {/* 股票头部卡片 */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5 glow-blue">
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <h1 className="text-3xl font-display font-black text-white tracking-tight">${ticker}</h1>
                  {info && <span className="text-q-muted text-sm font-medium">{info.name}</span>}
                </div>
                {info && (
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="tag tag-blue text-[10px]">{info.sector}</span>
                    <span className="tag tag-blue text-[10px]">{info.industry}</span>
                    {info.website && (
                      <a href={info.website} target="_blank" rel="noreferrer" className="text-[10px] text-q-muted hover:text-q-blue flex items-center gap-0.5">
                        {info.website.replace('https://','')} <ExternalLink size={9} />
                      </a>
                    )}
                  </div>
                )}
              </div>
              {price && (
                <div className="text-right flex-shrink-0">
                  <div className="text-4xl font-display font-black text-white">${fmt(price.price)}</div>
                  <div className={`flex items-center gap-1 justify-end mt-1 text-lg font-semibold ${pos ? 'text-q-green' : 'text-q-red'}`}>
                    {pos ? <TrendingUp size={18} /> : <TrendingDown size={18} />}
                    {fmtPct(price.change_pct)}
                    <span className="text-sm text-q-muted font-normal ml-1">今日</span>
                  </div>
                </div>
              )}
            </div>
            <div className="mt-3 flex justify-end">
              <div className="relative group">
                <button className="text-[11px] px-2 py-1 rounded border border-q-border text-q-muted hover:text-q-text">
                  悬停查看数据来源（1秒）
                </button>
                <div className="pointer-events-none absolute right-0 mt-2 w-[420px] max-h-80 overflow-auto rounded-lg border border-q-border bg-[#071028] p-3 text-[11px] text-q-dim opacity-0 group-hover:opacity-100 transition-opacity duration-300 delay-[1000ms] z-30">
                  <pre className="whitespace-pre-wrap break-all">{JSON.stringify(sourceMeta, null, 2)}</pre>
                </div>
              </div>
            </div>

            {(price || info) && (
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 mt-4 pt-4 border-t border-q-border/50">
                {[
                  { label: '总市值', value: fmtCompact(info?.market_cap) },
                  { label: '成交量', value: price?.volume ? `${(price.volume / 1e6).toFixed(1)}M` : '—' },
                  { label: '市盈率', value: info?.pe_ratio ? fmt(info.pe_ratio, 1) : '—' },
                  { label: '52周最高', value: info?.['52w_high'] ? `$${fmt(info['52w_high'])}` : '—' },
                  { label: '52周最低', value: info?.['52w_low'] ? `$${fmt(info['52w_low'])}` : '—' },
                  { label: 'Beta', value: info?.beta ? fmt(info.beta) : '—' },
                ].map(m => (
                  <div key={m.label}>
                    <div className="text-[10px] text-q-muted uppercase tracking-wide mb-0.5">{m.label}</div>
                    <div className="font-mono font-semibold text-sm text-q-text">{m.value}</div>
                  </div>
                ))}
              </div>
            )}
          </motion.div>

          {/* 标签页 */}
          <div className="flex items-center gap-1 border-b border-q-border overflow-x-auto">
            {TABS.map(tab => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 px-3 py-2.5 text-xs font-medium whitespace-nowrap border-b-2 transition-all ${activeTab === tab.id ? 'border-q-blue text-q-blue' : 'border-transparent text-q-muted hover:text-q-text hover:border-q-border'}`}>
                <tab.icon size={13} />{tab.label}
              </button>
            ))}
          </div>

          <AnimatePresence mode="wait">
            <motion.div key={activeTab} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }}>

              {activeTab === 'overview' && (
                <div className="grid grid-cols-1 xl:grid-cols-4 gap-5">
                  <div className="xl:col-span-3 glass-card p-5">
                    <CandlestickChart candles={candles?.candles || []} ticker={ticker} timeframe={timeframe} onTimeframeChange={setTimeframe} height={440} />
                  </div>
                  <div className="space-y-4">
                    <div className="glass-card p-4">
                      <div className="text-xs font-mono text-q-muted uppercase tracking-widest mb-3">分析师评级</div>
                      <div className="space-y-2">
                        {analyst.slice(0, 5).map((a, i) => (
                          <div key={i} className="flex items-center justify-between">
                            <span className="text-xs text-q-dim truncate max-w-[120px]">{a.firm}</span>
                            <span className={`tag text-[10px] ${ratingBg(a.rating)}`}>{ratingCN(a.rating)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    {info?.description && (
                      <div className="glass-card p-4">
                        <div className="text-xs font-mono text-q-muted uppercase tracking-widest mb-2">公司简介</div>
                        <p className="text-xs text-q-dim leading-relaxed line-clamp-6">{info.description}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'ai' && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
                  <div className="lg:col-span-2">
                    {!analysis ? (
                      <div className="glass-card p-8 flex items-center justify-center">
                        <button onClick={() => api.analyzeStock(ticker).then(r => { setAnalysis(r?.data); setMeta('ai', r?.meta); })} className="btn-primary flex items-center gap-2">
                          <Bot size={15} /> 运行 AI 分析
                        </button>
                      </div>
                    ) : <AIScoreCard data={analysis} />}
                  </div>
                  <div className="space-y-4">
                    <div className="glass-card p-4">
                      <div className="text-xs font-mono text-q-muted uppercase tracking-widest mb-3">风险因素</div>
                      <div className="space-y-2">
                        {risk.map((r, i) => (
                          <div key={i} className="flex items-start gap-2 p-2 rounded-lg bg-q-surface border border-q-border/50">
                            <span className="text-[10px] px-1.5 py-0.5 rounded bg-q-border text-q-muted flex-shrink-0 mt-0.5">{r.category}</span>
                            <p className="text-[11px] text-q-dim leading-snug">{r.risk}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'insider' && (
                <div className="glass-card p-4">
                  <div className="text-xs font-mono text-q-muted uppercase tracking-widest mb-4">内幕交易记录 — {ticker}</div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead><tr className="border-b border-q-border/50">{['内幕人员','职务','操作','股数','均价','总额','日期'].map(h => <th key={h} className="text-left py-2 px-3 text-[10px] font-mono font-semibold text-q-muted uppercase tracking-wider">{h}</th>)}</tr></thead>
                      <tbody>
                        {insider.map((row, i) => (
                          <tr key={i} className="border-b border-q-border/20 hover:bg-q-border/10 transition-colors">
                            <td className="py-2.5 px-3 text-xs font-medium text-q-text">{row.insider_name}</td>
                            <td className="py-2.5 px-3 text-[11px] text-q-muted">{row.role}</td>
                            <td className="py-2.5 px-3"><span className={`tag text-[10px] ${row.action === 'Purchase' ? 'tag-buy' : row.action === 'Sale' ? 'tag-sell' : 'tag-hold'}`}>{actionCN(row.action)}</span></td>
                            <td className="py-2.5 px-3 font-mono text-xs text-q-dim">{row.shares?.toLocaleString()}</td>
                            <td className="py-2.5 px-3 font-mono text-xs text-q-dim">${fmt(row.price)}</td>
                            <td className="py-2.5 px-3 font-mono text-xs font-semibold text-q-text">{row.amount}</td>
                            <td className="py-2.5 px-3 font-mono text-[11px] text-q-muted">{row.date}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {activeTab === 'whales' && (
                <div className="glass-card p-4">
                  <div className="text-xs font-mono text-q-muted uppercase tracking-widest mb-4">机构持仓 — {ticker}</div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {whales.map((w, i) => (
                      <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-q-surface border border-q-border/50 hover:border-q-border transition-colors">
                        <div className="w-10 h-10 rounded-full bg-q-border/50 flex items-center justify-center flex-shrink-0">
                          <BarChart2 size={16} className="text-q-muted" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-sm text-q-text truncate">{w.fund}</div>
                          <div className="text-xs text-q-muted">{w.shares?.toLocaleString()} 股</div>
                        </div>
                        <div className="text-right flex-shrink-0">
                          <div className="font-mono font-semibold text-sm text-q-text">{w.value}</div>
                          <div className={`font-mono text-xs ${w.change?.startsWith('+') ? 'text-q-green' : 'text-q-red'}`}>{w.change}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'financials' && revenue && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                  <div className="glass-card p-4">
                    <div className="text-xs font-mono text-q-muted uppercase tracking-widest mb-4">营收拆分</div>
                    <div className="space-y-3">
                      {revenue.segments?.map((seg: any, i: number) => (
                        <div key={i}>
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span className="text-q-text font-medium">{seg.segment}</span>
                            <span className="font-mono text-q-muted">${seg.revenue}B · {seg.pct}%</span>
                          </div>
                          <div className="h-2 bg-q-border rounded-full overflow-hidden">
                            <motion.div className="h-full rounded-full" style={{ background: 'linear-gradient(90deg, #00d4ff, #00ff88)' }}
                              initial={{ width: 0 }} animate={{ width: `${seg.pct}%` }} transition={{ duration: 0.8, delay: i * 0.1 }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="glass-card p-4">
                    <div className="text-xs font-mono text-q-muted uppercase tracking-widest mb-4">关键财务指标</div>
                    <div className="space-y-2.5">
                      {[
                        { label: '年度总营收', value: `$${revenue.total}B` },
                        { label: '财年', value: revenue.fiscal_year },
                        { label: '市盈率 P/E', value: info?.pe_ratio ? fmt(info.pe_ratio, 1) : '—' },
                        { label: '每股收益 EPS', value: info?.eps ? `$${fmt(info.eps)}` : '—' },
                        { label: '股息率', value: info?.dividend_yield ? `${fmt(info.dividend_yield)}%` : '—' },
                        { label: '全职员工数', value: info?.employees?.toLocaleString() || '—' },
                      ].map(m => (
                        <div key={m.label} className="flex justify-between py-1.5 border-b border-q-border/30">
                          <span className="text-xs text-q-muted">{m.label}</span>
                          <span className="text-xs font-mono font-semibold text-q-text">{m.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'sec' && (
                <div className="glass-card p-4">
                  <div className="text-xs font-mono text-q-muted uppercase tracking-widest mb-4">SEC 文件 — {ticker}</div>
                  <div className="space-y-2">
                    {sec.map((filing, i) => (
                      <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-q-surface border border-q-border/40 hover:border-q-border transition-colors">
                        <span className={`text-[10px] font-bold px-2 py-1 rounded font-mono flex-shrink-0 ${filing.form === '10-K' ? 'bg-q-blue/20 text-q-blue' : filing.form === '10-Q' ? 'bg-q-green/20 text-q-green' : 'bg-q-amber/20 text-q-amber'}`}>
                          {filing.form}
                        </span>
                        <div className="flex-1 min-w-0">
                          <div className="text-xs text-q-text font-medium">{filing.form === '10-K' ? '年度报告' : filing.form === '10-Q' ? '季度报告' : '重大事项披露'}</div>
                        </div>
                        <span className="font-mono text-[11px] text-q-muted flex-shrink-0">{filing.date}</span>
                        {filing.url && (
                          <a href={filing.url} target="_blank" rel="noreferrer" className="text-q-muted hover:text-q-blue transition-colors flex-shrink-0"><ExternalLink size={12} /></a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </motion.div>
          </AnimatePresence>
        </div>
      </Layout>
    </>
  );
}
