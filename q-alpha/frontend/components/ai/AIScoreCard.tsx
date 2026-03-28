import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { scoreColor, ratingBg } from '@/lib/utils';

interface AnalysisData {
  ticker: string;
  score: number;
  rating: string;
  explanation: string;
  risks: Array<{ type: string; message: string }>;
  sub_scores: Record<string, number>;
  indicators: {
    rsi: number;
    macd: { macd: number; signal: number; histogram: number };
    volume_score: number;
    moving_averages: { ma20?: number; ma50?: number; ma200?: number; current?: number };
  };
  signals: Record<string, string>;
  analyzed_at: string;
}

interface Props {
  data: AnalysisData;
  compact?: boolean;
}

export default function AIScoreCard({ data, compact = false }: Props) {
  const { score, rating, explanation, risks, sub_scores, indicators, signals } = data;
  const color = scoreColor(score);

  const ratingIcon = rating === 'BUY'
    ? <TrendingUp size={16} />
    : rating === 'SELL'
    ? <TrendingDown size={16} />
    : <Minus size={16} />;

  // Arc path for the score gauge
  const radius = 60;
  const strokeWidth = 8;
  const circumference = Math.PI * radius; // Half circle
  const progress = (score / 100) * circumference;

  return (
    <div className="glass-card p-5">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="text-xs font-mono text-q-muted uppercase tracking-widest mb-1">
            AI Composite Score
          </div>
          <div className="text-lg font-bold text-q-text">{data.ticker}</div>
        </div>
        <span className={`tag ${ratingBg(rating)} flex items-center gap-1 px-3 py-1.5 text-sm font-bold`}>
          {ratingIcon} {rating}
        </span>
      </div>

      {/* Gauge */}
      <div className="flex justify-center mb-4">
        <div className="relative" style={{ width: 144, height: 82 }}>
          <svg width={144} height={82} viewBox="0 0 144 82">
            {/* Background arc */}
            <path
              d="M 12 76 A 60 60 0 0 1 132 76"
              fill="none"
              stroke="#1a2a4a"
              strokeWidth={strokeWidth}
              strokeLinecap="round"
            />
            {/* Progress arc */}
            <motion.path
              d="M 12 76 A 60 60 0 0 1 132 76"
              fill="none"
              stroke={color}
              strokeWidth={strokeWidth}
              strokeLinecap="round"
              strokeDasharray={`${circumference}`}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset: circumference - progress }}
              transition={{ duration: 1.2, ease: 'easeOut', delay: 0.3 }}
              style={{ filter: `drop-shadow(0 0 6px ${color}88)` }}
            />
            {/* Score text */}
            <text x="72" y="68" textAnchor="middle" fill={color}
              style={{ fontSize: '28px', fontWeight: 800, fontFamily: 'IBM Plex Mono' }}>
              {score}
            </text>
          </svg>
          {/* Min/Max labels */}
          <div className="absolute bottom-0 left-0 text-[10px] font-mono text-q-muted">0</div>
          <div className="absolute bottom-0 right-0 text-[10px] font-mono text-q-muted">100</div>
        </div>
      </div>

      {!compact && (
        <>
          {/* Sub-scores */}
          <div className="grid grid-cols-2 gap-2 mb-4">
            {Object.entries(sub_scores).map(([key, val]) => (
              <div key={key} className="bg-q-surface rounded-lg p-2.5">
                <div className="text-[10px] text-q-muted uppercase tracking-wide mb-1">{key}</div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-q-border rounded-full overflow-hidden">
                    <motion.div
                      className="h-full rounded-full"
                      style={{ background: scoreColor(val) }}
                      initial={{ width: 0 }}
                      animate={{ width: `${val}%` }}
                      transition={{ duration: 0.8, delay: 0.1 }}
                    />
                  </div>
                  <span className="text-xs font-mono font-semibold" style={{ color: scoreColor(val) }}>{val}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Technical indicators */}
          <div className="glass-card !p-3 mb-4 space-y-2">
            <div className="text-[10px] font-mono text-q-muted uppercase tracking-widest mb-2">Technical Indicators</div>
            <div className="grid grid-cols-3 gap-2 text-center">
              <IndicatorCell label="RSI" value={indicators.rsi?.toFixed(1)} warn={indicators.rsi > 70 || indicators.rsi < 30} />
              <IndicatorCell label="MACD" value={indicators.macd?.histogram?.toFixed(3)} positive={indicators.macd?.histogram > 0} />
              <IndicatorCell label="Vol Score" value={indicators.volume_score?.toFixed(0)} />
            </div>
            {indicators.moving_averages && (
              <div className="grid grid-cols-3 gap-2 text-center pt-1 border-t border-q-border/50">
                <IndicatorCell label="MA20" value={`$${indicators.moving_averages.ma20?.toFixed(0)}`} />
                <IndicatorCell label="MA50" value={`$${indicators.moving_averages.ma50?.toFixed(0)}`} />
                <IndicatorCell label="MA200" value={`$${indicators.moving_averages.ma200?.toFixed(0)}`} />
              </div>
            )}
          </div>

          {/* Explanation */}
          <div className="mb-4 p-3 rounded-lg border-l-2 border-q-blue bg-q-blue/5">
            <div className="text-xs text-q-dim leading-relaxed"
              dangerouslySetInnerHTML={{ __html: explanation.replace(/\*\*(.+?)\*\*/g, '<strong style="color:#00d4ff">$1</strong>') }}
            />
          </div>

          {/* Risks */}
          {risks.length > 0 && (
            <div className="space-y-1.5">
              <div className="text-[10px] font-mono text-q-muted uppercase tracking-widest mb-2">Risk Flags</div>
              {risks.map((r, i) => (
                <RiskItem key={i} risk={r} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

function IndicatorCell({ label, value, warn = false, positive }: {
  label: string; value?: string; warn?: boolean; positive?: boolean;
}) {
  let color = '#e2e8f0';
  if (warn) color = '#f59e0b';
  if (positive === true) color = '#00ff88';
  if (positive === false) color = '#ff3366';

  return (
    <div className="bg-q-bg/50 rounded-lg p-1.5">
      <div className="text-[9px] text-q-muted uppercase tracking-wide">{label}</div>
      <div className="text-xs font-mono font-semibold mt-0.5" style={{ color }}>{value ?? '—'}</div>
    </div>
  );
}

function RiskItem({ risk }: { risk: { type: string; message: string } }) {
  const icons: Record<string, React.ReactNode> = {
    warning:     <AlertTriangle size={12} className="text-q-amber flex-shrink-0" />,
    opportunity: <CheckCircle size={12} className="text-q-green flex-shrink-0" />,
    info:        <Info size={12} className="text-q-blue flex-shrink-0" />,
  };
  const colors: Record<string, string> = {
    warning:     'border-q-amber/20 bg-q-amber/5',
    opportunity: 'border-q-green/20 bg-q-green/5',
    info:        'border-q-blue/20 bg-q-blue/5',
  };

  return (
    <div className={`flex items-start gap-2 px-2.5 py-2 rounded-lg border ${colors[risk.type] || 'border-q-border bg-q-surface'}`}>
      {icons[risk.type] || <Info size={12} />}
      <span className="text-[11px] text-q-dim leading-snug">{risk.message}</span>
    </div>
  );
}
