import streamlit as st
import pandas as pd
import googlemaps
import math
import datetime
import folium
import io
import re
from streamlit_folium import folium_static
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from streamlit_geolocation import streamlit_geolocation

# ==========================================
# 🔑 GOOGLE MAPS API ANAHTARINI BURAYA YAZ 🔑
# ==========================================
GOOGLE_MAPS_API_KEY = "BURAYA_KENDI_API_ANAHTARINI_YAZ"

# 1. Panel Sayfa Ayarları
st.set_page_config(page_title="Ersan Dizayn Rota Paneli", layout="wide", initial_sidebar_state="collapsed")

# 🌟 PREMIUM TASARIM CSS ENJEKSİYONU 🌟
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 24px;
        background-color: #1e1e24;
        border: 1px solid #333;
        border-bottom: none;
        color: #a0a0a0;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2b2b36 !important;
        color: white !important;
        border-top: 3px solid #1e88e5;
        box-shadow: 0 -4px 10px rgba(0,0,0,0.1);
    }
    
    /* İletişim / Yol Tarifi Butonları (Kart İçi HTML) */
    .action-btn {
        flex: 1;
        text-align: center;
        padding: 12px 0;
        border-radius: 10px;
        text-decoration: none !important;
        font-weight: 600;
        font-size: 14px;
        color: white !important;
        transition: all 0.3s ease;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 6px;
    }
    .btn-maps { background: linear-gradient(135deg, #1e88e5, #1565c0); box-shadow: 0 4px 10px rgba(30,136,229,0.3); }
    .btn-maps:hover { background: linear-gradient(135deg, #2196f3, #1976d2); transform: scale(1.02); }
    
    .btn-call { background: linear-gradient(135deg, #43a047, #2e7d32); box-shadow: 0 4px 10px rgba(67,160,71,0.3); }
    .btn-call:hover { background: linear-gradient(135deg, #4caf50, #388e3c); transform: scale(1.02); }
    
    .btn-wp { background: linear-gradient(135deg, #25d366, #128c7e); box-shadow: 0 4px 10px rgba(37,211,102,0.3); }
    .btn-wp:hover { background: linear-gradient(135deg, #2ae06d, #159f8e); transform: scale(1.02); }
    
    /* 🌟 STREAMLIT BUTONLARI (Şerit Liste Mantığı) 🌟 */
    div[data-testid="stButton"] button {
        background-color: #2b2b36;
        color: white;
        border: 1px solid #444;
        border-radius: 8px;
        padding: 14px 16px;
        font-weight: 500;
        letter-spacing: 0.3px;
        transition: all 0.2s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
        justify-content: flex-start !important; /* Yazıyı sola yaslar (Liste görünümü) */
        text-align: left !important;
    }
    div[data-testid="stButton"] button:hover {
        background-color: #3b3b46;
        border-color: #1e88e5;
        transform: translateY(-2px);
    }
    
    /* Ana Aksiyon Butonları (İleri, Hesapla vb. ORTALANSIN) */
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, #1e88e5, #1565c0);
        border: none;
        justify-content: center !important;
        text-align: center !important;
        font-weight: 700;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2196f3, #1976d2);
    }
</style>
""", unsafe_allow_html=True)

st.title("🚚 Ersan Dizayn Rota Kontrol Merkezi")

# SESSION STATE DEĞİŞKENLERİ
if 'harita_hazir' not in st.session_state: st.session_state.harita_hazir = False
if 'wizard_step' not in st.session_state: st.session_state.wizard_step = 0
if 'validated_data' not in st.session_state: st.session_state.validated_data = []
if 'validation_complete' not in st.session_state: st.session_state.validation_complete = False
if 'awaiting_confirmation' not in st.session_state: st.session_state.awaiting_confirmation = False
if 'temp_selection' not in st.session_state: st.session_state.temp_selection = None
if 'temp_lat' not in st.session_state: st.session_state.temp_lat = None
if 'temp_lng' not in st.session_state: st.session_state.temp_lng = None
if 'delivery_status' not in st.session_state: st.session_state.delivery_status = {} 

tab_kurulum, tab_harita = st.tabs(["📂 1. Veri Yükleme ve Doğrulama", "🗺️ 2. Planlama ve Harita"])

# --- SEKME 1: 📂 VERİ YÜKLEME VE ADRES DOĞRULAMA ---
with tab_kurulum:
    st.markdown("### ⚙️ Sistem Kurulumu")
    yuklenen_dosya_input = st.file_uploader("Sipariş Excel'i Yükle (.xlsx)", type=["xlsx"])

    if yuklenen_dosya_input:
        if GOOGLE_MAPS_API_KEY == "BURAYA_KENDI_API_ANAHTARINI_YAZ":
            st.error("⚠️ Lütfen kodun en üstündeki GOOGLE_MAPS_API_KEY değişkenine kendi API anahtarınızı yapıştırın!")
            st.stop()
            
        if 'uploaded_filename' not in st.session_state or st.session_state.uploaded_filename != yuklenen_dosya_input.name:
            st.session_state.uploaded_filename = yuklenen_dosya_input.name
            
            df_raw = pd.read_excel(yuklenen_dosya_input, usecols="G,H,I,J,P")
            df_raw.columns = ['Paket_No', 'Siparis_No', 'Alici_Ad', 'Adres', 'Telefon']
            df_raw = df_raw.dropna(subset=['Adres']).reset_index(drop=True)
            
            df_raw['Paket_No'] = df_raw['Paket_No'].astype(str).str.replace(r'\.0$', '', regex=True).replace('nan', '-')
            df_raw['Siparis_No'] = df_raw['Siparis_No'].astype(str).str.replace(r'\.0$', '', regex=True).replace('nan', '-')
            df_raw['Telefon'] = df_raw['Telefon'].astype(str).str.replace(r'\.0$', '', regex=True).replace('nan', '-')
            
            df_raw['Gizli_ID'] = df_raw.index + 1
            
            st.session_state.raw_df = df_raw
            st.session_state.wizard_step = 0
            st.session_state.validated_data = []
            st.session_state.validation_complete = False
            st.session_state.harita_hazir = False
            st.session_state.awaiting_confirmation = False

        if not st.session_state.validation_complete:
            df_raw = st.session_state.raw_df
            current = st.session_state.wizard_step
            total = len(df_raw)
            row = df_raw.iloc[current]

            st.markdown("---")
            st.markdown(f"### 📍 Adres Doğrulama Sihirbazı ({current + 1} / {total})")
            st.progress((current) / total)
            
            if not st.session_state.awaiting_confirmation:
                # SEÇİM EKRANI (ŞERİT BUTONLAR)
                if 'current_step_memory' not in st.session_state or st.session_state.current_step_memory != current:
                    st.session_state.current_step_memory = current
                    st.session_state.custom_search = row['Adres']
                
                html_secim = f"""
<div style="background-color: #2b2b36; padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 5px solid #1e88e5;">
<div style="font-size: 18px; font-weight: bold; color: white;">👤 {row['Alici_Ad']}</div>
<div style="color: #4caf50; font-size: 12px; font-weight: bold; margin-top: 8px; margin-bottom: 4px;">ŞOFÖRÜN GÖRECEĞİ ADRES:</div>
<div style="color: #e0e0e0; font-size: 15px;">{row['Adres']}</div>
</div>
"""
                st.markdown(html_secim, unsafe_allow_html=True)

                yeni_arama = st.text_area("🔍 Harita bulamadıysa, adresi sadeleştirip Enter'a basın:", value=st.session_state.custom_search, height=100)
                if yeni_arama != st.session_state.custom_search:
                    st.session_state.custom_search = yeni_arama
                    st.rerun()

                @st.cache_data(show_spinner=False)
                def get_candidates(api_key, address):
                    gmaps = googlemaps.Client(key=api_key)
                    try:
                        return gmaps.geocode(f"{address}, Türkiye")
                    except:
                        return []
                
                with st.spinner("Google Haritalar'dan alternatifler aranıyor..."):
                    res = get_candidates(GOOGLE_MAPS_API_KEY, st.session_state.custom_search)

                options = []
                for r in res:
                    options.append({
                        "label": r['formatted_address'],
                        "lat": r['geometry']['location']['lat'],
                        "lng": r['geometry']['location']['lng']
                    })

                st.markdown("👇 **Haritaya pin atılacak konumu TIKLAYARAK seçin:**")

                # Alternatifleri Tek Tıkla Seçilebilir Şerit Butonlar Haline Getirdik
                for i, opt in enumerate(options):
                    if st.button(f"📍 {opt['label']}", key=f"btn_opt_{current}_{i}", use_container_width=True):
                        st.session_state.temp_selection = opt['label']
                        st.session_state.temp_lat = opt['lat']
                        st.session_state.temp_lng = opt['lng']
                        st.session_state.awaiting_confirmation = True
                        st.rerun()

                # Sabit Seçenekler (Yine Şerit Buton Olarak)
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("⚠️ Orijinal metni kullan (Sisteme bırak)", key=f"btn_orig_{current}", use_container_width=True):
                    st.session_state.temp_selection = "⚠️ Orijinal metni kullan (Sisteme bırak)"
                    st.session_state.awaiting_confirmation = True
                    st.rerun()
                    
                if st.button("❌ Bu siparişi atla (Rotaya Ekleme)", key=f"btn_skip_{current}", use_container_width=True):
                    st.session_state.temp_selection = "❌ Bu siparişi atla (Rotaya Ekleme)"
                    st.session_state.awaiting_confirmation = True
                    st.rerun()

                st.markdown("---")
                if st.button("⬅️ Önceki Kayıt (Geri Dön)", disabled=(current == 0), use_container_width=True):
                    st.session_state.wizard_step -= 1
                    if len(st.session_state.validated_data) > 0:
                        st.session_state.validated_data.pop()
                    st.rerun()

            else:
                # ONAY EKRANI
                secim = st.session_state.temp_selection
                st.success("✅ **Sipariş Detay Onayı** (Teyit Ekranı)")
                
                c_paket, c_siparis, c_tel = st.columns(3)
                c_paket.markdown(f"📦 **Paket No:**\n`{row['Paket_No']}`")
                c_siparis.markdown(f"📑 **Sipariş No:**\n`{row['Siparis_No']}`")
                c_tel.markdown(f"📞 **Telefon:**\n`{row['Telefon']}`")
                
                st.markdown("---")
                yeni_musteri_adi = st.text_input("👤 Müşteri Adı (Yanlışsa düzeltebilirsiniz):", value=row['Alici_Ad'])
                
                st.info(f"📝 **Excel'deki Adres:**\n\n{row['Adres']}")
                st.warning(f"📍 **Haritada Seçilen Hedef:**\n\n{secim}")
                
                st.markdown("<br>", unsafe_allow_html=True)
                colA, colB = st.columns(2)
                with colA:
                    if st.button("⬅️ İptal (Seçimi Değiştir)", use_container_width=True):
                        st.session_state.awaiting_confirmation = False
                        st.rerun()
                with colB:
                    # BİLGİLER DOĞRU BUTONU ARTIK PRIMARY
                    if st.button("✅ BİLGİLER DOĞRU, SIRADAKİNE GEÇ", type="primary", use_container_width=True):
                        if secim == "❌ Bu siparişi atla (Rotaya Ekleme)":
                            pass 
                        elif secim == "⚠️ Orijinal metni kullan (Sisteme bırak)":
                            row_dict = row.to_dict()
                            row_dict['Alici_Ad'] = yeni_musteri_adi 
                            row_dict['Onayli_Enlem'] = None
                            row_dict['Onayli_Boylam'] = None
                            st.session_state.validated_data.append(row_dict)
                        else:
                            row_dict = row.to_dict()
                            row_dict['Alici_Ad'] = yeni_musteri_adi 
                            row_dict['Onayli_Enlem'] = st.session_state.temp_lat
                            row_dict['Onayli_Boylam'] = st.session_state.temp_lng
                            st.session_state.validated_data.append(row_dict)
                        
                        st.session_state.wizard_step += 1
                        st.session_state.awaiting_confirmation = False
                        if st.session_state.wizard_step >= total:
                            st.session_state.validation_complete = True
                            st.session_state.df_validated = pd.DataFrame(st.session_state.validated_data)
                        st.rerun()
        else:
            st.success(f"✅ BÜTÜN ADRESLER DOĞRULANDI! Toplam {len(st.session_state.df_validated)} sipariş rotaya eklenmeye hazır.")
            st.info("Lütfen sayfanın en üstünden '2. Planlama ve Harita' sekmesine geçiniz.")

# --- SEKME 2: 🗺️ PLANLAMA VE HARİTA ---
with tab_harita:
    harita_kutusu = st.container()
    st.markdown("---") 
    ayarlar_kutusu = st.container()
    st.markdown("---") 
    liste_kutusu = st.container()
    
    with ayarlar_kutusu:
        st.markdown("### 🔄 Rota Ayarları (Yeniden Planla)")
        
        if not st.session_state.validation_complete:
            st.warning("👈 Önce '1. Veri Yükleme ve Doğrulama' sekmesinden adresleri doğrulamanız gerekiyor!")
        else:
            try:
                df_excel = st.session_state.df_validated
                musteriler = []
                secenek_mapping = {}
                
                if st.session_state.harita_hazir and 'sirali_df' in st.session_state:
                    durak_map = {}
                    for i, r in st.session_state.sirali_df.iterrows():
                        if pd.notna(r.get('Gizli_ID')) and r.get('Gizli_ID') != '-':
                            durak_map[r['Gizli_ID']] = i + 1  
                            
                    for idx, row in df_excel.iterrows():
                        gizli_id = row['Gizli_ID']
                        if gizli_id in durak_map:
                            d_no = durak_map[gizli_id]
                            text = f"[{d_no}. Durak] {row['Alici_Ad']} ➔ {str(row['Adres'])[:35]}..."
                            sort_key = d_no
                        else:
                            text = f"[Bulunamadı] {row['Alici_Ad']} ➔ {str(row['Adres'])[:35]}..."
                            sort_key = 9999 + gizli_id
                        musteriler.append({"text": text, "sort_key": sort_key, "excel_idx": idx})
                    musteriler.sort(key=lambda x: x["sort_key"])
                else:
                    for idx, row in df_excel.iterrows():
                        text = f"[{idx+1}. Sıra] {row['Alici_Ad']} ➔ {str(row['Adres'])[:35]}..."
                        musteriler.append({"text": text, "excel_idx": idx})
                        
                musteri_listesi = [m["text"] for m in musteriler]
                secenek_mapping = {m["text"]: m["excel_idx"] for m in musteriler}
                
                secenekler = ["📍 GPS ile Konumumu Al", "🏢 Depo (Ersan Dizayn, İstanbul)", "✍️ Farklı Bir Adres Yaz"] + musteri_listesi
                
                default_baslangic_idx = 3 if len(musteri_listesi) > 0 else 0
                default_bitis_idx = len(secenekler) - 1 if len(musteri_listesi) > 0 else 0
                
                col_ayar1, col_ayar2 = st.columns(2)
                with col_ayar1:
                    secilen_baslangic = st.selectbox("🟢 Başlangıç Noktası:", secenekler, index=default_baslangic_idx)
                with col_ayar2:
                    ring_rotasi = st.checkbox("🔄 Rotayı bitirince tekrar Başlangıç Noktasına dön", value=False)
                    if not ring_rotasi:
                        secilen_bitis = st.selectbox("🔴 Bitiş Noktası:", secenekler, index=default_bitis_idx)
                    else:
                        secilen_bitis = secilen_baslangic
                        
                gps_lazim = ("📍 GPS ile Konumumu Al" in [secilen_baslangic, secilen_bitis])
                loc = None
                if gps_lazim:
                    st.info("👇 Lütfen mevcut konumunuzu almak için aşağıdaki butona basın.")
                    loc = streamlit_geolocation()

                ozel_baslangic = ""
                ozel_bitis = ""
                if secilen_baslangic == "✍️ Farklı Bir Adres Yaz":
                    ozel_baslangic = st.text_input("🟢 Başlangıç Adresinizi Yazın:")
                if not ring_rotasi and secilen_bitis == "✍️ Farklı Bir Adres Yaz":
                    ozel_bitis = st.text_input("🔴 Bitiş Adresinizi Yazın:")

                if st.button("🚀 Rotayı Hesapla ve Haritayı Çiz", type="primary", use_container_width=True):
                    if gps_lazim and not (loc and loc.get('latitude')):
                        st.error("Lütfen GPS konumunuzu almak için yukarıdaki butona tıklayın!")
                    elif secilen_baslangic == "✍️ Farklı Bir Adres Yaz" and not ozel_baslangic:
                        st.error("Lütfen özel başlangıç adresini yazın!")
                    elif not ring_rotasi and secilen_bitis == "✍️ Farklı Bir Adres Yaz" and not ozel_bitis:
                        st.error("Lütfen özel bitiş adresini yazın!")
                    else:
                        with st.spinner('📍 Onaylı koordinatlar yapay zekaya iletiliyor, rota çiziliyor...'):
                            try:
                                gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
                                
                                def parse_secim(secim):
                                    if secim.startswith("🏢"): return "depo", None
                                    elif secim.startswith("📍"): return "gps", None
                                    elif secim.startswith("✍️"): return "ozel", None
                                    elif secim in secenek_mapping: return "musteri", secenek_mapping[secim]
                                    else: return "unknown", None

                                start_tip, start_idx_raw = parse_secim(secilen_baslangic)
                                end_tip, end_idx_raw = parse_secim(secilen_bitis)

                                nodes = []
                                start_node_index, end_node_index = None, None

                                if start_tip != "musteri":
                                    if start_tip == "depo": s_ad, s_adres = "🏢 DEPO", "Ersan Dizayn, İstanbul"
                                    elif start_tip == "gps": s_ad, s_adres = "📍 ŞOFÖR (GPS)", f"{loc['latitude']},{loc['longitude']}"
                                    else: s_ad, s_adres = "🟢 ÖZEL BAŞLANGIÇ", ozel_baslangic
                                    nodes.append({'Siparis_No': 'START', 'Paket_No': '-', 'Gizli_ID': '-', 'Alici_Ad': s_ad, 'Adres': s_adres, 'Telefon': '-'})
                                    start_node_index = 0

                                if not ring_rotasi and end_tip != "musteri":
                                    if end_tip == "depo": e_ad, e_adres = "🏢 DEPO", "Ersan Dizayn, İstanbul"
                                    elif end_tip == "gps": e_ad, e_adres = "📍 ŞOFÖR (GPS)", f"{loc['latitude']},{loc['longitude']}"
                                    else: e_ad, e_adres = "🔴 ÖZEL BİTİŞ", ozel_bitis
                                    nodes.append({'Siparis_No': 'END', 'Paket_No': '-', 'Gizli_ID': '-', 'Alici_Ad': e_ad, 'Adres': e_adres, 'Telefon': '-'})
                                    end_node_index = len(nodes) - 1

                                musteri_offset = len(nodes)
                                for idx, row in df_excel.iterrows(): nodes.append(row.to_dict())

                                if start_tip == "musteri": start_node_index = musteri_offset + start_idx_raw
                                if ring_rotasi: end_node_index = start_node_index
                                elif end_tip == "musteri": end_node_index = musteri_offset + end_idx_raw

                                df_all = pd.DataFrame(nodes)
                                enlemler, boylamlar, gecerli_indeksler = [], [], []

                                for i, adres in enumerate(df_all['Adres']):
                                    lat, lon = 0.0, 0.0
                                    gizli_id = df_all['Gizli_ID'].iloc[i]
                                    
                                    if gizli_id == '-':
                                        if "," in str(adres) and str(adres).replace(',','').replace('.','').replace('-','').isdigit():
                                            l1, l2 = str(adres).split(",")
                                            lat, lon = float(l1), float(l2)
                                        else:
                                            try:
                                                res = gmaps.geocode(f"{adres}, Türkiye")
                                                if res: lat, lon = res[0]['geometry']['location']['lat'], res[0]['geometry']['location']['lng']
                                            except: pass
                                    else:
                                        row_data = df_excel[df_excel['Gizli_ID'] == gizli_id].iloc[0]
                                        if pd.notna(row_data['Onayli_Enlem']) and pd.notna(row_data['Onayli_Boylam']):
                                            lat, lon = float(row_data['Onayli_Enlem']), float(row_data['Onayli_Boylam'])
                                        else:
                                            try:
                                                res = gmaps.geocode(f"{adres}, Türkiye")
                                                if res: lat, lon = res[0]['geometry']['location']['lat'], res[0]['geometry']['location']['lng']
                                            except: pass
                                                
                                    if lat != 0.0 and lon != 0.0:
                                        enlemler.append(lat)
                                        boylamlar.append(lon)
                                        gecerli_indeksler.append(i)

                                if start_node_index not in gecerli_indeksler:
                                    st.error("❌ Başlangıç adresi haritada bulunamadı.")
                                    st.stop()
                                if end_node_index not in gecerli_indeksler:
                                    st.error("❌ Bitiş adresi haritada bulunamadı.")
                                    st.stop()

                                yeni_start_idx = gecerli_indeksler.index(start_node_index)
                                yeni_end_idx = gecerli_indeksler.index(end_node_index)

                                df_filtered = df_all.iloc[gecerli_indeksler].copy().reset_index(drop=True)
                                df_filtered['Enlem'] = enlemler
                                df_filtered['Boylam'] = boylamlar

                                def mesafe_hesapla(lat1, lon1, lat2, lon2):
                                    R = 6371 
                                    phi1, phi2 = math.radians(lat1), math.radians(lat2)
                                    dphi = math.radians(lat2 - lat1)
                                    dlambda = math.radians(lon2 - lon1)
                                    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
                                    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)) * 1000 

                                mesafe_matrisi = []
                                for i in range(len(df_filtered)):
                                    satir = []
                                    for j in range(len(df_filtered)):
                                        if i == j: satir.append(0)
                                        else: satir.append(int(mesafe_hesapla(df_filtered['Enlem'][i], df_filtered['Boylam'][i], df_filtered['Enlem'][j], df_filtered['Boylam'][j])))
                                    mesafe_matrisi.append(satir)

                                manager = pywrapcp.RoutingIndexManager(len(mesafe_matrisi), 1, [yeni_start_idx], [yeni_end_idx])
                                routing = pywrapcp.RoutingModel(manager)
                                def distance_callback(from_index, to_index): return mesafe_matrisi[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]
                                transit_callback_index = routing.RegisterTransitCallback(distance_callback)
                                routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

                                search_parameters = pywrapcp.DefaultRoutingSearchParameters()
                                search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
                                search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
                                search_parameters.time_limit.seconds = 3 

                                cozum = routing.SolveWithParameters(search_parameters)

                                if cozum:
                                    index = routing.Start(0)
                                    rota_sirasi = []
                                    while not routing.IsEnd(index):
                                        rota_sirasi.append(manager.IndexToNode(index))
                                        index = cozum.Value(routing.NextVar(index))
                                    rota_sirasi.append(manager.IndexToNode(index))
                                        
                                    sirali_df = df_filtered.iloc[rota_sirasi].copy().reset_index(drop=True)
                                    st.session_state.sirali_df = sirali_df 
                                    
                                    # Teslimat durumlarını sıfırla
                                    st.session_state.delivery_status = {}
                                    for g_id in sirali_df['Gizli_ID'].unique():
                                        st.session_state.delivery_status[g_id] = "pending"
                                        
                                    buffer = io.BytesIO()
                                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                                        sirali_df.to_excel(writer, index=False)
                                    st.session_state.buffer = buffer
                                    st.session_state.dosya_adi = f"Ersan_Rota_{datetime.datetime.now().strftime('%H%M')}.xlsx"
                                    
                                    st.session_state.harita_hazir = True
                                    st.rerun() 
                                else:
                                    st.error("Bu adresler arasında geçerli bir rota bulunamadı!")

                            except Exception as e:
                                st.error(f"Bir hata oluştu: {e}")

            except Exception as e:
                st.error(f"Excel okunurken hata oluştu: {e}")

    # --- ÜST KISIM: HARİTA BÖLÜMÜ VE SEVKİYAT KONTROLÜ ---
    if st.session_state.harita_hazir:
        with harita_kutusu:
            # 🏁 SEVKİYAT BİTTİ Mİ KONTROLÜ 🏁
            pending_count = 0
            total_customers = 0
            for idx, row in st.session_state.sirali_df.iterrows():
                if row['Gizli_ID'] != '-':
                    total_customers += 1
                    if st.session_state.delivery_status.get(row['Gizli_ID'], "pending") == "pending":
                        pending_count += 1
                        
            if total_customers > 0 and pending_count == 0:
                st.success("🎉 ŞAHANE İŞ! SEVKİYAT BİTMİŞTİR! Bütün teslimatlar tamamlandı. Eline sağlık şoför bey! 🚚💨")
                st.balloons()
            else:
                st.info(f"🚚 Kalan Teslimat: {pending_count} / {total_customers} | Aşağıdan güzergahı inceleyebilirsiniz.")
            
            # 🗺️ ANLIK GÜNCELLENEN HARİTA (Canlı Renkler)
            sirali_df = st.session_state.sirali_df
            baslangic_lat = sirali_df['Enlem'].iloc[0]
            baslangic_lon = sirali_df['Boylam'].iloc[0]
            m = folium.Map(location=[baslangic_lat, baslangic_lon], zoom_start=10)
            
            koordinat_listesi = []
            for idx, row in sirali_df.iterrows():
                lat, lon = row['Enlem'], row['Boylam']
                koordinat_listesi.append((lat, lon))
                
                g_id = row['Gizli_ID']
                status = st.session_state.delivery_status.get(g_id, "pending")
                popup_text = f"<b>Durak {idx+1}</b><br>{row['Alici_Ad']}<br>Tel: {row['Telefon']}"
                
                # Dinamik Harita Pin Renkleri
                if g_id == '-':
                    if idx == 0: renk_hex = '#4caf50' 
                    else: renk_hex = '#ff5252' 
                else:
                    if status == "success": renk_hex = '#4caf50' # Teslim Edildi (Yeşil)
                    elif status == "failed": renk_hex = '#ff5252' # Edilemedi (Kırmızı)
                    else: renk_hex = '#2196f3' # Bekliyor (Mavi)
                    
                marker_html = f'''
                <div style="background-color: {renk_hex}; color: white; border-radius: 50%; width: 26px; height: 26px; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 13px; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.5);">
                    {idx+1}
                </div>
                '''
                folium.Marker([lat, lon], popup=popup_text, tooltip=f"Durak {idx+1}", icon=folium.DivIcon(html=marker_html, icon_anchor=(13, 13))).add_to(m)
                
            folium.PolyLine(koordinat_listesi, color="#ff4b4b", weight=3, opacity=0.8).add_to(m)
            folium_static(m, width=1200, height=500)
            
            st.download_button("📥 Optimize Edilmiş Rotayı Excel Olarak İndir", data=st.session_state.buffer, file_name=st.session_state.dosya_adi, mime="application/vnd.ms-excel")

    # --- ALT KISIM: ŞOFÖR MODU BÖLÜMÜ ---
    if st.session_state.harita_hazir:
        with liste_kutusu:
            st.markdown("### 📱 Teslimat Sırası (Şoför Modu)")
            
            pending_orders = []
            completed_orders = []
            
            for idx, row in st.session_state.sirali_df.iterrows():
                g_id = row['Gizli_ID']
                if g_id == '-':
                    pending_orders.append((idx, row, 'start_end'))
                else:
                    status = st.session_state.delivery_status.get(g_id, "pending")
                    if status == "pending": pending_orders.append((idx, row, 'pending'))
                    else: completed_orders.append((idx, row, status))
                        
            # --------- 1. BEKLEYEN TESLİMATLAR ---------
            st.markdown("#### ⏳ Gidilecek Duraklar")
            for idx, row, status in pending_orders:
                durak_no = idx + 1
                lat, lon, g_id = row['Enlem'], row['Boylam'], row['Gizli_ID']
                
                tel_temiz = "".join(filter(str.isdigit, str(row['Telefon'])))
                if tel_temiz.startswith("0"): tel_temiz = "9" + tel_temiz
                if not tel_temiz.startswith("90") and len(tel_temiz) == 10: tel_temiz = "90" + tel_temiz
                
                if durak_no == 1: border_color, durak_etiketi = "#4caf50", "🟢 BAŞLANGIÇ"
                elif durak_no == len(st.session_state.sirali_df): border_color, durak_etiketi = "#ff5252", "🔴 BİTİŞ"
                else: border_color, durak_etiketi = "#2196f3", "📦 TESLİMAT"
                
                kart_html = f"""
<div style="background: linear-gradient(145deg, #22232a, #2a2b33); padding: 20px; border-radius: 16px; margin-bottom: 10px; border-left: 6px solid {border_color}; box-shadow: 0 8px 20px rgba(0,0,0,0.15);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<div style="display: flex; align-items: center; gap: 10px;">
<span style="background-color: {border_color}; color: white; padding: 6px 12px; border-radius: 8px; font-weight: 800; font-size: 16px;">#{durak_no}</span>
<span style="color: #b0b0b0; font-size: 11px; font-weight: 700; letter-spacing: 1px;">{durak_etiketi}</span>
</div>
</div>
<div style="font-size: 20px; font-weight: 700; color: #ffffff; margin-bottom: 6px; letter-spacing: 0.5px;">{row['Alici_Ad']}</div>
<div style="font-size: 13px; color: #b0b0b0; margin-bottom: 6px;">📦 Paket No: {row['Paket_No']}  |  📑 Sipariş: {row['Siparis_No']}</div>
<div style="font-size: 14px; color: #a0a0b0; margin-bottom: 20px; line-height: 1.5; display: flex; align-items: flex-start; gap: 6px;">
<span style="font-size: 16px;">📍</span><span>{row['Adres']}</span>
</div>
<div style="display: flex; gap: 10px;">
<a href="https://www.google.com/maps/dir/?api=1&destination={lat},{lon}" target="_blank" class="action-btn btn-maps">🗺️ Yol Tarifi</a>
<a href="tel:{tel_temiz}" class="action-btn btn-call">📞 Ara</a>
<a href="https://wa.me/{tel_temiz}" target="_blank" class="action-btn btn-wp">💬 WhatsApp</a>
</div>
</div>
"""
                st.markdown(kart_html, unsafe_allow_html=True)
                
                # Müşterilerde Onay / İptal Butonu (Şık, Sola Yaslı, Gri Tonlu Butonlar)
                if status == 'pending':
                    col_ok, col_fail = st.columns(2)
                    with col_ok:
                        if st.button("✅ Teslim Edildi", key=f"ok_{g_id}", use_container_width=True):
                            st.session_state.delivery_status[g_id] = "success"
                            st.rerun()
                    with col_fail:
                        if st.button("❌ İptal / Edilemedi", key=f"fail_{g_id}", use_container_width=True):
                            st.session_state.delivery_status[g_id] = "failed"
                            st.rerun()
                    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

            # --------- 2. TAMAMLANANLAR LİSTESİ ---------
            if len(completed_orders) > 0:
                st.markdown("---")
                st.markdown("#### 🏁 Tamamlanan İşlemler")
                
                for idx, row, status in completed_orders:
                    durak_no, g_id = idx + 1, row['Gizli_ID']
                    
                    if status == "success": bg_grad, border_color, durak_etiketi = "linear-gradient(145deg, #1b2e1f, #223827)", "#4caf50", "✅ TESLİM EDİLDİ"
                    else: bg_grad, border_color, durak_etiketi = "linear-gradient(145deg, #2e1b1b, #382222)", "#ff5252", "❌ EDİLEMEDİ"
                        
                    kart_html_comp = f"""
<div style="background: {bg_grad}; padding: 15px; border-radius: 12px; margin-bottom: 10px; border-left: 6px solid {border_color}; opacity: 0.8;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<div style="display: flex; align-items: center; gap: 10px;">
<span style="background-color: {border_color}; color: white; padding: 4px 10px; border-radius: 8px; font-weight: 800; font-size: 14px;">#{durak_no}</span>
<span style="color: white; font-size: 12px; font-weight: 700; letter-spacing: 1px;">{durak_etiketi}</span>
</div>
</div>
<div style="font-size: 18px; font-weight: 700; color: #ffffff; margin-bottom: 4px;"><del>{row['Alici_Ad']}</del></div>
<div style="font-size: 12px; color: #b0b0b0;">📍 {str(row['Adres'])[:50]}...</div>
</div>
"""
                    st.markdown(kart_html_comp, unsafe_allow_html=True)
                    if st.button("↩️ İşlemi Geri Al", key=f"undo_{g_id}", use_container_width=True):
                        st.session_state.delivery_status[g_id] = "pending"
                        st.rerun()
                    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
