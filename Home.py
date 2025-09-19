import streamlit as st
import pandas as pd
import altair as alt
import yfinance as yf
import plotly.graph_objects as go


st.set_page_config(
    page_title="Portfolio Dashboard",
    page_icon="📈",
    initial_sidebar_state="expanded",
    layout="wide"
)


st.subheader("📈 Momentum Investing Portfolio Dashboard")
st.info("Updated on 2025-08-31")

df = pd.read_csv("dataa.csv")
df["current_date"] = pd.to_datetime(df["current_date"])
df = df.sort_values("current_date").set_index("current_date")

portfolio = df.groupby("current_date")["total_portfolio_value"].last()
portfolio_returns = portfolio.pct_change().dropna()


from datetime import datetime, timedelta
end_date = max(portfolio.index.max(), datetime.now())

benchmark = yf.download("^CRSLDX", 
                       start=portfolio.index.min(), 
                       end=end_date + timedelta(days=30))["Close"] 
benchmark_monthly = benchmark.resample("ME").last()
benchmark_returns = benchmark_monthly.pct_change().dropna()

port_ret, bench_ret = portfolio_returns.align(benchmark_returns, join="inner")

if hasattr(bench_ret, 'squeeze'):
    bench_ret = bench_ret.squeeze()

port_cum = (1 + port_ret).cumprod()
bench_cum = (1 + bench_ret).cumprod()

fig = go.Figure()
fig.add_trace(go.Scatter(x=port_cum.index, y=(port_cum-1)*100, name="Portfolio", line_color="blue"))
fig.add_trace(go.Scatter(x=bench_cum.index, y=(bench_cum-1)*100, name="Benchmark", line_color="orange"))
fig.update_layout(title="Cumulative Returns (%)", xaxis_title="Date", yaxis_title="Return %")

st.plotly_chart(fig, use_container_width=True)


main_df = pd.read_csv("dataa.csv")

date_column = "current_date"  
main_df[date_column] = pd.to_datetime(main_df[date_column])
main_df = main_df.sort_values(by=date_column).reset_index(drop=True)
main_df["total_portfolio_value"] = pd.to_numeric(main_df["total_portfolio_value"], errors="coerce")

# ----------------------------
# Metrics Calculations
# ----------------------------
portfolio_value = main_df["total_portfolio_value"]

total_return = (portfolio_value.iloc[-1] / portfolio_value.iloc[0]) - 1
days = (main_df[date_column].iloc[-1] - main_df[date_column].iloc[0]).days
years = days / 365.25
cagr = (portfolio_value.iloc[-1] / portfolio_value.iloc[0]) ** (1 / years) - 1

running_max = portfolio_value.cummax()
drawdown = (portfolio_value - running_max) / running_max
max_drawdown = drawdown.min()
sharpe_ratio = cagr/-max_drawdown

# ----------------------------
# Layout
# ----------------------------






# KPIs in one row
col1, col2, col3, col4 = st.columns(4)
col1.metric("CAGR", f"{cagr:.2%}")
col2.metric("Overall Return", f"{total_return:.2%}")
col3.metric("Max Drawdown", f"{max_drawdown:.2%}")
col4.metric("Sharpe Ratio",f"{sharpe_ratio:.2}")

st.divider()


date = main_df[date_column].sort_values(ascending=False).tolist()


main_df["my_date"] = pd.to_datetime(main_df[date_column])
latest_date = main_df["my_date"].max()


latest_data = main_df[main_df["my_date"] == latest_date]
only_data = latest_data[latest_data["status"] == "Held"]
data_to_show = only_data[["ticker","shares_qty","bought_price","current_price","current_value"]]
st.subheader("Current Holding")
st.dataframe(data_to_show)

# ----------------------------
# Charts Section
# ----------------------------
st.subheader("Performance Visualizations")

# ---- Monthly Returns ----
monthly_returns = (
    main_df.resample("M", on=date_column)["total_portfolio_value"]
    .last()
    .pct_change()
    .dropna()
)

monthly_df = monthly_returns.reset_index().rename(columns={"total_portfolio_value": "monthly_return"})
monthly_df["color"] = monthly_df["monthly_return"].apply(lambda x: "green" if x > 0 else "red")

monthly_chart = (
    alt.Chart(monthly_df)
    .mark_bar()
    .encode(
        x=alt.X("current_date:T", title="Month"),
        y=alt.Y("monthly_return:Q", title="Monthly Return", axis=alt.Axis(format="%")),
        color=alt.Color("color:N", scale=None, legend=None),
        tooltip=["current_date", alt.Tooltip("monthly_return", format=".2%")]
    )
    .properties(title="Monthly Returns", height=300)
)

# ---- Yearly Returns ----
yearly_returns = (
    main_df.resample("Y", on=date_column)["total_portfolio_value"]
    .last()
    .pct_change()
    .dropna()
)
yearly_df = yearly_returns.reset_index().rename(columns={"total_portfolio_value": "yearly_return"})
yearly_df["year"] = yearly_df["current_date"].dt.year

yearly_chart = (
    alt.Chart(yearly_df)
    .mark_line(color="darkorange", interpolate="monotone", strokeWidth=3)
    .encode(
        x=alt.X("year:O", title="Year"),
        y=alt.Y("yearly_return:Q", title="Yearly Return", axis=alt.Axis(format="%")),
        tooltip=[alt.Tooltip("year:O", title="Year"), alt.Tooltip("yearly_return", format=".2%")]
    )
    .properties(title="Yearly Returns", height=300)
    +
    alt.Chart(yearly_df)
    .mark_point(size=80, filled=True, color="darkorange")
    .encode(x="year:O", y="yearly_return:Q", tooltip=["year", alt.Tooltip("yearly_return", format=".2%")])
    +
    alt.Chart(yearly_df)
    .mark_text(align="center", dy=-10, color="black")
    .encode(x="year:O", y="yearly_return:Q", text=alt.Text("yearly_return:Q", format=".1%"))
)

# ---- Drawdown Chart ----
# ---- Drawdown Calculation ----
main_df = main_df.sort_values(by=date_column).reset_index(drop=True)

# Running max
# Ensure numeric
main_df["total_portfolio_value"] = pd.to_numeric(main_df["total_portfolio_value"], errors="coerce")
main_df[date_column] = pd.to_datetime(main_df[date_column])

# Sort by date to avoid misaligned cummax
main_df = main_df.sort_values(by=date_column).reset_index(drop=True)

# Keep only last value per day (if duplicates exist)
main_df = main_df.groupby(date_column, as_index=False).last()

# Drawdown calculation
running_max = main_df["total_portfolio_value"].cummax()
drawdown = main_df["total_portfolio_value"] / running_max - 1

# DataFrame for plotting
dd_df = pd.DataFrame({
    date_column: main_df[date_column],
    "drawdown": drawdown
})

# Bar chart version of drawdown
dd_chart = alt.Chart(dd_df).mark_bar(color="red").encode(
    x=alt.X(f"{date_column}:T", title="Date"),
    y=alt.Y("drawdown:Q", title="Drawdown", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[-1, 0])),
    tooltip=[date_column, alt.Tooltip("drawdown", format=".2%")]
).properties(
    title="Drawdown (Underwater Plot)",
    height=300
)



# ----------------------------
# Show Charts
# ----------------------------
st.altair_chart(monthly_chart, use_container_width=True)
#st.altair_chart(yearly_chart, use_container_width=True)
st.altair_chart(dd_chart, use_container_width=True)

# ----------------------------
# Yearly Returns Table
# ----------------------------
st.subheader("📊 Yearly Returns Summary")

# prepare DataFrame first
df_display = yearly_df[["year", "yearly_return"]].reset_index(drop=True)

# optional CSS to center and enlarge table font
st.markdown("""
    <style>
        .stDataFrame table { font-size: 16px; }
        .stDataFrame td, .stDataFrame th { text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

# create a Styler (formatting + optional color)
def color_return(val):
    return "color: green; font-weight:600" if val >= 0 else "color: red; font-weight:600"

styled = (
    df_display
    .style
    .format({"yearly_return": "{:.2%}"})
    .applymap(color_return, subset=["yearly_return"])
)

st.dataframe(styled, use_container_width=True)





# Navigation
# Navigation







