import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from src.models import KPIRecord


def build_report(records: list[KPIRecord], out_path: str = "public/index.html"):
    renewable = [r for r in records if r.metric_name == "renewable_share_pct"]
    price_spread = [r for r in records if r.metric_name == "price_spread_eur_mwh"]
    price_stdev = [r for r in records if r.metric_name == "price_stdev_eur_mwh"]

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=("Renewable Share of Generation (%)", "Day-Ahead Price Volatility (EUR/MWh)"),
        row_heights=[0.5, 0.5],
        vertical_spacing=0.12,
    )

    fig.add_trace(
        go.Scatter(
            x=[r.timestamp for r in renewable],
            y=[r.value for r in renewable],
            mode="lines",
            name="Renewable share",
            line=dict(color="#2E7D32", width=2),
            fill="tozeroy",
            fillcolor="rgba(46,125,50,0.1)",
        ),
        row=1, col=1,
    )

    fig.add_trace(
        go.Bar(
            x=[r.timestamp for r in price_spread],
            y=[r.value for r in price_spread],
            name="Daily price spread",
            marker_color="#1565C0",
        ),
        row=2, col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=[r.timestamp for r in price_stdev],
            y=[r.value for r in price_stdev],
            mode="lines+markers",
            name="Price stdev",
            line=dict(color="#C62828", dash="dot"),
        ),
        row=2, col=1,
    )
    # Zero-line reference makes negative price events visually obvious
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)

    fig.update_layout(
        title=f"German Electricity Market KPIs — generated {datetime.utcnow():%Y-%m-%d %H:%M UTC}",
        template="plotly_white",
        height=800,
        showlegend=True,
    )
    fig.update_yaxes(title_text="%", row=1, col=1)
    fig.update_yaxes(title_text="EUR/MWh", row=2, col=1)

    fig.write_html(out_path, include_plotlyjs="cdn")
    return out_path