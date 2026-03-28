// Q-Alpha API Client
// Centralized HTTP client with error handling and base URL management

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private base: string;

  constructor(base: string) {
    this.base = base;
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.base}${path}`;
    try {
      const res = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: res.statusText }));
        throw new Error(err.error || `HTTP ${res.status}`);
      }
      return res.json();
    } catch (err: any) {
      console.error(`[Q-Alpha API] ${path}:`, err.message);
      throw err;
    }
  }

  // ── Stock ──────────────────────────────────────────────
  async getStockPrice(ticker: string) {
    return this.request<any>(`/api/stock/price?ticker=${ticker}`);
  }

  async getStockCandles(ticker: string, timeframe = '3mo') {
    return this.request<any>(`/api/stock/candles?ticker=${ticker}&timeframe=${timeframe}`);
  }

  async getStockInfo(ticker: string) {
    return this.request<any>(`/api/stock/info?ticker=${ticker}`);
  }

  // ── Market ────────────────────────────────────────────
  async getPopular() {
    return this.request<any>('/api/market/popular');
  }

  async getNews() {
    return this.request<any>('/api/market/news');
  }

  // ── AI ────────────────────────────────────────────────
  async analyzeStock(ticker: string) {
    return this.request<any>('/api/ai/analyze', {
      method: 'POST',
      body: JSON.stringify({ ticker }),
    });
  }

  async getFamousPortfolio(name: string) {
    return this.request<any>(`/api/portfolio/famous?celebrity_name=${encodeURIComponent(name)}`);
  }

  // ── Financial ─────────────────────────────────────────
  async getInsider(ticker: string) {
    return this.request<any>(`/api/insider?ticker=${ticker}`);
  }

  async getWhales(ticker: string) {
    return this.request<any>(`/api/whales?ticker=${ticker}`);
  }

  async getAnalyst(ticker: string) {
    return this.request<any>(`/api/analyst?ticker=${ticker}`);
  }

  async getInstitutional(ticker: string) {
    return this.request<any>(`/api/institutional?ticker=${ticker}`);
  }

  async getSECFilings(ticker: string) {
    return this.request<any>(`/api/sec?ticker=${ticker}`);
  }

  async getRisk(ticker: string) {
    return this.request<any>(`/api/risk?ticker=${ticker}`);
  }

  async getRevenue(ticker: string) {
    return this.request<any>(`/api/revenue?ticker=${ticker}`);
  }

  async getETF(ticker: string) {
    return this.request<any>(`/api/etf?ticker=${ticker}`);
  }

  async getSplits(ticker: string) {
    return this.request<any>(`/api/splits?ticker=${ticker}`);
  }

  async getTrends(keyword: string) {
    return this.request<any>(`/api/trends?keyword=${encodeURIComponent(keyword)}`);
  }

  async getConsumer(keyword: string) {
    return this.request<any>(`/api/consumer?keyword=${encodeURIComponent(keyword)}`);
  }

  async getPatents(company: string) {
    return this.request<any>(`/api/patents?company_name=${encodeURIComponent(company)}`);
  }

  async getAppRatings(app: string) {
    return this.request<any>(`/api/app-ratings?app_name=${encodeURIComponent(app)}`);
  }

  async getCNBC() {
    return this.request<any>('/api/media/cnbc');
  }

  async getCramer() {
    return this.request<any>('/api/media/cramer');
  }

  // ── Politicians ───────────────────────────────────────
  async searchPolitician(name: string) {
    return this.request<any>(`/api/politician/search?name=${encodeURIComponent(name)}`);
  }

  async getCongressTrading(member?: string) {
    const q = member ? `?member_name=${encodeURIComponent(member)}` : '';
    return this.request<any>(`/api/gov/congress-trading${q}`);
  }

  async getNetWorth(member: string) {
    return this.request<any>(`/api/gov/networth?member_name=${encodeURIComponent(member)}`);
  }

  async getInsiderScore(member: string) {
    return this.request<any>(`/api/gov/insider-score?member_name=${encodeURIComponent(member)}`);
  }

  async getLobbying(company: string) {
    return this.request<any>(`/api/gov/lobbying?company_name=${encodeURIComponent(company)}`);
  }

  async getContracts(agency?: string) {
    const q = agency ? `?agency_name=${encodeURIComponent(agency)}` : '';
    return this.request<any>(`/api/gov/contracts${q}`);
  }

  async getElections() {
    return this.request<any>('/api/gov/elections');
  }

  async getSpending(agency?: string) {
    const q = agency ? `?agency_name=${encodeURIComponent(agency)}` : '';
    return this.request<any>(`/api/gov/spending${q}`);
  }

  async getFundraising(politician: string) {
    return this.request<any>(`/api/gov/fundraising?politician_name=${encodeURIComponent(politician)}`);
  }

  async getCorporateDonations(company: string) {
    return this.request<any>(`/api/gov/corporate-donations?company_name=${encodeURIComponent(company)}`);
  }

  // ── Reports ───────────────────────────────────────────
  getReportUrl(ticker: string, format: 'html' | 'markdown' | 'json' = 'html') {
    return `${this.base}/api/report/download?ticker=${ticker}&format=${format}`;
  }
}

export const api = new ApiClient(API_BASE);
export default api;
