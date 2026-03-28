import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/router';
import Fuse from 'fuse.js';
import { Search, TrendingUp, X, ArrowRight } from 'lucide-react';
import { getTickerColor } from '@/lib/utils';

const STOCK_LIST = [
  { ticker: 'AAPL', name: 'Apple Inc.', sector: 'Technology' },
  { ticker: 'TSLA', name: 'Tesla, Inc.', sector: 'Automotive' },
  { ticker: 'NVDA', name: 'NVIDIA Corp', sector: 'Semiconductors' },
  { ticker: 'MSFT', name: 'Microsoft Corp', sector: 'Technology' },
  { ticker: 'GOOGL', name: 'Alphabet Inc.', sector: 'Technology' },
  { ticker: 'AMZN', name: 'Amazon.com Inc.', sector: 'E-Commerce' },
  { ticker: 'META', name: 'Meta Platforms', sector: 'Social Media' },
  { ticker: 'AMD',  name: 'Advanced Micro Devices', sector: 'Semiconductors' },
  { ticker: 'PLTR', name: 'Palantir Technologies', sector: 'Software' },
  { ticker: 'COIN', name: 'Coinbase Global', sector: 'Fintech' },
  { ticker: 'NFLX', name: 'Netflix Inc.', sector: 'Streaming' },
  { ticker: 'UBER', name: 'Uber Technologies', sector: 'Transport' },
  { ticker: 'SPOT', name: 'Spotify Technology', sector: 'Music' },
  { ticker: 'PYPL', name: 'PayPal Holdings', sector: 'Fintech' },
  { ticker: 'SQ',   name: 'Block Inc.', sector: 'Fintech' },
  { ticker: 'SHOP', name: 'Shopify Inc.', sector: 'E-Commerce' },
  { ticker: 'SNOW', name: 'Snowflake Inc.', sector: 'Cloud' },
  { ticker: 'PANW', name: 'Palo Alto Networks', sector: 'Cybersecurity' },
  { ticker: 'CRWD', name: 'CrowdStrike Holdings', sector: 'Cybersecurity' },
  { ticker: 'DDOG', name: 'Datadog Inc.', sector: 'Cloud' },
  { ticker: 'NET',  name: 'Cloudflare Inc.', sector: 'Cloud' },
  { ticker: 'JPM',  name: 'JPMorgan Chase', sector: 'Banking' },
  { ticker: 'GS',   name: 'Goldman Sachs', sector: 'Banking' },
  { ticker: 'BAC',  name: 'Bank of America', sector: 'Banking' },
  { ticker: 'V',    name: 'Visa Inc.', sector: 'Payments' },
  { ticker: 'MA',   name: 'Mastercard Inc.', sector: 'Payments' },
];

const fuse = new Fuse(STOCK_LIST, {
  keys: ['ticker', 'name', 'sector'],
  threshold: 0.35,
  includeScore: true,
});

interface Props {
  placeholder?: string;
  onSelect?: (ticker: string) => void;
  className?: string;
  autoFocus?: boolean;
}

export default function StockSearch({ placeholder = 'Search stocks, tickers...', onSelect, className = '', autoFocus }: Props) {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<typeof STOCK_LIST>([]);
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!query.trim()) { setResults([]); return; }
    const res = fuse.search(query).slice(0, 8).map(r => r.item);
    setResults(res);
    setSelected(0);
  }, [query]);

  useEffect(() => {
    if (autoFocus) inputRef.current?.focus();
  }, [autoFocus]);

  const handleSelect = useCallback((ticker: string) => {
    setQuery('');
    setOpen(false);
    if (onSelect) onSelect(ticker);
    else router.push(`/stock/${ticker}`);
  }, [onSelect, router]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!open || !results.length) return;
    if (e.key === 'ArrowDown') { e.preventDefault(); setSelected(s => Math.min(s + 1, results.length - 1)); }
    if (e.key === 'ArrowUp')   { e.preventDefault(); setSelected(s => Math.max(s - 1, 0)); }
    if (e.key === 'Enter')     { e.preventDefault(); handleSelect(results[selected].ticker); }
    if (e.key === 'Escape')    { setOpen(false); setQuery(''); }
  };

  return (
    <div className={`relative ${className}`}>
      {/* Input */}
      <div className={`flex items-center gap-2 px-3 py-2.5 rounded-xl bg-q-card border transition-all duration-200 ${
        open ? 'border-q-blue/60 shadow-glow-blue' : 'border-q-border hover:border-q-border/80'
      }`}>
        <Search size={15} className={`flex-shrink-0 transition-colors ${open ? 'text-q-blue' : 'text-q-muted'}`} />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={e => { setQuery(e.target.value); setOpen(true); }}
          onFocus={() => setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 150)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="flex-1 bg-transparent text-sm text-q-text placeholder:text-q-muted/50 outline-none min-w-0 font-mono"
        />
        {query && (
          <button onClick={() => { setQuery(''); setOpen(false); }} className="text-q-muted hover:text-q-text transition-colors">
            <X size={13} />
          </button>
        )}
        <span className="hidden sm:flex items-center gap-1 px-1.5 py-0.5 rounded border border-q-border text-[10px] text-q-muted font-mono flex-shrink-0">
          ⌘K
        </span>
      </div>

      {/* Dropdown */}
      <AnimatePresence>
        {open && results.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.97 }}
            transition={{ duration: 0.15 }}
            className="absolute top-full left-0 right-0 mt-2 z-50 glass-card overflow-hidden shadow-modal"
          >
            <div className="py-1">
              {results.map((item, idx) => {
                const color = getTickerColor(item.ticker);
                return (
                  <div
                    key={item.ticker}
                    onMouseEnter={() => setSelected(idx)}
                    onMouseDown={() => handleSelect(item.ticker)}
                    className={`flex items-center gap-3 px-4 py-2.5 cursor-pointer transition-colors ${
                      selected === idx ? 'bg-q-blue/10' : 'hover:bg-q-border/20'
                    }`}
                  >
                    {/* Ticker badge */}
                    <div
                      className="w-9 h-9 rounded-lg flex items-center justify-center text-xs font-bold font-mono flex-shrink-0"
                      style={{ background: `${color}22`, color, border: `1px solid ${color}44` }}
                    >
                      {item.ticker.slice(0, 2)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-semibold text-sm text-q-text">{item.ticker}</span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-q-border/60 text-q-muted">{item.sector}</span>
                      </div>
                      <div className="text-xs text-q-muted truncate">{item.name}</div>
                    </div>
                    {selected === idx && <ArrowRight size={13} className="text-q-blue flex-shrink-0" />}
                  </div>
                );
              })}
            </div>
            <div className="border-t border-q-border px-4 py-2 bg-q-surface/50">
              <div className="text-[10px] text-q-muted flex items-center gap-3">
                <span>↑↓ navigate</span>
                <span>↵ select</span>
                <span>esc close</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
