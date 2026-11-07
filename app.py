import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# Sayfa Genişlik Ayarı
st.set_page_config(page_title="Öğrenci Değerlendirme Sistemi", layout="wide")

st.title("🎨 Öğrenci Değerlendirme ve Takip Formu")
st.write("Her yıl yenilenen liste üzerinden öğrenci değerlendirme sistemi.")

# 1. Google Sheets Bağlantısı
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Verileri Google Sheets'ten oku
    df_ogrenciler = conn.read(worksheet="Aktif_Ogrenciler", ttl="0")
    df_gecmis = conn.read(worksheet="Degerlendirmeler", ttl="0")
except Exception as e:
    st.error(f"Veritabanına bağlanılamadı. Hata Detayı: {e}")
    st.info("Lütfen Streamlit Advanced Settings -> Secrets kısmındaki link yapısını ve Google Sheets sekme isimlerini kontrol edin.")
    st.stop()

# Güvenlik Kontrolü: Boş tablo kontrolü
if df_ogrenciler.empty or "ADI SOYADI" not in df_ogrenciler.columns:
    st.warning("⚠️ 'Aktif_Ogrenciler' sekmesinde öğrenci verisi bulunamadı veya sütun başlıkları (ADI SOYADI, NUMARASI, SEVIYE/SINIF) hatalı.")
    st.stop()

# 2. Üst Panel: Öğrenci Seçimi ve Genel Bilgiler
st.markdown("### 📋 1. Öğrenci ve Dönem Bilgisi")
col1, col2, col3 = st.columns(3)

with col1:
    # Öğrenci Arama Alanı (Ad Soyadı - Numara birleşik gösterim)
    df_ogrenciler["Arama_Metni"] = df_ogrenciler["ADI SOYADI"].astype(str) + " (" + df_ogrenciler["NUMARASI"].astype(str) + ")"
    secilen_ogrenci_metin = st.selectbox("Değerlendirilecek Öğrenciyi Seçin:", df_ogrenciler["Arama_Metni"].tolist())
    
    # Seçilen öğrencinin ham bilgilerini ayıkla
    ogrenci_satir = df_ogrenciler[df_ogrenciler["Arama_Metni"] == secilen_ogrenci_metin].iloc[0]
    ogrenci_adi = ogrenci_satir["ADI SOYADI"]
    ogrenci_no = ogrenci_satir["NUMARASI"]

with col2:
    # Sınıf Bilgisi
    varsayilan_sinif = str(ogrenci_satir["SEVIYE/SINIF"])
    siniflar = ["4 Yaş", "5 Yaş", "1 . Sın.", "2 . Sın.", "3 . Sın.", "4 . Sın."]
    if varsayilan_sinif not in siniflar:
        siniflar.append(varsayilan_sinif)
    secilen_sinif = st.selectbox("Seviye / Sınıf:", siniflar, index=siniflar.index(varsayilan_sinif))

with col3:
    # Değerlendirme Yılı
    guncel_yil = str(datetime.now().year)
    degerlendirme_yili = st.text_input("Tarih / Yıl:", value=guncel_yil)

st.divider()

# 3. Orta Panel: 20 Kriter ve Puanlama
st.markdown("### 📊 2. Kriter Değerlendirmesi")
st.caption("5: Fazlasıyla | 4: Sıklıkla | 3: Değişken/Bazen | 2: Nadiren | 1: Hiçbir Zaman")

kriterler = [
    "Derse girince öğretmenini uygun bir şekilde bekler.",
    "Malzemelerini eksiksiz ve uygun şekilde getirir.",
    "Çalışma süresince temiz ve düzenlidir.",
    "Ders sonunda ortamı temiz ve düzenli bırakır.",
    "Arkadaşlarının, kendinin ve okulun eşyalarına zarar vermez.",
    "Zamanını verimli biçimde kullanır, sıkılmadan çalışır.",
    "Arkadaşlarıyla işbirliği içinde ve saygılıdır.",
    "Konuyla ilgili bilgi alış verişinde bulunur.",
    "Duygu, düşünce ve hayallerini çalışmasında yansıtır.",
    "Farklı uygulama yöntem ve teknikleri denemeye açıktır.",
    "Çeşitli konularda resim ve çizim yapmaktan hoşlanır.",
    "Resimleri planlar, kompozisyonu parçalar arası uyumludur .",
    "Çalışmalarında hayal gücünü kullanır özgün yorumlar getirir.",
    "Verilen konuya uygun görsel sanat çalışmaları yapar.",
    "Verilen konuyu özgün bakış açısıyla ifede eder.",
    "3 boyutlu çalışmalar yapmaya ilgilidir.",
    "Problem durumlarına yönelik çözüm (fikir, malzeme) üretir.",
    "Sorumluluk almaya isteklidir.",
    "Farklı malzemeleri biraraya getirerek tasarımlar oluştururur.",
    "Sanata ve sanatçı eserlerine karşı ilgi duyar."
]

puanlar = {}
k_col1, k_col2 = st.columns(2)

for idx, kriter in enumerate(kriterler, 1):
    hedef_sutun = k_col1 if idx <= 10 else k_col2
    with hedef_sutun:
        puanlar[f"K{idx}"] = st.radio(
            f"**{idx}.** {kriter}",
            options=[5, 4, 3, 2, 1],
            format_func=lambda x: {5:"5 - Fazlasıyla", 4:"4 - Sıklıkla", 3:"3 - Bazen", 2:"2 - Nadiren", 1:"1 - Hiçbir Zaman"}[x],
            index=2,
            key=f"kriter_{idx}"
        )

st.divider()

# 4. Alt Panel: Eylem Planı ve Kaydetme
st.markdown("### ✍️ 3. Açıklamalar ve Eylem Planı")
eylem_plani = st.text_area("Öğrenciyle ilgili açıklamalar ve eylem planları:", height=150)

if st.button("💾 DEĞERLENDİRMEYİ KAYDET", type="primary"):
    yeni_kayit = {
        "TARIH_YIL": str(degerlendirme_yili),
        "ADI_SOYADI": str(ogrenci_adi),
        "NUMARASI": str(ogrenci_no),
        "SEVIYE_SINIF": str(secilen_sinif),
        **puanlar,
        "ACIKLAMA_EYLEM_PLANI": str(eylem_plani)
    }
    
    df_yeni = pd.DataFrame([yeni_kayit])
    df_guncel_degerlendirmeler = pd.concat([df_gecmis, df_yeni], ignore_index=True)
    
    try:
        conn.update(worksheet="Degerlendirmeler", data=df_guncel_degerlendirmeler)
        st.success(f"🎉 {ogrenci_adi} için {degerlendirme_yili} yılı değerlendirmesi başarıyla kaydedildi!")
        st.cache_data.clear() # Önbelleği temizle ki yeni kayıt hemen görünsün
    except Exception as e:
        st.error(f"Kayıt sırasında bir hata oluştu: {e}")

st.divider()

# 5. En Alt Panel: Geçmiş Kayıtlar
st.markdown(f"### 🕒 {ogrenci_adi} - Geçmiş Yıl Değerlendirmeleri")
if not df_gecmis.empty and "NUMARASI" in df_gecmis.columns:
    ogrenci_gecmis = df_gecmis[df_gecmis["NUMARASI"].astype(str) == str(ogrenci_no)]
    if not ogrenci_gecmis.empty:
        gosterilecek_gecmis = ogrenci_gecmis[["TARIH_YIL", "SEVIYE_SINIF", "ACIKLAMA_EYLEM_PLANI"]]
        st.dataframe(gosterilecek_gecmis, use_container_width=True, hide_index=True)
    else:
        st.info("Bu öğrenciye ait geçmiş yıllara dair bir kayıt bulunamadı.")
else:
    st.info("Henüz sistemde hiç geçmiş değerlendirme kaydı yok.")
