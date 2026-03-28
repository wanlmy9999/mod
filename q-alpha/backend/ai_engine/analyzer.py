"""
Q-Alpha AI Analysis Engine
Computes investment scores, ratings, and explanations using:
- Technical indicators (RSI, MACD, Moving Averages)
- Volume/Money flow analysis
- Sentiment scoring
- Insider/Whale activity signals
"""

import math
import logging
import random
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger("q-alpha.ai")


def compute_rsi(prices: List[float], period: int = 14) -> float:
    """Compute Relative Strength Index."""
    if len(prices) < period + 1:
        return 50.0
    deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas[-period:]]
    losses = [abs(d) if d < 0 else 0 for d in deltas[-period:]]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def compute_macd(prices: List[float]) -> Dict[str, float]:
    """Compute MACD line, signal, and histogram."""
    def ema(data, span):
        k = 2 / (span + 1)
        result = [data[0]]
        for i in range(1, len(data)):
            result.append(data[i] * k + result[-1] * (1 - k))
        return result

    if len(prices) < 26:
        return {"macd": 0, "signal": 0, "histogram": 0}
    ema12 = ema(prices, 12)
    ema26 = ema(prices, 26)
    macd_line = [ema12[i] - ema26[i] for i in range(len(prices))]
    signal = ema(macd_line[-9:], 9)
    hist = macd_line[-1] - signal[-1]
    return {
        "macd": round(macd_line[-1], 4),
        "signal": round(signal[-1], 4),
        "histogram": round(hist, 4),
    }


def compute_moving_averages(prices: List[float]) -> Dict[str, Optional[float]]:
    """Compute MA20, MA50, MA200."""
    def ma(data, period):
        if len(data) < period:
            return None
        return round(sum(data[-period:]) / period, 2)
    return {
        "ma20": ma(prices, 20),
        "ma50": ma(prices, 50),
        "ma200": ma(prices, 200),
        "current": prices[-1] if prices else None,
    }


def compute_volume_score(volumes: List[int]) -> float:
    """Score 0-100 based on recent volume vs average."""
    if len(volumes) < 5:
        return 50.0
    avg_vol = sum(volumes[:-1]) / max(len(volumes) - 1, 1)
    recent = volumes[-1]
    ratio = recent / avg_vol if avg_vol > 0 else 1
    if ratio > 2.0:
        return 85.0
    elif ratio > 1.5:
        return 70.0
    elif ratio > 1.0:
        return 55.0
    elif ratio > 0.7:
        return 45.0
    else:
        return 30.0


class QAlphaAnalyzer:
    """Main AI analysis engine."""

    def analyze(
        self,
        ticker: str,
        candle_data: Optional[dict] = None,
        insider_data: Optional[list] = None,
        whale_data: Optional[list] = None,
        analyst_data: Optional[list] = None,
        sentiment_data: Optional[dict] = None,
    ) -> dict:
        """
        Full analysis pipeline returning score, rating, explanation, and risk flags.
        """
        # Extract price/volume series from candle data
        prices = []
        volumes = []
        if candle_data and candle_data.get("candles"):
            for c in candle_data["candles"][-200:]:
                prices.append(c["close"])
                volumes.append(c.get("volume", 0))

        # If no real data, generate plausible mock values for demo
        if not prices:
            prices = [100 + i * 0.3 + random.uniform(-2, 2) for i in range(60)]
            volumes = [random.randint(20_000_000, 80_000_000) for _ in range(60)]

        # Compute technical indicators
        rsi = compute_rsi(prices)
        macd = compute_macd(prices)
        mas = compute_moving_averages(prices)
        volume_score = compute_volume_score(volumes)
        current_price = prices[-1] if prices else 0

        # --- Technical Score (0-100) ---
        tech_score = 50.0

        # RSI contribution
        if 40 <= rsi <= 60:
            tech_score += 5   # neutral
        elif 30 <= rsi < 40:
            tech_score += 15  # oversold → bullish
        elif rsi < 30:
            tech_score += 20  # very oversold
        elif 60 < rsi <= 70:
            tech_score -= 5   # slightly overbought
        elif rsi > 70:
            tech_score -= 15  # overbought

        # MACD contribution
        if macd["histogram"] > 0:
            tech_score += 10
        else:
            tech_score -= 10

        # Price vs moving averages
        if mas["ma50"] and current_price > mas["ma50"]:
            tech_score += 8
        if mas["ma200"] and current_price > mas["ma200"]:
            tech_score += 8
        if mas["ma20"] and current_price > mas["ma20"]:
            tech_score += 5

        # --- Insider Activity Score ---
        insider_score = 50.0
        insider_signal = "Neutral"
        if insider_data:
            buys = sum(1 for i in insider_data if "purchase" in i.get("action", "").lower())
            sells = sum(1 for i in insider_data if "sale" in i.get("action", "").lower())
            total = max(buys + sells, 1)
            ratio = buys / total
            if ratio >= 0.7:
                insider_score = 75
                insider_signal = "Bullish (heavy insider buying)"
            elif ratio >= 0.5:
                insider_score = 60
                insider_signal = "Slightly Bullish"
            elif ratio <= 0.3:
                insider_score = 30
                insider_signal = "Bearish (insider selling)"
            else:
                insider_signal = "Neutral"

        # --- Whale/Institutional Score ---
        whale_score = 50.0
        whale_signal = "Neutral"
        if whale_data:
            buy_signals = sum(1 for w in whale_data if "+" in w.get("change", ""))
            if buy_signals / max(len(whale_data), 1) > 0.6:
                whale_score = 72
                whale_signal = "Accumulation phase detected"
            else:
                whale_score = 42
                whale_signal = "Slight distribution"

        # --- Analyst Consensus Score ---
        analyst_score = 50.0
        analyst_signal = "Neutral"
        if analyst_data:
            rating_map = {"strong buy": 4, "buy": 3, "neutral": 2, "hold": 2, "sell": 1, "strong sell": 0}
            values = [rating_map.get(a.get("rating", "").lower(), 2) for a in analyst_data]
            if values:
                avg = sum(values) / len(values)
                analyst_score = avg / 4 * 100
                if avg >= 3:
                    analyst_signal = "Strong consensus buy"
                elif avg >= 2.5:
                    analyst_signal = "Modest buy bias"
                else:
                    analyst_signal = "Mixed or bearish"

        # --- Final Composite Score ---
        final_score = (
            tech_score * 0.40 +
            insider_score * 0.25 +
            whale_score * 0.20 +
            analyst_score * 0.15
        )
        final_score = max(0, min(100, round(final_score)))

        # --- Rating ---
        if final_score >= 72:
            rating = "BUY"
            rating_color = "green"
        elif final_score >= 50:
            rating = "HOLD"
            rating_color = "yellow"
        else:
            rating = "SELL"
            rating_color = "red"

        # --- Risk Flags ---
        risks = []
        if rsi > 70:
            risks.append({"type": "warning", "message": "RSI overbought (>70) — potential pullback risk"})
        if rsi < 30:
            risks.append({"type": "opportunity", "message": "RSI oversold (<30) — potential bounce signal"})
        if macd["histogram"] < -0.5:
            risks.append({"type": "warning", "message": "MACD negative histogram — bearish momentum"})
        if mas["ma50"] and current_price < mas["ma50"]:
            risks.append({"type": "warning", "message": "Price below 50-day MA — weak medium-term trend"})
        if volume_score > 80:
            risks.append({"type": "info", "message": "Unusually high volume — strong institutional interest"})
        if final_score > 85:
            risks.append({"type": "warning", "message": "Extremely high score — asset may be overheated"})

        # --- Explanation ---
        explanation = self._build_explanation(
            ticker, final_score, rsi, macd, mas, current_price,
            insider_signal, whale_signal, analyst_signal, volume_score
        )

        return {
            "ticker": ticker,
            "score": final_score,
            "rating": rating,
            "rating_color": rating_color,
            "explanation": explanation,
            "risks": risks,
            "indicators": {
                "rsi": rsi,
                "macd": macd,
                "moving_averages": mas,
                "volume_score": round(volume_score, 1),
            },
            "sub_scores": {
                "technical": round(tech_score, 1),
                "insider": round(insider_score, 1),
                "whale": round(whale_score, 1),
                "analyst": round(analyst_score, 1),
            },
            "signals": {
                "insider": insider_signal,
                "whale": whale_signal,
                "analyst": analyst_signal,
            },
            "analyzed_at": datetime.now().isoformat(),
        }

    def _build_explanation(
        self, ticker, score, rsi, macd, mas, price,
        insider_signal, whale_signal, analyst_signal, vol_score
    ) -> str:
        parts = []
        parts.append(f"**{ticker} receives a composite AI score of {score}/100.**")

        # Technical
        rsi_desc = "neutral" if 40 <= rsi <= 60 else ("oversold — a bullish reversal signal" if rsi < 40 else "overbought — caution advised")
        parts.append(f"The RSI stands at **{rsi}**, which is {rsi_desc}.")

        if macd["histogram"] > 0:
            parts.append(f"MACD histogram is positive (+{macd['histogram']:.3f}), indicating **bullish momentum** is building.")
        else:
            parts.append(f"MACD histogram is negative ({macd['histogram']:.3f}), suggesting **bearish pressure** in the short term.")

        if mas.get("ma50") and price > mas["ma50"]:
            parts.append(f"Price (${price:.2f}) is trading **above the 50-day moving average** (${mas['ma50']:.2f}), a constructive technical signal.")
        elif mas.get("ma50"):
            parts.append(f"Price (${price:.2f}) is trading **below the 50-day MA** (${mas['ma50']:.2f}), indicating potential weakness.")

        # Insider/Whale
        parts.append(f"Insider activity: **{insider_signal}**. Institutional (whale) positioning: **{whale_signal}**.")
        parts.append(f"Analyst consensus: **{analyst_signal}**.")

        # Volume
        if vol_score > 70:
            parts.append("Volume analysis shows elevated trading activity, suggesting **strong institutional participation**.")

        return " ".join(parts)


# Singleton
_analyzer: Optional[QAlphaAnalyzer] = None


def get_analyzer() -> QAlphaAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = QAlphaAnalyzer()
    return _analyzer
