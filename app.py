import streamlit as st
import pandas as pd
import datetime
import urllib.parse
import os
import requests

st.set_page_config(
    page_title="devia ouvir mais discos", 
    page_icon="🎶", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada com a estética de vinil (Dark Mode)
st.markdown("""
    <style>
    .main {
        background-color: #121212;
        color: #e0e0e0;
    }
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #333333;
        border-radius: 8px;
    }
    div[data-testid="stMetricValue"] {
        color: #f59e0b;
    }
    .vinyl-card {
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #2a2a2a;
        margin-bottom: 10px;
    }
    .spotify-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: #1db954;
        color: #ffffff !important;
        font-weight: 700;
        font-size: 14px;
        padding: 10px 20px;
        border-radius: 25px;
        text-decoration: none !important;
        margin-top: 15px;
        transition: background-color 0.2s ease, transform 0.1s ease;
        box-shadow: 0 4px 12px rgba(29, 185, 84, 0.3);
    }
    .spotify-btn:hover {
        background-color: #1ed760;
        transform: scale(1.02);
    }
    .spotify-icon {
        margin-right: 8px;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color: #ffffff; font-weight: 800;'>devia ouvir mais discos</h1>", unsafe_allow_html=True)
st.caption("Ouvindo, explorando e avaliando discos em toda a sua arte.")

# Dicionário robusto de códigos ISO estruturado
MAPA_ISO = {
    "Brasil": "br", "Brazil": "br",
    "Estados Unidos": "us", "Eua": "us", "United States": "us",
    "Reino Unido": "gb", "Inglaterra": "gb", "United Kingdom": "gb",
    "França": "fr", "France": "fr",
    "Argentina": "ar",
    "Cuba": "cu",
    "México": "mx", "Mexico": "mx",
    "Chile": "cl",
    "Colômbia": "co", "Colombia": "co",
    "Panamá": "pa", "Panama": "pa",
    "Puerto Rico": "pr",
    "República Dominicana": "do",
    "Perú": "pe", "Peru": "pe",
    "Costa Rica": "cr",
    "Venezuela": "ve",
    "Bolívia": "bo", "Bolivia": "bo",
    "Uruguay": "uy", "Uruguai": "uy",
    "Guatemala": "gt",
    "El Salvador": "sv",
    "Paraguay": "py", "Paraguai": "py",
    "Ecuador": "ec", "Equador": "ec",
    "Nicaragua": "ni", "Nicarágua": "ni",
    "Honduras": "hn",
    "España": "es", "Espanha": "es", "Spain": "es",
    "Itália": "it", "Italia": "it", "Italy": "it",
    "Portugal": "pt",
    "Japão": "jp", "Japan": "jp",
    "Jamaica": "jm",
    "Canadá": "ca", "Canada": "ca",
    "Alemanha": "de", "Germany": "de"
}

def obter_html_bandeira(pais):
    if not isinstance(pais, str):
        return str(pais)
    p_limpo = pais.strip().title()
    primeiro_pais = p_limpo.split(',')[0].strip()
    iso = MAPA_ISO.get(primeiro_pais, "un")
    url_bandeira = f"https://flagcdn.com/24x18/{iso}.png"
    return f'<img src="{url_bandeira}" style="width: 20px; height: 15px; vertical-align: middle; margin-right: 5px; border-radius: 2px;" alt="{pais}"> {pais}'

@st.cache_data
def load_data():
    if not os.path.exists("albums.csv"):
        st.error("⚠️ O arquivo 'albums.csv' não foi encontrado no GitHub.")
        return pd.DataFrame()
    
    df = pd.read_csv("albums.csv", on_bad_lines='skip')
    
    colunas_obrigatorias = {
        'Cover_Rating': 3,
        'Total_Tracks': 10,
        'Liked_Tracks': 8,
        'Favorite_Track': '',
        'My_Review': '',
        'Country': 'Brasil',
        'Spotify_Link': 'Spotify',
        'Colecao': 'Não'
    }
    for col, val_padrao in colunas_obrigatorias.items():
        if col not in df.columns:
            df[col] = val_padrao

    df = df.drop_duplicates(subset=['Artist', 'Album'], keep='first').reset_index(drop=True)
    
    df['Cover_Rating'] = df['Cover_Rating'].fillna(3).astype(int)
    df['Total_Tracks'] = df['Total_Tracks'].fillna(10).astype(int)
    df['Liked_Tracks'] = df['Liked_Tracks'].fillna(8).astype(int)
    df['Colecao'] = df['Colecao'].fillna('Não').astype(str)
    
    prop = df['Liked_Tracks'] / df['Total_Tracks']
    df['Nota_Calculada'] = (prop * 5.0 * 0.70) + (df['Cover_Rating'] * 0.30)
    
    return df

@st.cache_data
def buscar_capa_album(artist, album):
    try:
        termo = f"{artist} {album}"
        url = f"https://itunes.apple.com/search?term={urllib.parse.quote(termo)}&entity=album&limit=1"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                artwork = data['results'][0]['artworkUrl100']
                return artwork.replace('100x100b.jpg', '600x600bb.jpg').replace('100x100', '600x600')
    except Exception:
        pass
    return None

def obter_link_spotify(row):
    link_custom = str(row.get('Spotify_Link', '')).strip()
    if link_custom.startswith('http'):
        return link_custom
    query_sp = urllib.parse.quote(f"{row['Artist']} {row['Album']}")
    return f"https://open.spotify.com/search/{query_sp}"

df_albums = load_data()

if df_albums.empty:
    st.stop()

# MENU LATERAL REORGANIZADO
st.sidebar.markdown("### 🎛️ menu")
aba = st.sidebar.radio(
    "navegar", 
    [
        "álbum do dia", 
        "histórico", 
        "estatísticas", 
        "minha coleção", 
        "inserir manualmente"
    ]
)

# 1. ABA: ÁLBUM DO DIA
if aba == "álbum do dia":
    today_seed = int(datetime.date.today().strftime("%Y%m%d"))
    album_hoje = df_albums.sample(1, random_state=today_seed).iloc[0]
    
    st.markdown("### 💿 álbum do dia")
    
    col_pop1, col_pop2 = st.columns([1, 2])
    
    with col_pop1:
        st.markdown(f"### {album_hoje['Album']}")
        st.markdown(f"**Artista:** {album_hoje['Artist']}")
        
        pais_nome = str(album_hoje.get('Country', 'Brasil')).strip()
        html_bandeira = obter_html_bandeira(pais_nome)
        st.markdown(f"**País:** {html_bandeira}", unsafe_allow_html=True)
        
        st.markdown(f"**Lançamento:** {int(album_hoje['Released']) if pd.notna(album_hoje['Released']) else ''}")
        
        capa_url = buscar_capa_album(album_hoje['Artist'], album_hoje['Album'])
        if capa_url:
            st.image(capa_url, caption=album_hoje['Album'], use_column_width=True)
        else:
            st.info("💿 Capa indisponível no momento")
        
        url_spotify = obter_link_spotify(album_hoje)
        st.markdown(f"""
            <a href="{url_spotify}" target="_blank" class="spotify-btn">
                <span class="spotify-icon">🎧</span> ouvir álbum completo
            </a>
        """, unsafe_allow_html=True)
        
    with col_pop2:
        st.markdown("#### 🎵 registre sua audição")
        st.markdown("nota da capa (1 a 5)")
        
        atual_rating = int(album_hoje.get('Cover_Rating', 3)) - 1
        if atual_rating < 0 or