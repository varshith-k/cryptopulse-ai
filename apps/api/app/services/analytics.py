from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.schemas.analytics import AnomalyRecord, AnomalyResponse, SummaryResponse
from app.services.market import build_market_overview


def detect_market_anomalies(session: Session) -> AnomalyResponse:
    overview = build_market_overview(session)
    anomalies: list[AnomalyRecord] = []

    for asset in overview.assets:
        volatility_score = asset.rolling_volatility or 0
        momentum_score = abs(asset.percent_change_24h)
        rsi_score = 0.0

        if asset.rsi_14 is not None and (asset.rsi_14 >= 68 or asset.rsi_14 <= 35):
            rsi_score = 1.2

        anomaly_score = round((volatility_score * 0.7) + (momentum_score * 0.45) + rsi_score, 2)

        if anomaly_score < 3.4:
            continue

        direction = "upside breakout" if asset.percent_change_24h >= 0 else "downside stress"
        reasons = []
        if asset.rolling_volatility is not None and asset.rolling_volatility >= 3:
            reasons.append("elevated rolling volatility")
        if abs(asset.percent_change_24h) >= 3:
            reasons.append("large 24h directional move")
        if asset.rsi_14 is not None and asset.rsi_14 >= 68:
            reasons.append("RSI nearing overbought conditions")
        if asset.rsi_14 is not None and asset.rsi_14 <= 35:
            reasons.append("RSI nearing oversold conditions")

        anomalies.append(
            AnomalyRecord(
                symbol=asset.symbol,
                anomaly_score=anomaly_score,
                direction=direction,
                reason=", ".join(reasons) if reasons else "multi-factor market deviation",
                percent_change_24h=asset.percent_change_24h,
                rolling_volatility=asset.rolling_volatility,
                rsi_14=asset.rsi_14,
            )
        )

    recommendations = _build_recommendations(overview.assets, anomalies)
    return AnomalyResponse(
        generated_at=datetime.now(UTC).isoformat(),
        anomalies=anomalies,
        recommendations=recommendations,
    )


def generate_market_summary(session: Session, scope: str = "market") -> SummaryResponse:
    overview = build_market_overview(session)
    assets = overview.assets
    leaders = sorted(assets, key=lambda asset: asset.percent_change_24h, reverse=True)
    laggards = sorted(assets, key=lambda asset: asset.percent_change_24h)

    positive_count = sum(asset.percent_change_24h > 0 for asset in assets)
    average_volatility = (
        sum(asset.rolling_volatility or 0 for asset in assets) / len(assets) if assets else 0
    )

    if scope.lower() in {asset.symbol.lower() for asset in assets}:
        asset = next(item for item in assets if item.symbol.lower() == scope.lower())
        summary = (
            f"{asset.symbol} is trading at {asset.price_usd:.2f} USD with a "
            f"{asset.percent_change_24h:.2f}% 24-hour move. {asset.trend}"
        )
        highlights = [
            f"RSI 14: {asset.rsi_14:.1f}" if asset.rsi_14 is not None else "RSI 14 unavailable",
            (
                f"Rolling volatility: {asset.rolling_volatility:.2f}"
                if asset.rolling_volatility is not None
                else "Rolling volatility unavailable"
            ),
            f"24h volume: {asset.volume_24h:,.0f}" if asset.volume_24h is not None else "Volume unavailable",
        ]
        return SummaryResponse(
            generated_at=datetime.now(UTC).isoformat(),
            scope=asset.symbol,
            summary=summary,
            highlights=highlights,
        )

    leader = leaders[0] if leaders else None
    laggard = laggards[0] if laggards else None
    summary = (
        f"{positive_count} of {len(assets)} tracked assets are positive on the day. "
        f"{leader.symbol if leader else 'No leader'} is leading momentum, while "
        f"{laggard.symbol if laggard else 'no laggard'} is the weakest relative mover. "
        f"Average rolling volatility sits near {average_volatility:.2f}."
    )
    highlights = [
        f"Momentum leader: {leader.symbol} at {leader.percent_change_24h:.2f}%"
        if leader
        else "No momentum leader available",
        f"Weakest mover: {laggard.symbol} at {laggard.percent_change_24h:.2f}%"
        if laggard
        else "No weakest mover available",
        (
            f"Top watch insight: {overview.insights[0].title}."
            if overview.insights
            else "No insight cards available"
        ),
    ]
    return SummaryResponse(
        generated_at=datetime.now(UTC).isoformat(),
        scope="market",
        summary=summary,
        highlights=highlights,
    )


def recommend_metrics(session: Session) -> list[str]:
    overview = build_market_overview(session)
    anomalies = detect_market_anomalies(session)
    recommendations = _build_recommendations(overview.assets, anomalies.anomalies)
    return recommendations


def _build_recommendations(assets, anomalies: list[AnomalyRecord]) -> list[str]:
    recommendations: list[str] = []

    if anomalies:
        top = anomalies[0]
        recommendations.append(
            f"Inspect {top.symbol} order flow and shorter intraday candles because it has the highest anomaly score."
        )

    highest_rsi = max(
        (asset for asset in assets if asset.rsi_14 is not None),
        key=lambda asset: asset.rsi_14 or 0,
        default=None,
    )
    if highest_rsi is not None:
        recommendations.append(
            f"Monitor {highest_rsi.symbol} momentum exhaustion risk because RSI is elevated at {highest_rsi.rsi_14:.1f}."
        )

    highest_volatility = max(
        (asset for asset in assets if asset.rolling_volatility is not None),
        key=lambda asset: asset.rolling_volatility or 0,
        default=None,
    )
    if highest_volatility is not None:
        recommendations.append(
            f"Compare {highest_volatility.symbol} against BTC beta because it currently has the highest rolling volatility."
        )

    return recommendations[:3]
