import streamlit as st
import pandas as pd
import numpy as np

# ✅ Konfigurasi halaman
st.set_page_config(
    page_title="Perbandingan Harga Mobil 🚗💸",
    layout="wide",
    page_icon="🚗"
)

# ✅ Judul dan deskripsi aplikasi
st.markdown("""
# 🚗 Perbandingan Harga Mobil Baru Antar Lokasi
Selamat datang!  
Gunakan sidebar di kiri untuk memilih model, varian, dan lokasi perbandingan harga **OTR** (On The Road).  
""")

# ✅ Sidebar untuk input
st.sidebar.header("🔧 Filter")
# Load Data
df = pd.read_excel('harga_mobil_baru.xlsx')

# Konversi harga ke numerik
df['Harga OTR'] = pd.to_numeric(df['Harga OTR'], errors='coerce')

# Buat mapping varian dari model
model_varian_map = df.groupby('Model Series')['Varian'].unique().apply(list).to_dict()
lokasi_list = df['Lokasi'].unique().tolist()

# Sidebar dropdown
selected_model_series = st.sidebar.selectbox(
    '🚘 Pilih Model Series',
    options=list(model_varian_map.keys())
)

varian_options = model_varian_map.get(selected_model_series, [])
selected_varian = st.sidebar.selectbox(
    '🔢 Pilih Varian',
    options=varian_options
)

selected_lokasi1 = st.sidebar.selectbox(
    '📍 Pilih Lokasi 1',
    options=lokasi_list,
    index=lokasi_list.index('DKI') if 'DKI' in lokasi_list else 0
)

selected_lokasi2 = st.sidebar.selectbox(
    '📍 Pilih Lokasi 2',
    options=lokasi_list,
    index=lokasi_list.index('Jawa Barat') if 'Jawa Barat' in lokasi_list else 1
)

# Tombol hitung
if st.sidebar.button('🔍 Hitung Selisih Harga'):
    with st.container():
        st.subheader("📊 Hasil Perbandingan Harga")

        try:
            price1_df = df[(df['Model Series'] == selected_model_series) &
                           (df['Varian'] == selected_varian) &
                           (df['Lokasi'] == selected_lokasi1)]

            price2_df = df[(df['Model Series'] == selected_model_series) &
                           (df['Varian'] == selected_varian) &
                           (df['Lokasi'] == selected_lokasi2)]

            if not price1_df.empty and not price2_df.empty:
                price1 = price1_df['Harga OTR'].iloc[0]
                price2 = price2_df['Harga OTR'].iloc[0]

                absolute_price_difference = abs(price1 - price2)

                if price1 != 0:
                    percentage_price_difference = ((price2 - price1) / price1) * 100
                else:
                    percentage_price_difference = float('inf') if price2 != 0 else 0

                col1, col2 = st.columns(2)

               with col1:
                    st.markdown(f"""
                    <p style='font-size: 20px;'><strong>Model Series:</strong> {selected_model_series}</p>
                    <p style='font-size: 20px;'><strong>Varian:</strong> {selected_varian}</p>
                    <p style='font-size: 20px;'><strong>Lokasi 1:</strong> {selected_lokasi1}</p>
                    <p style='font-size: 22px;'><strong>Harga Lokasi 1:</strong> 🏷️ <strong>Rp {price1:,.0f}</strong></p>
                    """, unsafe_allow_html=True)

                with col2:
                     st.markdown(f"""
                    <p style='font-size: 20px;'><strong>Lokasi 2:</strong> {selected_lokasi2}</p>
                    <p style='font-size: 22px;'><strong>Harga Lokasi 2:</strong> 🏷️ <strong>Rp {price2:,.0f}</strong></p>
                    <p style='font-size: 22px;'><strong>Selisih Harga Absolut:</strong> 💰 <strong>Rp {absolute_price_difference:,.0f}</strong></p>
                    """, unsafe_allow_html=True)

            if percentage_price_difference != float('inf'):
                    st.markdown(f"<p style='font-size: 22px;'><strong>Selisih Persentase:</strong> 📈 {percentage_price_difference:.2f}%</p>", unsafe_allow_html=True)
            else:
                st.markdown("<p style='font-size: 22px;'><strong>Selisih Persentase:</strong> 🔁 Tidak terdefinisi (Harga Lokasi 1 = 0)</p>", unsafe_allow_html=True)

            else:
                st.warning(f"⚠️ Data tidak ditemukan untuk kombinasi tersebut di {selected_lokasi1} atau {selected_lokasi2}.")

        except Exception as e:
            st.error(f"❌ Terjadi kesalahan: {e}")

