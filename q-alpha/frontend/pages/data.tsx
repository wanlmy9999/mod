import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { motion, AnimatePresence } from 'framer-motion';
import { Database, Globe, TrendingUp, Users, BarChart2, FileText, Tv, Star, Building, Landmark, Search } from 'lucide-react';
import Layout from '@/components/layout/Layout';
import api from '@/lib/api';
import { ratingBg } from '@/lib/utils';

const DATA_CATEGORIES = [
  { id: 'insider',   label: '内幕交易',   icon: TrendingUp, color: 'text-q-green',  desc: 'SEC Form 4 买卖记录' },
  { id: 'whales',    label: '大资金动向', icon: BarChart2,   color: 'text-q-blue',   desc: '13F/13D 机构持仓变动' },
  { id: 'analyst',   label: '分析师评级', icon: Star,        color: 'text-q-amber',  desc: '华尔街一致预期评级' },
  { id: 'lobbying',  label: '企业游说',   icon: Building,    color: 'text-q-purple', desc: '企业向国会的游说金额' },
  { id: 'contracts', label: '政府合同',   icon: Landmark,    color: 'text-q-red',    desc: '联邦政府采购合同披露' },
  { id: 'trends',    label: '谷歌趋势',   icon: Globe,       color: 'text-q-blue',   desc: '搜索关键词热度指数' },
  { id: 'cnbc',      label: 'CNBC 推荐',  icon: Tv,          color: 'text-orange-400', desc: 'CNBC 节目股票推荐' },
  { id: 'cramer',    label: '克莱默追踪', icon: Tv,          color: 'text-pink-400', desc: '吉姆·克莱默交易追踪' },
];

export default function DataHubPage() {
  const [activeCategory, setActive] = useState('insider');
  const [ticker, setTicker]         = useState('AAPL');
  const [keyword, setKeyword]       = useState('NVDA AI chip');
  const [company, setCompany]       = useState('Apple');
  const [data, setData]             = useState<any>(null);
  const [loading, setLoading]       = useState(false);

  const loadData = async (category: string) => {
    setActive(category); setLoading(true); setData(null);
    try {
      let res;
      switch (category) {
        case 'insider':   res = await api.getInsider(ticker); break;
        case 'whales':    res = await api.getWhales(ticker); break;
        case 'analyst':   res = await api.getAnalyst(ticker); break;
        case 'lobbying':  res = await api.getLobbying(company); break;
        case 'contracts': res = await api.getContracts(); break;
        case 'trends':    res = await api.getTrends(keyword); break;
        case 'cnbc':      res = await api.getCNBC(); break;
        case 'cramer':    res = await api.getCramer(); break;
      }
      setData(res?.data);
    } catch {} finally { setLoading(false); }
  };

  useEffect(() => { loadData(activeCategory); }, []);

  const actionLabel = (a: string) => a === 'Purchase' ? '买入' : a === 'Sale' ? '卖出' : a;

  return (
    <>
      <Head><title>数据聚合中心 — Q-Alpha</title></Head>
      <Layout title="数据聚合中心">
        <div className="p-4 md:p-6 space-y-5 max-w-screen-xl mx-auto">
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-2xl font-display font-bold text-white">数据 <span className="text-q-blue">聚合中心</span></h1>
            <p className="text-q-muted text-sm mt-1">12+ 数据源统一聚合 · 延迟更新策略 · 自动 Fallback 机制</p>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">
            <div className="lg:col-span-1 space-y-1">
              {DATA_CATEGORIES.map(cat => (
                <button key={cat.id} onClick={() => loadData(cat.id)}
                  className={`w-full flex items-start gap-2.5 px-3 py-2.5 rounded-lg text-left transition-all ${activeCategory === cat.id ? 'bg-q-blue/10 border border-q-blue/30 text-q-blue' : 'text-q-muted hover:text-q-text hover:bg-q-border/20'}`}>
                  <cat.icon size={14} className={`mt-0.5 flex-shrink-0 ${activeCategory === cat.id ? 'text-q-blue' : cat.color}`} />
                  <div>
                    <div className="text-xs font-medium">{cat.label}</div>
                    <div className="text-[9px] text-q-muted/60 mt-0.5">{cat.desc}</div>
                  </div>
                </button>
              ))}
            </div>

            <div className="lg:col-span-4">
              <div className="glass-card p-4 mb-4">
                <div className="flex flex-wrap gap-3">
                  {['insider','whales','analyst'].includes(activeCategory) && (
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-q-muted uppercase font-mono">股票代码</span>
                      <input type="text" value={ticker} onChange={e => setTicker(e.target.value.toUpperCase())}
                        onBlur={() => loadData(activeCategory)}
                        className="bg-q-surface border border-q-border rounded-lg px-3 py-1.5 text-xs font-mono text-q-text outline-none focus:border-q-blue/60 w-24 uppercase" />
                    </div>
                  )}
                  {activeCategory === 'trends' && (
                    <div className="flex items-center gap-2 flex-1">
                      <span className="text-[10px] text-q-muted uppercase font-mono">搜索关键词</span>
                      <input type="text" value={keyword} onChange={e => setKeyword(e.target.value)}
                        onBlur={() => loadData('trends')}
                        className="bg-q-surface border border-q-border rounded-lg px-3 py-1.5 text-xs text-q-text outline-none focus:border-q-blue/60 flex-1" />
                    </div>
                  )}
                  {activeCategory === 'lobbying' && (
                    <div className="flex items-center gap-2 flex-1">
                      <span className="text-[10px] text-q-muted uppercase font-mono">公司名称</span>
                      <input type="text" value={company} onChange={e => setCompany(e.target.value)}
                        onBlur={() => loadData('lobbying')}
                        className="bg-q-surface border border-q-border rounded-lg px-3 py-1.5 text-xs text-q-text outline-none focus:border-q-blue/60 flex-1" />
                    </div>
                  )}
                  <button onClick={() => loadData(activeCategory)} className="btn-primary flex items-center gap-1.5 text-xs whitespace-nowrap">
                    <Search size={12} /> 加载数据
                  </button>
                </div>
              </div>

              <AnimatePresence mode="wait">
                <motion.div key={activeCategory} initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }} className="glass-card p-4">
                  <div className="flex items-center gap-2 mb-4">
                    {(() => { const cat = DATA_CATEGORIES.find(c => c.id === activeCategory); if (!cat) return null;
                      return <><cat.icon size={15} className={cat.color} /><span className="font-display font-semibold text-sm">{cat.label}</span></>;
                    })()}
                    {loading && <div className="ml-2 w-3 h-3 rounded-full border border-t-q-blue animate-spin" />}
                  </div>

                  {loading ? (
                    <div className="space-y-2.5">{[...Array(6)].map((_, i) => <div key={i} className="h-12 rounded-lg bg-q-border/30 animate-pulse" />)}</div>
                  ) : !data ? (
                    <div className="text-q-muted text-sm py-8 text-center">暂无数据，请点击"加载数据"</div>
                  ) : activeCategory === 'insider' && Array.isArray(data) ? (
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs">
                        <thead><tr className="border-b border-q-border/50">{['内幕人员','职务','操作','股数','均价','日期'].map(h => <th key={h} className="text-left py-2 px-2 text-[9px] font-mono text-q-muted uppercase tracking-wider">{h}</th>)}</tr></thead>
                        <tbody>
                          {data.map((row: any, i: number) => (
                            <tr key={i} className="border-b border-q-border/20 hover:bg-q-border/10">
                              <td className="py-2 px-2 font-medium text-q-text">{row.insider_name}</td>
                              <td className="py-2 px-2 text-q-muted">{row.role}</td>
                              <td className="py-2 px-2"><span className={`tag text-[9px] ${row.action === 'Purchase' ? 'tag-buy' : 'tag-sell'}`}>{actionLabel(row.action)}</span></td>
                              <td className="py-2 px-2 font-mono">{row.shares?.toLocaleString()}</td>
                              <td className="py-2 px-2 font-mono">${row.price}</td>
                              <td className="py-2 px-2 font-mono text-q-muted">{row.date}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : activeCategory === 'whales' && Array.isArray(data) ? (
                    <div className="space-y-2">
                      {data.map((w: any, i: number) => (
                        <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-q-surface border border-q-border/40">
                          <div className="flex-1"><div className="text-xs font-semibold text-q-text">{w.fund}</div><div className="text-[10px] text-q-muted">{w.shares?.toLocaleString()} 股 · {w.filing_date}</div></div>
                          <div className="text-right"><div className="font-mono font-semibold text-sm text-q-text">{w.value}</div><div className={`font-mono text-xs ${w.change?.startsWith('+') ? 'text-q-green' : 'text-q-red'}`}>{w.change}</div></div>
                        </div>
                      ))}
                    </div>
                  ) : activeCategory === 'analyst' && Array.isArray(data) ? (
                    <div className="space-y-2">
                      {data.map((a: any, i: number) => (
                        <div key={i} className="flex items-center gap-3 p-2.5 rounded-lg bg-q-surface border border-q-border/40">
                          <div className="flex-1 text-xs font-medium text-q-text">{a.firm}</div>
                          <span className={`tag text-[10px] ${ratingBg(a.rating)}`}>
                            {a.rating === 'Buy' || a.rating === 'Strong Buy' ? '买入' : a.rating === 'Sell' || a.rating === 'Strong Sell' ? '卖出' : '持有'}
                          </span>
                          <div className="font-mono text-xs text-q-muted">目标价: ${a.price_target}</div>
                          <div className="font-mono text-[10px] text-q-muted">{a.date}</div>
                        </div>
                      ))}
                    </div>
                  ) : activeCategory === 'trends' && data?.data ? (
                    <div>
                      <div className="flex items-center gap-2 mb-3">
                        <span className="text-xs text-q-muted">关键词：</span>
                        <span className="text-xs font-mono font-semibold text-q-blue">{data.keyword}</span>
                        <span className="text-xs text-q-muted ml-2">峰值热度：{data.peak}</span>
                      </div>
                      <div className="flex items-end gap-1 h-32">
                        {data.data.slice(-24).map((pt: any, i: number) => {
                          const maxV = Math.max(...data.data.slice(-24).map((p: any) => p.interest));
                          return (
                            <div key={i} className="flex-1 flex flex-col items-center gap-1 min-w-0">
                              <div className="w-full rounded-t-sm" style={{ height: `${(pt.interest / (maxV || 1)) * 100}%`, background: 'linear-gradient(to top, rgba(0,212,255,0.3), #00d4ff)', minHeight: 4 }} />
                              <span className="text-[8px] text-q-muted/60 truncate w-full text-center hidden sm:block">{pt.date?.slice(5)}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ) : Array.isArray(data) ? (
                    <div className="space-y-2">
                      {data.map((item: any, i: number) => (
                        <div key={i} className="p-3 rounded-lg bg-q-surface border border-q-border/40 text-xs">
                          <div className="flex items-start justify-between gap-2">
                            <div className="text-q-text font-medium">{item.show || item.agency || item.company || item.issue || '记录'}</div>
                            {item.amount && <span className="font-mono text-q-amber flex-shrink-0">{item.amount}</span>}
                          </div>
                          {(item.issue || item.description || item.ticker) && (
                            <div className="text-q-muted mt-1">{item.issue || item.description || ''}{item.ticker ? ` · $${item.ticker}` : ''}{item.action ? ` · ${actionLabel(item.action)}` : ''}</div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <pre className="text-[10px] text-q-muted overflow-auto max-h-80 bg-q-surface rounded-lg p-3">{JSON.stringify(data, null, 2)}</pre>
                  )}
                </motion.div>
              </AnimatePresence>
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
}
