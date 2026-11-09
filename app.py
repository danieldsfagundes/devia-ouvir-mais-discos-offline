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
        margin-bottom: 20px;
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

def obter_html_bandeira(pais):
    if not isinstance(pais, str):
        return str(pais)
    p = pais.strip().title()
    codigos_iso = {
        "Brasil": "br",
        "Estados Unidos": "us",
        "Eua": "us",
        "Reino Unido": "gb",
        "Inglaterra": "gb",
        "França": "fr",
        "Argentina": "ar",
        "Jamaica": "jm",
        "Canadá": "ca",
        "Alemanha": "de",
        "Espanha": "es",
        "Itália": "it",
        "Portugal": "pt",
        "Japão": "jp"
    }
    iso = codigos_iso.get(p, "br")
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
        'Spotify_Link': 'Spotify'
    }
    for col, val_padrao in colunas_obrigatorias.items():
        if col not in df.columns:
            df[col] = val_padrao

    df = df.drop_duplicates(subset=['Artist', 'Album'], keep='first').reset_index(drop=True)
    
    df['Cover_Rating'] = df['Cover_Rating'].fillna(3).astype(int)
    df['Total_Tracks'] = df['Total_Tracks'].fillna(10).astype(int)
    df['Liked_Tracks'] = df['Liked_Tracks'].fillna(8).astype(int)
    
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
    # Se for um link web real com http, usa ele. Caso contrário, usa a busca tradicional do Spotify.
    if link_custom.startswith('http'):
        return link_custom
    
    query_sp = urllib.parse.quote(f"{row['Artist']} {row['Album']}")
    return f"https://open.spotify.com/search/{query_sp}"

df_albums = load_data()

if df_albums.empty:
    st.stop()

# MENU LATERAL
st.sidebar.markdown("### 🎛️ menu")
aba = st.sidebar.radio(
    "navegar", 
    [
        "álbum do dia", 
        "coleção & histórico", 
        "estatísticas", 
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
        if atual_rating < 0 or atual_rating > 4:
            atual_rating = 2
            
        feedback_estrelas = st.feedback("stars", key="pop_cov_feedback")
        cov_p = (feedback_estrelas + 1) if feedback_estrelas is not None else (atual_rating + 1)
        
        tot_p = st.number_input("total de faixas", 1, 30, int(album_hoje.get('Total_Tracks', 10)), key="pop_tot")
        lik_p = st.number_input("faixas que gostou", 0, tot_p, int(album_hoje.get('Liked_Tracks', 8)), key="pop_lik")
        
        if st.button("salvar audição do dia", type="primary"):
            st.success("audição registrada com sucesso!")
            st.rerun()

# 2. ABA: COLEÇÃO & HISTÓRICO
elif aba == "coleção & histórico":
    st.markdown("### 📚 sua coleção de vinis & histórico")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        artistas_disponiveis = ["todos"] + sorted(df_albums['Artist'].dropna().astype(str).unique().tolist())
        filtro_artista = st.selectbox("filtrar por banda / artista", artistas_disponiveis)
    with col_f2:
        paises_disponiveis = ["todos"] + sorted(df_albums['Country'].dropna().astype(str).unique().tolist())
        filtro_pais = st.selectbox("filtrar por país", paises_disponiveis)
    with col_f3:
        anos_disponiveis = sorted(df_albums['Released'].dropna().unique().tolist())
        filtro_ano = st.selectbox("filtrar por ano de lançamento", ["todos"] + [str(int(a)) for a in anos_disponiveis])

    df_filtrado = df_albums.copy()
    if filtro_artista != "todos":
        df_filtrado = df_filtrado[df_filtrado['Artist'] == filtro_artista]
    if filtro_pais != "todos":
        df_filtrado = df_filtrado[df_filtrado['Country'] == filtro_pais]
    if filtro_ano != "todos":
        df_filtrado = df_filtrado[df_filtrado['Released'].astype(int).astype(str) == filtro_ano]

    df_filtrado = df_filtrado.sort_values(by='Nota_Calculada', ascending=False).reset_index(drop=True)

    st.caption(f"exibindo {len(df_filtrado)} discos no acervo (ordenados da nota mais alta para a mais baixa).")

    cols = st.columns(4)
    for idx, row in enumerate(df_filtrado.head(24).iterrows()):
        i, r = row
        col_atual = cols[idx % 4]
        with col_atual:
            pais_card = str(r.get('Country', 'Brasil')).strip()
            iso_card = "br" if "brasil" in pais_card.lower() else "us"
            ano_val = int(r['Released']) if pd.notna(r['Released']) else ''
            st.markdown(f"""
                <div class="vinyl-card">
                    <b style="color: #ffffff; font-size: 16px;">{r['Album']}</b><br>
                    <span style="color: #a0a0a0; font-size: 14px;">{r['Artist']}</span><br>
                    <span style="color: #888; font-size: 12px;"><img src="https://flagcdn.com/16x12/{iso_card}.png" style="vertical-align: middle;"> {pais_card}</span><br>
                    <span style="color: #f59e0b; font-size: 12px;">📅 {ano_val} | ⭐ Nota: {r['Nota_Calculada']:.1f}/5</span><br>
                    <hr style="border: 0.5px solid #333; margin: 8px 0;">
                    <span style="color: #1db954; font-size: 12px;">Capa: {int(r['Cover_Rating'])}/5 | Aprov: {int(r['Liked_Tracks'])}/{int(r['Total_Tracks'])}</span>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("editar / ver detalhes", key=f"btn_{i}"):
                st.session_state.album_editando = r['Album']

    if 'album_editando' in st.session_state:
        st.markdown("---")
        with st.expander("✏️ **detalhando e editando álbum selecionado**", expanded=True):
            album_sel_nome = st.session_state.album_editando
            row_sel = df_albums[df_albums['Album'] == album_sel_nome].iloc[0]
            sel_idx = df_albums[df_albums['Album'] == album_sel_nome].index[0]
            
            c_ed1, c_ed2 = st.columns(2)
            with c_ed1:
                st.markdown(f"### {row_sel['Album']}")
                st.markdown(f"**Artista:** {row_sel['Artist']}")
                
                pais_sel = str(row_sel.get('Country', 'Brasil')).strip()
                html_bandeira_sel = obter_html_bandeira(pais_sel)
                st.markdown(f"**País:** {html_bandeira_sel}", unsafe_allow_html=True)
                
                st.markdown(f"**Lançamento:** {int(row_sel['Released']) if pd.notna(row_sel['Released']) else ''}")
                
                capa_detalhe = buscar_capa_album(row_sel['Artist'], row_sel['Album'])
                if capa_detalhe:
                    st.image(capa_detalhe, caption=row_sel['Album'], width=300)
                
                url_spotify_detalhe = obter_link_spotify(row_sel)
                st.markdown(f"""
                    <a href="{url_spotify_detalhe}" target="_blank" class="spotify-btn">
                        <span class="spotify-icon">🎧</span> ouvir álbum completo
                    </a>
                """, unsafe_allow_html=True)
                
            with c_ed2:
                st.markdown("nota da capa (1 a 5)")
                fb_ed = st.feedback("stars", key=f"c_ed_feedback_{sel_idx}")
                atual_ed_rating = int(row_sel['Cover_Rating']) - 1
                if atual_ed_rating < 0 or atual_ed_rating > 4:
                    atual_ed_rating = 2
                nova_capa = (fb_ed + 1) if fb_ed is not None else (atual_ed_rating + 1)
                
                tot_f = st.number_input("total de músicas", 1, 30, int(row_sel['Total_Tracks']), key=f"t_ed_{sel_idx}")
                lik_f = st.number_input("músicas que gostou", 0, tot_f, int(row_sel['Liked_Tracks']), key=f"l_ed_{sel_idx}")
                fav_m = st.text_input("música favorita", value=str(row_sel['Favorite_Track']), key=f"f_ed_{sel_idx}")
                
                nota_capa_conv = (nova_capa / 5.0) * 5.0
                prop_musicas = (lik_f / tot_f) if tot_f > 0 else 0
                nota_musicas_conv = prop_musicas * 5.0
                nota_final_calculada = (nota_musicas_conv * 0.70) + (nota_capa_conv * 0.30)
                
                st.info(f"🎯 **nota final calculada: {nota_final_calculada:.2f} / 5**")
                
                if st.button("salvar alterações no acervo", type="primary"):
                    df_albums.loc[sel_idx, 'Cover_Rating'] = nova_capa
                    df_albums.loc[sel_idx, 'Total_Tracks'] = tot_f
                    df_albums.loc[sel_idx, 'Liked_Tracks'] = lik_f
                    df_albums.loc[sel_idx, 'Favorite_Track'] = fav_m
                    df_albums.to_csv("albums.csv", index=False)
                    st.success("salvo com sucesso!")
                    del st.session_state.album_editando
                    st.rerun()
            
            if st.button("fechar editor"):
                del st.session_state.album_editando
                st.rerun()

# 3. ABA: ESTATÍSTICAS
elif aba == "estatísticas":
    st.subheader("📊 estatísticas da sua coleção")
    c_s1, c_s2, c_s3 = st.columns(3)
    with c_s1:
        st.metric("total de discos catalogados", len(df_albums))
    with c_s2:
        media_aproveitamento = (df_albums['Liked_Tracks'] / df_albums['Total_Tracks']).mean() * 100
        st.metric("aproveitamento médio de faixas", f"{media_aproveitamento:.1f}%")
    with c_s3:
        st.metric("média de nota das capas", f"{df_albums['Cover_Rating'].mean():.1f} / 5")

# 4. ABA: INSERIR MANUALMENTE
elif aba == "inserir manualmente":
    st.subheader("➕ inserir novo disco manualmente")
    with st.form("form_manual"):
        m_artista = st.text_input("artista / banda")
        m_pais = st.text_input("país", value="Brasil")
        m_album = st.text_input("nome do álbum")
        m_ano = st.number_input("ano de lançamento", min_value=1900, max_value=2026, value=1975)
        m_spotify = st.text_input("link do álbum no Spotify", value="Spotify")
        
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            m_capa = st.slider("nota da capa (1 a 5)", 1, 5, 4)
            m_tot = st.number_input("total de músicas", 1, 30, 10)
        with c_m2:
            m_lik = st.number_input("músicas que gostou", 0, m_tot, 8)
            m_fav = st.text_input("música favorita")
            
        if st.form_submit_button("adicionar à coleção"):
            novo_registro = pd.DataFrame([{
                'Artist': m_artista,
                'Country': m_pais,
                'Album': m_album,
                'Released': m_ano,
                'Spotify_Link': m_spotify,
                'Cover_Rating': m_capa,
                'Total_Tracks': m_tot,
                'Liked_Tracks': m_lik,
                'Favorite_Track': m_fav,
                'My_Review': ''
            }])
            df_atualizado = pd.concat([df_albums, novo_registro], ignore_index=True)
            df_atualizado.to_csv("albums.csv", index=False)
            st.success(f"'{m_album}' adicionado com sucesso!")