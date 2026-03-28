import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { motion, AnimatePresence } from 'framer-motion';
import { LayoutDashboard, TrendingUp, Search, Bot, Database, BarChart2, Users, Globe, FileText, ChevronRight, Bell, Settings, Menu, X, Zap, Activity, ExternalLink } from 'lucide-react';

const NAV_ITEMS = [
  { href: '/',                 icon: LayoutDashboard, label: '数据仪表盘',   sub: 'Dashboard',        group: 'main' },
  { href: '/search',           icon: Search,          label: '智能搜索',     sub: 'Smart Search',     group: 'main' },
  { href: '/ai-analysis',      icon: Bot,             label: 'AI 分析引擎',  sub: 'AI Analysis',      group: 'main', badge: 'AI' },
  { href: '/data',             icon: Database,        label: '数据聚合中心', sub: 'Data Hub',         group: 'main' },
  { href: '/congress-trading', icon: Users,           label: '国会股票交易', sub: 'Congress Trading', group: 'gov' },
  { href: '/politicians',      icon: Globe,           label: '政治人物画像', sub: 'Politicians',      group: 'gov' },
  { href: '/insider',          icon: TrendingUp,      label: '内幕交易监控', sub: 'Insider Trading',  group: 'finance' },
  { href: '/whales',           icon: BarChart2,       label: '大资金动向',   sub: 'Whale Moves',      group: 'finance' },
  { href: '/reports',          icon: FileText,        label: '研究报告下载', sub: 'Reports',          group: 'tools' },
];

const GROUP_LABELS: Record<string, string> = {
  main:    '核心功能',
  gov:     '政治与政府',
  finance: '金融监控',
  tools:   '工具',
};

const FOOTER_APIS = [
  { name: 'Yahoo Finance', url: 'https://finance.yahoo.com',          tag: '股票行情 · K线 · ETF · 拆股数据',      free: true },
  { name: 'Finnhub',       url: 'https://finnhub.io',                 tag: '实时报价 · 财务指标 · 分析师评级',       free: true },
  { name: 'SEC EDGAR',     url: 'https://www.sec.gov/edgar',          tag: '内幕交易 · 机构持仓 · 风险因素',        free: true },
  { name: 'OpenSecrets',   url: 'https://www.opensecrets.org',        tag: '政治捐款 · 游说支出 · 选举筹款',        free: false },
  { name: 'USAspending',   url: 'https://www.usaspending.gov',        tag: '政府合同 · 财政支出',                   free: true },
  { name: 'House Stock Watcher', url: 'https://housestockwatcher.com',tag: '众议院股票披露 · STOCK法案',            free: true },
  { name: 'Senate Stock Watcher',url: 'https://senatestockwatcher.com',tag:'参议院股票披露',                       free: true },
  { name: 'Reddit API',    url: 'https://www.reddit.com/dev/api',     tag: '社区情绪 · WSB讨论热度',               free: true },
  { name: 'Google Trends', url: 'https://trends.google.com',          tag: '搜索热度 · 消费兴趣趋势',              free: true },
  { name: 'USPTO',         url: 'https://www.uspto.gov',              tag: '专利数据库 · 知识产权',                free: true },
  { name: 'Alpha Vantage', url: 'https://www.alphavantage.co',        tag: '技术指标 · 基本面数据',                free: true },
  { name: 'App Store / Google Play', url: 'https://developer.apple.com', tag: '应用评分 · 下载量趋势',            free: false },
];

interface LayoutProps { children: React.ReactNode; title?: string; }

export default function Layout({ children, title }: LayoutProps) {
  const router = useRouter();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [time, setTime] = useState('');

  useEffect(() => { setMobileOpen(false); }, [router.pathname]);
  useEffect(() => {
    const update = () => setTime(new Date().toLocaleTimeString('zh-CN', { hour12: false }));
    update();
    const id = setInterval(update, 1000);
    return () => clearInterval(id);
  }, []);

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-3 px-4 py-5 border-b border-q-border">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-q-blue to-q-green flex items-center justify-center flex-shrink-0">
          <Zap size={16} className="text-q-bg" />
        </div>
        {sidebarOpen && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="min-w-0">
            <div className="font-display font-bold text-lg tracking-wider text-white">Q<span className="text-q-blue">-Alpha</span></div>
            <div className="text-[10px] text-q-muted tracking-widest">量化智能平台</div>
          </motion.div>
        )}
      </div>
      <nav className="flex-1 overflow-y-auto py-3 px-2">
        {Object.keys(GROUP_LABELS).map(group => {
          const items = NAV_ITEMS.filter(i => i.group === group);
          return (
            <div key={group} className="mb-4">
              {sidebarOpen && <div className="px-3 py-1.5 text-[10px] font-mono font-semibold text-q-muted/50 tracking-widest uppercase">{GROUP_LABELS[group]}</div>}
              {items.map(item => {
                const active = router.pathname === item.href;
                return (
                  <Link key={item.href} href={item.href}>
                    <div className={`relative flex items-center gap-3 px-3 py-2.5 rounded-lg mb-0.5 cursor-pointer transition-all duration-200 group ${active ? 'bg-q-blue/10 text-q-blue border border-q-blue/20' : 'text-q-muted hover:text-q-text hover:bg-q-border/30'}`}>
                      {active && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 bg-q-blue rounded-full" />}
                      <item.icon size={17} className="flex-shrink-0" />
                      {sidebarOpen && (
                        <>
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium truncate">{item.label}</div>
                            <div className="text-[9px] text-q-muted/60 font-mono truncate">{item.sub}</div>
                          </div>
                          {item.badge && <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-q-blue/20 text-q-blue border border-q-blue/30">{item.badge}</span>}
                        </>
                      )}
                      {!sidebarOpen && (
                        <div className="absolute left-full ml-3 px-2 py-1 bg-q-card border border-q-border rounded text-xs text-q-text opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 transition-opacity">{item.label}</div>
                      )}
                    </div>
                  </Link>
                );
              })}
            </div>
          );
        })}
      </nav>
      <div className="border-t border-q-border p-3">
        <div className={`flex items-center gap-2 p-2 rounded-lg ${sidebarOpen ? '' : 'justify-center'}`}>
          <div className="w-6 h-6 rounded-full bg-gradient-to-br from-q-blue to-q-purple flex items-center justify-center flex-shrink-0">
            <Activity size={11} className="text-white" />
          </div>
          {sidebarOpen && (
            <div className="min-w-0">
              <div className="text-xs font-medium text-q-text">系统运行正常</div>
              <div className="text-[10px] text-q-green">● 全部数据源在线</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex flex-col h-screen bg-q-bg overflow-hidden">
      <div className="flex flex-1 min-h-0">
        {/* Desktop Sidebar */}
        <motion.aside initial={false} animate={{ width: sidebarOpen ? 220 : 60 }} transition={{ duration: 0.25, ease: 'easeInOut' }}
          className="hidden md:flex flex-col bg-q-surface border-r border-q-border flex-shrink-0 overflow-hidden z-30">
          <SidebarContent />
        </motion.aside>

        {/* Mobile Sidebar */}
        <AnimatePresence>
          {mobileOpen && (
            <>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/70 z-40 md:hidden" onClick={() => setMobileOpen(false)} />
              <motion.aside initial={{ x: -240 }} animate={{ x: 0 }} exit={{ x: -240 }} transition={{ duration: 0.25 }}
                className="fixed left-0 top-0 bottom-0 w-60 bg-q-surface border-r border-q-border z-50 md:hidden">
                <SidebarContent />
              </motion.aside>
            </>
          )}
        </AnimatePresence>

        {/* Main Area */}
        <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
          {/* Top Bar */}
          <header className="flex items-center justify-between px-4 md:px-6 py-3 border-b border-q-border bg-q-surface/80 backdrop-blur-sm z-20 flex-shrink-0">
            <div className="flex items-center gap-3">
              <button className="md:hidden p-1.5 rounded-lg hover:bg-q-border/40 text-q-muted" onClick={() => setMobileOpen(!mobileOpen)}>
                {mobileOpen ? <X size={18} /> : <Menu size={18} />}
              </button>
              <button className="hidden md:flex p-1.5 rounded-lg hover:bg-q-border/40 text-q-muted transition-colors" onClick={() => setSidebarOpen(!sidebarOpen)}>
                <ChevronRight size={16} className={`transition-transform ${sidebarOpen ? 'rotate-180' : ''}`} />
              </button>
              {title && <div className="text-sm font-medium text-q-text">{title}</div>}
            </div>
            <div className="flex items-center gap-2">
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-q-card border border-q-border">
                <div className="w-1.5 h-1.5 rounded-full bg-q-green animate-pulse" />
                <span className="text-xs font-mono text-q-muted">{time || '实时数据'}</span>
              </div>
              <button className="p-2 rounded-lg hover:bg-q-border/40 text-q-muted transition-colors"><Bell size={16} /></button>
              <button className="p-2 rounded-lg hover:bg-q-border/40 text-q-muted transition-colors"><Settings size={16} /></button>
            </div>
          </header>

          {/* Page Content */}
          <main className="flex-1 overflow-y-auto bg-q-bg bg-grid">
            <motion.div key={router.pathname} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
              {children}
            </motion.div>
          </main>
        </div>
      </div>

      {/* Footer — full width */}
      <footer className="border-t border-q-border bg-q-surface flex-shrink-0">
        <div className="px-4 md:px-6 py-4">
          {/* API Sources Grid */}
          <div className="mb-3">
            <div className="text-[10px] font-mono text-q-muted uppercase tracking-widest mb-2 flex items-center gap-2">
              <Globe size={10} />数据来源 · 合作 API 平台
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
              {FOOTER_APIS.map(api => (
                <a key={api.name} href={api.url} target="_blank" rel="noreferrer"
                  className="flex flex-col gap-0.5 p-2 rounded-lg bg-q-card border border-q-border hover:border-q-blue/40 hover:bg-q-blue/5 transition-all group">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-semibold text-q-text group-hover:text-q-blue transition-colors truncate">{api.name}</span>
                    <ExternalLink size={9} className="text-q-muted/40 group-hover:text-q-blue flex-shrink-0 ml-1" />
                  </div>
                  <span className="text-[9px] text-q-muted/60 leading-tight line-clamp-2">{api.tag}</span>
                  <span className={`text-[8px] px-1 py-0.5 rounded self-start mt-0.5 ${api.free ? 'bg-q-green/10 text-q-green/70' : 'bg-q-amber/10 text-q-amber/70'}`}>
                    {api.free ? '免费' : '付费'}
                  </span>
                </a>
              ))}
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 pt-2 border-t border-q-border/50">
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[10px] text-q-muted/60">
              <span className="font-bold text-q-muted">Q-Alpha v1.0</span>
              <span>量化金融智能分析平台</span>
              <span>数据更新：股票15秒 · 内幕/鲸鱼1小时 · Trends 6小时</span>
            </div>
            <div className="text-[10px] text-q-muted/40 font-mono">
              ⚠ 本平台数据仅供参考，不构成投资建议，投资有风险，入市需谨慎
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
