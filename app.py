import streamlit as st
import pandas as pd
import numpy as np

st.title('Perbandingan Harga Mobil Baru Antar Lokasi')
st.write('Pilih model, varian, dan dua lokasi untuk melihat selisih harga OTR.')

# Load Data
df = pd.read_excel('harga_mobil_baru.xlsx')

# Konversi kolom harga ke numerik
df['Harga OTR'] = pd.to_numeric(df['Harga OTR'], errors='coerce')

# Buat kamus varian per model series
model_varian_map = df.groupby('Model Series')['Varian'].unique().apply(list).to_dict()

# Buat daftar pilihan unik untuk lokasi
lokasi_list = df['Lokasi'].unique().tolist()

# Create dropdowns for Model Series, Varian, Lokasi 1, and Lokasi 2
selected_model_series = st.selectbox(
    'Pilih Model Series:',
    options=list(model_varian_map.keys())
)

# Get variants for the selected Model Series
varian_options = model_varian_map.get(selected_model_series, [])
selected_varian = st.selectbox(
    'Pilih Varian:',
    options=varian_options
)

selected_lokasi1 = st.selectbox(
    'Pilih Lokasi 1:',
    options=lokasi_list,
    index=lokasi_list.index('DKI') if 'DKI' in lokasi_list else 0 # Default to DKI if available
)

selected_lokasi2 = st.selectbox(
    'Pilih Lokasi 2:',
    options=lokasi_list,
    index=lokasi_list.index('Jawa Barat') if 'Jawa Barat' in lokasi_list else (lokasi_list.index('DKI') + 1) % len(lokasi_list) if 'DKI' in lokasi_list else 1 # Default to Jawa Barat or next location
)

# Button to trigger calculation
if st.button('Hitung Selisih Harga'):
    try:
        # Get prices for the selected varian in the two locations
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

            # Calculate percentage price difference, handling division by zero
            if price1 != 0:
                percentage_price_difference = ((price2 - price1) / price1) * 100
            else:
                percentage_price_difference = float('inf') if price2 != 0 else 0 # Handle case where price1 is zero

            st.write(f"**Model Series:** {selected_model_series}")
            st.write(f"**Varian:** {selected_varian}")
            st.write(f"**Lokasi 1:** {selected_lokasi1} (Harga: Rp {price1:,.0f})")
            st.write(f"**Lokasi 2:** {selected_lokasi2} (Harga: Rp {price2:,.0f})")
            st.write(f"**Selisih Harga Absolut:** Rp {absolute_price_difference:,.0f}")
            if percentage_price_difference != float('inf'):
                 st.write(f"**Selisih Harga Persentase:** {percentage_price_difference:.2f}%")
            else:
                 st.write(f"**Selisih Harga Persentase:** Infinite (Harga Lokasi 1 adalah nol)")

        else:
            st.warning(f"Data tidak ditemukan untuk {selected_model_series} - {selected_varian} "
                       f"di salah satu atau kedua lokasi terpilih ({selected_lokasi1}, {selected_lokasi2}).")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
