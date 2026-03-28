import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { motion } from 'framer-motion';
import { BarChart2, TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import Layout from '@/components/layout/Layout';
import api from '@/lib/api';
import { POPULAR_TICKERS } from '@/lib/utils';

export default function WhalesPage() {
  const [ticker, setTicker] = useState('AAPL');
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const load = async (t: string) => {
    setLoading(true);
    try { const res = await api.getWhales(t.toUpperCase()); setData(res?.data || []); }
    catch {} finally { setLoading(false); }
  };

  useEffect(() => { load(ticker); }, []);

  const accumulating = data.filter(d => d.change?.startsWith('+')).length;
  const distributing = data.length - accumulating;

  return (
    <>
      <Head><title>大资金动向 — Q-Alpha</title></Head>
      <Layout title="大资金动向">
        <div className="p-4 md:p-6 space-y-5 max-w-screen-xl mx-auto">
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-2xl font-display font-bold text-white">
              大资金 <span className="text-q-blue">动向追踪</span>
            </h1>
            <p className="text-q-muted text-sm mt-1">
              基于 SEC 13F/13D 文件追踪机构投资者持仓变动，识别主力资金的建仓与减仓行为 · 每小时更新
            </p>
          </motion.div>

          <div className="grid grid-cols-3 gap-3">
            {[
              { label: '追踪机构数量', value: data.length, color: 'text-q-blue', icon: BarChart2 },
              { label: '加仓机构', value: accumulating, color: 'text-q-green', icon: TrendingUp },
              { label: '减仓机构', value: distributing, color: 'text-q-red', icon: TrendingDown },
            ].map((s, i) => (
              <div key={i} className="glass-card p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] text-q-muted">{s.label}</span>
                  <s.icon size={13} className={s.color} />
                </div>
                <div className={`text-2xl font-display font-bold ${s.color}`}>{s.value}</div>
              </div>
            ))}
          </div>

          <div className="flex gap-1.5 flex-wrap">
            {POPULAR_TICKERS.slice(0, 8).map(t => (
              <button key={t} onClick={() => { setTicker(t); load(t); }}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all ${ticker === t ? 'bg-q-blue/20 text-q-blue border border-q-blue/30' : 'bg-q-card border border-q-border text-q-muted hover:text-q-text'}`}>
                {t}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {loading ? [...Array(6)].map((_, i) => (
              <div key={i} className="glass-card p-4 h-28 animate-pulse bg-q-border/20" />
            )) : data.map((whale, i) => {
              const isPos = whale.change?.startsWith('+');
              return (
                <motion.div key={i} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}
                  className={`glass-card p-4 transition-all hover:scale-[1.02] ${isPos ? 'hover:glow-green' : 'hover:glow-red'}`}>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${isPos ? 'bg-q-green/10' : 'bg-q-red/10'}`}>
                        <BarChart2 size={14} className={isPos ? 'text-q-green' : 'text-q-red'} />
                      </div>
                      <div>
                        <div className="text-xs font-semibold text-q-text leading-tight">{whale.fund}</div>
                        <div className="text-[10px] text-q-muted font-mono">{whale.filing_date}</div>
                      </div>
                    </div>
                    <div className={`flex items-center gap-1 text-xs font-mono font-bold ${isPos ? 'text-q-green' : 'text-q-red'}`}>
                      {isPos ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                      {whale.change}
                    </div>
                  </div>
                  <div className="flex items-end justify-between">
                    <div>
                      <div className="text-[10px] text-q-muted">持股数量</div>
                      <div className="font-mono text-sm font-semibold text-q-text">{whale.shares?.toLocaleString()}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] text-q-muted">市值</div>
                      <div className="font-mono text-sm font-bold text-q-blue">{whale.value}</div>
                    </div>
                  </div>
                  <div className="mt-2 pt-2 border-t border-q-border/30">
                    <span className={`text-[10px] font-semibold ${isPos ? 'text-q-green' : 'text-q-red'}`}>
                      {isPos ? '▲ 主力加仓' : '▼ 主力减仓'}
                    </span>
                    <span className="text-[10px] text-q-muted ml-2">最新13F披露</span>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </Layout>
    </>
  );
}
