// Q-Alpha 工具函数库

export function fmt(n: number | null | undefined, decimals = 2): string {
  if (n == null || isNaN(n)) return '—';
  return n.toLocaleString('zh-CN', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

export function fmtCompact(n: number | null | undefined): string {
  if (n == null || isNaN(n)) return '—';
  if (Math.abs(n) >= 1e12) return `$${(n / 1e12).toFixed(2)}万亿`;
  if (Math.abs(n) >= 1e8)  return `$${(n / 1e8).toFixed(2)}亿`;
  if (Math.abs(n) >= 1e6)  return `$${(n / 1e6).toFixed(2)}百万`;
  if (Math.abs(n) >= 1e3)  return `$${(n / 1e3).toFixed(1)}千`;
  return `$${n.toFixed(2)}`;
}

export function fmtPct(n: number | null | undefined): string {
  if (n == null || isNaN(n)) return '—';
  return `${n >= 0 ? '+' : ''}${n.toFixed(2)}%`;
}

export function changeColor(n: number | null | undefined): string {
  if (n == null) return 'text-q-muted';
  if (n > 0) return 'text-q-green';
  if (n < 0) return 'text-q-red';
  return 'text-q-muted';
}

export function ratingLabel(rating: string): string {
  const r = (rating || '').toUpperCase();
  if (r === 'BUY' || r === 'STRONG BUY') return '买入';
  if (r === 'SELL' || r === 'STRONG SELL') return '卖出';
  return '持有';
}

export function ratingColor(rating: string): string {
  const r = (rating || '').toUpperCase();
  if (r === 'BUY' || r === 'STRONG BUY') return 'text-q-green';
  if (r === 'SELL' || r === 'STRONG SELL') return 'text-q-red';
  return 'text-q-amber';
}

export function ratingBg(rating: string): string {
  const r = (rating || '').toUpperCase();
  if (r === 'BUY' || r === 'STRONG BUY') return 'tag-buy';
  if (r === 'SELL' || r === 'STRONG SELL') return 'tag-sell';
  return 'tag-hold';
}

export function partyColor(party: string): string {
  if (!party) return 'text-q-muted';
  return party.toLowerCase().includes('dem') ? 'text-blue-400' : 'text-red-400';
}

export function partyBg(party: string): string {
  if (!party) return '';
  return party.toLowerCase().includes('dem') ? 'tag-dem' : 'tag-rep';
}

export function partyLabel(party: string): string {
  if (!party) return '未知';
  if (party.toLowerCase().includes('dem')) return '民主党';
  if (party.toLowerCase().includes('rep')) return '共和党';
  return party;
}

export function chamberLabel(chamber: string): string {
  if (!chamber) return '';
  if (chamber.toLowerCase() === 'house') return '众议院';
  if (chamber.toLowerCase() === 'senate') return '参议院';
  return chamber;
}

export function scoreColor(score: number): string {
  if (score >= 72) return '#00ff88';
  if (score >= 50) return '#f59e0b';
  return '#ff3366';
}

export function scoreLabel(score: number): string {
  if (score >= 80) return '强烈买入';
  if (score >= 65) return '建议买入';
  if (score >= 50) return '持有观望';
  if (score >= 35) return '考虑减持';
  return '建议卖出';
}

export function relativeTime(dateStr: string): string {
  const now = new Date();
  const d = new Date(dateStr);
  const diff = Math.floor((now.getTime() - d.getTime()) / 1000);
  if (diff < 60) return `${diff}秒前`;
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`;
  return `${Math.floor(diff / 86400)}天前`;
}

export function getTickerColor(ticker: string): string {
  const colors = ['#00d4ff', '#00ff88', '#a855f7', '#f59e0b', '#ff6b35', '#06b6d4'];
  let hash = 0;
  for (let i = 0; i < ticker.length; i++) hash = ticker.charCodeAt(i) + ((hash << 5) - hash);
  return colors[Math.abs(hash) % colors.length];
}

export const POPULAR_TICKERS = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'AMD', 'PLTR', 'COIN'];
export const TIMEFRAMES = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '5y'];
export const TIMEFRAME_LABELS: Record<string, string> = {
  '1d': '1日', '5d': '5日', '1mo': '1月', '3mo': '3月', '6mo': '6月', '1y': '1年', '5y': '5年'
};
