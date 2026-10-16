
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="SpendSense | Expense Analyzer",
    page_icon="💰",
    layout="wide"
)

st.title("💰 SpendSense")
st.caption("Understand your spending. Make smarter decisions.")

REQUIRED_COLUMNS = [
    "date", "category", "description", "amount"
]

SAMPLE_FILE = Path(__file__).parent / "sample_expenses.csv"


# ---------------- LOAD SAMPLE DATA ----------------
def load_sample_data():
    return pd.read_csv(SAMPLE_FILE)


# ---------------- CLEAN AND VALIDATE DATA ----------------
def clean_data(df):
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()

    missing = set(REQUIRED_COLUMNS) - set(df.columns)

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing))
        )

    df = df[REQUIRED_COLUMNS].copy()

    df["date"] = pd.to_datetime(
        df["date"], errors="coerce"
    )
    df["amount"] = pd.to_numeric(
        df["amount"], errors="coerce"
    )
    df["category"] = (
        df["category"].fillna("").astype(str).str.strip()
    )
    df["description"] = (
        df["description"].fillna("").astype(str).str.strip()
    )

    # Remove rows with invalid dates, amounts,
    # empty categories, or negative expenses.
    df = df.dropna(subset=["date", "amount"])
    df = df[
        (df["amount"] >= 0)
        & (df["category"] != "")
    ].copy()

    df["month"] = df["date"].dt.to_period("M").astype(str)

    return df.sort_values("date")


# ---------------- SIDEBAR ----------------
st.sidebar.header("📂 Your Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload an expense CSV",
    type=["csv"],
    help=(
        "Required columns: date, category, "
        "description, amount"
    )
)

if uploaded_file is not None:
    try:
        raw_df = pd.read_csv(uploaded_file)
        df = clean_data(raw_df)
    except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as error:
        st.error(f"Could not read your CSV: {error}")
        st.stop()
    except Exception as error:
        st.error(f"Unexpected data error: {error}")
        st.stop()
else:
    try:
        df = clean_data(load_sample_data())
        st.sidebar.success("Using sample expense data")
    except Exception as error:
        st.error(f"Could not load sample data: {error}")
        st.stop()

if df.empty:
    st.warning("No valid expense records were found.")
    st.stop()

st.sidebar.caption(
    f"{len(df)} valid transactions loaded"
)


# ---------------- FILTERS ----------------
st.sidebar.header("🔎 Filters")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

categories = sorted(df["category"].unique())

selected_categories = st.sidebar.multiselect(
    "Categories",
    options=categories,
    default=categories
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = df[
        (df["date"].dt.date >= start_date)
        & (df["date"].dt.date <= end_date)
        & (df["category"].isin(selected_categories))
    ].copy()
else:
    filtered_df = df.iloc[0:0].copy()


# ---------------- EMPTY FILTER CHECK ----------------
if filtered_df.empty:
    st.warning(
        "No expenses match your filters. "
        "Change the date range or select more categories."
    )
    st.stop()


# ---------------- KEY METRICS ----------------
total_spent = filtered_df["amount"].sum()
average_expense = filtered_df["amount"].mean()
largest_expense = filtered_df["amount"].max()
transaction_count = len(filtered_df)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Spent", f"₹{total_spent:,.2f}")
col2.metric("Average Expense", f"₹{average_expense:,.2f}")
col3.metric("Largest Expense", f"₹{largest_expense:,.2f}")
col4.metric("Transactions", f"{transaction_count:,}")

st.divider()


# ---------------- CHARTS ----------------
left, right = st.columns(2)

with left:
    st.subheader("📊 Spending by Category")

    category_data = (
        filtered_df.groupby("category", as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
    )

    fig_category = px.bar(
        category_data,
        x="category",
        y="amount",
        color="category",
        text_auto=".2s",
        labels={
            "category": "Category",
            "amount": "Amount (₹)"
        }
    )

    fig_category.update_layout(
        showlegend=False,
        xaxis_title=None,
        yaxis_title="Amount (₹)"
    )

    st.plotly_chart(fig_category, use_container_width=True)

with right:
    st.subheader("🍩 Expense Distribution")

    fig_pie = px.pie(
        category_data,
        names="category",
        values="amount",
        hole=0.45
    )

    st.plotly_chart(fig_pie, use_container_width=True)


# ---------------- MONTHLY TREND ----------------
st.subheader("📈 Monthly Spending Trend")

monthly_data = (
    filtered_df.groupby("month", as_index=False)["amount"]
    .sum()
    .sort_values("month")
)

fig_monthly = px.line(
    monthly_data,
    x="month",
    y="amount",
    markers=True,
    labels={
        "month": "Month",
        "amount": "Total Spending (₹)"
    }
)

fig_monthly.update_layout(
    xaxis_title=None,
    yaxis_title="Amount (₹)"
)

st.plotly_chart(fig_monthly, use_container_width=True)


# ---------------- SPENDING INSIGHT ----------------
st.subheader("💡 Spending Insight")

top_category = category_data.iloc[0]
share = (top_category["amount"] / total_spent * 100) if total_spent else 0

st.info(
    f"Your highest-spending category is "
    f"**{top_category['category']}**, accounting for "
    f"**₹{top_category['amount']:,.2f}** "
    f"({share:.1f}% of filtered spending)."
)


# ---------------- TRANSACTION TABLE ----------------
st.subheader("🧾 Transaction History")

display_df = filtered_df[
    ["date", "category", "description", "amount"]
].copy()

display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ---------------- CSV EXPORT ----------------
csv_data = display_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Expenses",
    data=csv_data,
    file_name="spendsense_expenses.csv",
    mime="text/csv"
)

st.caption(
    "SpendSense analyzes the data you provide. "
    "It does not connect to bank accounts or provide financial advice."
)
