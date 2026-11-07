import streamlit as st
import pandas as pd
from datetime import datetime

# Sayfa Genişlik Ayarı
st.set_page_config(page_title="Öğrenci Değerlendirme Sistemi", layout="wide")

st.title("🎨 Öğrenci Değerlendirme ve Takip Formu")
st.write("Google Sheets tabanlı doğrudan veri okuma ve değerlendirme arayüzü.")

# CRITICAL CONFIGURATION: Secrets alanından linki çek
try:
    # Kullanıcının secrets alanına yazdığı linki al
    RAW_SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    # ID'yi ayıkla ve doğrudan CSV indirme linkine dönüştür
    if "/d/" in RAW_SHEET_URL:
        sheet_id = RAW_SHEET_URL.split("/d/")[1].split("/")[0]
    else:
        sheet_id = RAW_SHEET_URL
        
    # Her iki sekmeyi de doğrudan Google'ın ham export URL'sinden hatasız oku
    url_ogrenciler = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Aktif_Ogrenciler"
    url_gecmis = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Degerlendirmeler"
    
    df_ogrenciler = pd.read_csv(url_ogrenciler)
    try:
        df_gecmis = pd.read_csv(url_gecmis)
    except:
        df_gecmis = pd.DataFrame() # Eğer tablo henüz tamamen boşsa hata verme
        
except Exception as e:
    st.error(f"Bağlantı parametreleri çözümlenemedi: {e}")
    st.info("Lütfen Advanced Settings -> Secrets alanında 'spreadsheet' linkinin doğru tanımlandığından emin olun.")
    st.stop()

# Güvenlik Kontrolü: Sütun isimleri kontrolü
if df_ogrenciler.empty or "ADI SOYADI" not in df_ogrenciler.columns:
    st.warning("⚠️ Google Sheets 'Aktif_Ogrenciler' sekmesinde veri bulunamadı veya başlıklar hatalı. İlk satır mutlaka büyük harflerle 'ADI SOYADI', 'NUMARASI', 'SEVIYE/SINIF' olmalıdır.")
    st.stop()

# 2. Üst Panel: Öğrenci Seçimi ve Genel Bilgiler
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

# 3. Kriterler Panel
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

# 4. Açıklamalar ve Kayıt Formu Mantığı
st.markdown("### ✍️ 3. Açıklamalar ve Eylem Planı")
eylem_plani = st.text_area("Öğrenciyle ilgili açıklamalar ve eylem planları:", height=120)

# Not: Web tarayıcısı üzerinden doğrudan kaydetme için Google Apps Script entegrasyonu aşamasına geçmeden önce ekranın gelmesini doğrulayalım.
if st.button("💾 VERİLERİ HESAPLA VE EKRANDA GÖSTER", type="primary"):
    st.success("Veri yapısı hazırlandı! Google Sheets API kısıtlamasını aşmak için form ekranınız başarıyla bağlandı.")
    st.json({
        "YIL": degerlendirme_yili, "OGRENCI": ogrenci_adi, "NO": str(ogrenci_no), "SINIF": secilen_sinif,
        "PUANLAR": puanlar, "NOT": eylem_plani
    })

st.divider()

# 5. Geçmiş Listeleme
st.markdown(f"### 🕒 {ogrenci_adi} - Geçmiş Yıl Değerlendirmeleri")
if not df_gecmis.empty and "NUMARASI" in df_gecmis.columns:
    ogrenci_gecmis = df_gecmis[df_gecmis["NUMARASI"].astype(str) == str(ogrenci_no)]
    if not ogrenci_gecmis.empty:
        st.dataframe(ogrenci_gecmis[["TARIH_YIL", "SEVIYE_SINIF", "ACIKLAMA_EYLEM_PLANI"]], use_container_width=True, hide_index=True)
    else:
        st.info("Bu öğrenciye ait geçmiş kayıt bulunamadı.")
else:
    st.info("Henüz sistemde hiç geçmiş veri kaydı yok.")
