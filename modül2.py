import streamlit as st
import pandas as pd
import googlemaps
import math
import datetime
import folium
import io
import re
import requests
import random
import base64
import os
import urllib.parse
from streamlit_folium import folium_static
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from streamlit_geolocation import streamlit_geolocation

# ==========================================
# 🔑 API ANAHTARLARI (GELİŞMİŞ ARAMA MOTORLARI) 🔑
# ==========================================
GOOGLE_MAPS_API_KEY = "AIzaSyAbn2TCWJDpKimkoKKb0cNcGWQj9gUF-Mg"
YANDEX_API_KEY = "BURAYA_YANDEX_API_ANAHTARINI_YAZ" # developer.tech.yandex.com
MAPBOX_API_KEY = "BURAYA_MAPBOX_API_ANAHTARINI_YAZ" # account.mapbox.com

# ==========================================
# 🔑 NETGSM API AYARLARI (SMS İÇİN) 🔑
# ==========================================
NETGSM_KULLANICI = "8503056628"
NETGSM_SIFRE = "T6-7376K"
NETGSM_BASLIK = "ERSANDIZAYN" 

# ==========================================
# 🔑 TRENDYOL API AYARLARI (TESLİMAT İÇİN) 🔑
# ==========================================
TRENDYOL_SATICI_ID = "113341"
TRENDYOL_API_KEY = "ZXbDKYXoLmvup2bdlCZ8"
TRENDYOL_API_SECRET = "pwTNHm0dgSX6KORXBFIs"

# ==========================================
# 🔒 SİSTEM GÜVENLİK AYARLARI 🔒
# ==========================================
ADMIN_SIFRE = "1453" # Excel indirmek için gereken şifre

# ==========================================
# 👥 ŞOFÖR / KULLANICI HESAPLARI 👥
# ==========================================
SOFORLER = {
    "admin": "ersan123",
    "sofor1": "1111",
    "sofor2": "2222",
    "sofor3": "3333",
    "sofor4": "4444",
    "sofor5": "5555",
    "sofor6": "6666",
    "sofor7": "7777"
}

# Kayıt klasörünü oluştur
os.makedirs("gecmis_rotalar", exist_ok=True)

# 1. Panel Sayfa Ayarları
st.set_page_config(page_title="Ersan Dizayn Rota Paneli", layout="wide", initial_sidebar_state="collapsed")

# 🌟 PREMIUM TASARIM CSS ENJEKSİYONU 🌟
st.markdown("""
<style>
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; border-radius: 8px 8px 0px 0px; padding: 10px 24px;
        background-color: #1e1e24; border: 1px solid #333; border-bottom: none;
        color: #a0a0a0; transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2b2b36 !important; color: white !important;
        border-top: 3px solid #1e88e5; box-shadow: 0 -4px 10px rgba(0,0,0,0.1);
    }
    
    .action-btn {
        flex: 1; text-align: center; padding: 12px 0; border-radius: 10px;
        text-decoration: none !important; font-weight: 600; font-size: 14px;
        color: white !important; transition: all 0.3s ease;
        display: flex; justify-content: center; align-items: center; gap: 6px;
    }
    .btn-maps { background: linear-gradient(135deg, #1e88e5, #1565c0); box-shadow: 0 4px 10px rgba(30,136,229,0.3); }
    .btn-maps:hover { background: linear-gradient(135deg, #2196f3, #1976d2); transform: scale(1.02); }
    .btn-call { background: linear-gradient(135deg, #43a047, #2e7d32); box-shadow: 0 4px 10px rgba(67,160,71,0.3); }
    .btn-call:hover { background: linear-gradient(135deg, #4caf50, #388e3c); transform: scale(1.02); }
    
    div[data-testid="stButton"] button {
        background-color: #2b2b36; color: white; border: 1px solid #444; border-radius: 8px;
        padding: 14px 16px; font-weight: 500; letter-spacing: 0.3px; transition: all 0.2s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15); justify-content: flex-start !important; text-align: left !important;
    }
    div[data-testid="stButton"] button:hover { background-color: #3b3b46; border-color: #1e88e5; transform: translateY(-2px); }
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, #1e88e5, #1565c0); border: none;
        justify-content: center !important; text-align: center !important; font-weight: 700;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover { background: linear-gradient(135deg, #2196f3, #1976d2); }

    [data-testid="stNumberInputContainer"] {
        background-color: #2b2b36 !important; border: 1px solid #444 !important;
        border-radius: 8px !important; overflow: hidden;
    }
    [data-testid="stNumberInputContainer"]:focus-within {
        border-color: #1e88e5 !important; box-shadow: 0 0 8px rgba(30,136,229,0.5) !important;
    }
    [data-testid="stNumberInputContainer"] input {
        color: #ffc107 !important; font-weight: 800 !important; font-size: 18px !important;
        text-align: center !important; padding: 12px 0px !important;
    }
    [data-testid="stNumberInputContainer"] button, 
    [data-testid="stNumberInputStepUp"], 
    [data-testid="stNumberInputStepDown"] { display: none !important; }

    /* OTP KODU İÇİN ÖZEL INPUT TASARIMI */
    [data-testid="stTextInput"] > div > div > input {
        background-color: #1e1e24 !important; border: 2px solid #1e88e5 !important;
        color: #fff !important; font-size: 18px !important; font-weight: bold !important;
        text-align: center !important; border-radius: 8px !important; padding: 10px !important;
    }
    [data-testid="stTextInput"] > div > div > input:focus {
        box-shadow: 0 0 10px rgba(30, 136, 229, 0.7) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🛑 LOGIN (GİRİŞ) KONTROLÜ
# ==========================================
if 'kullanici' not in st.session_state:
    st.session_state.kullanici = None

if st.session_state.kullanici is None:
    st.markdown("<br><br><h1 style='text-align: center; color: #1e88e5;'>🚚 ERSAN DİZAYN</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #a0a0a0;'>Lojistik Sürücü Portalı</h3><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            kadi = st.text_input("👤 Kullanıcı Adı:")
            sifre = st.text_input("🔑 Şifre:", type="password")
            submit = st.form_submit_button("Sisteme Giriş Yap", type="primary", use_container_width=True)
            
            if submit:
                if kadi in SOFORLER and SOFORLER[kadi] == sifre:
                    st.session_state.kullanici = kadi
                    st.rerun()
                else:
                    st.error("❌ Kullanıcı adı veya şifre hatalı!")
    st.stop() 

# 🧠 YAPAY ZEKA: 4 MOTORLU ARAMA SİSTEMİ (Google + Mapbox + Yandex + OSM)
@st.cache_data(show_spinner=False)
def get_candidates(api_key, address):
    gmaps = googlemaps.Client(key=api_key)
    candidates = []
    seen_addresses = set()

    def add_result(res_list, kaynak="📍"):
        for r in res_list:
            addr = r.get('formatted_address', '')
            if addr and addr not in seen_addresses:
                seen_addresses.add(addr)
                candidates.append({"label": f"{kaynak} {addr}", "lat": r['geometry']['location']['lat'], "lng": r['geometry']['location']['lng']})

    # 1. MOTOR: GOOGLE MAPS
    try: add_result(gmaps.geocode(f"{address}, Türkiye"), "📍")
    except: pass

    if len(candidates) < 4:
        try:
            temiz_adres = re.sub(r'(?i)\b(no|numara|d|daire|kat|blok|iç kapı)\b\s*[:.]?\s*\d*[/a-zA-Z\d-]*', '', address)
            temiz_adres = temiz_adres.replace("/", " ").replace("-", " ")
            if temiz_adres.strip() != address.strip(): add_result(gmaps.geocode(f"{temiz_adres.strip()}, Türkiye"), "📍")
        except: pass
        
    # 2. MOTOR: MAPBOX (Yeni Eklenen Zeki Motor)
    if MAPBOX_API_KEY != "BURAYA_MAPBOX_API_ANAHTARINI_YAZ":
        try:
            safe_address = urllib.parse.quote(f"{address}, Türkiye")
            mapbox_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{safe_address}.json"
            m_params = {
                "access_token": MAPBOX_API_KEY,
                "country": "tr",
                "limit": 3,
                "language": "tr"
            }
            m_res = requests.get(mapbox_url, params=m_params, timeout=5)
            if m_res.status_code == 200:
                m_data = m_res.json()
                for feature in m_data.get("features", []):
                    addr = feature.get("place_name", "")
                    if addr and addr not in seen_addresses:
                        lon, lat = feature.get("center", [0, 0])
                        seen_addresses.add(addr)
                        candidates.append({"label": f"🟠 (MAPBOX) {addr}", "lat": lat, "lng": lon})
        except: pass

    # 3. MOTOR: YANDEX MAPS (Özellikle Türkiye sokaklarında efsane)
    if YANDEX_API_KEY != "BURAYA_YANDEX_API_ANAHTARINI_YAZ":
        try:
            yandex_url = "https://geocode-maps.yandex.ru/1.x/"
            y_params = {
                "apikey": YANDEX_API_KEY,
                "format": "json",
                "geocode": f"Türkiye, {address}",
                "results": 3
            }
            y_res = requests.get(yandex_url, params=y_params, timeout=5)
            if y_res.status_code == 200:
                y_data = y_res.json()
                features = y_data.get("response", {}).get("GeoObjectCollection", {}).get("featureMember", [])
                for f in features:
                    geo = f.get("GeoObject", {})
                    name = geo.get("name", "")
                    desc = geo.get("description", "")
                    full_addr = f"{name}, {desc}".strip(", ")
                    pos = geo.get("Point", {}).get("pos", "")
                    
                    if full_addr and pos and full_addr not in seen_addresses:
                        lon, lat = map(float, pos.split())
                        seen_addresses.add(full_addr)
                        candidates.append({"label": f"🟡 (YANDEX) {full_addr}", "lat": lat, "lng": lon})
        except: pass

    # 4. MOTOR: OPENSTREETMAP (Yedek Kurtarıcı)
    try:
        headers = {'User-Agent': 'ErsanDizaynLojistik/1.0'}
        osm_url = "https://nominatim.openstreetmap.org/search"
        params = {'q': f"{address}, Türkiye", 'format': 'json', 'limit': 3}
        response = requests.get(osm_url, headers=headers, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            for item in data:
                addr = item.get('display_name', '')
                if addr and addr not in seen_addresses:
                    seen_addresses.add(addr)
                    candidates.append({"label": f"🌍 (OSM) {addr}", "lat": float(item['lat']), "lng": float(item['lon'])})
    except: pass

    return candidates

# 📨 NETGSM SMS GÖNDERME FONKSİYONU
def netgsm_sms_gonder(tel, musteri, paket, urun, kod):
    tel_temiz = "".join(filter(str.isdigit, str(tel)))
    if len(tel_temiz) == 10: tel_temiz = "0" + tel_temiz
    elif tel_temiz.startswith("90") and len(tel_temiz) == 12: tel_temiz = "0" + tel_temiz[2:]
        
    mesaj = f"Sayin {musteri}, {paket} numarali {urun} siparisiniz dagitima cikmistir. Guvenli teslimat kodunuz: {kod}. Ersan Dizayn."
    tr_chars = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    mesaj = mesaj.translate(tr_chars)
    
    url = "https://api.netgsm.com.tr/sms/send/get"
    payload = {"usercode": NETGSM_KULLANICI, "password": NETGSM_SIFRE, "gsmno": tel_temiz, "message": mesaj, "msgheader": NETGSM_BASLIK}
    try:
        r = requests.get(url, params=payload, timeout=10)
        if r.status_code == 200 and r.text.startswith("00"): return True, "SMS Başarılı"
        else: return False, f"NetGSM Hata Kodu: {r.text}"
    except Exception as e: return False, f"Sistem Hatası: {str(e)}"

# 🛒 TRENDYOL API TESLİM EDİLDİ FONKSİYONU
def trendyol_teslim_edildi_yap(satici_id, api_key, api_secret, paket_no, siparis_no):
    if siparis_no == "-" or siparis_no == "":
        return False, "Sipariş numarası yok! Lütfen lokal teslimata tıklayın."
    
    auth_str = f"{api_key}:{api_secret}"
    b64_auth_str = base64.b64encode(auth_str.encode('ascii')).decode('ascii')
    headers = {"Authorization": f"Basic {b64_auth_str}", "Content-Type": "application/json"}
    
    try:
        sorgu_url = f"https://apigw.trendyol.com/integration/order/sellers/{satici_id}/orders?orderNumber={siparis_no}"
        req_sorgu = requests.get(sorgu_url, headers=headers, timeout=15)
        
        gercek_paket_id = None
        if req_sorgu.status_code == 200:
            data = req_sorgu.json()
            content = data.get("content", [])
            if content: gercek_paket_id = content[0].get("id") or content[0].get("shipmentPackageId")
        
        sadece_id = str(gercek_paket_id) if gercek_paket_id else str(paket_no).strip()
        
        url = f"https://apigw.trendyol.com/integration/order/sellers/{satici_id}/shipment-packages/{sadece_id}/manual-deliver"
        r = requests.put(url, headers=headers, json={}, timeout=15)
        
        if r.status_code in [200, 201, 204]: return True, "Trendyol'da başarıyla Teslim Edildi!"
        else: return False, f"Trendyol Hata: {r.status_code} - {r.text}"
            
    except Exception as e: return False, f"Bağlantı Hatası: {str(e)}"

# 📍 BÖLGE TESPİT FONKSİYONU
def bolge_bul(adresler):
    if not adresler: return "Istanbul"
    adresler_str = " ".join([str(a).lower() for a in adresler])
    
    if any(il in adresler_str for il in ["izmir", "balıkesir", "balikesir", "manisa"]): return "Izmir"
    if any(il in adresler_str for il in ["ankara", "bolu", "düzce", "duzce", "bilecik", "eskişehir", "eskisehir"]): return "Ankara"
    if any(il in adresler_str for il in ["kocaeli", "sakarya", "izmit", "adapazarı", "adapazari"]): return "Kocaeli-Sakarya"
    if any(il in adresler_str for il in ["tekirdağ", "tekirdag", "çorlu", "corlu"]): return "Tekirdag"
    if any(il in adresler_str for il in ["adana", "mersin", "içel", "icel"]): return "Adana-Mersin"
    if any(il in adresler_str for il in ["antalya", "alanya"]): return "Antalya"
    
    return "Istanbul" 

# 🎨 EXCEL RENKLENDİRME FONKSİYONU
def get_colored_excel(df, status_dict):
    df_export = df.copy()
    durum_listesi = []
    
    for g_id in df_export['Gizli_ID']:
        st_val = status_dict.get(g_id, "pending")
        if st_val == "success_trendyol": durum_listesi.append("Trendyol Teslim Edildi")
        elif st_val == "success_local": durum_listesi.append("Lokal (HB/N11) Teslim Edildi")
        elif st_val == "failed": durum_listesi.append("Teslim Edilemedi")
        else: durum_listesi.append("Bekliyor")
        
    df_export['Teslimat_Durumu'] = durum_listesi

    def apply_colors(row):
        g_id = row['Gizli_ID']
        st_val = status_dict.get(g_id, "pending")
        if st_val == "success_trendyol": return ['background-color: #c6efce; color: #006100'] * len(row) 
        elif st_val == "success_local": return ['background-color: #bdd7ee; color: #002060'] * len(row) 
        elif st_val == "failed": return ['background-color: #ffc7ce; color: #9c0006'] * len(row) 
        else: return [''] * len(row)

    styled_df = df_export.style.apply(apply_colors, axis=1)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        styled_df.to_excel(writer, index=False, sheet_name='Rota Durumu')
        worksheet = writer.sheets['Rota Durumu']
        worksheet.set_column('A:Z', 15)
    
    return output.getvalue()

# 🤖 OTOMATİK KAYDETME (AUTO-SAVE) FONKSİYONU
def otomatik_kaydet():
    if 'sirali_df' not in st.session_state or not st.session_state.harita_hazir:
        return
        
    sirali_df = st.session_state.sirali_df
    
    musteri_adresleri = sirali_df[~sirali_df['Gizli_ID'].isin(['start_node', 'end_node'])]['Adres'].tolist()
    bolge_adi = bolge_bul(musteri_adresleri)
    
    teslim_edilen = 0
    teslim_edilemeyen = 0
    for g_id, status in st.session_state.delivery_status.items():
        if g_id in ['start_node', 'end_node']: continue
        if status in ["success_trendyol", "success_local"]: teslim_edilen += 1
        elif status == "failed": teslim_edilemeyen += 1
            
    excel_data = get_colored_excel(sirali_df, st.session_state.delivery_status)
    
    zaman = st.session_state.rota_olusturma_zamani
    kullanici = st.session_state.kullanici
    
    yeni_dosya_adi = f"{bolge_adi}_{kullanici}_{zaman}_T{teslim_edilen}_H{teslim_edilemeyen}.xlsx"
    yeni_dosya_yolu = f"gecmis_rotalar/{yeni_dosya_adi}"
    
    eski_dosya_yolu = st.session_state.get('aktif_dosya_yolu')
    if eski_dosya_yolu and eski_dosya_yolu != yeni_dosya_yolu:
        if os.path.exists(eski_dosya_yolu):
            try: os.remove(eski_dosya_yolu)
            except: pass
            
    with open(yeni_dosya_yolu, "wb") as f:
        f.write(excel_data)
        
    st.session_state.aktif_dosya_yolu = yeni_dosya_yolu


st.title("🚚 Ersan Dizayn Rota Kontrol Merkezi")

# ==========================================
# SESSION STATE DEĞİŞKENLERİ
# ==========================================
if 'harita_hazir' not in st.session_state: st.session_state.harita_hazir = False
if 'wizard_step' not in st.session_state: st.session_state.wizard_step = 0
if 'validated_data' not in st.session_state: st.session_state.validated_data = []
if 'validation_complete' not in st.session_state: st.session_state.validation_complete = False
if 'awaiting_confirmation' not in st.session_state: st.session_state.awaiting_confirmation = False
if 'temp_selection' not in st.session_state: st.session_state.temp_selection = None
if 'temp_lat' not in st.session_state: st.session_state.temp_lat = None
if 'temp_lng' not in st.session_state: st.session_state.temp_lng = None
if 'delivery_status' not in st.session_state: st.session_state.delivery_status = {} 
if 'df_validated' not in st.session_state: 
    st.session_state.df_validated = pd.DataFrame(columns=['Paket_No', 'Siparis_No', 'Alici_Ad', 'Adres', 'Urun_Adi', 'Adet', 'Telefon', 'Gizli_ID', 'Onayli_Enlem', 'Onayli_Boylam', 'Teslimat_Kodu'])
if 'manual_search_results' not in st.session_state: st.session_state.manual_search_results = []
if 'manual_selected' not in st.session_state: st.session_state.manual_selected = None

tab_kurulum, tab_harita, tab_profil = st.tabs(["📂 1. Veri Yükleme", "🗺️ 2. Planlama ve Harita", "👤 3. Profil ve Geçmiş"])

# --- SEKME 1: 📂 VERİ YÜKLEME VE ADRES DOĞRULAMA ---
with tab_kurulum:
    st.markdown("### ⚙️ Sistem Kurulumu")
    yuklenen_dosya_input = st.file_uploader("Sipariş Excel'i Yükle (.xlsx)", type=["xlsx"])

    if yuklenen_dosya_input:
        if 'uploaded_filename' not in st.session_state or st.session_state.uploaded_filename != yuklenen_dosya_input.name:
            st.session_state.uploaded_filename = yuklenen_dosya_input.name
            
            try:
                df_raw = pd.read_excel(yuklenen_dosya_input, usecols="B,H,I,J,N,O,P")
                df_raw.columns = ['Paket_No', 'Siparis_No', 'Alici_Ad', 'Adres', 'Urun_Adi', 'Adet', 'Telefon']
            except ValueError:
                st.error("❌ Excel sütunları eşleşmedi! Lütfen B,H,I,J,N,O,P sütunlarının dolu olduğundan emin olun.")
                st.stop()
                
            df_raw = df_raw.dropna(subset=['Adres']).reset_index(drop=True)
            
            df_raw['Paket_No'] = df_raw['Paket_No'].astype(str).str.replace(r'\.0$', '', regex=True).replace('nan', '-')
            df_raw['Siparis_No'] = df_raw['Siparis_No'].astype(str).str.replace(r'\.0$', '', regex=True).replace('nan', '-')
            df_raw['Telefon'] = df_raw['Telefon'].astype(str).str.replace(r'\.0$', '', regex=True).replace('nan', '-')
            df_raw['Urun_Adi'] = df_raw['Urun_Adi'].astype(str).replace('nan', '-')
            df_raw['Adet'] = df_raw['Adet'].astype(str).str.replace(r'\.0$', '', regex=True).replace('nan', '1')
            df_raw['Gizli_ID'] = df_raw.index + 1
            
            try:
                benzersiz_kodlar = random.sample(range(1000, 10000), len(df_raw))
                df_raw['Teslimat_Kodu'] = [str(kod) for kod in benzersiz_kodlar]
            except ValueError:
                df_raw['Teslimat_Kodu'] = [str(random.randint(10000, 99999)) for _ in range(len(df_raw))]
            
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
                if 'current_step_memory' not in st.session_state or st.session_state.current_step_memory != current:
                    st.session_state.current_step_memory = current
                    st.session_state.custom_search = str(row['Adres']).replace("\n", " ")
                
                html_secim = f"""<div style="background-color: #2b2b36; padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 5px solid #1e88e5;">
<div style="display: flex; justify-content: space-between; align-items: flex-start;">
<div style="font-size: 18px; font-weight: bold; color: white; flex: 1;">👤 {row['Alici_Ad']}</div>
<div style="text-align: right; background: rgba(255, 193, 7, 0.15); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(255, 193, 7, 0.3); margin-left: 10px;">
<span style="font-size: 18px; font-weight: 900; color: #ffc107;">{row['Adet']}x</span> <span style="font-size: 14px; font-weight: 700; color: #fffde7;">{row['Urun_Adi']}</span>
</div></div>
<div style="color: #4caf50; font-size: 12px; font-weight: bold; margin-top: 12px; margin-bottom: 4px;">ŞOFÖRÜN GÖRECEĞİ ADRES:</div>
<div style="color: #e0e0e0; font-size: 15px;">{row['Adres']}</div></div>"""
                st.markdown(html_secim, unsafe_allow_html=True)
                
                st.info("💡 **TÜYO:** Çok az seçenek çıkıyorsa, bina numarası ve daireyi silip sadece **Sokak/Mahalle/İlçe** bırakıp Enter'a basın.")
                yeni_arama = st.text_area("🔍 Adresi sadeleştirip tekrar ara (Enter'a bas):", value=st.session_state.custom_search, height=80)
                
                if yeni_arama != st.session_state.custom_search:
                    st.session_state.custom_search = yeni_arama
                    st.rerun()

                with st.spinner("Motorlar Arıyor..."):
                    options = get_candidates(GOOGLE_MAPS_API_KEY, st.session_state.custom_search)

                st.markdown("👇 **Haritaya pin atılacak konumu TIKLAYARAK seçin:**")
                for i, opt in enumerate(options):
                    if st.button(f"{opt['label']}", key=f"btn_opt_{current}_{i}", use_container_width=True):
                        st.session_state.temp_selection = opt['label']
                        st.session_state.temp_lat = opt['lat']
                        st.session_state.temp_lng = opt['lng']
                        st.session_state.awaiting_confirmation = True
                        st.rerun()

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
                    if len(st.session_state.validated_data) > 0: st.session_state.validated_data.pop()
                    st.rerun()

            else:
                secim = st.session_state.temp_selection
                st.success("✅ **Sipariş Detay Onayı** (Teyit Ekranı)")
                
                c_paket, c_siparis, c_tel = st.columns(3)
                c_paket.markdown(f"📦 **Paket No:**\n`{row['Paket_No']}`")
                c_siparis.markdown(f"📑 **Sipariş No:**\n`{row['Siparis_No']}`")
                c_tel.markdown(f"📞 **Telefon:**\n`{row['Telefon']}`")
                
                c_urun, c_adet = st.columns([3, 1])
                c_urun.markdown(f"🛒 **Ürün:**\n`{row['Urun_Adi']}`")
                c_adet.markdown(f"🔢 **Adet:**\n`{row['Adet']}`")
                
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
                    if st.button("✅ BİLGİLER DOĞRU, SIRADAKİNE GEÇ", type="primary", use_container_width=True):
                        if secim == "❌ Bu siparişi atla (Rotaya Ekleme)": pass 
                        elif secim == "⚠️ Orijinal metni kullan (Sisteme bırak)":
                            row_dict = row.to_dict()
                            row_dict['Alici_Ad'] = yeni_musteri_adi 
                            row_dict['Onayli_Enlem'], row_dict['Onayli_Boylam'] = None, None
                            st.session_state.validated_data.append(row_dict)
                        else:
                            row_dict = row.to_dict()
                            row_dict['Alici_Ad'] = yeni_musteri_adi 
                            row_dict['Onayli_Enlem'], row_dict['Onayli_Boylam'] = st.session_state.temp_lat, st.session_state.temp_lng
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
    manuel_ekleme_kutusu = st.container()
    st.markdown("---")
    ayarlar_kutusu = st.container()
    st.markdown("---") 
    harita_kutusu = st.container()
    st.markdown("---") 
    liste_kutusu = st.container()
    
    with manuel_ekleme_kutusu:
        with st.expander("➕ MANUEL SİPARİŞ / YENİ ADRES EKLE (Tıkla Aç)", expanded=False):
            col_search, col_btn = st.columns([4, 1])
            with col_search: man_arama = st.text_input("📍 Aranacak Adresi Yazın:")
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Adresi Bul 🔍", use_container_width=True):
                    if man_arama.strip() != "":
                        with st.spinner("Aranıyor..."):
                            st.session_state.manual_search_results = get_candidates(GOOGLE_MAPS_API_KEY, man_arama)
                            st.session_state.manual_selected = None
            
            if st.session_state.get('manual_search_results') and not st.session_state.get('manual_selected'):
                for i, opt in enumerate(st.session_state.manual_search_results):
                    if st.button(f"{opt['label']}", key=f"man_add_opt_{i}", use_container_width=True):
                        st.session_state.manual_selected = opt
                        st.rerun()
            
            if st.session_state.get('manual_selected'):
                st.success(f"✅ Seçilen Konum: {st.session_state.manual_selected['label']}")
                m_ad = st.text_input("👤 Müşteri Adı:", placeholder="Örn: Ahmet Yılmaz")
                c_tel, c_sip = st.columns(2)
                m_tel = c_tel.text_input("📞 Telefon:")
                m_sip = c_sip.text_input("📑 Sipariş No:")
                c_pak, c_ur, c_ad = st.columns([2, 3, 1])
                m_pak = c_pak.text_input("📦 Paket No:")
                m_urun = c_ur.text_input("🛒 Ürün Adı:", placeholder="Örn: Siyah Ayna")
                m_adet = c_ad.text_input("🔢 Adet:", value="1")
                
                col_iptal, col_ekle = st.columns(2)
                with col_iptal:
                    if st.button("⬅️ İptal Et", use_container_width=True):
                        st.session_state.manual_selected = None
                        st.session_state.manual_search_results = []
                        st.rerun()
                with col_ekle:
                    if st.button("💾 Kaydet ve Listeye Ekle", type="primary", use_container_width=True):
                        max_id = 0
                        if len(st.session_state.df_validated) > 0: max_id = st.session_state.df_validated['Gizli_ID'].max()
                        
                        yeni_kod = str(random.randint(1000, 9999))
                        if 'Teslimat_Kodu' in st.session_state.df_validated.columns:
                            while yeni_kod in st.session_state.df_validated['Teslimat_Kodu'].tolist():
                                yeni_kod = str(random.randint(1000, 9999))
                        
                        new_row = {
                            'Paket_No': m_pak if m_pak else "-", 'Siparis_No': m_sip if m_sip else "-",
                            'Alici_Ad': m_ad if m_ad else "Manuel Müşteri", 'Adres': st.session_state.manual_selected['label'],
                            'Urun_Adi': m_urun if m_urun else "-", 'Adet': m_adet if m_adet else "1",
                            'Telefon': m_tel if m_tel else "-", 'Gizli_ID': max_id + 1,
                            'Onayli_Enlem': st.session_state.manual_selected['lat'], 'Onayli_Boylam': st.session_state.manual_selected['lng'],
                            'Teslimat_Kodu': yeni_kod
                        }
                        st.session_state.df_validated = pd.concat([st.session_state.df_validated, pd.DataFrame([new_row])], ignore_index=True)
                        st.session_state.validation_complete = True 
                        st.session_state.manual_selected = None
                        st.session_state.manual_search_results = []
                        st.success("✅ Eklendi! Rotayı yeniden hesaplayabilirsiniz.")
                        st.rerun()

    with ayarlar_kutusu:
        st.markdown("### 🔄 Rota Ayarları (Yeniden Planla)")
        if len(st.session_state.df_validated) == 0:
            st.warning("👈 Excel yükleyerek veya 'Manuel Sipariş Ekle' bölümünden sipariş ekleyin.")
        else:
            try:
                df_excel = st.session_state.df_validated
                musteriler = []
                secenek_mapping = {}
                
                if st.session_state.harita_hazir and 'sirali_df' in st.session_state:
                    durak_map = {r['Gizli_ID']: i + 1 for i, r in st.session_state.sirali_df.iterrows() if pd.notna(r.get('Gizli_ID')) and r.get('Gizli_ID') not in ['start_node', 'end_node']}
                    for idx, row in df_excel.iterrows():
                        gizli_id = row['Gizli_ID']
                        if gizli_id in durak_map: 
                            d_no = durak_map[gizli_id]
                            text = f"[{d_no}. Durak] {row['Alici_Ad']} ➔ {str(row['Adres'])[:35]}..."
                            sort_key = d_no
                        else: 
                            d_no = None
                            text = f"[Yeni Eklendi] {row['Alici_Ad']} ➔ {str(row['Adres'])[:35]}..."
                            sort_key = 9999 + gizli_id
                        musteriler.append({"text": text, "sort_key": sort_key, "excel_idx": idx})
                    musteriler.sort(key=lambda x: x["sort_key"])
                else:
                    for idx, row in df_excel.iterrows():
                        musteriler.append({"text": f"[{idx+1}. Sıra] {row['Alici_Ad']} ➔ {str(row['Adres'])[:35]}...", "excel_idx": idx})
                        
                musteri_listesi = [m["text"] for m in musteriler]
                secenek_mapping = {m["text"]: m["excel_idx"] for m in musteriler}
                secenekler = ["📍 GPS ile Konumumu Al", "🏢 Depo (Ersan Dizayn, İstanbul)", "✍️ Farklı Bir Adres Yaz"] + musteri_listesi
                
                default_baslangic_idx = 3 if len(musteri_listesi) > 0 else 0
                default_bitis_idx = len(secenekler) - 1 if len(musteri_listesi) > 0 else 0
                
                col_ayar1, col_ayar2 = st.columns(2)
                with col_ayar1: secilen_baslangic = st.selectbox("🟢 Başlangıç Noktası:", secenekler, index=default_baslangic_idx)
                with col_ayar2:
                    ring_rotasi = st.checkbox("🔄 Rotayı bitirince tekrar Başlangıç Noktasına dön", value=False)
                    if ring_rotasi: secilen_bitis = secilen_baslangic
                    else: secilen_bitis = st.selectbox("🔴 Bitiş Noktası:", secenekler, index=default_bitis_idx)
                        
                gps_lazim = ("📍 GPS ile Konumumu Al" in [secilen_baslangic, secilen_bitis])
                if gps_lazim: loc = streamlit_geolocation()
                else: loc = None

                ozel_baslangic = st.text_input("🟢 Başlangıç Adresinizi Yazın:") if secilen_baslangic == "✍️ Farklı Bir Adres Yaz" else ""
                ozel_bitis = st.text_input("🔴 Bitiş Adresinizi Yazın:") if not ring_rotasi and secilen_bitis == "✍️ Farklı Bir Adres Yaz" else ""

                if st.button("🚀 Rotayı Hesapla ve Haritayı Çiz", type="primary", use_container_width=True):
                    if gps_lazim and not (loc and loc.get('latitude')): st.error("Lütfen GPS konumunuzu almak için yukarıdaki butona tıklayın!")
                    elif secilen_baslangic == "✍️ Farklı Bir Adres Yaz" and not ozel_baslangic: st.error("Lütfen özel başlangıç adresini yazın!")
                    elif not ring_rotasi and secilen_bitis == "✍️ Farklı Bir Adres Yaz" and not ozel_bitis: st.error("Lütfen özel bitiş adresini yazın!")
                    else:
                        with st.spinner('📍 Yapay Zeka en kısa rotayı hesaplıyor, lütfen bekleyin...'):
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
                                if start_tip != "musteri":
                                    if start_tip == "depo": s_ad, s_adres = "🏢 DEPO", "Ersan Dizayn, İstanbul"
                                    elif start_tip == "gps": s_ad, s_adres = "📍 ŞOFÖR (GPS)", f"{loc['latitude']},{loc['longitude']}"
                                    else: s_ad, s_adres = "🟢 ÖZEL BAŞLANGIÇ", ozel_baslangic
                                        
                                    nodes.append({'Siparis_No': 'START', 'Paket_No': '-', 'Urun_Adi': '-', 'Adet': '-', 'Gizli_ID': 'start_node', 'Alici_Ad': s_ad, 'Adres': s_adres, 'Telefon': '-', 'Teslimat_Kodu': '-'})
                                    start_node_index = 0

                                if not ring_rotasi and end_tip != "musteri":
                                    if end_tip == "depo": e_ad, e_adres = "🏢 DEPO", "Ersan Dizayn, İstanbul"
                                    elif end_tip == "gps": e_ad, e_adres = "📍 ŞOFÖR (GPS)", f"{loc['latitude']},{loc['longitude']}"
                                    else: e_ad, e_adres = "🔴 ÖZEL BİTİŞ", ozel_bitis
                                        
                                    nodes.append({'Siparis_No': 'END', 'Paket_No': '-', 'Urun_Adi': '-', 'Adet': '-', 'Gizli_ID': 'end_node', 'Alici_Ad': e_ad, 'Adres': e_adres, 'Telefon': '-', 'Teslimat_Kodu': '-'})
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
                                    
                                    if gizli_id in ['start_node', 'end_node']:
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

                                yeni_start_idx = gecerli_indeksler.index(start_node_index)
                                yeni_end_idx = gecerli_indeksler.index(end_node_index)

                                df_filtered = df_all.iloc[gecerli_indeksler].copy().reset_index(drop=True)
                                df_filtered['Enlem'] = enlemler
                                df_filtered['Boylam'] = boylamlar

                                def mesafe_hesapla(lat1, lon1, lat2, lon2):
                                    R = 6371 
                                    phi1, phi2 = math.radians(lat1), math.radians(lat2)
                                    a = math.sin(math.radians(lat2 - lat1)/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(math.radians(lon2 - lon1)/2)**2
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
                                    
                                    st.session_state.delivery_status = {}
                                    for g_id in sirali_df['Gizli_ID'].unique():
                                        st.session_state.delivery_status[g_id] = "pending"
                                        
                                    # 🌟 İLK OTOMATİK KAYIT (T0_H0)
                                    st.session_state.rota_olusturma_zamani = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
                                    st.session_state.aktif_dosya_yolu = None
                                    st.session_state.harita_hazir = True
                                    otomatik_kaydet()
                                    
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
            pending_count = 0
            total_customers = 0
            for idx, row in st.session_state.sirali_df.iterrows():
                if row['Gizli_ID'] not in ['start_node', 'end_node']:
                    total_customers += 1
                    if st.session_state.delivery_status.get(row['Gizli_ID'], "pending") == "pending": pending_count += 1
                        
            if total_customers > 0 and pending_count == 0:
                st.success("🎉 ŞAHANE İŞ! SEVKİYAT BİTMİŞTİR! Bütün teslimatlar tamamlandı. Eline sağlık şoför bey! 🚚💨")
                st.balloons()
            else: 
                st.info(f"🚚 Kalan Teslimat: {pending_count} / {total_customers} | Aşağıdan güzergahı inceleyebilirsiniz.")
            
            sirali_df = st.session_state.sirali_df
            m = folium.Map(location=[sirali_df['Enlem'].iloc[0], sirali_df['Boylam'].iloc[0]], zoom_start=10)
            
            koordinat_listesi = []
            for idx, row in sirali_df.iterrows():
                lat = row['Enlem']
                lon = row['Boylam']
                g_id = row['Gizli_ID']
                koordinat_listesi.append((lat, lon))
                status = st.session_state.delivery_status.get(g_id, "pending")
                
                if g_id in ['start_node', 'end_node']: 
                    renk_hex = '#4caf50' if g_id == 'start_node' else '#ff5252' 
                else: 
                    if status == "success_trendyol": renk_hex = '#4caf50' 
                    elif status == "success_local": renk_hex = '#2196f3' 
                    elif status == "failed": renk_hex = '#ff5252' 
                    else: renk_hex = '#ff9800' 
                    
                marker_html = f'<div style="background-color: {renk_hex}; color: white; border-radius: 50%; width: 26px; height: 26px; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 13px; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.5);">{idx+1}</div>'
                folium.Marker([lat, lon], popup=f"<b>Durak {idx+1}</b><br>{row['Alici_Ad']}<br>Tel: {row['Telefon']}", tooltip=f"Durak {idx+1}", icon=folium.DivIcon(html=marker_html, icon_anchor=(13, 13))).add_to(m)
                
            folium.PolyLine(koordinat_listesi, color="#ff4b4b", weight=3, opacity=0.8).add_to(m)
            folium_static(m, width=1200, height=500)

    # --- ALT KISIM: ŞOFÖR MODU (OTP + TRENDYOL ENTEGRASYONU) ---
    if st.session_state.harita_hazir:
        with liste_kutusu:
            st.markdown("### 📱 Teslimat Sırası (Şoför Modu)")
            
            pending_orders = []
            completed_orders = []
            
            for idx, row in st.session_state.sirali_df.iterrows():
                g_id = row['Gizli_ID']
                if g_id in ['start_node', 'end_node']: 
                    pending_orders.append((idx, row, 'start_end'))
                else:
                    status = st.session_state.delivery_status.get(g_id, "pending")
                    if status == "pending": pending_orders.append((idx, row, 'pending'))
                    else: completed_orders.append((idx, row, status))
                        
            st.markdown("#### ⏳ Gidilecek Duraklar")
            
            for idx, row, status in pending_orders:
                durak_no = idx + 1
                lat = row['Enlem']
                lon = row['Boylam']
                g_id = row['Gizli_ID']
                gizli_kod = row.get('Teslimat_Kodu', '0000') 
                
                tel_temiz = "".join(filter(str.isdigit, str(row['Telefon'])))
                if tel_temiz.startswith("0"): tel_temiz = "9" + tel_temiz
                if not tel_temiz.startswith("90") and len(tel_temiz) == 10: tel_temiz = "90" + tel_temiz
                
                if durak_no == 1: border_color, durak_etiketi = "#4caf50", "🟢 BAŞLANGIÇ"
                elif durak_no == len(st.session_state.sirali_df): border_color, durak_etiketi = "#ff5252", "🔴 BİTİŞ"
                else: border_color, durak_etiketi = "#ff9800", "📦 TESLİMAT BEKLİYOR" 
                
                urun_html = ""
                if g_id not in ['start_node', 'end_node']:
                    urun_html = f"""<div style="text-align: right; background: rgba(255, 193, 7, 0.1); padding: 6px 12px; border-radius: 8px; border: 1px solid rgba(255, 193, 7, 0.3); flex-shrink: 0; margin-left: 10px;">
<div style="font-size: 22px; font-weight: 900; color: #ffc107; line-height: 1;">{row['Adet']} ADET</div>
<div style="font-size: 13px; font-weight: 700; color: #fffde7; margin-top: 4px; max-width: 150px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{row['Urun_Adi']}">{row['Urun_Adi']}</div>
</div>"""
                
                kart_html = f"""<div style="background: linear-gradient(145deg, #22232a, #2a2b33); padding: 20px; border-radius: 16px; margin-bottom: 10px; border-left: 6px solid {border_color}; box-shadow: 0 8px 20px rgba(0,0,0,0.15);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<div style="display: flex; align-items: center; gap: 10px;">
<span style="background-color: {border_color}; color: white; padding: 6px 12px; border-radius: 8px; font-weight: 800; font-size: 16px;">#{durak_no}</span>
<span style="color: #b0b0b0; font-size: 11px; font-weight: 700; letter-spacing: 1px;">{durak_etiketi}</span>
</div>
</div>
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
<div style="font-size: 20px; font-weight: 700; color: #ffffff; letter-spacing: 0.5px; flex: 1;">{row['Alici_Ad']}</div>
{urun_html}
</div>
<div style="font-size: 13px; color: #b0b0b0; margin-bottom: 6px;">📦 Paket No: {row['Paket_No']}  |  📑 Sipariş: {row['Siparis_No']}</div>
<div style="font-size: 14px; color: #a0a0b0; margin-bottom: 20px; line-height: 1.5; display: flex; align-items: flex-start; gap: 6px;">
<span style="font-size: 16px;">📍</span><span>{row['Adres']}</span>
</div>
<div style="display: flex; gap: 10px;">
<a href="https://www.google.com/maps/dir/?api=1&destination={lat},{lon}" target="_blank" class="action-btn btn-maps">🗺️ Yol Tarifi</a>
<a href="tel:{tel_temiz}" class="action-btn btn-call">📞 Ara</a>
</div>
</div>"""
                st.markdown(kart_html, unsafe_allow_html=True)
                
                if status == 'pending':
                    if 1 < durak_no < len(st.session_state.sirali_df):
                        
                        if st.session_state.get(f"show_otp_{idx}_{g_id}", False):
                            st.info("🔒 **Güvenli Teslimat:** Müşteriye SMS ile giden 4 haneli kodu girin.")
                            c_kod, c_onay, c_vazgec = st.columns([4, 4, 3])
                            with c_kod:
                                girilen_kod = st.text_input("Kod:", key=f"inp_{idx}_{g_id}", placeholder="Örn: 1234", label_visibility="collapsed")
                            with c_onay:
                                if st.button("✔️ Doğrula", key=f"dogrula_{idx}_{g_id}", type="primary", use_container_width=True):
                                    if girilen_kod == str(gizli_kod):
                                        with st.spinner("İşleniyor..."):
                                            sip_no = str(row['Siparis_No']).strip()
                                            
                                            if sip_no.startswith('2') or sip_no.startswith('4') or g_id in ['start_node', 'end_node']:
                                                basari, msj = True, "Lokal Teslimat"
                                                durum_sonucu = "success_local"
                                            else:
                                                basari, msj = trendyol_teslim_edildi_yap(TRENDYOL_SATICI_ID, TRENDYOL_API_KEY, TRENDYOL_API_SECRET, row['Paket_No'], sip_no)
                                                durum_sonucu = "success_trendyol"
                                                
                                            if basari:
                                                st.session_state.delivery_status[g_id] = durum_sonucu
                                                st.session_state[f"show_otp_{idx}_{g_id}"] = False
                                                otomatik_kaydet() 
                                                st.toast("✅ Paket Başarıyla Teslim Edildi!")
                                                st.rerun()
                                            else:
                                                st.error(f"❌ TRENDYOL REDDETTİ:\n\n{msj}")
                                                st.session_state[f"trendyol_hata_{idx}_{g_id}"] = True
                                    else:
                                        st.error("❌ Hatalı Kod! Lütfen tekrar deneyin.")
                            with c_vazgec:
                                if st.button("⬅️ Vazgeç", key=f"vzg_{idx}_{g_id}", use_container_width=True):
                                    st.session_state[f"show_otp_{idx}_{g_id}"] = False
                                    st.session_state[f"trendyol_hata_{idx}_{g_id}"] = False
                                    st.rerun()
                                    
                            if st.session_state.get(f"trendyol_hata_{idx}_{g_id}", False):
                                st.warning("Trendyol API bu siparişi reddetti. Sistemi devam ettirmek için lokal teslim edebilirsiniz.")
                                if st.button("⚠️ Trendyol'u Yoksay ve Sadece Uygulamada Teslim Et", key=f"force_{idx}_{g_id}", use_container_width=True):
                                    st.session_state.delivery_status[g_id] = "success_local" 
                                    st.session_state[f"show_otp_{idx}_{g_id}"] = False
                                    st.session_state[f"trendyol_hata_{idx}_{g_id}"] = False
                                    otomatik_kaydet() 
                                    st.rerun()

                        else:
                            c_ok, c_fail, c_sms = st.columns([3, 3, 3])
                            with c_ok:
                                if st.button("✅ Teslim Edildi", key=f"ok_{idx}_{g_id}", use_container_width=True):
                                    st.session_state[f"show_otp_{idx}_{g_id}"] = True
                                    st.rerun()
                            with c_fail:
                                if st.button("❌ İptal / Edilemedi", key=f"fail_{idx}_{g_id}", use_container_width=True):
                                    st.session_state.delivery_status[g_id] = "failed" 
                                    otomatik_kaydet() 
                                    st.rerun()
                            with c_sms:
                                if st.button("📨 SMS Gönder", key=f"sms_{idx}_{g_id}", use_container_width=True):
                                    with st.spinner("SMS Gönderiliyor..."):
                                        basari, msj = netgsm_sms_gonder(tel_temiz, row['Alici_Ad'], row['Paket_No'], row['Urun_Adi'], gizli_kod)
                                        if basari: st.toast(f"✅ {row['Alici_Ad']} kişisine SMS gönderildi!")
                                        else: st.error(f"❌ {msj}")
                            
                            c_sira, c_tasi, _ = st.columns([3, 3, 3])
                            with c_sira:
                                maks_durak = max(2, len(st.session_state.sirali_df) - 1)
                                hedef_sira = st.number_input("Sıra No", min_value=2, max_value=maks_durak, value=durak_no, key=f"sira_{idx}_{g_id}", label_visibility="collapsed")
                            with c_tasi:
                                if st.button("🔄 Taşı", key=f"move_{idx}_{g_id}", type="primary", use_container_width=True):
                                    eski_idx = idx
                                    yeni_idx = hedef_sira - 1
                                    if eski_idx != yeni_idx:
                                        row_to_move = st.session_state.sirali_df.iloc[eski_idx:eski_idx+1]
                                        df_temp = st.session_state.sirali_df.drop(st.session_state.sirali_df.index[eski_idx])
                                        df_top = df_temp.iloc[:yeni_idx]
                                        df_bottom = df_temp.iloc[yeni_idx:]
                                        st.session_state.sirali_df = pd.concat([df_top, row_to_move, df_bottom]).reset_index(drop=True)
                                        st.rerun() 
                    else:
                        # 1. veya Son duraksa
                        if st.session_state.get(f"show_otp_{idx}_{g_id}", False):
                            st.info("🔒 **Güvenli Teslimat:** Müşteriye SMS ile giden 4 haneli kodu girin.")
                            c_kod, c_onay, c_vazgec = st.columns([4, 4, 3])
                            with c_kod:
                                girilen_kod = st.text_input("Kod:", key=f"inp_{idx}_{g_id}", placeholder="Örn: 1234", label_visibility="collapsed")
                            with c_onay:
                                if st.button("✔️ Doğrula", key=f"dogrula_{idx}_{g_id}", type="primary", use_container_width=True):
                                    if girilen_kod == str(gizli_kod):
                                        with st.spinner("İşleniyor..."):
                                            basari, msj = True, "Lokal Teslimat"
                                            if basari:
                                                st.session_state.delivery_status[g_id] = "success_local"
                                                st.session_state[f"show_otp_{idx}_{g_id}"] = False
                                                otomatik_kaydet() 
                                                st.toast("✅ Paket Başarıyla Teslim Edildi!")
                                                st.rerun()
                                    else:
                                        st.error("❌ Hatalı Kod! Lütfen tekrar deneyin.")
                            with c_vazgec:
                                if st.button("⬅️ Vazgeç", key=f"vzg_{idx}_{g_id}", use_container_width=True):
                                    st.session_state[f"show_otp_{idx}_{g_id}"] = False
                                    st.rerun()
                        else:
                            c_ok, c_fail, c_sms = st.columns([3, 3, 3])
                            with c_ok:
                                if st.button("✅ Teslim Edildi", key=f"ok_{idx}_{g_id}", use_container_width=True):
                                    st.session_state[f"show_otp_{idx}_{g_id}"] = True
                                    st.rerun()
                            with c_fail:
                                if st.button("❌ İptal / Edilemedi", key=f"fail_{idx}_{g_id}", use_container_width=True):
                                    st.session_state.delivery_status[g_id] = "failed"
                                    otomatik_kaydet() 
                                    st.rerun()
                            with c_sms:
                                if st.button("📨 SMS Gönder", key=f"sms_{idx}_{g_id}", use_container_width=True):
                                    with st.spinner("SMS Gönderiliyor..."):
                                        basari, msj = netgsm_sms_gonder(tel_temiz, row['Alici_Ad'], row['Paket_No'], row['Urun_Adi'], gizli_kod)
                                        if basari: st.toast(f"✅ {row['Alici_Ad']} kişisine SMS gönderildi!")
                                        else: st.error(f"❌ {msj}")

                    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

            if len(completed_orders) > 0:
                st.markdown("---")
                st.markdown("#### 🏁 Tamamlanan İşlemler")
                
                for idx, row, status in completed_orders:
                    durak_no = idx + 1
                    g_id = row['Gizli_ID']
                    
                    if status == "success_trendyol": 
                        bg_grad = "linear-gradient(145deg, #1b2e1f, #223827)"
                        border_color = "#4caf50" 
                        durak_etiketi = "✅ TRENDYOL ONAYLI"
                    elif status == "success_local": 
                        bg_grad = "linear-gradient(145deg, #18283b, #1f354d)"
                        border_color = "#2196f3" 
                        durak_etiketi = "☑️ LOKAL TESLİMAT"
                    elif status == "failed":
                        bg_grad = "linear-gradient(145deg, #2e1b1b, #382222)"
                        border_color = "#ff5252" 
                        durak_etiketi = "❌ EDİLEMEDİ"
                    else:
                        continue 
                        
                    kart_html_comp = f"""<div style="background: {bg_grad}; padding: 15px; border-radius: 12px; margin-bottom: 10px; border-left: 6px solid {border_color}; opacity: 0.9;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<div style="display: flex; align-items: center; gap: 10px;">
<span style="background-color: {border_color}; color: white; padding: 4px 10px; border-radius: 8px; font-weight: 800; font-size: 14px;">#{durak_no}</span>
<span style="color: white; font-size: 12px; font-weight: 700; letter-spacing: 1px;">{durak_etiketi}</span>
</div>
</div>
<div style="font-size: 18px; font-weight: 700; color: #ffffff; margin-bottom: 4px;"><del>{row['Alici_Ad']}</del></div>
<div style="font-size: 12px; color: #b0b0b0;">📍 {str(row['Adres'])[:50]}...</div>
</div>"""
                    st.markdown(kart_html_comp, unsafe_allow_html=True)
                    
                    if st.button("↩️ İşlemi Geri Al", key=f"undo_{idx}_{g_id}", use_container_width=True):
                        st.session_state.delivery_status[g_id] = "pending"
                        otomatik_kaydet() 
                        st.rerun()
                        
                    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)


# --- SEKME 3: 👤 PROFİL VE GEÇMİŞ KONTROLÜ (YENİLENMİŞ EFSANE TASARIM) ---
with tab_profil:
    st.markdown(f"### 👤 Hoş Geldin, {st.session_state.kullanici.upper()}!")
    st.markdown("Buradan geçmişte tamamladığın rotaları görüntüleyebilir ve hesabından güvenli bir şekilde çıkış yapabilirsin.")
    
    col_cikis, _ = st.columns([1, 4])
    with col_cikis:
        if st.button("🚪 Sistemden Çıkış Yap", type="primary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
            
    st.markdown("---")
    st.markdown("#### 📜 Geçmiş Rotalarım (Analizli)")
    st.info("💡 **Bilgi:** Rotaları indirebilmek veya SİLEBİLMEK için Admin yetkisi gereklidir. Raporlamalar otomatik hesaplanmıştır.")
    
    gecmis_dosyalar = [f for f in os.listdir("gecmis_rotalar") if f.endswith(".xlsx") and (f"_{st.session_state.kullanici}_" in f or f.startswith(f"{st.session_state.kullanici}_"))]
    
    if len(gecmis_dosyalar) == 0:
        st.warning("Henüz kaydedilmiş bir geçmiş rotan bulunmuyor. Sen rotanı oluşturdukça sistem burayı otomatik dolduracak.")
    else:
        for dosya in sorted(gecmis_dosyalar, reverse=True):
            isim_temiz = dosya.replace(".xlsx", "")
            parcalar = isim_temiz.split("_")
            
            bolge_gosterim = "Bilinmiyor"
            tarih_gosterim = ""
            teslim_gosterim = "?"
            hata_gosterim = "?"
            
            if len(parcalar) >= 6:
                bolge_gosterim = parcalar[0].replace("-", " ")
                tarih_gosterim = f"{parcalar[2]} {parcalar[3].replace('-', ':')}"
                teslim_gosterim = parcalar[4].replace("T", "")
                hata_gosterim = parcalar[5].replace("H", "")
            else:
                tarih_gosterim = f"{parcalar[1]} {parcalar[2].replace('-', ':')}"
            
            col_file, col_down = st.columns([3, 2])
            with col_file:
                rapor_html = f"""
                <div style='padding:15px; background-color:#2b2b36; border-radius:8px; border-left: 5px solid #1e88e5; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>
                    <div style='font-size: 16px; font-weight: bold; color: white; margin-bottom: 5px;'>📍 Teslimat Bölgesi: <span style='color:#1e88e5;'>{bolge_gosterim.upper()}</span></div>
                    <div style='font-size: 13px; color: #a0a0a0; margin-bottom: 12px;'>🗓️ Kayıt Tarihi: {tarih_gosterim}</div>
                    <div style='display: flex; gap: 15px;'>
                        <div style='background-color: rgba(76, 175, 80, 0.1); border: 1px solid #4caf50; padding: 4px 10px; border-radius: 6px; color: #4caf50; font-weight: bold; font-size: 13px;'>✅ Toplam Teslim: {teslim_gosterim}</div>
                        <div style='background-color: rgba(244, 67, 54, 0.1); border: 1px solid #f44336; padding: 4px 10px; border-radius: 6px; color: #f44336; font-weight: bold; font-size: 13px;'>❌ İptal/Hata: {hata_gosterim}</div>
                    </div>
                </div>
                """
                st.markdown(rapor_html, unsafe_allow_html=True)
            
            with col_down:
                st.markdown("<br><br>", unsafe_allow_html=True) 
                
                if st.session_state.get(f"auth_{dosya}", False):
                    c_dl, c_del = st.columns([7, 3])
                    with c_dl:
                        with open(f"gecmis_rotalar/{dosya}", "rb") as f:
                            st.download_button("📥 İndir", data=f.read(), file_name=dosya, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"dl_{dosya}", use_container_width=True)
                    with c_del:
                        if st.button("🗑️ Sil", key=f"del_{dosya}", use_container_width=True):
                            try:
                                os.remove(f"gecmis_rotalar/{dosya}")
                                st.toast("✅ Dosya başarıyla silindi!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Silinemedi: {e}")
                else:
                    col_p, col_b = st.columns([2, 1])
                    with col_p:
                        pwd = st.text_input("Şifre", key=f"pwd_{dosya}", type="password", label_visibility="collapsed", placeholder="Admin Şifresi")
                    with col_b:
                        if st.button("Kilit Aç", key=f"btn_ac_{dosya}", use_container_width=True):
                            if pwd == ADMIN_SIFRE:
                                st.session_state[f"auth_{dosya}"] = True
                                st.rerun()
                            elif pwd != "":
                                st.error("❌ Hata")
            st.markdown("<hr style='margin: 15px 0; border-color: #333;'>", unsafe_allow_html=True)
