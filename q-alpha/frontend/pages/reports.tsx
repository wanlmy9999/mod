import React, { useState } from 'react';
import Head from 'next/head';
import { motion } from 'framer-motion';
import { FileText, Download, Bot, BarChart2, Globe, Loader, CheckCircle } from 'lucide-react';
import Layout from '@/components/layout/Layout';
import StockSearch from '@/components/common/StockSearch';
import api from '@/lib/api';
import { POPULAR_TICKERS, scoreColor } from '@/lib/utils';

const FORMAT_OPTIONS = [
  { id: 'html',     label: 'HTML 报告',   icon: Globe,    desc: '深色主题交互式报告，含完整图表', ext: 'html' },
  { id: 'markdown', label: 'Markdown',    icon: FileText,  desc: '适用于 Notion / GitHub / 文档', ext: 'md'   },
  { id: 'json',     label: 'JSON 数据',   icon: BarChart2, desc: '结构化原始数据，供二次开发', ext: 'json' },
];

export default function ReportsPage() {
  const [ticker, setTicker]   = useState('AAPL');
  const [format, setFormat]   = useState<'html' | 'markdown' | 'json'>('html');
  const [preview, setPreview] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const runPreview = async (t: string) => {
    setTicker(t); setLoading(true); setPreview(null);
    try { const res = await api.analyzeStock(t); setPreview(res?.data); }
    catch {} finally { setLoading(false); }
  };

  const reportSections = [
    '一、AI 综合评分与投资建议',
    '二、关键市场数据（总市值、市盈率、52周高低）',
    '三、技术指标分析（RSI、MACD、均线系统）',
    '四、AI 分析逻辑与评分依据',
    '五、内幕交易记录（SEC Form 4）',
    '六、机构大资金持仓（13F/13D）',
    '七、华尔街分析师评级汇总',
    '八、风险因素与预警信号',
    '九、公司基本信息与业务描述',
    '免责声明',
  ];

  return (
    <>
      <Head><title>研究报告下载 — Q-Alpha</title></Head>
      <Layout title="研究报告下载">
        <div className="p-4 md:p-6 space-y-6 max-w-3xl mx-auto">
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-2xl font-display font-bold text-white">
              研究报告 <span className="text-q-blue">生成器</span>
            </h1>
            <p className="text-q-muted text-sm mt-1">
              AI 自动生成专业投资研究报告，包含技术分析、内幕信号、机构持仓、风险预警等完整内容
            </p>
          </motion.div>

          {/* 报告包含内容说明 */}
          <div className="glass-card p-4">
            <div className="text-xs font-mono text-q-muted uppercase tracking-widest mb-3 flex items-center gap-2">
              <CheckCircle size={11} className="text-q-green" /> 报告包含以下章节
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
              {reportSections.map(s => (
                <div key={s} className="flex items-center gap-2 text-[11px] text-q-dim">
                  <div className="w-1 h-1 rounded-full bg-q-green/60 flex-shrink-0" />
                  {s}
                </div>
              ))}
            </div>
          </div>

          {/* 步骤一：选择股票 */}
          <div className="glass-card p-5 space-y-4">
            <div className="text-xs font-mono text-q-muted uppercase tracking-widest flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-q-blue/20 text-q-blue border border-q-blue/30 flex items-center justify-center text-[10px] font-bold">1</span>
              选择分析股票
            </div>
            <StockSearch className="w-full" placeholder="搜索股票代码..." onSelect={runPreview} />
            <div className="flex gap-1.5 flex-wrap">
              {POPULAR_TICKERS.slice(0, 6).map(t => (
                <button key={t} onClick={() => runPreview(t)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all ${ticker === t ? 'bg-q-blue/20 text-q-blue border border-q-blue/30' : 'bg-q-card border border-q-border text-q-muted hover:text-q-text'}`}>
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* 步骤二：选择格式 */}
          <div className="glass-card p-5 space-y-3">
            <div className="text-xs font-mono text-q-muted uppercase tracking-widest flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-q-blue/20 text-q-blue border border-q-blue/30 flex items-center justify-center text-[10px] font-bold">2</span>
              选择报告格式
            </div>
            <div className="grid grid-cols-3 gap-3">
              {FORMAT_OPTIONS.map(f => (
                <button key={f.id} onClick={() => setFormat(f.id as any)}
                  className={`p-3 rounded-xl text-left transition-all border ${format === f.id ? 'bg-q-blue/10 border-q-blue/40 text-q-blue' : 'bg-q-surface border-q-border text-q-muted hover:border-q-border/80 hover:text-q-text'}`}>
                  <f.icon size={16} className="mb-2" />
                  <div className="text-xs font-semibold">{f.label}</div>
                  <div className="text-[10px] mt-0.5 opacity-70">{f.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* 步骤三：预览与下载 */}
          {(preview || loading) && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5 space-y-4">
              <div className="text-xs font-mono text-q-muted uppercase tracking-widest flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-q-green/20 text-q-green border border-q-green/30 flex items-center justify-center text-[10px] font-bold">3</span>
                预览与下载
              </div>

              {loading ? (
                <div className="flex items-center gap-3 py-4 text-q-muted">
                  <Loader size={16} className="animate-spin text-q-blue" />
                  <span className="text-sm">正在生成 {ticker} 分析报告...</span>
                </div>
              ) : preview && (
                <>
                  <div className="flex items-center gap-5 p-4 rounded-xl bg-q-surface border border-q-border">
                    <div className="text-center">
                      <div className="text-4xl font-display font-black" style={{ color: scoreColor(preview.score) }}>
                        {preview.score}
                      </div>
                      <div className="text-[10px] text-q-muted font-mono mt-1">AI 评分</div>
                    </div>
                    <div className="flex-1">
                      <div className={`text-xl font-display font-bold ${preview.rating === 'BUY' ? 'text-q-green' : preview.rating === 'SELL' ? 'text-q-red' : 'text-q-amber'}`}>
                        {preview.rating === 'BUY' ? '建议买入' : preview.rating === 'SELL' ? '建议卖出' : '持有观望'}
                      </div>
                      <div className="text-xs text-q-muted mt-0.5">
                        ${ticker} · 报告包含 {reportSections.length} 个章节
                      </div>
                    </div>
                    <a href={api.getReportUrl(ticker, format)}
                      target={format === 'html' ? '_blank' : undefined}
                      download={format !== 'html' ? `qalpha_${ticker}_report.${FORMAT_OPTIONS.find(f => f.id === format)?.ext}` : undefined}
                      rel="noreferrer"
                      className="btn-primary inline-flex items-center gap-2 text-sm px-5 py-2.5 flex-shrink-0">
                      <Download size={14} />
                      下载 {FORMAT_OPTIONS.find(f => f.id === format)?.label}
                    </a>
                  </div>

                  <div className="p-4 rounded-xl border-l-2 border-q-blue bg-q-blue/5">
                    <div className="text-[10px] font-mono text-q-muted uppercase tracking-widest mb-2 flex items-center gap-1.5">
                      <Bot size={10} /> 报告摘要预览
                    </div>
                    <p className="text-xs text-q-dim leading-relaxed"
                      dangerouslySetInnerHTML={{ __html: (preview.explanation || '').replace(/\*\*(.+?)\*\*/g, '<strong style="color:#00d4ff">$1</strong>') }} />
                  </div>

                  <div className="flex gap-2 flex-wrap">
                    <span className="text-[10px] text-q-muted self-center">其他格式：</span>
                    {FORMAT_OPTIONS.filter(f => f.id !== format).map(f => (
                      <a key={f.id} href={api.getReportUrl(ticker, f.id as any)}
                        target={f.id === 'html' ? '_blank' : undefined}
                        download={f.id !== 'html' ? `qalpha_${ticker}.${f.ext}` : undefined}
                        rel="noreferrer"
                        className="text-[11px] text-q-blue hover:underline flex items-center gap-1">
                        <f.icon size={10} /> {f.label}
                      </a>
                    ))}
                  </div>
                </>
              )}
            </motion.div>
          )}
        </div>
      </Layout>
    </>
  );
}
