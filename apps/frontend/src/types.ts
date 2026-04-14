export type MarketAsset = {
  symbol: string;
  name: string;
  price_usd: number;
  percent_change_24h: number;
  volume_24h: number | null;
  market_cap: number | null;
  trend: string;
  sma_20: number | null;
  ema_20: number | null;
  rsi_14: number | null;
  macd: number | null;
  signal: number | null;
  rolling_volatility: number | null;
};

export type InsightCard = {
  title: string;
  content: string;
};

export type MarketOverviewResponse = {
  generated_at: string;
  assets: MarketAsset[];
  insights: InsightCard[];
};

export type AlertRead = {
  id: string;
  symbol: string;
  alert_type: string;
  threshold: number | null;
  is_active: boolean;
  created_at: string;
};

export type AgentResponse = {
  question: string;
  answer: string;
  grounded: boolean;
  sources: string[];
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type UserRead = {
  id: string;
  email: string;
  created_at: string;
};
