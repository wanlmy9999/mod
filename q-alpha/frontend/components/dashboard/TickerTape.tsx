import React, { useEffect, useState } from 'react';
import api from '@/lib/api';

interface TickerItem { ticker: string; price: number; change_pct: number; name?: string; }

const FALLBACK: TickerItem[] = [
  { ticker: 'AAPL', price: 189.50, change_pct: 1.24, name: '苹果公司' },
  { ticker: 'TSLA', price: 248.30, change_pct: -2.15, name: '特斯拉' },
  { ticker: 'NVDA', price: 875.40, change_pct: 3.67, name: '英伟达' },
  { ticker: 'MSFT', price: 415.20, change_pct: 0.89, name: '微软' },
  { ticker: 'GOOGL', price: 174.80, change_pct: -0.43, name: '谷歌母公司' },
  { ticker: 'AMZN', price: 202.10, change_pct: 1.56, name: '亚马逊' },
  { ticker: 'META', price: 521.60, change_pct: 2.33, name: 'Meta平台' },
  { ticker: 'AMD', price: 162.30, change_pct: -1.12, name: 'AMD半导体' },
];

export default function TickerTape() {
  const [items, setItems] = useState<TickerItem[]>(FALLBACK);
  useEffect(() => {
    const load = async () => {
      try { const res = await api.getPopular(); if (res?.data?.length) setItems(res.data); } catch {}
    };
    load();
    const id = setInterval(load, 15000);
    return () => clearInterval(id);
  }, []);

  const doubled = [...items, ...items];
  return (
    <div className="flex items-center overflow-hidden border-b border-q-border bg-q-surface/60 backdrop-blur-sm h-9 relative">
      <div className="absolute left-0 top-0 bottom-0 w-12 bg-gradient-to-r from-q-surface to-transparent z-10 pointer-events-none" />
      <div className="absolute right-0 top-0 bottom-0 w-12 bg-gradient-to-l from-q-surface to-transparent z-10 pointer-events-none" />
      <div className="absolute left-2 z-20 text-[9px] font-mono text-q-muted/50 tracking-widest uppercase hidden sm:block">实时</div>
      <div className="flex">
        <div className="ticker-tape-track">
          {doubled.map((item, idx) => {
            const pos = item.change_pct >= 0;
            return (
              <div key={`${item.ticker}-${idx}`} className="flex items-center gap-2 px-5 border-r border-q-border/40 h-9 hover:bg-q-border/20 transition-colors cursor-default">
                <span className="font-mono font-semibold text-xs text-white tracking-wider">{item.ticker}</span>
                <span className="font-mono text-xs text-q-muted">${item.price?.toFixed(2)}</span>
                <span className={`font-mono text-[10px] font-medium ${pos ? 'text-q-green' : 'text-q-red'}`}>
                  {pos ? '▲' : '▼'} {Math.abs(item.change_pct).toFixed(2)}%
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
