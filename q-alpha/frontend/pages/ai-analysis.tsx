import React, { useState } from 'react';
import Head from 'next/head';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, Zap, TrendingUp, BarChart2, Shield, Download, Loader } from 'lucide-react';
import Layout from '@/components/layout/Layout';
import AIScoreCard from '@/components/ai/AIScoreCard';
import StockSearch from '@/components/common/StockSearch';
import api from '@/lib/api';

const QUICK_TICKERS = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'META', 'AMZN', 'AMD', 'GOOGL'];

export default function AIAnalysisPage() {
  const [ticker, setTicker] = useState('');
  const [analysis, setAna] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [portfolio, setPortf] = useState<any>(null);
  const [mode, setMode] = useState<'stock' | 'portfolio'>('stock');
  const [celeb, setCeleb] = useState('');

  const runAnalysis = async (t: string) => {
    setTicker(t); setLoading(true); setError(''); setAna(null);
    try {
      const res = await api.analyzeStock(t);
      setAna(res?.data);
    } catch (e: any) { setError(e.message || '分析失败'); }
    finally { setLoading(false); }
  };

  const loadPortfolio = async (name: string) => {
    setLoading(true); setPortf(null);
    try { const res = await api.getFamousPortfolio(name); setPortf(res?.data); }
    catch {} finally { setLoading(false); }
  };

  return (
    <>
      <Head><title>AI 分析引擎 — Q-Alpha</title></Head>
      <Layout title="AI 分析引擎">
        <div className="p-4 md:p-6 space-y-6 max-w-screen-xl mx-auto">

          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="text-center py-6">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-q-blue/10 border border-q-blue/20 mb-4">
              <Zap size={13} className="text-q-blue" />
              <span className="text-xs font-mono text-q-blue tracking-wider">Q-ALPHA AI 智能分析引擎</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-display font-black text-white mb-3">
              AI 投资 <span className="text-neon-blue">分析报告</span>
            </h1>
            <p className="text-q-muted max-w-lg mx-auto text-sm leading-relaxed">
              综合技术指标、内幕交易信号、机构持仓动向与分析师评级，为任意股票生成 0-100 分的复合评分与投资建议
            </p>
          </motion.div>

          {/* 模式切换 */}
          <div className="flex justify-center gap-2">
            {[
              { id: 'stock', label: '股票分析', icon: TrendingUp },
              { id: 'portfolio', label: '名人投资组合', icon: BarChart2 },
            ].map(m => (
              <button key={m.id} onClick={() => setMode(m.id as any)}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all ${mode === m.id ? 'bg-q-blue/20 text-q-blue border border-q-blue/40 shadow-glow-blue' : 'text-q-muted bg-q-card border border-q-border hover:border-q-border/80'}`}>
                <m.icon size={14} />{m.label}
              </button>
            ))}
          </div>

          <AnimatePresence mode="wait">
            {mode === 'stock' && (
              <motion.div key="stock" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <div className="max-w-lg mx-auto">
                  <StockSearch className="w-full" placeholder="输入股票代码，例如 AAPL、TSLA、NVDA…" onSelect={runAnalysis} autoFocus />
                </div>
                <div className="flex justify-center flex-wrap gap-2 mt-3">
                  {QUICK_TICKERS.map(t => (
                    <button key={t} onClick={() => runAnalysis(t)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all ${ticker === t ? 'bg-q-blue/20 text-q-blue border border-q-blue/40' : 'bg-q-card border border-q-border text-q-muted hover:text-q-blue hover:border-q-blue/30'}`}>
                      {t}
                    </button>
                  ))}
                </div>

                <AnimatePresence>
                  {loading && (
                    <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }} className="max-w-2xl mx-auto mt-6">
                      <div className="glass-card p-8 text-center glow-blue">
                        <div className="flex justify-center mb-4">
                          <div className="relative w-16 h-16">
                            <div className="absolute inset-0 rounded-full border-2 border-q-blue/20" />
                            <div className="absolute inset-0 rounded-full border-2 border-t-q-blue animate-spin" />
                            <Bot size={20} className="absolute inset-0 m-auto text-q-blue" />
                          </div>
                        </div>
                        <div className="text-q-blue font-display font-semibold mb-1">正在分析 {ticker}…</div>
                        <div className="text-q-muted text-sm">计算 RSI、MACD、内幕信号、机构持仓…</div>
                        <div className="mt-4 space-y-1.5 text-left max-w-xs mx-auto">
                          {['加载价格数据与K线', '获取内幕交易记录', '分析机构持仓变动', '计算复合评分'].map((step, i) => (
                            <motion.div key={step} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.3 }}
                              className="flex items-center gap-2 text-xs text-q-muted">
                              <div className="w-1.5 h-1.5 rounded-full bg-q-blue/50 animate-pulse" />
                              {step}
                            </motion.div>
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  )}
                  {analysis && !loading && (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl mx-auto mt-6">
                      <AIScoreCard data={analysis} />
                      <div className="flex justify-center gap-3 mt-4 flex-wrap">
                        <a href={api.getReportUrl(analysis.ticker, 'html')} target="_blank" rel="noreferrer"
                          className="btn-primary flex items-center gap-2 text-xs">
                          <Download size={12} /> 下载 HTML 完整报告
                        </a>
                        <a href={api.getReportUrl(analysis.ticker, 'markdown')} download className="btn-primary flex items-center gap-2 text-xs">
                          <Download size={12} /> 下载 Markdown 报告
                        </a>
                        <a href={api.getReportUrl(analysis.ticker, 'json')} download className="btn-primary flex items-center gap-2 text-xs">
                          <Download size={12} /> 导出 JSON 数据
                        </a>
                      </div>
                    </motion.div>
                  )}
                  {error && (
                    <div className="max-w-lg mx-auto mt-6 p-4 rounded-xl bg-q-red/10 border border-q-red/30 text-q-red text-sm text-center">{error}</div>
                  )}
                </AnimatePresence>
              </motion.div>
            )}

            {mode === 'portfolio' && (
              <motion.div key="portfolio" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
                <div className="text-center text-xs text-q-muted mb-2">选择知名投资人或政治人物查看其持仓组合</div>
                <div className="flex justify-center flex-wrap gap-3">
                  {[
                    { name: 'Nancy Pelosi', label: '美国众议员' },
                    { name: 'Warren Buffett', label: '股神·伯克希尔' },
                    { name: 'Tommy Tuberville', label: '美国参议员' },
                    { name: 'Dan Goldman', label: '美国众议员' },
                  ].map(p => (
                    <button key={p.name} onClick={() => { setCeleb(p.name); loadPortfolio(p.name); }}
                      className={`glass-card px-5 py-3 text-left transition-all cursor-pointer ${celeb === p.name ? 'glow-blue border-q-blue/40' : 'hover:glow-blue'}`}>
                      <div className="font-semibold text-sm text-q-text">{p.name}</div>
                      <div className="text-xs text-q-muted">{p.label}</div>
                    </button>
                  ))}
                </div>
                {loading && <div className="flex justify-center py-8"><Loader size={24} className="text-q-blue animate-spin" /></div>}
                {portfolio && !loading && (
                  <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5 max-w-2xl mx-auto">
                    <div className="flex items-center gap-2 mb-4">
                      <BarChart2 size={16} className="text-q-blue" />
                      <h3 className="font-display font-semibold">{portfolio.name} — 持仓组合</h3>
                    </div>
                    <div className="space-y-3">
                      {portfolio.holdings?.map((h: any, i: number) => (
                        <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-q-surface border border-q-border/50">
                          <span className="font-mono font-bold text-q-blue text-sm w-14">{h.ticker}</span>
                          <div className="flex-1 min-w-0">
                            <div className="text-xs text-q-muted">{h.shares?.toLocaleString()} 股</div>
                          </div>
                          <div className="text-right">
                            <div className="font-mono font-semibold text-sm text-q-text">{h.value}</div>
                            <div className="text-xs text-q-green font-mono">{h.return}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* 评分说明 */}
          {!analysis && !loading && mode === 'stock' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }} className="max-w-3xl mx-auto">
              <div className="text-center text-xs text-q-muted uppercase tracking-widest mb-4 font-mono">评分算法说明</div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {[
                  { icon: TrendingUp, label: '技术面', desc: 'RSI · MACD · 均线系统', color: 'text-q-blue', weight: '40%' },
                  { icon: Shield, label: '内幕信号', desc: 'SEC Form 4 买卖比例', color: 'text-q-green', weight: '25%' },
                  { icon: BarChart2, label: '机构动向', desc: '13F/13D 持仓变动', color: 'text-q-amber', weight: '20%' },
                  { icon: Bot, label: '分析师共识', desc: '华尔街评级汇总', color: 'text-q-purple', weight: '15%' },
                ].map(item => (
                  <div key={item.label} className="glass-card p-4 text-center">
                    <item.icon size={20} className={`${item.color} mx-auto mb-2`} />
                    <div className="font-semibold text-sm text-q-text">{item.label}</div>
                    <div className="text-[10px] text-q-muted mt-1 leading-relaxed">{item.desc}</div>
                    <div className={`text-lg font-display font-bold ${item.color} mt-2`}>{item.weight}</div>
                    <div className="text-[10px] text-q-muted">权重占比</div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

        </div>
      </Layout>
    </>
  );
}
