
import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# 1. Konfigurasi halaman
# -------------------------
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# -------------------------
# 2. Membaca dataset
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard.csv")

    # Mengubah kolom tanggal menjadi format datetime
    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"],
        dayfirst=True,
        errors="coerce"
    )

    # Menghitung estimasi nilai penjualan
    df["Sales"] = df["Quantity"] * df["UnitPrice"]

    return df


df = load_data()

# -------------------------
# 3. Judul dashboard
# -------------------------
st.title("📊 Sales Performance Dashboard")
st.caption(
    "Dashboard interaktif untuk mengeksplorasi transaksi, "
    "produk, pelanggan, negara, dan sumber pemasaran."
)

# -------------------------
# 4. Filter interaktif
# -------------------------
st.sidebar.header("Filter Data")

months = sorted(
    df["InvoiceMonth"].dropna().unique().tolist()
)
selected_months = st.sidebar.multiselect(
    "Pilih bulan",
    options=months,
    default=months
)

countries = sorted(
    df["Country"].dropna().unique().tolist()
)
selected_countries = st.sidebar.multiselect(
    "Pilih negara",
    options=countries,
    default=countries
)

sources = sorted(
    df["Source"].dropna().unique().tolist()
)
selected_sources = st.sidebar.multiselect(
    "Pilih sumber pemasaran",
    options=sources,
    default=sources
)

# -------------------------
# 5. Menerapkan filter
# -------------------------
filtered_df = df[
    df["InvoiceMonth"].isin(selected_months)
    & df["Country"].isin(selected_countries)
    & df["Source"].isin(selected_sources)
].copy()

if filtered_df.empty:
    st.warning("Tidak ada data untuk kombinasi filter ini.")
    st.stop()

# -------------------------
# 6. KPI / metrik utama
# -------------------------
total_transactions = filtered_df["InvoiceNo"].nunique()
total_quantity = filtered_df["Quantity"].sum()
total_sales = filtered_df["Sales"].sum()
total_customers = filtered_df["CustomerID"].nunique()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Transaksi",
    f"{total_transactions:,}"
)
col2.metric(
    "Total Kuantitas",
    f"{total_quantity:,}"
)
col3.metric(
    "Estimasi Nilai Penjualan",
    f"{total_sales:,.2f}"
)
col4.metric(
    "Pelanggan Unik",
    f"{total_customers:,}"
)

st.divider()

# -------------------------
# 7. Grafik penjualan per bulan
# -------------------------
st.subheader("Tren Penjualan per Bulan")

monthly_sales = (
    filtered_df.groupby("InvoiceMonth", as_index=False)
    .agg(Sales=("Sales", "sum"))
)

fig_month = px.bar(
    monthly_sales,
    x="InvoiceMonth",
    y="Sales",
    title="Estimasi Nilai Penjualan per Bulan",
    labels={
        "InvoiceMonth": "Bulan",
        "Sales": "Estimasi Penjualan"
    },
    color="Sales",
    color_continuous_scale="Teal"
)

st.plotly_chart(fig_month, use_container_width=True)

# -------------------------
# 8. Grafik berdasarkan negara
# -------------------------
left, right = st.columns(2)

with left:
    st.subheader("Penjualan berdasarkan Negara")

    country_sales = (
        filtered_df.groupby("Country", as_index=False)
        .agg(Sales=("Sales", "sum"))
        .sort_values("Sales", ascending=False)
        .head(10)
    )

    fig_country = px.bar(
        country_sales.sort_values("Sales"),
        x="Sales",
        y="Country",
        orientation="h",
        title="10 Negara berdasarkan Nilai Penjualan",
        labels={
            "Sales": "Estimasi Penjualan",
            "Country": "Negara"
        }
    )

    st.plotly_chart(fig_country, use_container_width=True)

with right:
    st.subheader("Sumber Pemasaran")

    source_sales = (
        filtered_df.groupby("Source", as_index=False)
        .agg(Sales=("Sales", "sum"))
        .sort_values("Sales", ascending=False)
    )

    fig_source = px.pie(
        source_sales,
        names="Source",
        values="Sales",
        title="Kontribusi Nilai Penjualan per Sumber"
    )

    st.plotly_chart(fig_source, use_container_width=True)

# -------------------------
# 9. Produk teratas
# -------------------------
st.subheader("10 Produk dengan Estimasi Penjualan Tertinggi")

product_sales = (
    filtered_df.groupby("Description", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Quantity=("Quantity", "sum")
    )
    .sort_values("Sales", ascending=False)
    .head(10)
)

fig_product = px.bar(
    product_sales.sort_values("Sales"),
    x="Sales",
    y="Description",
    orientation="h",
    hover_data=["Quantity"],
    labels={
        "Sales": "Estimasi Penjualan",
        "Description": "Nama Produk",
        "Quantity": "Kuantitas"
    }
)

st.plotly_chart(fig_product, use_container_width=True)

# -------------------------
# 10. Tabel data
# -------------------------
with st.expander("Lihat data transaksi yang sudah difilter"):
    st.dataframe(
        filtered_df,
        use_container_width=True
    )

st.caption(
    "Catatan: estimasi nilai penjualan dihitung dari Quantity × UnitPrice. "
    "Interpretasi bisnis perlu mempertimbangkan retur dan aturan dataset."
)
