import streamlit as st
import pandas as pd
import googlemaps
import math
import datetime
import folium
import io
from streamlit_folium import folium_static
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from streamlit_geolocation import streamlit_geolocation

# 1. Panel Sayfa Ayarları (wide layout telefonda sütunları üst üste bindirir, temiz durur)
st.set_page_config(page_title="Ersan Dizayn Rota Paneli", layout="wide")
st.title("🚚 Ersan Dizayn Rota Kontrol Merkezi")

if 'harita_hazir' not in st.session_state:
    st.session_state.harita_hazir = False

# 2. MENÜ SİSTEMİ (SEKMELER)
# Ana sayfa akışını 3 temiz sekmeye bölüyoruz
tab_setup, tab_settings, tab_driver = st.tabs(["⚙️ Kurulum", "🔄 Rota Ayarları", "🗺️ Harita ve Şoför Modu"])

# --- SEKME 1: ⚙️ KURULUM (Girdiler) ---
with tab_setup:
    st.subheader("Kurulum ve Veri Girişi")
    col1, col2 = st.columns(2)
    with col1:
        api_key_input = st.text_input("Google Maps API Anahtarınız:", type="password", help="Dün Google'dan aldığımız o uzun AIza... ile başlayan şifre.")
    with col2:
        yuklenen_dosya_input = st.file_uploader("Sipariş Excel'i Yükle (.xlsx)", type=["xlsx"])
    
    if yuklenen_dosya_input:
        st.success("Excel dosyası başarıyla okundu. Lütfen '🔄 Rota Ayarları' sekmesine geçin.")

# --- SEKME 2: 🔄 ROTA AYARLARI (Seçimler ve Hesaplama) ---
with tab_settings:
    st.subheader("Güzergah Planlama")
    
    if not yuklenen_dosya_input:
        st.warning("🔄 Ayarları yapabilmek için önce '⚙️ Kurulum' sekmesinden Excel dosyasını yüklemelisiniz!")
    else:
        # Exceli Okuma ve Temizleme
        try:
            # Excel okumak için openpyxl gerekir (requirements.txt'de var)
            df_excel = pd.read_excel(yuklenen_dosya_input, usecols="H,I,J,P")
            df_excel.columns = ['Siparis_No', 'Alici_Ad', 'Adres', 'Telefon']
            df_excel = df_excel.dropna(subset=['Adres']).reset_index(drop=True)
            
            # Müşteri Listesini Sıra Numarasıyla Formatlama -> [1] Müşteri ➔ Adres
            musteri_listesi = [f"[{i+1}] {row['Alici_Ad']} ➔ {row['Adres']}" for i, row in df_excel.iterrows()]
            secenekler = ["🏢 Depo (Ersan Dizayn, İstanbul)", "📍 GPS ile Konumumu Al", "✍️ Farklı Bir Adres Yaz"] + musteri_listesi
            
            col_ayar1, col_ayar2 = st.columns(2)
            
            with col_ayar1:
                secilen_baslangic = st.selectbox("🟢 Başlangıç Noktası (Güne Nereden Başlıyorsun?):", secenekler, index=0)
                
            with col_ayar2:
                # Checkbox'ı varsayılan olarak kapalı yaptık ki Bitiş menüsü hemen görünsün (user requested)
                ring_rotasi = st.checkbox("🔄 Rotayı bitirince tekrar Başlangıç Noktasına dön", value=False)
                if not ring_rotasi:
                    secilen_bitis = st.selectbox("🔴 Bitiş Noktası (Günü Nerede Bitiriyorsun?):", secenekler, index=0)
                else:
                    secilen_bitis = secilen_baslangic
                    
            # Eğer GPS seçildiyse Konum Butonunu Göster
            gps_lazim = ("📍 GPS ile Konumumu Al" in [secilen_baslangic, secilen_bitis])
            loc = None
            if gps_lazim:
                st.info("👇 Lütfen mevcut konumunuzu almak için aşağıdaki butona basın ve tarayıcıdan izin verin.")
                loc = streamlit_geolocation()

            # Eğer Farklı Adres seçildiyse Metin Kutularını Göster
            ozel_baslangic = ""
            ozel_bitis = ""
            if secilen_baslangic == "✍️ Farklı Bir Adres Yaz":
                ozel_baslangic = st.text_input("🟢 Başlangıç Adresinizi Yazın:")
            if not ring_rotasi and secilen_bitis == "✍️ Farklı Bir Adres Yaz":
                ozel_bitis = st.text_input("🔴 Bitiş Adresinizi Yazın:")

            # HESAPLAMA BUTONU (Artık Ayarlar sekmesinin en altında)
            if st.button("🚀 Rotayı Hesapla ve Haritayı Çiz", use_container_width=True):
                if not api_key_input:
                    st.warning("Lütfen API Anahtarını 'Kurulum' sekmesine girin!")
                elif gps_lazim and not (loc and loc.get('latitude')):
                    st.warning("Lütfen GPS konumunuzu almak için yukarıdaki butona tıklayın!")
                elif secilen_baslangic == "✍️ Farklı Bir Adres Yaz" and not ozel_baslangic:
                    st.warning("Lütfen özel başlangıç adresini yazın!")
                elif not ring_rotasi and secilen_bitis == "✍️ Farklı Bir Adres Yaz" and not ozel_bitis:
                    st.warning("Lütfen özel bitiş adresini yazın!")
                else:
                    with st.spinner('📍 Adresler işleniyor, yapay zeka en kısa yolu buluyor...'):
                        try:
                            gmaps = googlemaps.Client(key=api_key_input)
                            
                            # --- BAŞLANGIÇ ADRESİNİ ÇÖZÜMLEME ---
                            start_adres, start_ad = "", ""
                            if secilen_baslangic == "🏢 Depo (Ersan Dizayn, İstanbul)":
                                start_adres, start_ad = "Ersan Dizayn, İstanbul", "🏢 DEPO"
                            elif secilen_baslangic == "📍 GPS ile Konumumu Al":
                                lat, lon = loc['latitude'], loc['longitude']
                                start_adres, start_ad = f"{lat},{lon}", "📍 ŞOFÖR (GPS)"
                            elif secilen_baslangic == "✍️ Farklı Bir Adres Yaz":
                                start_adres, start_ad = ozel_baslangic, "🟢 ÖZEL BAŞLANGIÇ"
                            else:
                                start_adres = secilen_baslangic.split(" ➔ ")[1]
                                start_ad = secilen_baslangic.split("] ")[1].split(" ➔ ")[0]

                            # --- BİTİŞ ADRESİNİ ÇÖZÜMLEME ---
                            end_adres, end_ad = "", ""
                            if not ring_rotasi:
                                if secilen_bitis == "🏢 Depo (Ersan Dizayn, İstanbul)":
                                    end_adres, end_ad = "Ersan Dizayn, İstanbul", "🏢 DEPO"
                                elif secilen_bitis == "📍 GPS ile Konumumu Al":
                                    lat, lon = loc['latitude'], loc['longitude']
                                    end_adres, end_ad = f"{lat},{lon}", "📍 ŞOFÖR (GPS)"
                                elif secilen_bitis == "✍️ Farklı Bir Adres Yaz":
                                    end_adres, end_ad = ozel_bitis, "🔴 ÖZEL BİTİŞ"
                                else:
                                    end_adres = secilen_bitis.split(" ➔ ")[1]
                                    end_ad = secilen_bitis.split("] ")[1].split(" ➔ ")[0]

                            # --- ROTA LİSTESİNİ OLUŞTURMA ---
                            nodes = []
                            nodes.append({'Siparis_No': 'START', 'Alici_Ad': start_ad, 'Adres': start_adres, 'Telefon': '-'})
                            
                            for idx, row in df_excel.iterrows():
                                if row['Adres'] == start_adres or (not ring_rotasi and row['Adres'] == end_adres):
                                    continue
                                nodes.append(row.to_dict())
                                
                            if not ring_rotasi:
                                nodes.append({'Siparis_No': 'END', 'Alici_Ad': end_ad, 'Adres': end_adres, 'Telefon': '-'})
                                
                            df = pd.DataFrame(nodes)

                            # --- KOORDİNAT BULMA ---
                            enlemler, boylamlar = [], []
                            for adres in df['Adres']:
                                if "," in str(adres) and str(adres).replace(',','').replace('.','').replace('-','').isdigit():
                                    lat, lon = adres.split(",")
                                    enlemler.append(float(lat))
                                    boylamlar.append(float(lon))
                                else:
                                    tam_adres = f"{adres}, Türkiye"
                                    try:
                                        res = gmaps.geocode(tam_adres)
                                        if res:
                                            enlemler.append(res[0]['geometry']['location']['lat'])
                                            boylamlar.append(res[0]['geometry']['location']['lng'])
                                        else:
                                            enlemler.append(0.0)
                                            boylamlar.append(0.0)
                                    except:
                                        enlemler.append(0.0)
                                        boylamlar.append(0.0)

                            df['Enlem'] = enlemler
                            df['Boylam'] = boylamlar
                            df = df[df['Enlem'] != 0.0].reset_index(drop=True)

                            # --- MESAFE MATRİSİ ---
                            def mesafe_hesapla(lat1, lon1, lat2, lon2):
                                R = 6371 
                                phi1, phi2 = math.radians(lat1), math.radians(lat2)
                                dphi = math.radians(lat2 - lat1)
                                dlambda = math.radians(lon2 - lon1)
                                a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
                                return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)) * 1000 

                            mesafe_matrisi = []
                            for i in range(len(df)):
                                satir = []
                                for j in range(len(df)):
                                    if i == j:
                                        satir.append(0)
                                    else:
                                        dist = mesafe_hesapla(df['Enlem'][i], df['Boylam'][i], df['Enlem'][j], df['Boylam'][j])
                                        satir.append(int(dist))
                                mesafe_matrisi.append(satir)

                            # --- OR-TOOLS YAPAY ZEKA ---
                            start_idx = 0
                            end_idx = 0 if ring_rotasi else len(df) - 1
                            
                            manager = pywrapcp.RoutingIndexManager(len(mesafe_matrisi), 1, [start_idx], [end_idx])
                            routing = pywrapcp.RoutingModel(manager)

                            def distance_callback(from_index, to_index):
                                from_node = manager.IndexToNode(from_index)
                                to_node = manager.IndexToNode(to_index)
                                return mesafe_matrisi[from_node][to_node]

                            transit_callback_index = routing.RegisterTransitCallback(distance_callback)
                            routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

                            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
                            search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

                            cozum = routing.SolveWithParameters(search_parameters)

                            if cozum:
                                index = routing.Start(0)
                                rota_sirasi = []
                                while not routing.IsEnd(index):
                                    rota_sirasi.append(manager.IndexToNode(index))
                                    index = cozum.Value(routing.NextVar(index))
                                
                                if ring_rotasi:
                                    rota_sirasi.append(0) 
                                else:
                                    rota_sirasi.append(end_idx)
                                    
                                sirali_df = df.iloc[rota_sirasi].copy().reset_index(drop=True)

                                # --- HARİTAYI NUMARALI ÇİZİM ---
                                baslangic_lat = sirali_df['Enlem'].iloc[0]
                                baslangic_lon = sirali_df['Boylam'].iloc[0]
                                m = folium.Map(location=[baslangic_lat, baslangic_lon], zoom_start=10)
                                
                                koordinat_listesi = []
                                for idx, row in sirali_df.iterrows():
                                    lat, lon = row['Enlem'], row['Boylam']
                                    koordinat_listesi.append((lat, lon))
                                    popup_text = f"<b>Durak {idx+1}</b><br>{row['Alici_Ad']}<br>Tel: {row['Telefon']}"
                                    
                                    # İğne Renkleri
                                    if idx == 0:
                                        renk_hex = '#43a047' # Yeşil (Başlangıç)
                                    elif idx == len(sirali_df)-1:
                                        renk_hex = '#ff4b4b' # Kırmızı (Bitiş)
                                    else:
                                        renk_hex = '#1e88e5' # Mavi (Teslimatlar)
                                        
                                    # Haritadaki iğnenin içine numara yazdıran özel HTML kodu
                                    marker_html = f'''
                                    <div style="background-color: {renk_hex}; color: white; border-radius: 50%; width: 26px; height: 26px; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 13px; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.5);">
                                        {idx+1}
                                    </div>
                                    '''
                                    folium.Marker(
                                        [lat, lon], 
                                        popup=popup_text, 
                                        tooltip=f"{idx+1}. Durak", 
                                        icon=folium.DivIcon(html=marker_html, icon_anchor=(13, 13))
                                    ).add_to(m)
                                    
                                folium.PolyLine(koordinat_listesi, color="#ff4b4b", weight=3, opacity=0.8).add_to(m)
                                
                                # Verileri Session State'e kaydet
                                st.session_state.m = m
                                st.session_state.sirali_df = sirali_df 
                                
                                buffer = io.BytesIO()
                                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                                    sirali_df.to_excel(writer, index=False)
                                st.session_state.buffer = buffer
                                st.session_state.dosya_adi = f"Ersan_Rota_{datetime.datetime.now().strftime('%H%M')}.xlsx"
                                
                                st.session_state.harita_hazir = True
                                st.success("✅ Rota hesaplandı! Lütfen final güzergahını görmek için '🗺️ Harita ve Şoför Modu' sekmesine geçin.")

                        except Exception as e:
                            st.error(f"Bir hata oluştu: {e}")

        except Exception as e:
            st.error(f"Excel okunurken hata oluştu (openpyxl eksik olabilir): {e}")

# --- SEKME 3: 🗺️ HARİTA VE ŞOFÖR MODU (Sonuçlar) ---
with tab_driver:
    st.subheader("Final Güzergahı")
    
    if not st.session_state.harita_hazir:
        st.warning("🗺️ Rota ekranını görebilmek için önce '🔄 Rota Ayarları' sekmesinden hesaplama yapmalısınız!")
    else:
        st.success("✅ Rota, belirlediğiniz ayarlara göre optimize edildi!")
        
        # Telefonda bu sütunlar üst üste biner, çok temiz durur
        harita_sutunu, liste_sutunu = st.columns([6, 4])
        
        with harita_sutunu:
            st.markdown("**🗺️ Güzergah Haritası**")
            folium_static(st.session_state.m, width=700, height=500)
            st.download_button(
                label="📥 Optimize Edilmiş Rotayı Excel Olarak İndir",
                data=st.session_state.buffer,
                file_name=st.session_state.dosya_adi,
                mime="application/vnd.ms-excel"
            )
            
        with liste_sutunu:
            st.markdown("### 📱 Şoför Modu (Teslimat Sırası)")
            # Telefondaki kaydırılabilir kart listesi
            with st.container(height=500):
                for idx, row in st.session_state.sirali_df.iterrows():
                    durak_no = idx + 1
                    lat = row['Enlem']
                    lon = row['Boylam']
                    
                    # Telefon numarasını temizle ve formatla
                    tel_temiz = "".join(filter(str.isdigit, str(row['Telefon'])))
                    if tel_temiz.startswith("0"):
                        tel_temiz = "9" + tel_temiz
                    if not tel_temiz.startswith("90") and len(tel_temiz) == 10:
                        tel_temiz = "90" + tel_temiz
                    
                    if durak_no == 1:
                        border_color, durak_etiketi = "#43a047", "BAŞLANGIÇ NOKTASI"
                    elif durak_no == len(st.session_state.sirali_df):
                        border_color, durak_etiketi = "#ff4b4b", "BİTİŞ NOKTASI"
                    else:
                        border_color, durak_etiketi = "#1e88e5", "TESLİMAT"
                    
                    # HTML KART TASARIMI (Sol Yaslı)
                    kart_html = f"""
<div style="background-color: #262730; padding: 15px; border-radius: 12px; margin-bottom: 15px; border-left: 6px solid {border_color}; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<span style="background-color: {border_color}; color: white; padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 14px;">{durak_no}</span>
<span style="color: #9c9c9c; font-size: 12px; font-weight: bold;">{durak_etiketi}</span>
</div>
<div style="font-size: 18px; font-weight: bold; color: white; margin-bottom: 5px;">{row['Alici_Ad']}</div>
<div style="font-size: 13px; color: #cfcfcf; margin-bottom: 15px; line-height: 1.4;">📍 {row['Adres']}</div>
<div style="display: flex; gap: 8px;">
<a href="https://www.google.com/maps/dir/?api=1&destination={lat},{lon}" target="_blank" style="flex: 1; background-color: #1e88e5; color: white; text-align: center; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 14px;">🗺️ Git</a>
<a href="tel:{tel_temiz}" style="flex: 1; background-color: #43a047; color: white; text-align: center; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 14px;">📞 Ara</a>
<a href="https://wa.me/{tel_temiz}" target="_blank" style="flex: 1; background-color: #25d366; color: white; text-align: center; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 14px;">💬 WP</a>
</div>
</div>
"""
                    st.markdown(kart_html, unsafe_allow_html=True)
