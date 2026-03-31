import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
import json
import os
import threading
import sqlite3
from datetime import datetime
import time
import webbrowser
import random
import urllib.parse
import re
import pandas as pd
import base64  # HB için gerekli

try:
    from curl_cffi import requests as crequests
except ImportError:
    messagebox.showerror("HATA", "Terminale şunu yaz:\npip install curl_cffi customtkinter pandas")
    exit()

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

CONFIG_FILE = "coni_config.json"
DB_FILE = "siparisler.db"
AYAR_DOSYASI = "coni_lojistik_matrix_v18.json" 
ESKI_AYAR_DOSYASI = "coni_lojistik_data_v17.json" 

TURKIYE_HARITASI = {
    "ADANA": ["ALADAĞ", "CEYHAN", "ÇUKUROVA", "FEKE", "İMAMOĞLU", "KARAİSALI", "KARATAŞ", "KOZAN", "POZANTI", "SAİMBEYLİ", "SARIÇAM", "SEYHAN", "TUFANBEYLİ", "YUMURTALIK", "YÜREĞİR"],
    "ADIYAMAN": ["BESNİ", "ÇELİKHAN", "GERGER", "GÖLBAŞI", "KAHTA", "MERKEZ", "SAMSAT", "SİNCİK", "TUT"],
    "AFYONKARAHİSAR": ["BAŞMAKÇI", "BAYAT", "BOLVADİN", "ÇAY", "ÇOBANLAR", "DAZKIRI", "DİNAR", "EMİRDAĞ", "EVCİLER", "HOCALAR", "İHSANİYE", "İSCEHİSAR", "KIZILÖREN", "MERKEZ", "SANDIKLI", "SİNANPAŞA", "SULTANDAĞI", "ŞUHUT"],
    "AĞRI": ["DİYADİN", "DOĞUBAYAZIT", "ELEŞKİRT", "HAMUR", "MERKEZ", "PATNOS", "TAŞLIÇAY", "TUTAK"], 
    "AMASYA": ["GÖYNÜCEK", "GÜMÜŞHACIKÖY", "HAMAMÖZÜ", "MERKEZ", "MERZİFON", "SULUOVA", "TAŞOVA"],
    "ANKARA": ["AKYURT", "ALTINDAĞ", "AYAŞ", "BALA", "BEYPAZARI", "ÇAMLIDERE", "ÇANKAYA", "ÇUBUK", "ELMADAĞ", "ETİMESGUT", "EVREN", "GÖLBAŞI", "GÜDÜL", "HAYMANA", "KAHRAMANKAZAN", "KALECİK", "KEÇİÖREN", "KIZILCAHAMAM", "MAMAK", "NALLIHAN", "POLATLI", "PURSAKLAR", "SİNCAN", "ŞEREFLİKOÇHİSAR", "YENİMAHALLE"],
    "ANTALYA": ["AKSEKİ", "AKSU", "ALANYA", "DEMRE", "DÖŞEMEALTI", "ELMALI", "FİNİKE", "GAZİPAŞA", "GÜNDOĞMUŞ", "İBRADI", "KAŞ", "KEMER", "KEPEZ", "KONYAALTI", "KORKUTELİ", "KUMLUCA", "MANAVGAT", "MURATPAŞA", "SERİK"],
    "ARTVİN": ["ARDANUÇ", "ARHAVİ", "BORÇKA", "HOPA", "KEMALPAŞA", "MERKEZ", "MURGUL", "ŞAVŞAT", "YUSUFELİ"],
    "AYDIN": ["BOZDOĞAN", "BUHARKENT", "ÇİNE", "DİDİM", "EFELER", "GERMENCİK", "İNCİRLİOVA", "KARACASU", "KARPUZLU", "KOÇARLI", "KÖŞK", "KUŞADASI", "KUYUCAK", "NAZİLLİ", "SÖKE", "SULTANHİSAR", "YENİPAZAR"],
    "BALIKESİR": ["ALTIEYLÜL", "AYVALIK", "BALYA", "BANDIRMA", "BİGADİÇ", "BURHANİYE", "DURSUNBEY", "EDREMİT", "ERDEK", "GÖMEÇ", "GÖNEN", "HAVRAN", "İVRİNDİ", "KARESİ", "KEPSUT", "MANYAS", "MARMARA", "SAVAŞTEPE", "SINDIRGI", "SUSURLUK"],
    "BİLECİK": ["BOZÜYÜK", "GÖLPAZARI", "İNHİSAR", "MERKEZ", "OSMANELİ", "PAZARYERİ", "SÖĞÜT", "YENİPAZAR"],
    "BİNGÖL": ["MERKEZ", "ADAKLI", "GENÇ", "KARLIOVA", "KİĞI", "SOLHAN", "YAYLADERE", "YEDİSU"],
    "BİTLİS": ["MERKEZ", "ADİLCEVAZ", "AHLAT", "GÜROYMAK", "HİZAN", "MUTKİ", "TATVAN"],
    "BOLU": ["DÖRTDİVAN", "GEREDE", "GÖYNÜK", "KIBRISCIK", "MENGEN", "MERKEZ", "MUDURNU", "SEBEN", "YENİÇAĞA"],
    "BURDUR": ["MERKEZ", "AĞLASUN", "ALTINYAYLA", "BUCAK", "ÇAVDIR", "ÇELTİKÇİ", "GÖLHİSAR", "KARAMANLI", "KEMER", "TEFENNİ", "YEŞİLOVA"],
    "BURSA": ["BÜYÜKORHAN", "GEMLİK", "GÜRSU", "HARMANCIK", "İNEGÖL", "İZNİK", "KARACABEY", "KELES", "KESTEL", "MUDANYA", "MUSTAFAKEMALPAŞA", "NİLÜFER", "ORHANELİ", "ORHANGAZİ", "OSMANGAZİ", "YENİŞEHİR", "YILDIRIM"],
    "ÇANAKKALE": ["AYVACIK", "BAYRAMİÇ", "BİGA", "BOZCAADA", "ÇAN", "ECEABAT", "EZİNE", "GELİBOLU", "LAPSEKİ", "MERKEZ", "YENİCE"],
    "ÇANKIRI": ["MERKEZ", "ATKARACALAR", "BAYRAMÖREN", "ÇERKEŞ", "ELDİVAN", "ILGAZ", "KIZILIRMAK", "KORGUN", "KURŞUNLU", "ORTA", "ŞABANÖZÜ", "YAPRAKLI"],
    "ÇORUM": ["ALACA", "BAYAT", "BOĞAZKALE", "DODURGA", "İSKİLİP", "KARGI", "LAÇİN", "MECİTÖZÜ", "MERKEZ", "OĞUZLAR", "ORTAKÖY", "OSMANCIK", "SUNGURLU", "UĞURLUDAĞ"],
    "DENİZLİ": ["ACIPAYAM", "BABADAĞ", "BAKLAN", "BEKİLLİ", "BEYAĞAÇ", "BOZKURT", "BULDAN", "ÇAL", "ÇAMELİ", "ÇARDAK", "ÇİVRİL", "GÜNEY", "HONAZ", "KALE", "MERKEZEFENDİ", "PAMUKKALE", "SARAYKÖY", "SERİNHİSAR", "TAVAS"],
    "DİYARBAKIR": ["BAĞLAR", "BİSMİL", "ÇERMİK", "ÇINAR", "ÇÜNGÜŞ", "DİCLE", "EĞİL", "ERGANİ", "HANİ", "HAZRO", "KAYAPINAR", "KOCAKÖY", "KULP", "LİCE", "SİLVAN", "SUR", "YENİŞEHİR"],
    "DÜZCE": ["AKÇAKOCA", "CUMAYERİ", "ÇİLİMLİ", "GÖLYAKA", "GÜMÜŞOVA", "KAYNAŞLI", "MERKEZ", "YIĞLICA"],
    "EDİRNE": ["ENEZ", "HAVSA", "İPSALA", "KEŞAN", "LALAPAŞA", "MERİÇ", "MERKEZ", "SÜLOĞLU", "UZUNKÖPRÜ"],
    "ELAZIĞ": ["AĞIN", "ALACAKAYA", "ARICAK", "BASKİL", "KARAKOÇAN", "KEBAN", "KOVANCILAR", "MADEN", "MERKEZ", "PALU", "SİVRİCE"],
    "ERZİNCAN": ["ÇAYIRLI", "İLİÇ", "KEMAH", "KEMALİYE", "MERKEZ", "OTLUKBELİ", "REFAHİYE", "TERCAN", "ÜZÜMLÜ"],
    "ERZURUM": ["AŞKALE", "AZİZİYE", "ÇAT", "HINIS", "HORASAN", "İSPİR", "KARAÇOBAN", "KARAYAZI", "KÖPRÜKÖY", "NARMAN", "OLTU", "OLUR", "PALANDÖKEN", "PASİNLER", "PAZARYOLU", "ŞENKAYA", "TEKMAN", "TORTUM", "UZUNDERE", "YAKUTİYE"],
    "ESKİŞEHİR": ["ALPU", "BEYLİKOVA", "ÇİFTELER", "GÜNYÜZÜ", "HAN", "İNÖNÜ", "MAHMUDİYE", "MİHALGAZİ", "MİHALIÇÇIK", "ODUNPAZARI", "SARICAKAYA", "SEYİTGAZİ", "SİVRİHİSAR", "TEPEBAŞI"],
    "GAZİANTEP": ["ARABAN", "İSLAHİYE", "KARKAMIŞ", "NİZİP", "NURDAĞI", "OĞUZELİ", "ŞAHİNBEY", "ŞEHİTKAMİL", "YAVUZELİ"],
    "GİRESUN": ["ALUCRA", "BULANCAK", "ÇAMOLUK", "ÇANAKÇI", "DERELİ", "DOĞANKENT", "ESPİYE", "EYNESİL", "GÖRELE", "GÜCE", "KEŞAP", "MERKEZ", "PİRAZİZ", "ŞEBİNKARAHİSAR", "TİREBOLU", "YAĞLIDERE"],
    "GÜMÜŞHANE": ["KELKİT", "KÖSE", "KÜRTÜN", "MERKEZ", "ŞİRAN", "TORUL"],
    "HAKKARİ": ["ÇUKURCA", "DERECİK", "MERKEZ", "ŞEMDİNLİ", "YÜKSEKOVA"],
    "HATAY": ["ALTINÖZÜ", "ANTAKYA", "ARSUZ", "BELEN", "DEFNE", "DÖRTYOL", "ERZİN", "HASSA", "İSKENDERUN", "KIRIKHAN", "KUMLUCA", "PAYAS", "REYHANLI", "SAMANDAĞ", "YAYLADAĞI"],
    "ISPARTA": ["AĞLASUN", "AKSU", "ATABEY", "BUCAK", "ÇAVDIR", "ÇELTİKÇİ", "GÖLHİSAR", "KARAMANLI", "KEMER", "MERKEZ", "TEFENNİ", "YEŞİLOVA"],
    "MERSİN": ["AKDENİZ", "ANAMUR", "AYDINCIK", "BOZYAZI", "ÇAMLIYAYLA", "ERDEMLİ", "GÜLNAR", "MEZİTLİ", "MUT", "SİLİFKE", "TARSUS", "TOROSLAR", "YENİŞEHİR"],
    "İSTANBUL": ["ADALAR", "ARNAVUTKÖY", "ATAŞEHİR", "AVCILAR", "BAĞCILAR", "BAHÇELİEVLER", "BAKIRKÖY", "BAŞAKŞEHİR", "BAYRAMPAŞA", "BEŞİKTAŞ", "BEYKOZ", "BEYLİKDÜZÜ", "BEYOĞLU", "BÜYÜKÇEKMECE", "ÇATALCA", "ÇEKMEKÖY", "ESENLER", "ESENYURT", "EYÜPSULTAN", "FATİH", "GAZİOSMANPAŞA", "GÜNGÖREN", "KADIKÖY", "KAĞITHANE", "KARTAL", "KÜÇÜKÇEKMECE", "MALTEPE", "PENDİK", "SANCAKTEPE", "SARIYER", "SİLİVRİ", "SULTANBEYLİ", "SULTANGAZİ", "ŞİLE", "ŞİŞLİ", "TUZLA", "ÜMRANİYE", "ÜSKÜDAR", "ZEYTİNBURNU"],
    "İZMİR": ["ALİAĞA", "BALÇOVA", "BAYINDIR", "BAYRAKLI", "BERGAMA", "BEYDAĞ", "BORNOVA", "BUCA", "ÇEŞME", "ÇİĞLİ", "DİKİLİ", "FOÇA", "GAZİEMİR", "GÜZELBAHÇE", "KARABAĞLAR", "KARABURUN", "KARŞIYAKA", "KEMALPAŞA", "KINIK", "KİRAZ", "KONAK", "MENDERES", "MENEMEN", "NARLIDERE", "ÖDEMİŞ", "SEFERİHİSAR", "SELÇUK", "TİRE", "TORBALI", "URLA"],
    "KARS": ["AKYAKA", "ARPAÇAY", "DİGOR", "KAĞIZMAN", "MERKEZ", "SARIKAMIŞ", "SELİM", "SUSUZ"],
    "KASTAMONU": ["MERKEZ", "ABANA", "AĞLI", "ARAÇ", "AZDAVAY", "BOZKURT", "CİDE", "ÇATALZEYTİN", "DADAY", "DEVREKANİ", "DOĞANYURT", "HANÖNÜ", "İHSANGAZİ", "İNEBOLU", "KÜRE", "PINARBAŞI", "SEYDİLER", "ŞENPAZAR", "TAŞKÖPRÜ", "TOSYA"],
    "KAYSERİ": ["BÜNYAN", "AKKIŞLA", "DEVELİ", "FELAHİYE", "HACILAR", "İNCESU", "KOCASİNAN", "MELİKGAZİ", "ÖZVATAN", "PINARBAŞI", "SARIOĞLAN", "SARIZ", "TALAS", "TOMARZA", "YAHYALI", "YEŞİLHİSAR"],
    "KIRKLARELİ": ["MERKEZ", "BABAESKİ", "DEMİRKÖY", "KOFÇAZ", "LÜLEBURGAZ", "PEHLİVANKÖY", "PINARHİSAR", "VİZE"],
    "KIRŞEHİR": ["MERKEZ", "AKÇAKENT", "AKPINAR", "BOZTEPE", "ÇİÇEKDAĞI", "KAMAN", "MUCUR"],
    "KOCAELİ": ["BAŞİSKELE", "ÇAYIROVA", "DARICA", "DERİNCE", "DİLOVASI", "GEBZE", "GÖLCÜK", "İZMİT", "KANDIRA", "KARAMÜRSEL", "KARTEPE", "KÖRFEZ"],
    "KONYA": ["AKÖREN", "AKŞEHİR", "ALTINEKİN", "BEYŞEHİR", "BOZKIR", "CİHANBEYLİ", "ÇELTİK", "ÇUMRA", "DERBENT", "DEREBUCAK", "DOĞANHİSAR", "EMİRGAZİ", "EREĞLİ", "GÜNEYSINIR", "HADİM", "HALKAPINAR", "HÜYÜK", "ILGIN", "KADINHANI", "KARAPINAR", "KARATAY", "KULU", "MERAM", "SARAYÖNÜ", "SELÇUKLU", "SEYDİŞEHİR", "TAŞKENT", "TUZLUKÇU", "YALIHÜYÜK", "YUNAK"],
    "KÜTAHYA": ["MERKEZ", "ALTINTAŞ", "ASLANAPA", "ÇAVDARHİSAR", "DOMANİÇ", "DUMLUPINAR", "EMET", "GEDİZ", "HİSARCIK", "PAZARLAR", "ŞAPHANE", "SİMAV", "TAVŞANLI"],
    "MALATYA": ["AKÇADAĞ", "ARAİGİR", "ARGUVAN", "BATTALGAZİ", "DARENDE", "DOĞANŞEHİR", "DOĞANYOL", "HEKİMHAN", "KALE", "KULUNCAK", "PÜTÜRGE", "YAZIHAN", "YEŞİLYURT"],
    "MANİSA": ["AHMETLİ", "AKHİSAR", "ALAŞEHİR", "DEMİRCİ", "GÖLMARMARA", "GÖRDES", "KIRKAĞAÇ", "KÖPRÜBAŞI", "KULA", "SALİHLİ", "SARIGÖL", "SARUHANLI", "SELENDİ", "SOMA", "ŞEHZADELER", "TURGUTLU", "YUNUSEMRE"],
    "KAHRAMANMARAŞ": ["AFŞİN", "ANDIRIN", "ÇAĞLAYANCERİT", "DULKADİROĞLU", "EKİNÖZÜ", "ELBİSTAN", "GÖKSUN", "NURHAK", "ONİKİŞUBAT", "PAZARCIK", "TÜRKOĞLU"],
    "MARDİN": ["ARTUKLU", "DARGEÇİT", "DERİK", "KIZILTEPE", "MAZIDAĞI", "MİDYAT", "NUSAYBİN", "ÖMERLİ", "SAVUR", "YEŞİLLİ"],
    "MUĞLA": ["BODRUM", "DALAMAN", "DATÇA", "FETHİYE", "KAVAKLIDERE", "KÖYCEĞİZ", "MARMARİS", "MENTEŞE", "MİLAS", "ORTACA", "SEYDİKEMER", "ULA", "YATAĞAN"],
    "MUŞ": ["MERKEZ", "BULANIK", "HASKÖY", "KORKUT", "MALAZGİRT", "VARTO"],
    "NEVŞEHİR": ["MERKEZ", "ACIGÖL", "AVANOS", "DERİNKUYU", "GÜLŞEHİR", "HACIBEKTAŞ", "KOZAKLI", "ÜRGÜP"],
    "NİĞDE": ["MERKEZ", "ALTUNHİSAR", "BOR", "ÇAMARDI", "ÇİFTLİK", "ULUKIŞLA"],
    "ORDU": ["AKKUŞ", "ALTINORDU", "AYBASTI", "ÇAMAŞ", "ÇATALPINAR", "ÇAYBAŞI", "FATSA", "GÖLKÖY", "GÜLYALI", "GÜRGENTEPE", "İKİZCE", "KABADÜZ", "KABATAŞ", "KORGAN", "KUMRU", "MESUDİYE", "PERŞEMBE", "ULUBEY", "ÜNYE"],
    "RİZE": ["MERKEZ", "ARDEŞEN", "ÇAMLIHEMŞİN", "ÇAYELİ", "DEREPAZARI", "FINDIKLI", "GÜNEYSU", "HEMŞİN", "İKİZDERE", "İYİDERE", "KALKANDERE", "PAZAR"],
    "SAKARYA": ["ADAPAZARI", "AKYAZI", "ARİFİYE", "ERENLER", "FERİZLİ", "GEYVE", "HENDEK", "KARAPÜRÇEK", "KARASU", "KAYNARCA", "KOCAALİ", "PAMUKOVA", "SAPANCA", "SERDİVAN", "SÖĞÜTLÜ", "TARAKLI"],
    "SAMSUN": ["19 MAYIS", "ALAÇAM", "ASARCIK", "ATAKUM", "AYVACIK", "BAFRA", "CANİK", "ÇARŞAMBA", "HAVZA", "İLKADIM", "KAVAK", "LADİK", "SALIPAZARI", "TEKKEKÖY", "TERME", "VEZİRKÖPRÜ", "YAKAKENT"],
    "SİİRT": ["MERKEZ", "AYDINLAR", "BAYKAN", "ERUH", "KURTALAN", "PERVARİ", "ŞİRVAN"],
    "SİNOP": ["MERKEZ", "AYANCIK", "BOYABAT", "DİKMEN", "DURAĞAN", "ERFELEK", "GERZE", "SARAYDÜZÜ", "TÜRKELİ"],
    "SİVAS": ["MERKEZ", "AKINCILAR", "ALTINYAYLA", "DİVRİĞİ", "DOĞANŞAR", "GEMEREK", "GÖLOVA", "GÜRÜN", "HAFİK", "İMRANLI", "KANGAL", "KOYULHİSAR", "SUŞEHRİ", "ŞARKIŞLA", "ULAŞ", "YILDIZELİ", "ZARA"],
    "TEKİRDAĞ": ["ÇERKEZKÖY", "ÇORLU", "ERGENE", "HAYRABOLU", "KAPAKLI", "MALKARA", "MARMARAEREĞLİSİ", "MURATLI", "SARAY", "SÜLEYMANPAŞA", "ŞARKÖY"],
    "TOKAT": ["MERKEZ", "ALMUS", "ARTOVA", "BAŞÇİFTLİK", "ERBAA", "NİKSAR", "PAZAR", "REŞADİYE", "SULUSARAY", "TURHAL", "YEŞİLYURT", "ZİLE"],
    "TRABZON": ["MERKEZ", "AKÇAABAT", "ARAKLI", "ARSİN", "BEŞİKDÜZÜ", "ÇARŞIBAŞI", "ÇAYKARA", "DERNEKPAZARI", "DÜZKÖY", "HAYRAT", "KÖPRÜBAŞI", "MAÇKA", "OF", "ORTAHİSAR", "SÜRMENE", "ŞALPAZARI", "TONYA", "VAKFIKEBİR", "YOMRA"],
    "TUNCELİ": ["MERKEZ", "ÇEMİŞGEZEK", "HOZAT", "MAZGİRT", "NAZIMİYE", "OVACIK", "PERTEK", "PÜLÜMÜR"],
    "ŞANLIURFA": ["MERKEZ", "AKÇAKALE", "BİRECİK", "BOZOVA", "CEYLANPINAR", "EYYÜBİYE", "HALFETİ", "HALİLİYE", "HARRAN", "HİLVAN", "KARAKÖPRÜ", "SİVEREK", "SURUÇ", "VİRANŞEHİR"],
    "UŞAK": ["BANAZ", "EŞME", "KARAHALLI", "MERKEZ", "SİVASLI", "ULUBEY"],
    "VAN": ["MERKEZ", "BAHÇESARAY", "BAŞKALE", "ÇALDIRAN", "ÇATAK", "EDREMİT", "ERCİŞ", "GEVAŞ", "GÜRPINAR", "İPEKYOLU", "MURADİYE", "ÖZALP", "TUŞBA"],
    "YOZGAT": ["MERKEZ", "ALACA", "AYDINCIK", "BOĞAZLIYAN", "ÇANDIR", "ÇAYIRALAN", "ÇEKEREK", "KADIŞEHRİ", "SARAYKENT", "SARIKAYA", "SORGUN", "ŞEFAATLİ", "YENİFAKILI", "YERKÖY"],
    "ZONGULDAK": ["MERKEZ", "ALAPLI", "ÇAYCUMA", "DEVREK", "EREĞLİ", "GÖKÇEBEY", "KİLİMLİ", "KOZLU"],
    "AKSARAY": ["MERKEZ", "AĞAÇÖREN", "ESKİL", "GÜLAĞAÇ", "GÜZELYURT", "ORTAKÖY", "SARIYAHŞİ", "SULTANHANI"],
    "BAYBURT": ["MERKEZ", "AYDINTEPE", "DEMİRÖZÜ"],
    "KARAMAN": ["MERKEZ", "AYRANCI", "BAŞYAYLA", "ERMENEK", "KAZIMKARABEKİR", "SARIVELİLER"],
    "KIRIKKALE": ["MERKEZ", "BAHŞİLİ", "BALIŞEYH", "ÇELEBİ", "DELİCE", "KARAKEÇİLİ", "KESKİN", "SULAKYURT", "YAHŞİHAN"],
    "BATMAN": ["MERKEZ", "BEŞİRİ", "GERCÜŞ", "HASANKEYF", "KOZLUK", "SASON"],
    "ŞIRNAK": ["MERKEZ", "BEYTÜŞŞEBAP", "CİZRE", "GÜÇLÜKONAK", "İDİL", "SİLOPİ", "ULUDERE"],
    "BARTIN": ["AMASRA", "KURUCAŞİLE", "MERKEZ", "ULUS"],
    "ARDAHAN": ["ÇILDIR", "DAMAL", "GÖLE", "HANAK", "MERKEZ", "POSOF"],
    "IĞDIR": ["MERKEZ", "ARALIK", "KARAKOYUNLU", "TUZLUCA"],
    "YALOVA": ["ALTINOVA", "ARMUTLU", "ÇINARCIK", "ÇİFTLİKKÖY", "MERKEZ", "TERMAL"],
    "KARABÜK": ["MERKEZ", "EFLANİ", "ESKİPAZAR", "OVACIK", "SAFRANBOLU", "YENİCE"],
    "KİLİS": ["ELBEYLİ", "MUSABEYLİ", "POLATELİ", "MERKEZ"],
    "OSMANİYE": ["MERKEZ", "BAHÇE", "DÜZİÇİ", "HASANBEYLİ", "KADİRLİ", "SUMBAS", "TOPRAKKALE"]
}

SABIT_URUNLER = [
    "50X50 SİYAH ÇAP", "50X50 BEYAZ ÇAP", "50X50 GOLD ÇAP", "50X50 ESKİTME ÇAP",
    "60X60 SİYAH ÇAP", "60X60 BEYAZ ÇAP", "60X60 GOLD ÇAP", "60X60 ESKİTME ÇAP",
    "70X70 SİYAH ÇAP", "70X70 BEYAZ ÇAP", "70X70 GOLD ÇAP", "70X70 ESKİTME ÇAP",
    "80X80 SİYAH ÇAP", "80X80 BEYAZ ÇAP", "80X80 GOLD ÇAP", "80X80 ESKİTME ÇAP",
    "65X90 NATUREL AHŞAP", "65X90 CEVİZ AHŞAP", 
    "160X48 ASİMETRİK", "20X30 ASİMETRİK", "80X80"
]

VARSAYILAN_VERILER = {
    "desi_bilgileri": {
        "60x160": 15, "160x60": 15, "48x160": 15, "160x48": 15, "50x160": 12,
        "65x180": 17, "70x180": 19, "80x180": 28, "100x180": 30,
        "65X180 GOLD": 17, "65X180 BEYAZ": 17, "65X180 SİYAH": 17, "65X180": 17,
        "50x50": 5, "60x60": 8, "70x70": 10, "80x80": 12, "90x90": 13, "100x100": 15,
        "AURA ASİMETRİK": 15, "DÜZ AURA ASİMETRİK": 15, "70x180 ASİMETRİK": 19,
        "3x3": 28, "KAPI": 28, "65x90": 12
    }
}

# --- YARDIMCI FONKSİYONLAR ---
def normalize_tr(text):
    if not isinstance(text, str): return ""
    text = text.strip()
    mapping = {"i": "İ", "ı": "I", "ş": "Ş", "ğ": "Ğ", "ü": "Ü", "ö": "Ö", "ç": "Ç",
               "İ": "İ", "I": "I", "Ş": "Ş", "Ğ": "Ğ", "Ü": "Ü", "Ö": "Ö", "Ç": "Ç"}
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text.upper()

def sade_urun_bul(urun_adi):
    if not isinstance(urun_adi, str): return ""
    U = normalize_tr(urun_adi)
    
    if "ALINACAK" in U or "VERİLECEK" in U or "VERILECEK" in U: return urun_adi

    torpil_renk = ""
    renkler = ["SİYAH", "SIYAH", "GOLD", "ESKİTME", "GÜMÜŞ", "BEYAZ", "KROM", "FÜME", "FUME"]
    for r in renkler:
        if r in U:
            torpil_renk = " " + r.replace("SIYAH", "SİYAH").replace("FUME", "FÜME")
            break
            
    def contains_size(text, s1, s2):
        pattern = fr"(^|[^0-9])({s1}\s*[xX]\s*{s2}|{s2}\s*[xX]\s*{s1})([^0-9]|$)"
        return re.search(pattern, text) is not None

    if contains_size(U, "48", "160") or "ASBODUZ" in U: return ("DÜZ AURA ASİMETRİK" + torpil_renk).strip()
    if contains_size(U, "60", "160"): return ("AURA ASİMETRİK" + torpil_renk).strip()

    renk_listesi = ["ESKİTME", "BEYAZ", "SİYAH", "MAVİ", "KIRMIZI", "YEŞİL", "GRİ", "TURUNCU", 
                    "SARI", "MOR", "GOLD", "GÜMÜŞ", "PEMBE", "LACİVERT", "VİZON", "KREM"]
    
    ek_bilgi = ""
    if "DEĞİŞİM" in U: ek_bilgi = " (DEĞİŞİM)"
    elif "İADE" in U: ek_bilgi = " (İADE)"
    elif "İPTAL" in U: ek_bilgi = " (İPTAL)"

    malzeme_tag = ""
    if "AHŞAP" in U or "AHSAP" in U:
        if "NATUREL" in U: malzeme_tag = "NATUREL AHŞAP"
        elif "CEVİZ" in U or "CEVIZ" in U or "WALNUT" in U: malzeme_tag = "CEVİZ AHŞAP"
        else: malzeme_tag = "AHŞAP"

    if "EROS" in U and ("AHŞAP" in U or "AHSAP" in U) and "ASİMETRİK" in U and "AYAKLI" in U and "AYNA" in U: return "CEVİZ AHŞAP"
    if ("AHŞAP" in U or "AHSAP" in U) and "ASİMETRİK" in U and "AYAKLI" in U and "AYNA" in U and contains_size(U, "80", "180") and "EROS" not in U: return "NATUREL AHŞAP"

    renk_bulundu = ""
    def renk_ara():
        nonlocal renk_bulundu
        for r in renk_listesi:
            if "ESKİTME" in U: return "ESKİTME"
            if r in U: return r
        return ""
    
    if re.search(r"(^|[^A-ZÇĞİÖŞÜ0-9])DEKOR([^A-ZÇĞİÖŞÜ0-9]|$)", U):
        renk_bulundu = renk_ara()
        return ("KAPI " + renk_bulundu + ek_bilgi).strip()

    m3 = re.search(r"(3\s*[xX]\s*3)[-\s]*([A-ZÇĞİÖŞÜ]+)", U)
    if m3: return (m3.group(1).replace(" ", "") + " " + m3.group(2) + ek_bilgi).strip()

    if re.search(r"(^|[^A-ZÇĞİÖŞÜ0-9])AURA([^A-ZÇĞİÖŞÜ0-9]|$)", U):
        if "AYAKLI" in U: aura_base = "AYAKLI AURA ASİMETRİK"
        elif "DÜZ" in U: aura_base = "DÜZ AURA ASİMETRİK"
        else: aura_base = "AURA ASİMETRİK"
        
        if malzeme_tag: return (aura_base + " - " + malzeme_tag + ek_bilgi).strip()
        else:
            renk_bulundu = renk_ara()
            if renk_bulundu: return (aura_base + " - " + renk_bulundu + ek_bilgi).strip()
            return (aura_base + ek_bilgi).strip()

    m_cap = re.search(r"(\d{2,3})\s*CM", U)
    if m_cap and ("YUVARLAK" in U or "ÇAP" in U or "Ø" in U):
        val = m_cap.group(1)
        olcu = f"{val}X{val}"
        if malzeme_tag: return (olcu + " " + malzeme_tag + " ÇAP" + ek_bilgi).strip()
        else:
            renk_bulundu = renk_ara()
            return (olcu + " " + renk_bulundu + " ÇAP" + ek_bilgi).strip()

    olcu_bulundu = ""
    m_olcu = re.search(r"(\d{2,4})\s*[xX]\s*(\d{2,4})", U)
    if m_olcu:
        d1, d2 = int(m_olcu.group(1)), int(m_olcu.group(2))
        olcu_bulundu = f"{d1}X{d2}" if d1 < d2 else f"{d2}X{d1}"

    if not malzeme_tag: renk_bulundu = renk_ara()

    if "ASİMETRİK" in U and "AURA" not in U:
        sonuc = olcu_bulundu
        if malzeme_tag: sonuc += " " + malzeme_tag
        elif renk_bulundu: sonuc += " " + renk_bulundu
        return (sonuc + " ASİMETRİK" + ek_bilgi).strip()

    sonuc = olcu_bulundu
    if malzeme_tag: sonuc += " " + malzeme_tag
    elif renk_bulundu: sonuc += " " + renk_bulundu

    if ("ÇAP" in U or "Ø" in U) and "ÇAP" not in sonuc: sonuc += " ÇAP"
        
    return (sonuc + ek_bilgi).strip()

# =========================================================================
# MATRİS AYAR PENCERESİ SİNİFİ (Toplevel)
# =========================================================================
class MatrisAyarPenceresi(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("TÜRKİYE LOJİSTİK MATRİSİ (AÇIK: Biz Teslim, KAPALI: Kargo)")
        self.geometry("1100x700")
        self.transient(parent)
        
        self.secili_il = None

        self.loj_container = ctk.CTkFrame(self, fg_color="transparent")
        self.loj_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.frame_iller = ctk.CTkFrame(self.loj_container, width=320)
        self.frame_iller.pack(side="left", fill="y", padx=(0, 20))

        ctk.CTkLabel(self.frame_iller, text="📍 81 İL ŞALTERLERİ", font=("Roboto", 16, "bold")).pack(pady=10)

        self.il_arama = ctk.CTkEntry(self.frame_iller, placeholder_text="İl Ara...")
        self.il_arama.pack(fill="x", padx=10, pady=5)
        self.il_arama.bind("<KeyRelease>", self.filtrele_iller)

        self.scroll_iller = ctk.CTkScrollableFrame(self.frame_iller, fg_color="#1E1E1E", width=280)
        self.scroll_iller.pack(fill="both", expand=True, padx=10, pady=10)

        self.frame_detay = ctk.CTkFrame(self.loj_container)
        self.frame_detay.pack(side="right", fill="both", expand=True)

        self.lbl_secili_il = ctk.CTkLabel(self.frame_detay, text="👈 Yönetmek için soldan bir il seçin", font=("Roboto", 18, "bold"), text_color="#F39C12")
        self.lbl_secili_il.pack(pady=20)

        self.tab_detay = ctk.CTkTabview(self.frame_detay)
        self.tab_detay.pack(fill="both", expand=True, padx=20, pady=10)

        self.tab_ilceler = self.tab_detay.add("İlçeler (Şalterler)")
        self.tab_urunler = self.tab_detay.add("Ürünler (Şalterler)")
        
        f_yeni_urun = ctk.CTkFrame(self.tab_urunler, fg_color="transparent")
        f_yeni_urun.pack(fill="x", pady=5)
        ctk.CTkLabel(f_yeni_urun, text="Listede olmayan yeni ürün ekle:").pack(side="left", padx=5)
        self.entry_yeni_urun = ctk.CTkEntry(f_yeni_urun, placeholder_text="Örn: 90x90 MAVİ ÇAP", width=180)
        self.entry_yeni_urun.pack(side="left", padx=5)
        ctk.CTkButton(f_yeni_urun, text="Sisteme Tanıt", width=80, fg_color="#2980B9", command=self.sisteme_yeni_urun_ekle).pack(side="left")

        self.scroll_ilceler = ctk.CTkScrollableFrame(self.tab_ilceler, fg_color="#1E1E1E")
        self.scroll_ilceler.pack(fill="both", expand=True, padx=10, pady=10)

        self.scroll_urunler = ctk.CTkScrollableFrame(self.tab_urunler, fg_color="#1E1E1E")
        self.scroll_urunler.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_iller_listesi()

    def filtrele_iller(self, event):
        arama_metni = self.il_arama.get().upper()
        self.load_iller_listesi(filtre=arama_metni)

    def load_iller_listesi(self, filtre=""):
        for w in self.scroll_iller.winfo_children(): w.destroy()
        
        iller_matrix = self.parent.lojistik_ayarlar.get("iller", {})
        iller = sorted(iller_matrix.keys())
        
        for il in iller:
            if filtre and filtre not in il: continue
            
            il_aktif_mi = iller_matrix[il].get("il_aktif", False)
            renk = "#27AE60" if il_aktif_mi else "#C0392B"
            f = ctk.CTkFrame(self.scroll_iller, fg_color="#34495E", border_width=2, border_color=renk)
            f.pack(fill="x", pady=2, padx=2)

            btn = ctk.CTkButton(f, text=il, fg_color="transparent", anchor="w", font=("Roboto", 14, "bold"), hover_color="#2C3E50", command=lambda i=il: self.load_il_detay(i))
            btn.pack(side="left", fill="x", expand=True)

            switch_var = ctk.IntVar(value=1 if il_aktif_mi else 0)
            switch = ctk.CTkSwitch(f, text="", variable=switch_var, width=40, progress_color="#2ECC71", button_color="#F1C40F", command=lambda i=il, v=switch_var: self.toggle_il(i, v))
            switch.pack(side="right", padx=5)

    def load_il_detay(self, il):
        self.secili_il = il
        il_kurallari = self.parent.lojistik_ayarlar["iller"][il]
        il_aktif = il_kurallari.get("il_aktif", False)
        
        durum = "AÇIK (İLE BİZ GİDİYORUZ)" if il_aktif else "KAPALI (TÜM İL KARGOYA GİDER)"
        renk = "#2ECC71" if il_aktif else "#E74C3C"
        self.lbl_secili_il.configure(text=f"{il} ili Seçildi | Genel Durum: {durum}", text_color=renk)

        for w in self.scroll_ilceler.winfo_children(): w.destroy()
        for w in self.scroll_urunler.winfo_children(): w.destroy()

        ilceler_dict = il_kurallari.get("ilceler", {})
        for ilce in sorted(ilceler_dict.keys()):
            ilce_aktif = ilceler_dict[ilce]
            f = ctk.CTkFrame(self.scroll_ilceler, fg_color="#2C3E50")
            f.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(f, text=ilce, font=("Consolas", 14)).pack(side="left", padx=10, pady=5)
            s_var = ctk.IntVar(value=1 if ilce_aktif else 0)
            s = ctk.CTkSwitch(f, text="Biz Teslim / Kargo", variable=s_var, progress_color="#2ECC71", command=lambda i=il, ic=ilce, v=s_var: self.toggle_ilce(i, ic, v))
            s.pack(side="right", padx=10)

        urunler_dict = il_kurallari.get("urunler", {})
        for u in self.parent.lojistik_ayarlar.get("TUM_URUNLER", SABIT_URUNLER):
            if u not in urunler_dict: urunler_dict[u] = True
                
        for urun in sorted(urunler_dict.keys()):
            urun_aktif = urunler_dict[urun]
            f = ctk.CTkFrame(self.scroll_urunler, fg_color="#2C3E50")
            f.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(f, text=urun, font=("Consolas", 14)).pack(side="left", padx=10, pady=5)
            s_var = ctk.IntVar(value=1 if urun_aktif else 0)
            s = ctk.CTkSwitch(f, text="Açık / Kapalı", variable=s_var, progress_color="#2ECC71", command=lambda i=il, u=urun, v=s_var: self.toggle_urun(i, u, v))
            s.pack(side="right", padx=10)

    def toggle_il(self, il, switch_var):
        yeni_durum = (switch_var.get() == 1)
        self.parent.lojistik_ayarlar["iller"][il]["il_aktif"] = yeni_durum
        self.parent.ayarlari_kaydet()
        self.load_iller_listesi(filtre=self.il_arama.get().upper())
        if self.secili_il == il: self.load_il_detay(il)
        self.parent.tabloyu_doldur()

    def toggle_ilce(self, il, ilce, switch_var):
        yeni_durum = (switch_var.get() == 1)
        self.parent.lojistik_ayarlar["iller"][il]["ilceler"][ilce] = yeni_durum
        self.parent.ayarlari_kaydet()
        self.parent.tabloyu_doldur()

    def toggle_urun(self, il, urun, switch_var):
        yeni_durum = (switch_var.get() == 1)
        self.parent.lojistik_ayarlar["iller"][il]["urunler"][urun] = yeni_durum
        self.parent.ayarlari_kaydet()
        self.parent.tabloyu_doldur()

    def sisteme_yeni_urun_ekle(self):
        yeni_urun = self.entry_yeni_urun.get().strip().upper()
        if not yeni_urun: return
        
        tum_urunler = self.parent.lojistik_ayarlar.get("TUM_URUNLER", [])
        if yeni_urun not in tum_urunler:
            tum_urunler.append(yeni_urun)
            self.parent.lojistik_ayarlar["TUM_URUNLER"] = tum_urunler
            
            for il in self.parent.lojistik_ayarlar["iller"].keys():
                self.parent.lojistik_ayarlar["iller"][il]["urunler"][yeni_urun] = True
                
            self.parent.ayarlari_kaydet()
            self.entry_yeni_urun.delete(0, tk.END)
            messagebox.showinfo("Başarılı", f"{yeni_urun} eklendi ve full iller için Biz Teslim (Açık) yapıldı.")
            if self.secili_il: self.load_il_detay(self.secili_il)
        else:
            messagebox.showwarning("Hata", "Ürün zaten listede car.")

# =========================================================================
# OTOPİLOT ANA EKRAN (SiparisEkrani V25 Pro - Kusursuz PIN Motoru)
# =========================================================================
class SiparisEkrani(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("İRSAN DİZAYN | OTOPİLOT V25 PRO (Tam Korumalı PIN Motoru)")
        self.geometry("1550x750")

        self.api_config = self.load_config()
        self.lojistik_ayarlar = self.ayarlari_yukle() 
        
        self.durum_sozlugu = {
            "Tümü": "ALL",
            "Yeni": "Created",
            "Kargoluk": "PENDING_KARGO",
            "Sevkiyatlık": "PENDING_SEVKIYAT",
            "Toplanıyor": "Picking",
            "Kargoda": "Shipped",
            "Teslim Edilen": "Delivered",
            "İptal": "Cancelled"
        }
        
        self.sort_col = "termin_tarihi_ms" 
        self.sort_dir = "ASC" 
        self.tumunu_secildi_mi = False 
        
        self.son_cekilen_satirlar = [] 
        self.kolon_filtreleri = {}     
        self.islem_yapiyor = False 
        self.otopilot_mesaji = "" 
        
        self.db_kur()
        self.setup_ui()
        self.sag_tik_menusunu_kur() 
        
        if self.api_config.get("TY_ID"):
            self.tabloyu_doldur() 
            self.otomatik_yenileme_dongusu() 
        else:
            messagebox.showwarning("Uyarı", "coni_config.json bulunamadı! Önce ayarları kaydet.")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f)
            except: pass
        return {}

    def ayarlari_yukle(self):
        if os.path.exists(AYAR_DOSYASI):
            try:
                with open(AYAR_DOSYASI, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "TUM_URUNLER" not in data: data["TUM_URUNLER"] = SABIT_URUNLER.copy()
                    return data
            except: pass

        data = {
            "desi_bilgileri": VARSAYILAN_VERILER["desi_bilgileri"],
            "TUM_URUNLER": SABIT_URUNLER.copy(),
            "iller": {}
        }

        eski_gidilen_iller = []
        eski_yasakli_ilceler = []
        eski_yasakli_urunler = []

        if os.path.exists(ESKI_AYAR_DOSYASI):
            try:
                with open(ESKI_AYAR_DOSYASI, "r", encoding="utf-8") as f:
                    eski_data = json.load(f)
                    eski_gidilen_iller = eski_data.get("gidilen_iller", [])
                    eski_yasakli_ilceler = eski_data.get("yasakli_ilceler", [])
                    eski_yasakli_urunler = eski_data.get("yasakli_urunler", [])
            except: pass

        if not eski_gidilen_iller:
            eski_gidilen_iller = ["İSTANBUL", "KOCAELİ", "SAKARYA", "BURSA", "YALOVA", "TEKİRDAĞ", "EDİRNE", "KIRKLARELİ"]
            eski_yasakli_ilceler = ["İSTANBUL|ADALAR", "İSTANBUL|ŞİLE"] 

        for il_adi, ilceler in TURKIYE_HARITASI.items():
            il_aktif_mi = il_adi in eski_gidilen_iller
            
            ilce_dict = {}
            for ilce in ilceler:
                ilce_aktif_mi = f"{il_adi}|{ilce}" not in eski_yasakli_ilceler
                ilce_dict[ilce] = ilce_aktif_mi

            urun_dict = {}
            for urun in SABIT_URUNLER:
                urun_aktif_mi = True
                for y_urun_kurali in eski_yasakli_urunler:
                    if "|" in y_urun_kurali:
                        y_il, y_urun = y_urun_kurali.split("|", 1)
                        if y_il == il_adi and y_urun in urun:
                            urun_aktif_mi = False
                            break
                urun_dict[urun] = urun_aktif_mi

            data["iller"][il_adi] = {
                "il_aktif": il_aktif_mi,
                "ilceler": ilce_dict,
                "urunler": urun_dict
            }

        self.ayarlari_kaydet(data)
        return data

    def ayarlari_kaydet(self, ayarlar=None):
        if ayarlar is None: ayarlar = self.lojistik_ayarlar
        with open(AYAR_DOSYASI, "w", encoding="utf-8") as f: json.dump(ayarlar, f, ensure_ascii=False, indent=4)

    # ---> YENİ: KENDİ KENDİNİ TEMİZLEYEN OTOPİLOT DB MOTORU <---
    def db_kur(self):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS SiparislerV6 (
                paket_id TEXT PRIMARY KEY, siparis_no TEXT, siparis_tarihi_ms INTEGER, termin_tarihi_ms INTEGER,
                musteri_adi TEXT, teslimat_adresi TEXT, il TEXT, ilce TEXT, stok_kodu TEXT, adet INTEGER,
                telefon TEXT, durum TEXT, teslimat_tipi TEXT, teslimat_kodu TEXT, foto_yolu TEXT, teslim_eden TEXT, teslim_tarihi_ms INTEGER)''')
            
            # 1. ESKİDEN TESLİM EDİLENLERİN VE İPTALLERİN PIN KODUNU BOŞALT
            cursor.execute("UPDATE SiparislerV6 SET teslimat_kodu='' WHERE durum IN ('Delivered', 'Cancelled')")
            
            # 2. AYNI KODU ALMIŞ "AKTİF" SİPARİŞLERİN KODUNU SIFIRLA (Döngüde benzersiz olanını kendi atayacak)
            cursor.execute("""
                UPDATE SiparislerV6 SET teslimat_kodu='' 
                WHERE paket_id IN (
                    SELECT paket_id FROM SiparislerV6 
                    WHERE teslimat_kodu IN (
                        SELECT teslimat_kodu FROM SiparislerV6 
                        WHERE teslimat_kodu != '' 
                        GROUP BY teslimat_kodu HAVING COUNT(*) > 1
                    )
                )
            """)
            conn.commit()

    def normalize_tr(self, text):
        return normalize_tr(text) 

    def teslimat_tipi_belirle(self, il, ilce, urun_isimleri):
        il = self.normalize_tr(il)
        ilce = self.normalize_tr(ilce)
        
        iller_matrix = self.lojistik_ayarlar.get("iller", {})
        il_kurallari = iller_matrix.get(il)

        if not il_kurallari or not il_kurallari.get("il_aktif", False):
            return "📦 KARGO"

        if il_kurallari.get("ilceler", {}).get(ilce, True) == False:
            return "📦 KARGO"

        kargo_urun_sayisi = 0
        for urun in urun_isimleri:
            urun_ust = self.normalize_tr(urun)
            sade_ad = sade_urun_bul(urun_ust) 
            
            if il_kurallari.get("urunler", {}).get(sade_ad, True) == False:
                kargo_urun_sayisi += 1

        if len(urun_isimleri) > 0 and kargo_urun_sayisi == len(urun_isimleri): 
            return "📦 KARGO"
            
        return "🚚 SEVKİYAT"

    # ---> YENİ: MERKEZİ VE KUSURSUZ PIN ÜRETME MOTORU <---
    def pin_yonetimi(self, cursor, paket_id, durum_db, mevcut_pin):
        # Teslim ve iptallere PIN verilmez
        if durum_db in ["Delivered", "Cancelled"]:
            return "" 
        
        # Eğer zaten bir PIN'i varsa, başka aktif bir siparişle çakışmıyorsa koru
        if mevcut_pin and str(mevcut_pin).strip() != "":
            cursor.execute("SELECT 1 FROM SiparislerV6 WHERE teslimat_kodu=? AND paket_id!=? AND teslimat_kodu!=''", (mevcut_pin, paket_id))
            if not cursor.fetchone():
                return mevcut_pin 
        
        # Eğer PIN yoksa veya çakışıyorsa dünya üzerinde tek olan yeni PIN üret
        while True:
            aday_pin = str(random.randint(1000, 9999))
            cursor.execute("SELECT 1 FROM SiparislerV6 WHERE teslimat_kodu=? AND teslimat_kodu!=''", (aday_pin,))
            if not cursor.fetchone():
                return aday_pin

    def sistemi_sifirla_ve_esitle(self):
        cevap = messagebox.askyesno("Tam Sıfırlama Onayı", "Veritabanındaki full kayıtlar silinecek.\nTrendyol, HB ve N11'den son 10 AYIN BÜTÜN geçmiş siparişleri parça parça çekilecek.\n\nBu işlem 1-2 dakika sürebilir. Emin misiniz?")
        if not cevap: return
        
        self.btn_yenile.configure(state="disabled")
        self.btn_sifirla.configure(state="disabled")
        self.lbl_durum.configure(text="Hafıza temizleniyor...", text_color="orange")
        
        try:
            with sqlite3.connect(DB_FILE) as conn:
                conn.cursor().execute("DROP TABLE IF EXISTS SiparislerV6")
                conn.commit()
            self.db_kur() 
        except Exception as e:
            messagebox.showerror("Veritabanı Hatası", f"Dosya kilitli olabilir: {e}")
            self.btn_sifirla.configure(state="normal")
            return
            
        threading.Thread(target=self.api_istegi_yap, kwargs={"derin_tarama": True}, daemon=True).start()

    def otomatik_yenileme_dongusu(self):
        if not self.islem_yapiyor: self.siparisleri_cek_thread()
        self.after(120000, self.otomatik_yenileme_dongusu) 

    def matris_ekranini_ac(self):
        MatrisAyarPenceresi(self)

    def setup_ui(self):
        self.header_frame = ctk.CTkFrame(self, height=60, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(20, 5))
        ctk.CTkLabel(self.header_frame, text="🚚 İRSAN DİZAYN OTOPİLOT V25", font=("Roboto", 24, "bold"), text_color="#F27A1A").pack(side="left")
        
        self.btn_yenile = ctk.CTkButton(self.header_frame, text="🔄 YENİLE", command=self.siparisleri_cek_thread, fg_color="#2E8B57", hover_color="#1e5c3a", font=("Roboto", 13, "bold"), width=100)
        self.btn_yenile.pack(side="right", padx=5)

        self.btn_sifirla = ctk.CTkButton(self.header_frame, text="⚙️ HAFIZAYI SIFIRLA & EŞİTLE", command=self.sistemi_sifirla_ve_esitle, fg_color="#8B0000", hover_color="#600000", font=("Roboto", 13, "bold"))
        self.btn_sifirla.pack(side="right", padx=10)

        self.btn_matris = ctk.CTkButton(self.header_frame, text="⚙️ ROTA MATRİSİ", command=self.matris_ekranini_ac, fg_color="#F39C12", hover_color="#D68910", font=("Roboto", 13, "bold"))
        self.btn_matris.pack(side="right", padx=10)

        self.lbl_durum = ctk.CTkLabel(self.header_frame, text="Hazır.", text_color="gray", font=("Roboto", 13, "bold"))
        self.lbl_durum.pack(side="right", padx=15)
        
        ctk.CTkLabel(self, text="⚡ Otopilot Devrede. SADECE SEVKİYAT olan siparişler 16 saat kala otomatik kargolanır.", text_color="#00E5FF", font=("Roboto", 11, "italic")).pack(anchor="w", padx=25, pady=(0,5))

        self.toolbar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.toolbar_frame.pack(fill="x", padx=20, pady=5)
        
        self.secili_filtre = ctk.StringVar(value="Tümü")
        self.seg_btn = ctk.CTkSegmentedButton(self.toolbar_frame, values=list(self.durum_sozlugu.keys()), variable=self.secili_filtre, command=lambda v: self.ana_filtre_degisti(), font=("Roboto", 13, "bold"), selected_color="#F27A1A")
        self.seg_btn.pack(side="left")
        
        self.btn_tumunu_sec = ctk.CTkButton(self.toolbar_frame, text="☑ Tümünü Seç", command=self.tumunu_sec_toggle, fg_color="#4B0082", font=("Roboto", 13, "bold"))
        self.btn_tumunu_sec.pack(side="left", padx=(20, 0))
        
        self.btn_kargola = ctk.CTkButton(self.toolbar_frame, text="🚀 SEÇİLİLERİ KARGOLA", command=self.secilileri_kargola, fg_color="#B22222", font=("Roboto", 13, "bold"))
        self.btn_kargola.pack(side="left", padx=(10, 0))
        
        self.btn_excel_sms = ctk.CTkButton(self.toolbar_frame, text="📂 EXCEL YÜKLE (SMS GÖNDER)", command=self.excel_ile_sms_baslat, fg_color="#8E44AD", hover_color="#732D91", text_color="white", font=("Roboto", 13, "bold"))
        self.btn_excel_sms.pack(side="left", padx=(10, 0))
        
        self.btn_filtre_temizle = ctk.CTkButton(self.toolbar_frame, text="🧹 Filtreleri Sıfırla", command=self.kolon_filtrelerini_sifirla, width=120, fg_color="#d35400")
        self.btn_filtre_temizle.pack(side="right", padx=(10, 0))
        self.btn_ara = ctk.CTkButton(self.toolbar_frame, text="🔍 ARA", command=self.ana_filtre_degisti, width=80, fg_color="#1f538d")
        self.btn_ara.pack(side="right", padx=(10, 0))
        self.entry_arama = ctk.CTkEntry(self.toolbar_frame, placeholder_text="İsim, İlçe, İl, Stok No...", width=180)
        self.entry_arama.pack(side="right")
        self.entry_arama.bind("<Return>", lambda e: self.ana_filtre_degisti())

        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=15)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=35, fieldbackground="#2b2b2b", borderwidth=0)
        style.map("Treeview", background=[("selected", "#19517B")], foreground=[("selected", "white")]) 
        style.configure("Treeview.Heading", background="#1f538d", foreground="white", font=("Roboto", 11, "bold"))

        columns = ("Secim", "TeslimatTipi", "SiparisTarihi", "TerminTarihi", "KalanSure", "PaketID", "SiparisNo", "TeslimatKodu", "Musteri", "Adres", "Il", "Ilce", "StokKodu", "Adet", "Durum")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="none") 
        self.tree.tag_configure('tek_satir', background='#242424') 
        self.tree.tag_configure('cift_satir', background='#2f2f2f') 
        self.tree.tag_configure('acil', foreground='#FF4444', font=("Roboto", 10, "bold")) 
        self.tree.tag_configure('teslim_edildi', foreground='#2ECC71', font=("Roboto", 11, "bold"))
        
        self.orijinal_basliklar = {"Secim": "✔", "TeslimatTipi": "Lojistik Tipi", "SiparisTarihi": "Sipariş Tarihi", "TerminTarihi": "Son Kargolama", "KalanSure": "Kalan Süre", "PaketID": "Paket ID", "SiparisNo": "Sipariş No", "TeslimatKodu": "Teslim Pini", "Musteri": "İsim Soyisim", "Adres": "Teslimat Adresi", "Il": "İl", "Ilce": "İlçe", "StokKodu": "Stok Kodu", "Adet": "Adet", "Durum": "Durum"}
        for col in columns:
            if col not in ["PaketID", "Secim"]: self.tree.heading(col, text=self.orijinal_basliklar[col], command=lambda c=col: self.sutun_sirala(c))
            else: self.tree.heading(col, text=self.orijinal_basliklar[col])

        self.tree.column("Secim", width=40, anchor="center")
        self.tree.column("TeslimatTipi", width=150, anchor="center")
        self.tree.column("SiparisTarihi", width=120, anchor="center")
        self.tree.column("TerminTarihi", width=120, anchor="center")
        self.tree.column("KalanSure", width=110, anchor="center")
        self.tree.column("PaketID", width=0, stretch=False) 
        self.tree.column("SiparisNo", width=110, anchor="center")
        self.tree.column("TeslimatKodu", width=90, anchor="center")
        self.tree.column("Musteri", width=150, anchor="w")
        self.tree.column("Adres", width=230, anchor="w")
        self.tree.column("Il", width=100, anchor="center")
        self.tree.column("Ilce", width=120, anchor="center")
        self.tree.column("StokKodu", width=120, anchor="center")
        self.tree.column("Adet", width=50, anchor="center")
        self.tree.column("Durum", width=100, anchor="center")

        self.tree.bind('<ButtonRelease-1>', self.kutucuk_tiklandi) 
        self.tree.bind("<Button-3>", self.sag_tik_yoneticisi) 
        self.tree.bind("<Double-1>", self.cift_tikla_tarayici) 

        scroll_y = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=scroll_y.set, xscroll=scroll_x.set)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

    def excel_ile_sms_baslat(self):
        dosya_yolu = filedialog.askopenfilename(filetypes=[("Excel Dosyası", "*.xlsx;*.xls")])
        if not dosya_yolu: return

        try:
            df = pd.read_excel(dosya_yolu, dtype=str)
            col_siparis, col_telefon, col_isim = None, None, None

            for col in df.columns:
                c_str = str(col).upper()
                if "SİPARİŞ NUMA" in c_str or "SIPARIS NO" in c_str or "SİPARİŞ" in c_str or "PAKET" in c_str:
                    col_siparis = col
                if "TELEFON" in c_str or "TEL" in c_str:
                    col_telefon = col
                if "İSİM" in c_str or "ISIM" in c_str or "ALICI" in c_str or "MÜŞTERİ" in c_str:
                    col_isim = col
            
            if not col_siparis:
                messagebox.showerror("Hata", "Excel dosyasında 'Sipariş No' başlıklı bir sütun bulunamadı!")
                return
                
            if not col_telefon and len(df.columns) >= 16:
                col_telefon = df.columns[15] 

            if not col_telefon:
                messagebox.showerror("Hata", "Excel'de 'TELEFON' veya P sütunu bulunamadı!")
                return

            siparis_verileri = []
            for idx, row in df.iterrows():
                sip_raw = str(row[col_siparis]).replace(".0", "").replace("nan", "").strip()
                sip = sip_raw.replace("-", " ").split()[0].strip() if sip_raw else ""
                
                if len(sip) > 5:
                    tel_raw = str(row[col_telefon]).replace(".0", "").replace("nan", "").strip() if pd.notna(row[col_telefon]) else ""
                    tel = ''.join(filter(str.isdigit, tel_raw))
                    isim = str(row[col_isim]).strip() if col_isim and pd.notna(row[col_isim]) else "Müşterimiz"
                    if isim.lower() == "nan": isim = "Müşterimiz"
                    
                    siparis_verileri.append({"sip_no": sip, "telefon": tel, "musteri": isim})

            if not siparis_verileri:
                messagebox.showwarning("Uyarı", "Excel'de geçerli sipariş numarası bulunamadı.")
                return

            if not messagebox.askyesno("SMS Gönderim Onayı", f"Excel'den {len(siparis_verileri)} adet sipariş okundu.\n\nNetGSM üzerinden SMS'ler gönderilsin mi?"): return
            threading.Thread(target=self.excel_sms_thread, args=(siparis_verileri,), daemon=True).start()

        except Exception as e: messagebox.showerror("Hata", f"Excel okuma hatası:\n{e}")

    def excel_sms_thread(self, siparis_verileri):
        self.btn_excel_sms.configure(state="disabled", text="SMS GÖNDERİLİYOR...")
        basarili_sms, hatali_sms, bulunamayan = 0, 0, 0

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            for veri in siparis_verileri:
                sip_no, excel_tel, excel_isim = veri["sip_no"], veri["telefon"], veri["musteri"]
                cursor.execute("SELECT musteri_adi, teslimat_kodu, telefon FROM SiparislerV6 WHERE siparis_no=? OR paket_id=?", (sip_no, sip_no))
                sonuc = cursor.fetchone()

                if sonuc:
                    db_musteri, teslimat_kodu, db_tel = sonuc
                    db_tel_temiz = ''.join(filter(str.isdigit, str(db_tel)))
                    nihai_telefon = excel_tel if excel_tel and len(str(excel_tel)) >= 10 else db_tel_temiz
                    
                    nihai_musteri = excel_isim if excel_isim and excel_isim != "Müşterimiz" else db_musteri
                    if "n11 müşteri" in str(nihai_musteri).lower(): nihai_musteri = "Değerli Müşterimiz"

                    if nihai_telefon and len(str(nihai_telefon)) >= 10:
                        ayrik_kod = " ".join(str(teslimat_kodu)) if teslimat_kodu else "KOD YOK"
                        mesaj = f"Sayin {nihai_musteri},\n{sip_no} numarali Irsan Dizayn siparisiniz kendi araclarimizla sevkiyata cikmistir.\n\nTeslimat PIN Kodunuz:\n[ {ayrik_kod} ]\n\nBizi tercih ettiginiz icin tesekkur ederiz."
                        
                        if self.netgsm_sms_gonder(nihai_telefon, mesaj): basarili_sms += 1
                        else: hatali_sms += 1
                        time.sleep(0.5) 
                    else: bulunamayan += 1
                else: bulunamayan += 1 

        self.after(0, lambda: messagebox.showinfo("Sevkiyat SMS Bitti", f"İşlem Tamamlandı!\n\n✅ Başarılı: {basarili_sms}\n❌ Hatalı: {hatali_sms}\n⚠️ Tel Eksik/Bulunamayan: {bulunamayan}"))
        self.after(0, lambda: self.btn_excel_sms.configure(state="normal", text="📂 EXCEL YÜKLE (SMS GÖNDER)"))

    def netgsm_sms_gonder(self, telefon, mesaj):
        NETGSM_USERCODE = "8503056628"   
        NETGSM_PASSWORD = "T6-7376K" 
        NETGSM_BASLIK = "ERSANDIZAYN"   

        temiz_tel = ''.join(filter(str.isdigit, str(telefon)))
        if temiz_tel.startswith("90") and len(temiz_tel) == 12: temiz_tel = temiz_tel[2:]
        elif temiz_tel.startswith("0") and len(temiz_tel) == 11: temiz_tel = temiz_tel[1:]

        if len(temiz_tel) != 10: return False

        url = "https://api.netgsm.com.tr/sms/send/get"
        params = {"usercode": NETGSM_USERCODE, "password": NETGSM_PASSWORD, "gsmno": temiz_tel, "message": mesaj, "msgheader": NETGSM_BASLIK, "filter": "0"}
        
        try:
            r = crequests.get(url, params=params, timeout=10)
            if r.status_code == 200 and r.text.startswith("00"): return True
            else:
                print(f"NetGSM Hata Döndü: {r.text} - Numara: {temiz_tel}")
                return False
        except Exception as e:
            print(f"NetGSM Bağlantı Hatası: {e}")
            return False

    def sag_tik_yoneticisi(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "heading": self.baslik_filtre_menu(self.tree.column(self.tree.identify_column(event.x), "id"))
        elif region == "cell":
            item = self.tree.identify_row(event.y)
            if item:
                self.secili_sag_tik_satiri = item
                self.sag_tik_menu.post(event.x_root, event.y_root)

    def baslik_filtre_menu(self, col_name):
        if col_name in ["Secim", "PaketID"]: return 
        col_idx = self.tree["columns"].index(col_name)
        gecerli_satirlar = []
        for satir in self.son_cekilen_satirlar:
            satir_uygun = True
            for f_col, f_izinler in self.kolon_filtreleri.items():
                if f_col == col_name: continue 
                if satir[self.tree["columns"].index(f_col)] not in f_izinler: satir_uygun = False; break
            if satir_uygun: gecerli_satirlar.append(satir)

        tum_degerler = sorted(list(set([satir[col_idx] for satir in gecerli_satirlar])))
        if not tum_degerler: return messagebox.showinfo("Bilgi", "Filtrelenecek veri kalmadı.")

        top = ctk.CTkToplevel(self)
        top.title(f"Filtre: {self.orijinal_basliklar[col_name]}")
        top.geometry("300x400")
        top.transient(self); top.grab_set()
        aktif_secimler = self.kolon_filtreleri.get(col_name, tum_degerler)

        btn_frame = ctk.CTkFrame(top, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)
        cb_listesi = []
        ctk.CTkButton(btn_frame, text="Tümünü Seç", width=130, command=lambda: [cb.select() for cb in cb_listesi]).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Temizle", width=130, command=lambda: [cb.deselect() for cb in cb_listesi]).pack(side="right", padx=5)

        scroll_frame = ctk.CTkScrollableFrame(top)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
        for deger in tum_degerler:
            var = tk.BooleanVar(value=(deger in aktif_secimler))
            cb = ctk.CTkCheckBox(scroll_frame, text=str(deger), variable=var)
            cb.pack(anchor="w", pady=5, padx=5)
            cb._filtre_degeri = deger; cb_listesi.append(cb)

        def uygula():
            secilenler = [cb._filtre_degeri for cb in cb_listesi if cb.get()]
            if len(secilenler) == len(tum_degerler):
                if col_name in self.kolon_filtreleri: del self.kolon_filtreleri[col_name]
            else: self.kolon_filtreleri[col_name] = secilenler
            self.agaci_guncelle(); top.destroy()
        ctk.CTkButton(top, text="Uygula", command=uygula, fg_color="green").pack(pady=10, padx=10, fill="x")

    def kolon_filtrelerini_sifirla(self): self.kolon_filtreleri = {}; self.agaci_guncelle()
    
    # Filtreleri (Yeni, Kargoda, Tümü) değiştirdiğimizde sütun filtrelerini de sıfırlıyoruz ki Tümü'nde siparişler saklanmasın!
    def ana_filtre_degisti(self): self.kolon_filtreleri = {}; self.tabloyu_doldur()

    def cift_tikla_tarayici(self, event):
        if self.tree.identify_column(event.x) == '#1': return 
        item = self.tree.identify_row(event.y)
        if item:
            try: webbrowser.open(f"https://partner.trendyol.com/orders/shipment-packages?orderNumber={self.tree.item(item, 'values')[6]}")
            except: pass

    def sag_tik_menusunu_kur(self):
        self.sag_tik_menu = tk.Menu(self, tearoff=0, font=("Roboto", 11), bg="#2b2b2b", fg="white")
        self.sag_tik_menu.add_command(label="📋 Sipariş Numarasını Kopyala", command=self.kopyala_siparis_no)
        self.sag_tik_menu.add_command(label="👤 İsim Soyismi Kopyala", command=self.kopyala_isim)
        self.secili_sag_tik_satiri = None

    def kopyala_siparis_no(self):
        if self.secili_sag_tik_satiri: self.clipboard_clear(); self.clipboard_append(self.tree.item(self.secili_sag_tik_satiri, "values")[6])
    def kopyala_isim(self):
        if self.secili_sag_tik_satiri: self.clipboard_clear(); self.clipboard_append(self.tree.item(self.secili_sag_tik_satiri, "values")[8])

    def tumunu_sec_toggle(self):
        self.tumunu_secildi_mi = not self.tumunu_secildi_mi
        yeni_simge = "☑" if self.tumunu_secildi_mi else "☐"
        for item in self.tree.get_children():
            veri = list(self.tree.item(item, "values"))
            veri[0] = yeni_simge 
            self.tree.item(item, values=veri)
            if self.tumunu_secildi_mi: self.tree.selection_add(item)
            else: self.tree.selection_remove(item)
        self.btn_tumunu_sec.configure(text="☐ Seçimi Temizle" if self.tumunu_secildi_mi else "☑ Tümünü Seç")

    def kutucuk_tiklandi(self, event):
        if self.tree.identify("region", event.x, event.y) == "cell" and self.tree.identify_column(event.x) == '#1': 
            item = self.tree.identify_row(event.y)
            if item:
                veri = list(self.tree.item(item, "values"))
                if veri[0] == "☐": veri[0] = "☑"; self.tree.selection_add(item)
                else: veri[0] = "☐"; self.tree.selection_remove(item)
                self.tree.item(item, values=veri)

    def secilileri_kargola(self):
        paket_id_listesi = []
        isaretli_sayisi = 0
        for item in self.tree.get_children():
            veri = self.tree.item(item, "values")
            if veri[0] == "☑":
                isaretli_sayisi += 1
                if "Kargoda" in veri[14] or "Teslim" in veri[14] or "İptal" in veri[14]: continue
                paket_id_listesi.append(veri[5])
        if isaretli_sayisi == 0: return messagebox.showwarning("Uyarı", "Kutucukları işaretleyin (☑).")
        if not messagebox.askyesno("Onay", f"{isaretli_sayisi} adet sipariş Kargolanacak.\nEmin misiniz?"): return
        if not paket_id_listesi: return messagebox.showinfo("Bilgi", "Seçilenler zaten kargolanmış veya iptal.")

        self.btn_kargola.configure(state="disabled", text="KARGOLANIYOR...")
        threading.Thread(target=self.kargolama_thread, args=(paket_id_listesi, False), daemon=True).start()

    def kargolama_thread(self, paket_id_listesi, sessiz_mod=False):
        sid, key, secret = self.api_config.get("TY_ID"), self.api_config.get("TY_KEY"), self.api_config.get("TY_SECRET")
        basarili, hatali = 0, 0
        for pid in paket_id_listesi:
            if str(pid).startswith("N11_") or str(pid).startswith("HB_"): 
                hatali += 1
                continue
                
            url = f"https://apigw.trendyol.com/integration/order/sellers/{sid}/shipment-packages/{pid}/alternative-delivery"
            payload = {"isPhoneNumber": True, "trackingInfo": "02162060272"}
            headers = {"Content-Type": "application/json"}
            istek_basarili = False
            for _ in range(3):
                try:
                    r = crequests.put(url, auth=(key, secret), headers=headers, json=payload, impersonate="chrome110", timeout=15)
                    if r.status_code in [200, 201]:
                        istek_basarili = True
                        basarili += 1
                        with sqlite3.connect(DB_FILE) as conn:
                            conn.cursor().execute("UPDATE SiparislerV6 SET durum='Shipped', teslimat_tipi='✅ Oto-Kurtarma' WHERE paket_id=?", (pid,))
                            conn.commit()
                        break
                    time.sleep(1)
                except: time.sleep(1)
            if not istek_basarili: hatali += 1
                
        if not sessiz_mod: 
            self.after(0, self.kargolama_bitti, basarili, hatali)
        else:
            if basarili > 0:
                self.otopilot_mesaji = f"⚡ OTOPİLOT {basarili} SİPARİŞİ KURTARDI!"
            self.after(0, self.tabloyu_doldur)

    def kargolama_bitti(self, basarili, hatali):
        self.btn_kargola.configure(state="normal", text="🚀 SEÇİLİLERİ KARGOLA")
        messagebox.showinfo("Bitti", f"✅ Başarılı: {basarili}\n❌ Hatalı/Kargoda: {hatali}")
        self.tabloyu_doldur()

    def sutun_sirala(self, col_id):
        sql_map = {"TeslimatTipi": "teslimat_tipi", "SiparisTarihi": "siparis_tarihi_ms", "TerminTarihi": "termin_tarihi_ms", "KalanSure": "termin_tarihi_ms", "SiparisNo": "siparis_no", "TeslimatKodu": "teslimat_kodu", "Musteri": "musteri_adi", "Adres": "teslimat_adresi", "Il": "il", "Ilce": "ilce", "StokKodu": "stok_kodu", "Adet": "adet", "Durum": "durum"}
        db_col = sql_map.get(col_id, "termin_tarihi_ms")
        if self.sort_col == db_col: self.sort_dir = "ASC" if self.sort_dir == "DESC" else "DESC"
        else: self.sort_col, self.sort_dir = db_col, "DESC" if db_col == "siparis_tarihi_ms" else "ASC"
        self.tabloyu_doldur()

    def siparisleri_cek_thread(self):
        if self.islem_yapiyor: return 
        self.islem_yapiyor = True
        self.btn_yenile.configure(state="disabled")
        self.btn_sifirla.configure(state="disabled")
        self.lbl_durum.configure(text="Trendyol'dan veriler çekiliyor...", text_color="#00E5FF")
        threading.Thread(target=self.api_istegi_yap, kwargs={"derin_tarama": False}, daemon=True).start()

    def api_istegi_yap(self, derin_tarama=False):
        sid, key, secret = self.api_config.get("TY_ID"), self.api_config.get("TY_KEY"), self.api_config.get("TY_SECRET")
        if not sid or not key or not secret:
            self.after(0, lambda: self.lbl_durum.configure(text="API Bilgileri Eksik!", text_color="red"))
            self.after(0, lambda: self.btn_yenile.configure(state="normal"))
            self.islem_yapiyor = False
            return

        url = f"https://api.trendyol.com/sapigw/suppliers/{sid}/orders"
        zaman_dilimleri = []
        suan_ms = int(time.time() * 1000)
        on_uc_gun_ms = 13 * 24 * 60 * 60 * 1000
        dongu_sayisi = 23 if derin_tarama else 3 

        for i in range(dongu_sayisi):
            bitis = suan_ms - (i * on_uc_gun_ms)
            baslangic = bitis - on_uc_gun_ms
            zaman_dilimleri.append((baslangic, bitis))

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            
            # --- TRENDYOL SİPARİŞLERİNİ ÇEKME ---
            for baslangic, bitis in zaman_dilimleri:
                sayfa = 0
                while True:
                    if derin_tarama:
                        tarih_str = datetime.fromtimestamp(baslangic/1000).strftime('%d.%m.%y')
                        self.after(0, lambda s=sayfa, t=tarih_str: self.lbl_durum.configure(text=f"Tarama: {t} | Sayfa {s+1} çekiliyor...", text_color="orange"))
                    else:
                        self.after(0, lambda s=sayfa: self.lbl_durum.configure(text=f"Otopilot güncelliyor... (Sayfa {s+1})", text_color="#00E5FF"))

                    params = {"page": sayfa, "size": 100, "startDate": baslangic, "endDate": bitis, "orderByField": "PackageLastModifiedDate", "orderByDirection": "DESC"}
                    try:
                        r = crequests.get(url, auth=(key, secret), params=params, impersonate="chrome110", timeout=20)
                        if r.status_code == 200:
                            veri = r.json()
                            siparisler = veri.get("content", [])
                            total_pages = veri.get("totalPages", 0)
                            
                            if not siparisler: break 
                                
                            for s in siparisler:
                                paket_id, sip_no, durum = str(s.get("id")), s.get("orderNumber"), s.get("status")
                                sip_tarih_ms, termin_tarihi_ms = s.get("orderDate", 0), s.get("agreedDeliveryDate", 0)
                                musteri = f"{s.get('customerFirstName', '')} {s.get('customerLastName', '')}"
                                adres_obj = s.get("shipmentAddress", {})
                                adres = adres_obj.get("fullAddress", f"{adres_obj.get('address1','')} {adres_obj.get('address2','')}").replace("\n", " ")
                                il, ilce, telefon = adres_obj.get("city", ""), adres_obj.get("district", ""), adres_obj.get("phone", "")
                                lines = s.get("lines", [])
                                stok_kodu, toplam_adet = " + ".join([l.get("merchantSku", "") for l in lines]), sum([l.get("quantity", 0) for l in lines])
                                urun_isimleri = [l.get("productName", "") for l in lines]
                                
                                if durum in ["Shipped", "Delivered"]: teslimat_tipi = f"🚚 {s.get('cargoProviderName', 'Kargo')}"
                                elif durum == "Cancelled": teslimat_tipi = "❌ İptal Edildi"
                                else: teslimat_tipi = self.teslimat_tipi_belirle(il, ilce, urun_isimleri)

                                cursor.execute("SELECT teslimat_kodu, durum, teslimat_tipi FROM SiparislerV6 WHERE paket_id=?", (paket_id,))
                                mevcut_kayit = cursor.fetchone()
                                db_eski_pin = mevcut_kayit[0] if mevcut_kayit else ""
                                
                                if mevcut_kayit:
                                    db_durum, db_tip = mevcut_kayit[1], mevcut_kayit[2]
                                    if db_durum == "Delivered" and db_tip and ("Şoför" in db_tip or "Instagram" in db_tip):
                                        durum = "Delivered"
                                        teslimat_tipi = db_tip
                                
                                # Kusursuz PIN Ataması
                                teslimat_kodu = self.pin_yonetimi(cursor, paket_id, durum, db_eski_pin)

                                if mevcut_kayit:
                                    cursor.execute('''UPDATE SiparislerV6 SET 
                                        siparis_no=?, siparis_tarihi_ms=?, termin_tarihi_ms=?, musteri_adi=?, teslimat_adresi=?, il=?, ilce=?, stok_kodu=?, adet=?, telefon=?, durum=?, teslimat_tipi=?, teslimat_kodu=? 
                                        WHERE paket_id=?''', 
                                        (sip_no, sip_tarih_ms, termin_tarihi_ms, musteri, adres, il, ilce, stok_kodu, toplam_adet, telefon, durum, teslimat_tipi, teslimat_kodu, paket_id))
                                else:
                                    cursor.execute('''INSERT INTO SiparislerV6 
                                        (paket_id, siparis_no, siparis_tarihi_ms, termin_tarihi_ms, musteri_adi, teslimat_adresi, il, ilce, stok_kodu, adet, telefon, durum, teslimat_tipi, teslimat_kodu) 
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                                        (paket_id, sip_no, sip_tarih_ms, termin_tarihi_ms, musteri, adres, il, ilce, stok_kodu, toplam_adet, telefon, durum, teslimat_tipi, teslimat_kodu))
                            conn.commit()
                            
                            sayfa += 1
                            if sayfa >= total_pages: break 
                        else: break 
                    except Exception as e: break
            
           # --- N11 SİPARİŞLERİNİ ÇEKME ---
            n11_key, n11_sec = self.api_config.get("N11_KEY", ""), self.api_config.get("N11_SECRET", "")
            if n11_key and n11_sec:
                self.after(0, lambda: self.lbl_durum.configure(text="N11 Arşivi Süpürülüyor (Son 6 Ay)...", text_color="#F39C12"))
                url_n11 = "https://api.n11.com/rest/delivery/v1/shipmentPackages"
                headers_n11 = {"appkey": n11_key, "appsecret": n11_sec, "Accept": "application/json"}
                
                n11_zaman_dilimleri = []
                suan_ms = int(time.time() * 1000)
                on_bes_gun_ms = 15 * 24 * 60 * 60 * 1000
                for i in range(12): 
                    bitis = suan_ms - (i * on_bes_gun_ms)
                    baslangic = bitis - on_bes_gun_ms
                    n11_zaman_dilimleri.append((baslangic, bitis))
                
                n11_statuler = ["Created", "Picking", "Unpacked", "Shipped", "Delivered", "Cancelled", "Invoiced", "UnSupplied"]
                
                for n11_st in n11_statuler:
                    for baslangic, bitis in n11_zaman_dilimleri:
                        sayfa_n11 = 0
                        while True:
                            try:
                                n11_params = {"page": sayfa_n11, "size": 100, "status": n11_st, "startDate": baslangic, "endDate": bitis, "orderByField": "false"}
                                r_n11 = crequests.get(url_n11, headers=headers_n11, params=n11_params, timeout=20)
                                if r_n11.status_code == 200:
                                    veri_n11 = r_n11.json()
                                    n11_siparisler = veri_n11.get("content", veri_n11.get("shipmentPackageList", []))
                                    if not n11_siparisler: break 
                                        
                                    for s in n11_siparisler:
                                        sip_no = str(s.get("orderNumber"))
                                        n11_id = s.get("id")
                                        paket_id = f"N11_{n11_id if n11_id else sip_no}" 
                                        durum_n11 = s.get("shipmentPackageStatus", n11_st)
                                        termin_tarihi_ms = s.get("agreedDeliveryDate") or (suan_ms + (3 * 24 * 60 * 60 * 1000))
                                        sip_tarih_ms = s.get("orderDate") or suan_ms
                                        
                                        addr = s.get("shippingAddress", {})
                                        musteri = s.get("customerfullName") or addr.get("fullName") or "N11 Müşterisi"
                                        adres_tam = f"{addr.get('address','')} {addr.get('district','')} {addr.get('city','')}".replace("\n", " ")
                                        il, ilce, telefon = addr.get("city", ""), addr.get("district", ""), addr.get("gsm", addr.get("phone", ""))
                                        
                                        lines = s.get("lines", [])
                                        stok_kodu = " + ".join([str(l.get("sellerCode", "")) for l in lines])
                                        toplam_adet = sum([int(l.get("quantity", 0)) for l in lines])
                                        urun_isimleri = [l.get("productName", "") for l in lines]
                                        kargo_adi = s.get('shipmentCompanyName') or s.get('cargoProviderName') or 'Kargo'
                                        
                                        if durum_n11 in ["Shipped", "Delivered", "Invoiced", "Unpacked"]: teslimat_tipi = f"🚚 N11-{kargo_adi}"
                                        elif durum_n11 == "Cancelled": teslimat_tipi = "❌ İptal Edildi"
                                        else: teslimat_tipi = self.teslimat_tipi_belirle(il, ilce, urun_isimleri)

                                        cursor.execute("SELECT teslimat_kodu, durum, teslimat_tipi FROM SiparislerV6 WHERE paket_id=?", (paket_id,))
                                        mevcut_kayit = cursor.fetchone()
                                        db_eski_pin = mevcut_kayit[0] if mevcut_kayit else ""
                                        
                                        if mevcut_kayit:
                                            db_durum, db_tip = mevcut_kayit[1], mevcut_kayit[2]
                                            if db_durum == "Delivered" and db_tip and ("Şoför" in db_tip or "Instagram" in db_tip):
                                                durum_n11 = "Delivered"
                                                teslimat_tipi = db_tip
                                                
                                        # Kusursuz PIN Ataması
                                        teslimat_kodu = self.pin_yonetimi(cursor, paket_id, durum_n11, db_eski_pin)

                                        if mevcut_kayit:
                                            cursor.execute('''UPDATE SiparislerV6 SET 
                                                siparis_no=?, siparis_tarihi_ms=?, termin_tarihi_ms=?, musteri_adi=?, teslimat_adresi=?, il=?, ilce=?, stok_kodu=?, adet=?, telefon=?, durum=?, teslimat_tipi=?, teslimat_kodu=? 
                                                WHERE paket_id=?''', 
                                                (sip_no, sip_tarih_ms, termin_tarihi_ms, musteri, adres_tam, il, ilce, stok_kodu, toplam_adet, telefon, durum_n11, teslimat_tipi, teslimat_kodu, paket_id))
                                        else:
                                            cursor.execute('''INSERT INTO SiparislerV6 
                                                (paket_id, siparis_no, siparis_tarihi_ms, termin_tarihi_ms, musteri_adi, teslimat_adresi, il, ilce, stok_kodu, adet, telefon, durum, teslimat_tipi, teslimat_kodu) 
                                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                                                (paket_id, sip_no, sip_tarih_ms, termin_tarihi_ms, musteri, adres_tam, il, ilce, stok_kodu, toplam_adet, telefon, durum_n11, teslimat_tipi, teslimat_kodu))
                                    conn.commit()
                                    if len(n11_siparisler) < 100: break
                                    sayfa_n11 += 1
                                else: break
                            except Exception as e: break
                            
               # --- HEPSİBURADA SİPARİŞLERİNİ ÇEKME ---
                hb_merchant_id = "825de3f9-24ba-4680-ad4b-bebd55241016"
                hb_password = "qWvMVSnZRYew" 

                if hb_merchant_id and hb_password:
                    self.after(0, lambda: self.lbl_durum.configure(text="HB Orders & Packages Çekiliyor...", text_color="#3498db"))
                    
                    url_hb_orders = f"https://oms-external.hepsiburada.com/orders/merchantid/{hb_merchant_id}"
                    url_hb_packages = f"https://oms-external.hepsiburada.com/packages/merchantid/{hb_merchant_id}"
                    
                    b64_auth = base64.b64encode(f"{hb_merchant_id}:{hb_password}".encode("utf-8")).decode("utf-8")
                    headers_hb = {"Accept": "application/json", "Authorization": f"Basic {b64_auth}", "User-Agent": "ersandizayn_dev"}
                    suan_ms = int(time.time() * 1000)
                    
                    with sqlite3.connect(DB_FILE) as conn:
                        cursor = conn.cursor()
                        offset, limit = 0, 50
                        
                        while True:
                            try:
                                r_hb = crequests.get(url_hb_orders, headers=headers_hb, params={"offset": str(offset), "limit": str(limit)}, impersonate="chrome110", timeout=20)
                                
                                if r_hb.status_code == 200:
                                    veri_hb = r_hb.json()
                                    hb_siparisler = veri_hb if isinstance(veri_hb, list) else veri_hb.get("items", veri_hb.get("data", []))
                                    if not hb_siparisler: break
                                        
                                    for s in hb_siparisler:
                                        sip_no = str(s.get("orderNumber", s.get("packageNumber", "Bilinmiyor")))
                                        hb_id = s.get("id", "")
                                        paket_id = f"HB_{hb_id if hb_id else sip_no}"
                                        
                                        raw_st = str(s.get("status", "open")).lower()
                                        durum_db = {"unpacked": "Created", "open": "Created", "created": "Created", "packed": "Picking", "readytoship": "Picking", "approved": "Created", "shipped": "Shipped", "delivered": "Delivered", "cancelled": "Cancelled"}.get(raw_st, "Created")
                                        
                                        ot = str(s.get("orderDate") or "")
                                        sip_tarih_ms = int(datetime.strptime(ot[:19], "%Y-%m-%dT%H:%M:%S").timestamp() * 1000) if len(ot) >= 19 else suan_ms
                                        
                                        dt = str(s.get("dueDate") or s.get("estimatedArrivalDate") or "")
                                        termin_tarih_ms = int(datetime.strptime(dt[:19], "%Y-%m-%dT%H:%M:%S").timestamp() * 1000) if len(dt) >= 19 else (suan_ms + 259200000)
                                        
                                        musteri = s.get("recipientName") or s.get("customerName") or "HB Müşterisi"
                                        adres_tam = str(s.get("shippingAddressDetail", s.get("shippingAddress", ""))).replace("\n", " ").strip()
                                        il = s.get("shippingCity", "")
                                        ilce = s.get("shippingTown") or s.get("shippingDistrict", "")
                                        tel = s.get("phoneNumber", "")
                                        
                                        items = s.get("items", s.get("lines", s.get("products", [])))
                                        stok = " + ".join([str(l.get("merchantSku", "")) for l in items])
                                        adet = sum([int(l.get("quantity", 1)) for l in items])
                                        urun_adlari = [l.get("productName", "") for l in items]
                                        teslimat_tipi = self.teslimat_tipi_belirle(il, ilce, urun_adlari)

                                        cursor.execute("SELECT teslimat_kodu, durum, teslimat_tipi FROM SiparislerV6 WHERE paket_id=?", (paket_id,))
                                        mevcut_kayit = cursor.fetchone()
                                        db_eski_pin = mevcut_kayit[0] if mevcut_kayit else ""
                                        
                                        if mevcut_kayit:
                                            _, e_durum, e_tip = mevcut_kayit
                                            if e_durum == "Delivered" and e_tip and ("Şoför" in e_tip or "Instagram" in e_tip):
                                                durum_db = "Delivered"
                                                teslimat_tipi = e_tip
                                        
                                        teslimat_kodu = self.pin_yonetimi(cursor, paket_id, durum_db, db_eski_pin)
                                        
                                        if mevcut_kayit:
                                            cursor.execute('''UPDATE SiparislerV6 SET 
                                                siparis_no=?, siparis_tarihi_ms=?, termin_tarihi_ms=?, musteri_adi=?, teslimat_adresi=?, il=?, ilce=?, stok_kodu=?, adet=?, telefon=?, durum=?, teslimat_tipi=?, teslimat_kodu=? 
                                                WHERE paket_id=?''', 
                                                (sip_no, sip_tarih_ms, termin_tarih_ms, musteri, adres_tam, il, ilce, stok, adet, tel, durum_db, teslimat_tipi, teslimat_kodu, paket_id))
                                        else:
                                            cursor.execute('''INSERT INTO SiparislerV6 
                                                (paket_id, siparis_no, siparis_tarihi_ms, termin_tarihi_ms, musteri_adi, teslimat_adresi, il, ilce, stok_kodu, adet, telefon, durum, teslimat_tipi, teslimat_kodu) 
                                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                                                (paket_id, sip_no, sip_tarih_ms, termin_tarih_ms, musteri, adres_tam, il, ilce, stok, adet, tel, durum_db, teslimat_tipi, teslimat_kodu))
                                    conn.commit()
                                    if len(hb_siparisler) < limit: break
                                    offset += limit
                                else: break
                            except Exception as e: break

                        # HB Sevk Edilmiş/Teslim Edilmiş Paketlerin Durum Güncellemesi
                        hb_ozel_servisler = {"/shipped": "Shipped", "/delivered": "Delivered"}
                        for uzanti, db_durum in hb_ozel_servisler.items():
                            offset, limit = 0, 50
                            while True:
                                try:
                                    r_hb = crequests.get(f"{url_hb_packages}{uzanti}", headers=headers_hb, params={"offset": str(offset), "limit": str(limit)}, impersonate="chrome110", timeout=20)
                                    if r_hb.status_code == 200:
                                        veri_hb = r_hb.json()
                                        hb_siparisler = veri_hb if isinstance(veri_hb, list) else veri_hb.get("items", veri_hb.get("data", []))
                                        if not hb_siparisler: break
                                            
                                        for s in hb_siparisler:
                                            sip_no = str(s.get("OrderNumber", s.get("orderNumber", s.get("packageNumber", ""))))
                                            hb_id = str(s.get("Id", s.get("id", "")))
                                            paket_id = f"HB_{hb_id if hb_id else sip_no}"
                                            
                                            cursor.execute("SELECT teslimat_kodu, durum, teslimat_tipi FROM SiparislerV6 WHERE paket_id=?", (paket_id,))
                                            mevcut = cursor.fetchone()
                                            db_eski_pin = mevcut[0] if mevcut else ""
                                            
                                            teslimat_kodu = self.pin_yonetimi(cursor, paket_id, db_durum, db_eski_pin)
                                            
                                            if mevcut:
                                                _, e_durum, e_tip = mevcut
                                                if not (e_durum == "Delivered" and e_tip and ("Şoför" in e_tip or "Instagram" in e_tip)):
                                                    cursor.execute("UPDATE SiparislerV6 SET durum=?, teslimat_tipi='🚚 HB-Kargo', teslimat_kodu=? WHERE paket_id=?", (db_durum, teslimat_kodu, paket_id))
                                            else:
                                                ot = str(s.get("orderDate", s.get("OrderDate", "")))
                                                sip_ms = int(datetime.strptime(ot[:19], "%Y-%m-%dT%H:%M:%S").timestamp() * 1000) if len(ot) >= 19 else suan_ms
                                                
                                                dt = str(s.get("dueDate", s.get("DueDate", "")))
                                                ter_ms = int(datetime.strptime(dt[:19], "%Y-%m-%dT%H:%M:%S").timestamp() * 1000) if len(dt) >= 19 else (suan_ms + 259200000)
                                                
                                                musteri = s.get("recipientName", s.get("RecipientName", "HB Müşterisi"))
                                                il = s.get("shippingCity", s.get("ShippingCity", ""))
                                                ilce = s.get("shippingTown", s.get("ShippingTown", ""))
                                                tel = s.get("phoneNumber", s.get("PhoneNumber", ""))
                                                
                                                items = s.get("items", s.get("lines", s.get("products", [])))
                                                stok = " + ".join([str(l.get("merchantSku", l.get("MerchantSku", ""))) for l in items])
                                                adet = sum([int(l.get("quantity", l.get("Quantity", 1))) for l in items])
                                                
                                                cursor.execute('''INSERT INTO SiparislerV6 
                                                    (paket_id, siparis_no, siparis_tarihi_ms, termin_tarihi_ms, musteri_adi, teslimat_adresi, il, ilce, stok_kodu, adet, telefon, durum, teslimat_tipi, teslimat_kodu) 
                                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                                                    (paket_id, sip_no, sip_ms, ter_ms, musteri, "HB Paket", il, ilce, stok, adet, tel, db_durum, "🚚 HB-Kargo", teslimat_kodu))
                                        conn.commit()
                                        if len(hb_siparisler) < limit: break
                                        offset += limit
                                    else: break
                                except Exception as e: break
        
    def tabloyu_doldur(self):
        filtre_adi = self.secili_filtre.get()
        hedef_durum = self.durum_sozlugu.get(filtre_adi, "ALL")
        arama_metni = self.normalize_tr(self.entry_arama.get().strip())
        self.tumunu_secildi_mi = False
        self.btn_tumunu_sec.configure(text="☑ Tümünü Seç")
        self.son_cekilen_satirlar.clear()
        oto_kargolanacak_paketler = [] 
        suan = datetime.now() 

        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                query = "SELECT paket_id, siparis_no, siparis_tarihi_ms, termin_tarihi_ms, musteri_adi, teslimat_adresi, il, ilce, stok_kodu, adet, telefon, durum, teslimat_tipi, teslimat_kodu FROM SiparislerV6 WHERE 1=1"
                params = []
                
                if hedef_durum == "PENDING_KARGO": query += " AND durum IN ('Created', 'Picking') AND teslimat_tipi LIKE ?"; params.append('%KARGO%')
                elif hedef_durum == "PENDING_SEVKIYAT": query += " AND durum IN ('Created', 'Picking') AND teslimat_tipi LIKE ?"; params.append('%SEVKİYAT%')
                elif hedef_durum != "ALL": query += " AND durum = ?"; params.append(hedef_durum)

                query += f" ORDER BY {self.sort_col} {self.sort_dir}"
                cursor.execute(query, params)
                kayitlar = cursor.fetchall()

                for kayit in kayitlar:
                    paket_id, sip_no, sip_ms, termin_ms, musteri, adres_tam, il, ilce, stok, adet, telefon, durum_ing, teslimat_tipi, teslimat_kodu = kayit
                    adres = adres_tam[:37] + "..." if len(adres_tam) > 40 else adres_tam
                    
                    if termin_ms > 0 and durum_ing in ["Created", "Picking"] and "SEVKİYAT" in teslimat_tipi:
                        termin_date = datetime.fromtimestamp(termin_ms / 1000.0)
                        fark = termin_date - suan
                        if fark.total_seconds() < 3600: 
                            oto_kargolanacak_paketler.append(paket_id)
                    
                    if arama_metni and arama_metni not in self.normalize_tr(f"{sip_no} {musteri} {il} {ilce} {stok} {teslimat_tipi} {teslimat_kodu}"): continue 
                        
                    sip_tarih_str = datetime.fromtimestamp(sip_ms / 1000.0).strftime('%d.%m.%y %H:%M') if sip_ms > 0 else "-"
                    termin_tarih_str = datetime.fromtimestamp(termin_ms / 1000.0).strftime('%d.%m.%y %H:%M') if termin_ms > 0 else "-"
                    durum_tr = {"Created": "Yeni Sipariş", "Picking": "Toplanıyor", "Shipped": "Kargoda", "Delivered": "Teslim Edildi", "Cancelled": "İptal Edildi"}.get(durum_ing, durum_ing)

                    satir = ("☐", teslimat_tipi, sip_tarih_str, termin_tarih_str, "-", paket_id, sip_no, teslimat_kodu, musteri, adres, il, ilce, stok, adet, durum_tr)
                    self.son_cekilen_satirlar.append(satir)
        except Exception as e: self.lbl_durum.configure(text=f"Hata: {str(e)}", text_color="red")
        
        self.agaci_guncelle() 
        self.btn_yenile.configure(state="normal")
        self.btn_sifirla.configure(state="normal")
        
        if oto_kargolanacak_paketler:
            threading.Thread(target=self.kargolama_thread, args=(oto_kargolanacak_paketler, True), daemon=True).start()

    def agaci_guncelle(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        suan = datetime.now()
        listelenen_sayisi = 0

        for col in self.tree["columns"]:
            if col in ["Secim", "PaketID"]: continue
            metin = self.orijinal_basliklar[col]
            if col in self.kolon_filtreleri: metin += " (F)"
            if col == getattr(self, "sort_col", ""): metin += " ▼" if self.sort_dir == "DESC" else " ▲"
            self.tree.heading(col, text=metin)

        for satir in self.son_cekilen_satirlar:
            gecerli = True
            for col_name, izin_verilenler in self.kolon_filtreleri.items():
                if satir[self.tree["columns"].index(col_name)] not in izin_verilenler: gecerli = False; break
            if not gecerli: continue 

            listelenen_sayisi += 1
            satir_listesi = list(satir)
            termin_tarih_str, durum_tr, teslimat_tipi = satir_listesi[3], satir_listesi[14], satir_listesi[1]
            satir_etiketi = ['cift_satir' if listelenen_sayisi % 2 == 0 else 'tek_satir']
            kalan_str = "-"
            
            if "Şoför Teslimatı" in teslimat_tipi or "📸 Şoför" in teslimat_tipi or "📱 Instagram" in teslimat_tipi:
                satir_etiketi.append('teslim_edildi')
            
            if termin_tarih_str != "-" and durum_tr not in ["Kargoda", "Teslim Edildi", "İptal Edildi"]:
                termin_tarihi = datetime.strptime(termin_tarih_str, '%d.%m.%y %H:%M')
                fark = termin_tarihi - suan
                if fark.total_seconds() > 0:
                    g, s, dk = fark.days, fark.seconds // 3600, (fark.seconds % 3600) // 60
                    if g > 0: 
                        kalan_str = f"{g} gün, {s} sa."
                    elif s > 0: 
                        kalan_str = f"{s} sa. {dk} dk."
                        satir_etiketi.append('acil')
                    else: 
                        kalan_str = f"🚨 {dk} Dk!"
                        satir_etiketi.append('acil')
                else:
                    kalan_str = "⚠️ GECİKTİ"
                    satir_etiketi.append('acil')

            satir_listesi[4] = kalan_str 
            self.tree.insert("", "end", values=tuple(satir_listesi), tags=tuple(satir_etiketi))

        if self.otopilot_mesaji != "":
            self.lbl_durum.configure(text=self.otopilot_mesaji, text_color="#00FF00")
            self.otopilot_mesaji = ""
        else:
            self.lbl_durum.configure(text=f"Aktif Kayıt: {listelenen_sayisi} | Otopilot Devrede ⚡", text_color="#00FF00")

if __name__ == "__main__":
    app = SiparisEkrani()
    app.mainloop()
