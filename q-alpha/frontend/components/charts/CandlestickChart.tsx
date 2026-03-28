import React, { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { TIMEFRAMES } from '@/lib/utils';

interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface Props {
  candles: Candle[];
  ticker: string;
  timeframe: string;
  onTimeframeChange?: (tf: string) => void;
  height?: number;
}

export default function CandlestickChart({ candles, ticker, timeframe, onTimeframeChange, height = 420 }: Props) {
  const option = useMemo(() => {
    if (!candles?.length) return {};

    const dates = candles.map(c => new Date(c.time).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    const ohlc = candles.map(c => [c.open, c.close, c.low, c.high]);
    const volumes = candles.map(c => c.volume);
    const closes = candles.map(c => c.close);

    // MA calculations
    const ma = (arr: number[], period: number) =>
      arr.map((_, i) => i < period - 1 ? null : arr.slice(i - period + 1, i + 1).reduce((a, b) => a + b) / period);

    const ma20 = ma(closes, 20);
    const ma50 = ma(closes, 50);

    return {
      backgroundColor: 'transparent',
      animation: true,
      animationDuration: 600,
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
        backgroundColor: '#0d1526',
        borderColor: '#1a2a4a',
        textStyle: { color: '#e2e8f0', fontSize: 12, fontFamily: 'IBM Plex Mono' },
        formatter: (params: any[]) => {
          const c = params.find(p => p.seriesName === 'OHLC');
          if (!c) return '';
          const [open, close, low, high] = c.data;
          const vol = volumes[c.dataIndex];
          const isGreen = close >= open;
          const color = isGreen ? '#00ff88' : '#ff3366';
          return `
            <div style="min-width:160px">
              <div style="color:#8892a4;margin-bottom:6px;font-size:11px">${dates[c.dataIndex]}</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:12px">
                <span style="color:#8892a4">Open</span><span style="color:${color}">$${open.toFixed(2)}</span>
                <span style="color:#8892a4">High</span><span style="color:${color}">$${high.toFixed(2)}</span>
                <span style="color:#8892a4">Low</span><span style="color:${color}">$${low.toFixed(2)}</span>
                <span style="color:#8892a4">Close</span><span style="color:${color}">$${close.toFixed(2)}</span>
                <span style="color:#8892a4">Vol</span><span style="color:#e2e8f0">${(vol / 1e6).toFixed(1)}M</span>
              </div>
            </div>
          `;
        },
      },
      legend: {
        top: 4,
        right: 8,
        textStyle: { color: '#8892a4', fontSize: 11 },
        inactiveColor: '#3a4a5a',
        data: ['OHLC', 'MA20', 'MA50'],
      },
      axisPointer: {
        link: [{ xAxisIndex: 'all' }],
        label: { backgroundColor: '#0d1526', color: '#e2e8f0', fontSize: 11 },
      },
      dataZoom: [
        {
          type: 'inside', xAxisIndex: [0, 1], start: Math.max(0, 100 - (60 / candles.length) * 100), end: 100,
        },
        {
          type: 'slider', xAxisIndex: [0, 1], bottom: 4, height: 24, start: 70, end: 100,
          backgroundColor: '#0a0f1e',
          fillerColor: 'rgba(0,212,255,0.08)',
          borderColor: '#1a2a4a',
          handleStyle: { color: '#00d4ff' },
          textStyle: { color: '#8892a4', fontSize: 10 },
        },
      ],
      grid: [
        { left: 56, right: 16, top: 30, height: '58%' },
        { left: 56, right: 16, top: '75%', height: '15%' },
      ],
      xAxis: [
        {
          type: 'category', data: dates, gridIndex: 0, scale: true,
          boundaryGap: true, axisLine: { lineStyle: { color: '#1a2a4a' } },
          axisTick: { show: false }, axisLabel: { show: false },
          splitLine: { lineStyle: { color: '#1a2a4a33' } },
        },
        {
          type: 'category', data: dates, gridIndex: 1, scale: true,
          boundaryGap: true, axisLine: { lineStyle: { color: '#1a2a4a' } },
          axisTick: { show: false },
          axisLabel: { color: '#8892a4', fontSize: 10, fontFamily: 'IBM Plex Mono' },
          splitLine: { show: false },
        },
      ],
      yAxis: [
        {
          scale: true, gridIndex: 0, splitNumber: 6,
          axisLine: { show: false }, axisTick: { show: false },
          axisLabel: {
            color: '#8892a4', fontSize: 10, fontFamily: 'IBM Plex Mono',
            formatter: (v: number) => `$${v.toFixed(0)}`,
          },
          splitLine: { lineStyle: { color: '#1a2a4a44', type: 'dashed' } },
        },
        {
          scale: true, gridIndex: 1, splitNumber: 2,
          axisLine: { show: false }, axisTick: { show: false },
          axisLabel: {
            color: '#8892a4', fontSize: 9, fontFamily: 'IBM Plex Mono',
            formatter: (v: number) => `${(v / 1e6).toFixed(0)}M`,
          },
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: 'OHLC', type: 'candlestick', xAxisIndex: 0, yAxisIndex: 0, data: ohlc,
          itemStyle: {
            color: '#00ff88', color0: '#ff3366',
            borderColor: '#00ff88', borderColor0: '#ff3366', borderWidth: 1,
          },
        },
        {
          name: 'MA20', type: 'line', data: ma20, xAxisIndex: 0, yAxisIndex: 0,
          smooth: true, showSymbol: false,
          lineStyle: { color: '#00d4ff', width: 1.5, opacity: 0.8 },
        },
        {
          name: 'MA50', type: 'line', data: ma50, xAxisIndex: 0, yAxisIndex: 0,
          smooth: true, showSymbol: false,
          lineStyle: { color: '#a855f7', width: 1.5, opacity: 0.8 },
        },
        {
          name: 'Volume', type: 'bar', xAxisIndex: 1, yAxisIndex: 1,
          data: volumes.map((v, i) => ({
            value: v,
            itemStyle: {
              color: candles[i].close >= candles[i].open
                ? 'rgba(0,255,136,0.5)'
                : 'rgba(255,51,102,0.5)',
            },
          })),
        },
      ],
    };
  }, [candles]);

  return (
    <div>
      {/* Timeframe selector */}
      <div className="flex items-center gap-1 mb-3">
        {TIMEFRAMES.map(tf => (
          <button
            key={tf}
            onClick={() => onTimeframeChange?.(tf)}
            className={`px-2.5 py-1 rounded text-xs font-mono font-medium transition-all ${
              timeframe === tf
                ? 'bg-q-blue/20 text-q-blue border border-q-blue/40'
                : 'text-q-muted hover:text-q-text hover:bg-q-border/40'
            }`}
          >
            {tf.toUpperCase()}
          </button>
        ))}
      </div>

      {candles?.length ? (
        <ReactECharts
          option={option}
          style={{ height: `${height}px`, width: '100%' }}
          notMerge={true}
          lazyUpdate={false}
          theme="dark"
        />
      ) : (
        <div className="flex items-center justify-center h-64 text-q-muted">
          <div className="text-center">
            <div className="text-2xl mb-2">📊</div>
            <div className="text-sm">Loading chart data...</div>
          </div>
        </div>
      )}
    </div>
  );
}
