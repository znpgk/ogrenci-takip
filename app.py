import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Sayfa Ayarları
st.set_page_config(page_title="Öğrenci Değerlendirme Sistemi", layout="wide")

st.title("🎨 Öğrenci Değerlendirme ve Takip Formu")
st.write("Google kısıtlamalarından bağımsız, tarayıcı tabanlı değerlendirme ve Excel raporlama sistemi.")

# 1. Google Sheets'ten Sadece Aktif Öğrencileri Okuyoruz
try:
    RAW_SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    # URL içinden sadece Tablo ID'sini güvenli bir şekilde cımbızla çekiyoruz
    if "/d/" in RAW_SHEET_URL:
        sheet_id = RAW_SHEET_URL.split("/d/")[1].split("/")[0]
    else:
        sheet_id = RAW_SHEET_URL
        
    # Doğru ve standart Google CSV indirme link yapısı
    url_ogrenciler = f"https://google.com{sheet_id}/export?format=csv&sheet=Aktif_Ogrenciler"
    df_ogrenciler = pd.read_csv(url_ogrenciler)
except Exception as e:
    st.error(f"Öğrenci listesi okunamadı. Lütfen Secrets alanındaki linki kontrol edin. Hata: {e}")
    st.stop()

if df_ogrenciler.empty or "ADI SOYADI" not in df_ogrenciler.columns:
    st.warning("⚠️ 'Aktif_Ogrenciler' sekmesinde veri bulunamadı veya başlıklar hatalı.")
    st.stop()

# 2. Oturum Hafızası (Girdiğiniz notların tarayıcıda birikmesi için)
if "gecmis_notlar" not in st.session_state:
    st.session_state.gecmis_notlar = []

# 3. Üst Panel: Öğrenci Seçimi
st.markdown("### 📋 1. Öğrenci ve Dönem Bilgisi")
col1, col2, col3 = st.columns(3)

with col1:
    df_ogrenciler["Arama_Metni"] = df_ogrenciler["ADI SOYADI"].astype(str) + " (" + df_ogrenciler["NUMARASI"].astype(str) + ")"
    secilen_ogrenci_metin = st.selectbox("Değerlendirilecek Öğrenciyi Seçin:", df_ogrenciler["Arama_Metni"].tolist())
    
    ogrenci_satir = df_ogrenciler[df_ogrenciler["Arama_Metni"] == secilen_ogrenci_metin].iloc[0]
    ogrenci_adi = ogrenci_satir["ADI SOYADI"]
    ogrenci_no = ogrenci_satir["NUMARASI"]

with col2:
    varsayilan_sinif = str(ogrenci_satir["SEVIYE/SINIF"])
    siniflar = ["4 Yaş", "5 Yaş", "1 . Sın.", "2 . Sın.", "3 . Sın.", "4 . Sın."]
    if varsayilan_sinif not in siniflar:
        siniflar.append(varsayilan_sinif)
    secilen_sinif = st.selectbox("Seviye / Sınıf:", siniflar, index=siniflar.index(varsayilan_sinif))

with col3:
    guncel_yil = str(datetime.now().year)
    degerlendirme_yili = st.text_input("Tarih / Yıl:", value=guncel_yil)

st.divider()

# 4. Kriterler Paneli
st.markdown("### 📊 2. Kriter Değerlendirmesi")
st.caption("5: Fazlasıyla | 4: Sıklıkla | 3: Değişken/Bazen | 2: Nadiren | 1: Hiçbir Zaman")

kriterler = [
    "Derse girince öğretmenini uygun bir şekilde bekler.", "Malzemelerini eksiksiz ve uygun şekilde getirir.",
    "Çalışma süresince temiz ve düzenlidir.", "Ders sonunda ortamı temiz ve düzenli bırakır.",
    "Arkadaşlarının, kendinin ve okulun eşyalarına zarar vermez.", "Zamanını verimli biçimde kullanır, sıkılmadan çalışır.",
    "Arkadaşlarıyla işbirliği içinde ve saygılıdır.", "Konuyla ilgili bilgi alış verişinde bulunur.",
    "Duygu, düşünce ve hayallerini çalışmasında yansıtır.", "Farklı uygulama yöntem ve teknikleri denemeye açıktır.",
    "Çeşitli konularda resim ve çizim yapmaktan hoşlanır.", "Resimleri planlar, kompozisyonu parçalar arası uyumludur .",
    "Çalışmalarında hayal gücünü kullanır özgün yorumlar getirir.", "Verilen konuya uygun görsel sanat çalışmaları yapar.",
    "Verilen konuyu özgün bakış açısıyla ifede eder.", "3 boyutlu çalışmalar yapmaya ilgilidir.",
    "Problem durumlarına yönelik çözüm (fikir, malzeme) üretir.", "Sorumluluk almaya isteklidir.",
    "Farklı malzemeleri biraraya getirerek tasarımlar oluştururur.", "Sanata ve sanatçı eserlerine karşı ilgi duyar."
]

puanlar = {}
k_col1, k_col2 = st.columns(2)

for idx, kriter in enumerate(kriterler, 1):
    hedef_sutun = k_col1 if idx <= 10 else k_col2
    with hedef_sutun:
        puanlar[f"K{idx}"] = st.radio(f"**{idx}.** {kriter}", options=[5, 4, 3, 2, 1], index=2, key=f"kr_{idx}")

st.divider()

# 5. Açıklamalar ve Listeye Ekleme
st.markdown("### ✍️ 3. Açıklamalar ve Eylem Planı")
eylem_plani = st.text_area("Öğrenciyle ilgili açıklamalar ve eylem planları:", height=120)

if st.button("➕ DEĞERLENDİRMEYİ LİSTEYE EKLE", type="primary"):
    yeni_kayit = {
        "TARIH_YIL": degerlendirme_yili,
        "ADI_SOYADI": ogrenci_adi,
        "NUMARASI": ogrenci_no,
        "SEVIYE_SINIF": secilen_sinif,
        **puanlar,
        "ACIKLAMA_EYLEM_PLANI": eylem_plani
    }
    st.session_state.gecmis_notlar.append(yeni_kayit)
    st.success(f"🎉 {ogrenci_adi} başarıyla geçici listeye eklendi! Sayfayı kapatmadan veya yenilemeden önce en alttaki butondan Excel dosyanızı indirmeyi unutmayın.")

st.divider()

# 6. Mevcut Eklenenleri Gösterme ve Excel İndirme Paneli
st.markdown("### 📥 4. Eklenen Değerlendirmeler ve Excel Çıktısı Al")

if st.session_state.gecmis_notlar:
    df_rapor = pd.DataFrame(st.session_state.gecmis_notlar)
    st.dataframe(df_rapor[["TARIH_YIL", "ADI_SOYADI", "NUMARASI", "SEVIYE_SINIF", "ACIKLAMA_EYLEM_PLANI"]], use_container_width=True)
    
    # Excel'e Dönüştürme Bellek Ayarı
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_rapor.to_excel(writer, index=False, sheet_name='Degerlendirmeler')
    
    st.download_button(
        label="📥 TÜM LİSTEYİ EXCEL OLARAK BİLGİSAYARA İNDİR",
        data=buffer.getvalue(),
        file_name=f"Ogrenci_Degerlendirme_Raporu_{guncel_yil}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.info("Henüz bu oturumda listeye eklenmiş bir değerlendirme yok. Yukarıdaki formdan öğrencileri eklemeye başlayabilirsiniz.")

