import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Altis Café Intelligence", page_icon="☕", layout="wide")

st.title("☕ Altis Café: Real-World Sales & Operations Intelligence")
st.markdown("Analyzing live transaction records to optimize item profitability, daily revenue trends, and operational flow.")
st.markdown("---")

# 2. Load Real-World Dataset from Public Repository
@st.cache_data
def load_real_cafe_data():
    url = "https://raw.githubusercontent.com/shaadyalii/Dirty-Cafe-Sales-Dataset/main/clean_cafe_sales.csv"
    try:
        df = pd.read_csv(url)
    except Exception:
        fallback_url = "https://raw.githubusercontent.com/hamza-amjad10/Data-Cleaning-Preprocessing-for-Cafe-Sales-Dataset/main/Clean_data.csv"
        df = pd.read_csv(fallback_url)
    
    # Standardize column names if needed
    df.columns = [col.strip().replace(" ", "") for col in df.columns]
    
    # Ensure numeric columns are properly cast
    for col in ['Quantity', 'PricePerUnit', 'TotalSpent']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df.dropna(subset=['TotalSpent', 'Quantity'])

df = load_real_cafe_data()

# 3. Sidebar Filtering Options
st.sidebar.header("🎛️ Analytics Controls")

if 'Item' in df.columns:
    all_items = df['Item'].dropna().unique()
    selected_items = st.sidebar.multiselect("Filter by Menu Item:", options=all_items, default=all_items[:min(5, len(all_items))])
    filtered_df = df[df['Item'].isin(selected_items)]
else:
    filtered_df = df

# 4. Key Performance Indicators (KPIs)
total_revenue = filtered_df['TotalSpent'].sum() if 'TotalSpent' in filtered_df.columns else 0
total_orders = len(filtered_df)
avg_order_value = filtered_df['TotalSpent'].mean() if total_orders > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Transactions", f"{total_orders:,}")
col3.metric("Average Spend per Order", f"${avg_order_value:.2f}")

st.markdown("---")

# 5. Visualizations with Real Data
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📊 Top Revenue Generating Items")
    if not filtered_df.empty and 'Item' in filtered_df.columns:
        item_rev = filtered_df.groupby('Item')['TotalSpent'].sum().reset_index().sort_values(by='TotalSpent', ascending=False).head(8)
        fig_items = px.bar(
            item_rev, x='TotalSpent', y='Item', orientation='h',
            labels={'TotalSpent': 'Total Revenue ($)', 'Item': 'Menu Item'},
            title="Revenue Contribution by Item",
            color='TotalSpent',
            color_continuous_scale='teal' # Fixed color scale name
        )
        fig_items.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        st.plotly_chart(fig_items, use_container_width=True)
    else:
        st.warning("No data available for current selection.")

with col_b:
    st.subheader("💳 Sales Breakdown by Payment Method")
    if not filtered_df.empty and 'PaymentMethod' in filtered_df.columns:
        pay_df = filtered_df.groupby('PaymentMethod')['TotalSpent'].sum().reset_index()
        fig_pay = px.pie(
            pay_df, names='PaymentMethod', values='TotalSpent', hole=0.4,
            title="Revenue Share by Payment Type"
        )
        st.plotly_chart(fig_pay, use_container_width=True)
    else:
        st.warning("Payment method data unavailable.")

# 6. Strategic Business Insight Box
st.markdown("### 💡 Strategic Inventory & Sales Insights")
if not filtered_df.empty and 'Item' in filtered_df.columns:
    top_seller = filtered_df.groupby('Item')['Quantity'].sum().idxmax()
    st.info(f"**Top Performing Product:** **{top_seller}** has the highest sales volume in units. Ensure raw ingredient inventory for this item is fully stocked prior to peak weekly trading hours.")
else:
    st.info("Select items from the sidebar to generate dynamic inventory insights.")

# Raw Data View
with st.expander("🔍 Inspect Cleaned Real-World Transaction Dataset"):
    st.dataframe(filtered_df.head(100), use_container_width=True)