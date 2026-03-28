import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { Search as SearchIcon, TrendingUp, Bot, ArrowRight, Zap } from 'lucide-react';
import Fuse from 'fuse.js';
import { useRouter } from 'next/router';
import Layout from '@/components/layout/Layout';
import api from '@/lib/api';
import { getTickerColor, fmtPct } from '@/lib/utils';

const STOCKS = [
  { ticker: 'AAPL', name: 'Apple Inc.', sector: '科技', type: 'stock' },
  { ticker: 'TSLA', name: 'Tesla, Inc.', sector: '新能源汽车', type: 'stock' },
  { ticker: 'NVDA', name: 'NVIDIA Corp', sector: '半导体', type: 'stock' },
  { ticker: 'MSFT', name: 'Microsoft Corp', sector: '科技', type: 'stock' },
  { ticker: 'GOOGL', name: 'Alphabet Inc.', sector: '科技', type: 'stock' },
  { ticker: 'AMZN', name: 'Amazon.com Inc.', sector: '电商/云计算', type: 'stock' },
  { ticker: 'META', name: 'Meta Platforms', sector: '社交媒体', type: 'stock' },
  { ticker: 'AMD',  name: 'Advanced Micro Devices', sector: '半导体', type: 'stock' },
  { ticker: 'PLTR', name: 'Palantir Technologies', sector: '软件/AI', type: 'stock' },
  { ticker: 'COIN', name: 'Coinbase Global', sector: '金融科技', type: 'stock' },
  { ticker: 'NFLX', name: 'Netflix Inc.', sector: '流媒体', type: 'stock' },
  { ticker: 'UBER', name: 'Uber Technologies', sector: '出行', type: 'stock' },
  { ticker: 'SNOW', name: 'Snowflake Inc.', sector: '云数据', type: 'stock' },
  { ticker: 'CRWD', name: 'CrowdStrike Holdings', sector: '网络安全', type: 'stock' },
  { ticker: 'PANW', name: 'Palo Alto Networks', sector: '网络安全', type: 'stock' },
  { ticker: 'JPM',  name: 'JPMorgan Chase', sector: '银行', type: 'stock' },
  { ticker: 'GS',   name: 'Goldman Sachs', sector: '投行', type: 'stock' },
  { ticker: 'V',    name: 'Visa Inc.', sector: '支付', type: 'stock' },
  { ticker: 'MA',   name: 'Mastercard Inc.', sector: '支付', type: 'stock' },
  { ticker: 'SHOP', name: 'Shopify Inc.', sector: '电商', type: 'stock' },
];

const fuse = new Fuse(STOCKS, { keys: ['ticker', 'name', 'sector'], threshold: 0.35, includeScore: true });
const TRENDING = ['NVDA', 'TSLA', 'AAPL', 'AMD', 'META'];

export default function SearchPage() {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<typeof STOCKS>(STOCKS.slice(0, 12));
  const [prices, setPrices] = useState<Record<string, any>>({});
  const [filter, setFilter] = useState<'all' | 'stock'>('all');
  const [aiMode, setAiMode] = useState(false);

  useEffect(() => {
    if (!query.trim()) { setResults(STOCKS.slice(0, 16)); return; }
    setResults(fuse.search(query).map(r => r.item));
  }, [query]);

  useEffect(() => {
    results.slice(0, 8).forEach(r => {
      if (!prices[r.ticker]) {
        api.getStockPrice(r.ticker).then(res => {
          if (res?.data) setPrices(prev => ({ ...prev, [r.ticker]: res.data }));
        }).catch(() => {});
      }
    });
  }, [results]);

  return (
    <>
      <Head><title>智能搜索 — Q-Alpha</title></Head>
      <Layout title="智能搜索">
        <div className="p-4 md:p-6 max-w-4xl mx-auto space-y-5">

          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-2xl font-display font-bold text-white mb-4">
              <span className="text-neon-blue">智能</span> 搜索
            </h1>
            <div className="relative">
              <SearchIcon size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-q-muted" />
              <input type="text" value={query} onChange={e => setQuery(e.target.value)}
                placeholder="搜索股票代码、公司名称、行业…"
                className="w-full pl-11 pr-12 py-4 bg-q-card border border-q-border rounded-xl text-q-text placeholder:text-q-muted/50 outline-none font-mono text-base focus:border-q-blue/60 focus:shadow-glow-blue transition-all"
                autoFocus />
              {query && <button onClick={() => setQuery('')} className="absolute right-4 top-1/2 -translate-y-1/2 text-q-muted hover:text-q-text transition-colors">✕</button>}
            </div>
          </motion.div>

          <div className="flex items-center gap-2 flex-wrap">
            <div className="text-[10px] font-mono text-q-muted uppercase tracking-widest flex items-center gap-2 mr-2">
              <TrendingUp size={11} /> 热门搜索
            </div>
            {TRENDING.map(t => (
              <button key={t} onClick={() => setQuery(t)}
                className="px-3 py-1.5 rounded-lg bg-q-card border border-q-border text-xs font-mono text-q-blue hover:glow-blue transition-all">
                {t}
              </button>
            ))}
            <div className="flex-1" />
            <button onClick={() => setAiMode(!aiMode)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${aiMode ? 'bg-q-purple/20 text-q-purple border border-q-purple/30' : 'text-q-muted bg-q-card border border-q-border'}`}>
              <Zap size={12} /> AI 快速分析
            </button>
          </div>

          <AnimatePresence>
            <motion.div className="grid grid-cols-1 sm:grid-cols-2 gap-3" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              {results.map((item, i) => {
                const price = prices[item.ticker];
                const color = getTickerColor(item.ticker);
                return (
                  <motion.div key={item.ticker} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}>
                    <Link href={`/stock/${item.ticker}`}>
                      <div className="glass-card p-4 cursor-pointer hover:scale-[1.01] hover:glow-blue transition-all group">
                        <div className="flex items-start gap-3">
                          <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xs font-bold font-mono flex-shrink-0"
                            style={{ background: `${color}22`, color, border: `1px solid ${color}44` }}>
                            {item.ticker.slice(0, 2)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="font-mono font-bold text-sm text-q-text">${item.ticker}</span>
                              <span className="text-[10px] px-1.5 py-0.5 rounded bg-q-border/60 text-q-muted">{item.sector}</span>
                            </div>
                            <div className="text-xs text-q-muted mt-0.5 truncate">{item.name}</div>
                          </div>
                          {price && (
                            <div className="text-right flex-shrink-0">
                              <div className="font-mono font-semibold text-sm text-q-text">${price.price?.toFixed(2)}</div>
                              <div className={`font-mono text-xs ${price.change_pct >= 0 ? 'text-q-green' : 'text-q-red'}`}>{fmtPct(price.change_pct)}</div>
                            </div>
                          )}
                          {aiMode && (
                            <button onClick={e => { e.preventDefault(); router.push(`/ai-analysis?ticker=${item.ticker}`); }}
                              className="flex-shrink-0 p-1.5 rounded-lg bg-q-purple/20 text-q-purple border border-q-purple/30 hover:bg-q-purple/30 transition-colors" title="AI 分析">
                              <Bot size={12} />
                            </button>
                          )}
                          <ArrowRight size={13} className="text-q-muted/30 group-hover:text-q-blue transition-colors flex-shrink-0 mt-1" />
                        </div>
                      </div>
                    </Link>
                  </motion.div>
                );
              })}
            </motion.div>
          </AnimatePresence>

          {results.length === 0 && query && (
            <div className="text-center py-12 text-q-muted">
              <SearchIcon size={32} className="mx-auto mb-3 opacity-30" />
              <div className="text-sm">未找到 "{query}" 相关结果</div>
              <div className="text-xs mt-1">请尝试输入股票代码，如 AAPL、NVDA</div>
            </div>
          )}
        </div>
      </Layout>
    </>
  );
}
