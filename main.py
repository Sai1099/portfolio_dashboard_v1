import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Portfolio Dashboard",
    page_icon="📈",
    initial_sidebar_state="collapsed",
    layout="wide"
)

# ----------------------------
# Load Data
# ----------------------------
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

# ----------------------------
# Layout
# ----------------------------
st.title("📈 Momentum Investing Portfolio Dashboard")

# KPIs in one row
col1, col2, col3 = st.columns(3)
col1.metric("CAGR", f"{cagr:.2%}")
col2.metric("Overall Return", f"{total_return:.2%}")
col3.metric("Max Drawdown", f"{max_drawdown:.2%}")

st.divider()

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
st.altair_chart(yearly_chart, use_container_width=True)
st.altair_chart(dd_chart, use_container_width=True)

# ----------------------------
# Yearly Returns Table
# ----------------------------
st.subheader("📊 Yearly Returns Summary")
st.dataframe(yearly_df[["year", "yearly_return"]].style.format({"yearly_return": "{:.2%}"}))
