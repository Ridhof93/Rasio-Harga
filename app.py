import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ✅ Konfigurasi halaman
st.set_page_config(
    page_title="Perbandingan Harga Mobil 🚗💸",
    layout="wide",
    page_icon="🚗"
)

# ✅ Judul dan deskripsi aplikasi
st.markdown("""
<h1 style='font-size: 40px;'>🚗 Perbandingan Harga Mobil Baru Antar Lokasi</h1>
<p style='font-size: 20px;'>Selamat datang! Gunakan sidebar di kiri untuk memilih model, varian, dan lokasi perbandingan harga <strong>OTR</strong> (On The Road).</p>
""", unsafe_allow_html=True)

# ✅ Sidebar untuk input
st.sidebar.header("🔧 Filter")

# Load data
df = pd.read_excel('harga_mobil_baru.xlsx')
df['Harga OTR'] = pd.to_numeric(df['Harga OTR'], errors='coerce')

# Dropdown options
model_varian_map = df.groupby('Model Series')['Varian'].unique().apply(list).to_dict()
lokasi_list = df['Lokasi'].unique().tolist()

selected_model_series = st.sidebar.selectbox('🚘 Pilih Model Series', options=list(model_varian_map.keys()))
varian_options = model_varian_map.get(selected_model_series, [])
selected_varian = st.sidebar.selectbox('🔢 Pilih Varian', options=varian_options)
selected_lokasi1 = st.sidebar.selectbox('📍 Pilih Lokasi 1', options=lokasi_list, index=lokasi_list.index('DKI') if 'DKI' in lokasi_list else 0)
selected_lokasi2 = st.sidebar.selectbox('📍 Pilih Lokasi 2', options=lokasi_list, index=lokasi_list.index('Jawa Barat') if 'Jawa Barat' in lokasi_list else 1)

# Hitung dan tampilkan
if st.sidebar.button('🔍 Hitung Selisih Harga'):
    st.subheader("📊 Hasil Perbandingan Harga")

    try:
        price1_df = df[(df['Model Series'] == selected_model_series) & (df['Varian'] == selected_varian) & (df['Lokasi'] == selected_lokasi1)]
        price2_df = df[(df['Model Series'] == selected_model_series) & (df['Varian'] == selected_varian) & (df['Lokasi'] == selected_lokasi2)]

        if not price1_df.empty and not price2_df.empty:
            price1 = price1_df['Harga OTR'].iloc[0]
            price2 = price2_df['Harga OTR'].iloc[0]
            absolute_price_difference = abs(price1 - price2)
            percentage_price_difference = ((price2 - price1) / price1 * 100) if price1 != 0 else float('inf')

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                    <p style='font-size: 20px;'><strong>Model Series:</strong> {selected_model_series}</p>
                    <p style='font-size: 20px;'><strong>Varian:</strong> {selected_varian}</p>
                    <p style='font-size: 20px;'><strong>Lokasi 1:</strong> {selected_lokasi1}</p>
                    <p style='font-size: 22px;'><strong>Harga Lokasi 1:</strong> 🏷️ <strong>Rp {price1:,.0f}</strong></p>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                    <p style='font-size: 20px;'><strong>Model Series:</strong> {selected_model_series}</p>
                    <p style='font-size: 20px;'><strong>Varian:</strong> {selected_varian}</p>
                    <p style='font-size: 20px;'><strong>Lokasi 2:</strong> {selected_lokasi2}</p>
                    <p style='font-size: 22px;'><strong>Harga Lokasi 2:</strong> 🏷️ <strong>Rp {price2:,.0f}</strong></p>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                    <p style='font-size: 22px;'><strong>Selisih Harga Absolut:</strong> 💰 <strong>Rp {absolute_price_difference:,.0f}</strong></p>
                """, unsafe_allow_html=True)

                if percentage_price_difference != float('inf'):
                    st.markdown(
                        f"<p style='font-size: 22px;'><strong>Selisih Persentase:</strong> 📈 {percentage_price_difference:.2f}%</p>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        "<p style='font-size: 22px;'><strong>Selisih Persentase:</strong> 🔁 Tidak terdefinisi (Harga Lokasi 1 = 0)</p>",
                        unsafe_allow_html=True
                    )

            # ✅ Data hasil perbandingan
            hasil_df = pd.DataFrame({
                'Model Series': [selected_model_series],
                'Varian': [selected_varian],
                f'Harga {selected_lokasi1}': [price1],
                f'Harga {selected_lokasi2}': [price2],
                'Selisih Harga (Rp)': [absolute_price_difference],
                'Selisih Persentase (%)': [None if percentage_price_difference == float('inf') else round(percentage_price_difference, 2)]
            })

            # ✅ Download ke Excel
            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Perbandingan Harga')
                return output.getvalue()

            excel_data = to_excel(hasil_df)
            st.download_button("📥 Download Hasil ke Excel", data=excel_data, file_name="perbandingan_harga.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            # ✅ Download ke PDF
            def create_pdf(df):
                output = BytesIO()
                doc = SimpleDocTemplate(output, pagesize=A4)
                styles = getSampleStyleSheet()
                story = [Paragraph("Hasil Perbandingan Harga Mobil", styles['Title']), Spacer(1, 12)]

                for col in df.columns:
                    story.append(Paragraph(f"<strong>{col}:</strong> {df[col][0]}", styles['Normal']))
                    story.append(Spacer(1, 6))

                doc.build(story)
                return output.getvalue()

            pdf_data = create_pdf(hasil_df)
            st.download_button("📄 Download Hasil ke PDF", data=pdf_data, file_name="perbandingan_harga.pdf", mime="application/pdf")

        else:
            st.warning("⚠️ Data tidak ditemukan untuk kombinasi tersebut.")
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan: {e}")
