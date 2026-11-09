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

def carregar_dados_frescos():
    if not os.path.exists("albums.csv"):
        return pd.DataFrame()
    df = pd.read_csv("albums.csv", on_bad_lines='skip', dtype=str)
    
    colunas_obrigatorias = {
        'Cover_Rating': '3',
        'Liked_Tracks': '4',
        'Favorite_Track': '',
        'My_Review': '',
        'Country': 'Brasil',
        'Spotify_Link': 'Spotify',
        'Colecao': 'Não',
        'Released': '1975'
    }
    for col, val_padrao in colunas_obrigatorias.items():
        if col not in df.columns:
            df[col] = val_padrao

    df = df.drop_duplicates(subset=['Artist', 'Album'], keep='first').reset_index(drop=True)
    
    df['Cover_Rating'] = pd.to_numeric(df['Cover_Rating'], errors='coerce').fillna(3).astype(int)
    df['Liked_Tracks'] = pd.to_numeric(df['Liked_Tracks'], errors='coerce').fillna(4).astype(int)
    df['Released'] = pd.to_numeric(df['Released'], errors='coerce').fillna(1975).astype(int)
    df['Colecao'] = df['Colecao'].fillna('Não').astype(str)
    df['Favorite_Track'] = df['Favorite_Track'].fillna('').astype(str)
    df['Favorite_Track'] = df['Favorite_Track'].apply(lambda x: '' if x.lower() == 'nan' else x)
    
    df['Nota_Calculada'] = (df['Liked_Tracks'] * 0.70) + (df['Cover_Rating'] * 0.30)
    
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

df_albums = carregar_dados_frescos()

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
        
        val_c = row_val = album_hoje.get('Cover_Rating', 3)
        try:
            cur_c = int(float(val_c)) - 1
        except:
            cur_c = 2
        cur_c = max(0, min(4, cur_c))
        
        feedback_estrelas = st.feedback("stars", key="pop_cov_feedback")
        cov_p = (feedback_estrelas + 1) if feedback_estrelas is not None else (cur_c + 1)
        
        st.markdown("nota das músicas (1 a 5)")
        val_l = album_hoje.get('Liked_Tracks', 4)
        try:
            cur_l = int(float(val_l)) - 1
        except:
            cur_l = 3
        cur_l = max(0, min(4, cur_l))
        
        feedback_lik = st.feedback("stars", key="pop_lik_feedback")
        lik_p = (feedback_lik + 1) if feedback_lik is not None else (cur_l + 1)
        
        if st.button("salvar audição do dia", type="primary"):
            st.success("audição registrada com sucesso!")
            st.rerun()

# 2. ABA: MINHA COLEÇÃO
elif aba == "minha coleção":
    st.markdown("### 💽 minha coleção de vinis")
    
    df_colecao = df_albums[df_albums['Colecao'].str.strip().str.lower().isin(['sim', 's', 'yes', 'true', '1'])].copy()
    df_colecao = df_colecao.sort_values(by='Nota_Calculada', ascending=False).reset_index(drop=True)
    
    st.caption(f"exibindo {len(df_colecao)} discos cadastrados na sua coleção.")
    
    if df_colecao.empty:
        st.info("💡 Nenhum disco marcado como 'Sim' na coleção ainda. Edite os álbuns no Histórico para adicioná-los!")
    else:
        lista_discos = df_colecao.head(24).to_dict('records')
        for row_idx in range(0, len(lista_discos), 4):
            cols = st.columns(4)
            for col_idx in range(4):
                flat_idx = row_idx + col_idx
                if flat_idx < len(lista_discos):
                    r = lista_discos[flat_idx]
                    with cols[col_idx]:
                        pais_card = str(r.get('Country', 'Brasil')).strip()
                        p_primario = pais_card.split(',')[0].strip().title()
                        iso_card = MAPA_ISO.get(p_primario, "un")
                        ano_val = int(r['Released']) if pd.notna(r['Released']) else ''
                        st.markdown(f"""
                            <div class="vinyl-card">
                                <b style="color: #ffffff; font-size: 16px;">{r['Album']}</b><br>
                                <span style="color: #a0a0a0; font-size: 14px;">{r['Artist']}</span><br>
                                <span style="color: #888; font-size: 12px;"><img src="https://flagcdn.com/16x12/{iso_card}.png" style="vertical-align: middle;"> {pais_card}</span><br>
                                <span style="color: #f59e0b; font-size: 12px;">📅 {ano_val} | ⭐ Nota: {r['Nota_Calculada']:.1f}/5</span><br>
                                <hr style="border: 0.5px solid #333; margin: 8px 0;">
                                <span style="color: #1db954; font-size: 12px;">Capa: {int(float(r['Cover_Rating']))}/5 | Aprov: {int(float(r['Liked_Tracks']))}/5</span>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("editar / ver detalhes", key=f"btn_col_{flat_idx}"):
                            st.session_state.album_editando = r['Album']

            for col_idx in range(4):
                flat_idx = row_idx + col_idx
                if flat_idx < len(lista_discos):
                    r = lista_discos[flat_idx]
                    if st.session_state.get('album_editando') == r['Album']:
                        st.markdown("---")
                        with st.container():
                            st.markdown(f"✏️ **Editando: {r['Album']} ({r['Artist']})**")
                            
                            df_fresh = pd.read_csv("albums.csv", dtype=str)
                            match_idx = df_fresh[(df_fresh['Album'] == r['Album']) & (df_fresh['Artist'] == r['Artist'])].index
                            if len(match_idx) > 0:
                                sel_idx = match_idx[0]
                                row_sel = df_fresh.loc[sel_idx]
                            else:
                                row_sel = r
                                sel_idx = 0
                            
                            c_ed1, c_ed2 = st.columns(2)
                            with c_ed1:
                                cap = buscar_capa_album(str(row_sel['Artist']), str(row_sel['Album']))
                                if cap:
                                    st.image(cap, width=220)
                                url_sp = obter_link_spotify(row_sel)
                                st.markdown(f'<a href="{url_sp}" target="_blank" class="spotify-btn">🎧 ouvir no spotify</a>', unsafe_allow_html=True)
                            with c_ed2:
                                st.markdown("nota da capa (1 a 5)")
                                try:
                                    cur_c = int(float(row_sel.get('Cover_Rating', 3))) - 1
                                except:
                                    cur_c = 2
                                cur_c = max(0, min(4, cur_c))
                                fb_ed = st.feedback("stars", key=f"col_c_{flat_idx}")
                                nova_capa = (fb_ed + 1) if fb_ed is not None else (cur_c + 1)
                                
                                st.markdown("nota das músicas (1 a 5)")
                                try:
                                    cur_l = int(float(row_sel.get('Liked_Tracks', 4))) - 1
                                except:
                                    cur_l = 3
                                cur_l = max(0, min(4, cur_l))
                                fb_l = st.feedback("stars", key=f"col_l_{flat_idx}")
                                novo_lik = (fb_l + 1) if fb_l is not None else (cur_l + 1)
                                
                                fav_val = str(row_sel.get('Favorite_Track', ''))
                                if fav_val.lower() == 'nan': fav_val = ''
                                fav_m = st.text_input("música favorita", value=fav_val, key=f"col_f_{flat_idx}")
                                colecao_atual = str(row_sel.get('Colecao', 'Não')).strip().capitalize()
                                idx_col = 0 if colecao_atual in ['Sim', 'S', 'True', 'Yes'] else 1
                                nova_colecao = st.selectbox("minha coleção", ["Sim", "Não"], index=idx_col, key=f"col_s_{flat_idx}")
                                
                                if st.button("salvar alterações", type="primary", key=f"col_save_{flat_idx}"):
                                    df_all = pd.read_csv("albums.csv", dtype=str)
                                    m_idx = df_all[(df_all['Album'] == str(r['Album'])) & (df_all['Artist'] == str(r['Artist']))].index
                                    if len(m_idx) > 0:
                                        idx_s = m_idx[0]
                                        df_all.loc[idx_s, 'Cover_Rating'] = str(int(nova_capa))
                                        df_all.loc[idx_s, 'Liked_Tracks'] = str(int(novo_lik))
                                        df_all.loc[idx_s, 'Favorite_Track'] = str(fav_m)
                                        df_all.loc[idx_s, 'Colecao'] = str(nova_colecao)
                                        df_all.to_csv("albums.csv", index=False)
                                        st.success("Salvo com sucesso!")
                                        del st.session_state.album_editando
                                        st.rerun()
                                    else:
                                        st.error("Erro ao localizar álbum para salvar.")
                                        
                                if st.button("fechar editor", key=f"col_close_{flat_idx}"):
                                    del st.session_state.album_editando
                                    st.rerun()
                        st.markdown("---")

# 3. ABA: HISTÓRICO
elif aba == "histórico":
    st.markdown("### 📚 histórico")
    
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

    lista_discos_hist = df_filtrado.head(24).to_dict('records')
    for row_idx in range(0, len(lista_discos_hist), 4):
        cols = st.columns(4)
        for col_idx in range(4):
            flat_idx = row_idx + col_idx
            if flat_idx < len(lista_discos_hist):
                r = lista_discos_hist[flat_idx]
                with cols[col_idx]:
                    pais_card = str(r.get('Country', 'Brasil')).strip()
                    p_primario = pais_card.split(',')[0].strip().title()
                    iso_card = MAPA_ISO.get(p_primario, "un")
                    ano_val = int(r['Released']) if pd.notna(r['Released']) else ''
                    st.markdown(f"""
                        <div class="vinyl-card">
                            <b style="color: #ffffff; font-size: 16px;">{r['Album']}</b><br>
                            <span style="color: #a0a0a0; font-size: 14px;">{r['Artist']}</span><br>
                            <span style="color: #888; font-size: 12px;"><img src="https://flagcdn.com/16x12/{iso_card}.png" style="vertical-align: middle;"> {pais_card}</span><br>
                            <span style="color: #f59e0b; font-size: 12px;">📅 {ano_val} | ⭐ Nota: {r['Nota_Calculada']:.1f}/5</span><br>
                            <hr style="border: 0.5px solid #333; margin: 8px 0;">
                            <span style="color: #1db954; font-size: 12px;">Capa: {int(float(r['Cover_Rating']))}/5 | Aprov: {int(float(r['Liked_Tracks']))}/5</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("editar / ver detalhes", key=f"btn_hist_{flat_idx}"):
                        st.session_state.album_editando = r['Album']

        for col_idx in range(4):
            flat_idx = row_idx + col_idx
            if flat_idx < len(lista_discos_hist):
                r = lista_discos_hist[flat_idx]
                if st.session_state.get('album_editando') == r['Album']:
                    st.markdown("---")
                    with st.container():
                        st.markdown(f"✏️ **Editando: {r['Album']} ({r['Artist']})**")
                        
                        df_fresh = pd.read_csv("albums.csv", dtype=str)
                        match_idx = df_fresh[(df_fresh['Album'] == r['Album']) & (df_fresh['Artist'] == r['Artist'])].index
                        if len(match_idx) > 0:
                            sel_idx = match_idx[0]
                            row_sel = df_fresh.loc[sel_idx]
                        else:
                            row_sel = r
                            sel_idx = 0
                        
                        c_ed1, c_ed2 = st.columns(2)
                        with c_ed1:
                            cap = buscar_capa_album(str(row_sel['Artist']), str(row_sel['Album']))
                            if cap:
                                st.image(cap, width=220)
                            url_sp = obter_link_spotify(row_sel)
                            st.markdown(f'<a href="{url_sp}" target="_blank" class="spotify-btn">🎧 ouvir no spotify</a>', unsafe_allow_html=True)
                        with c_ed2:
                            st.markdown("nota da capa (1 a 5)")
                            try:
                                cur_c = int(float(row_sel.get('Cover_Rating', 3))) - 1
                            except:
                                cur_c = 2
                            cur_c = max(0, min(4, cur_c))
                            fb_ed = st.feedback("stars", key=f"hist_c_{flat_idx}")
                            nova_capa = (fb_ed + 1) if fb_ed is not None else (cur_c + 1)
                            
                            st.markdown("nota das músicas (1 a 5)")
                            try:
                                cur_l = int(float(row_sel.get('Liked_Tracks', 4))) - 1
                            except:
                                cur_l = 3
                            cur_l = max(0, min(4, cur_l))
                            fb_l = st.feedback("stars", key=f"hist_l_{flat_idx}")
                            novo_lik = (fb_l + 1) if fb_l is not None else (cur_l + 1)
                            
                            fav_val = str(row_sel.get('Favorite_Track', ''))
                            if fav_val.lower() == 'nan': fav_val = ''
                            fav_m = st.text_input("música favorita", value=fav_val, key=f"hist_f_{flat_idx}")
                            
                            colecao_atual = str(row_sel.get('Colecao', 'Não')).strip().capitalize()
                            idx_col = 0 if colecao_atual in ['Sim', 'S', 'True', 'Yes'] else 1
                            nova_colecao = st.selectbox("minha coleção", ["Sim", "Não"], index=idx_col, key=f"hist_s_{flat_idx}")
                            
                            if st.button("salvar alterações", type="primary", key=f"hist_save_{flat_idx}"):
                                df_all = pd.read_csv("albums.csv", dtype=str)
                                m_idx = df_all[(df_all['Album'] == str(r['Album'])) & (df_all['Artist'] == str(r['Artist']))].index
                                if len(m_idx) > 0:
                                    idx_s = m_idx[0]
                                    df_all.loc[idx_s, 'Cover_Rating'] = str(int(nova_capa))
                                    df_all.loc[idx_s, 'Liked_Tracks'] = str(int(novo_lik))
                                    df_all.loc[idx_s, 'Favorite_Track'] = str(fav_m)
                                    df_all.loc[idx_s, 'Colecao'] = str(nova_colecao)
                                    df_all.to_csv("albums.csv", index=False)
                                    st.success("Salvo com sucesso!")
                                    del st.session_state.album_editando
                                    st.rerun()
                                else:
                                    st.error("Erro ao localizar álbum para salvar.")
                                    
                            if st.button("fechar editor", key=f"hist_close_{flat_idx}"):
                                del st.session_state.album_editando
                                st.rerun()
                    st.markdown("---")

# 4. ABA: ESTATÍSTICAS
elif aba == "estatísticas":
    st.subheader("📊 estatísticas da sua coleção")
    c_s1, c_s2, c_s3 = st.columns(3)
    with c_s1:
        st.metric("total de discos catalogados", len(df_albums))
    with c_s2:
        media_aproveitamento = (df_albums['Liked_Tracks'].astype(float) / 5.0).mean() * 100
        st.metric("aproveitamento médio", f"{media_aproveitamento:.1f}%")
    with c_s3:
        st.metric("média de nota das capas", f"{df_albums['Cover_Rating'].astype(float).mean():.1f} / 5")

# 5. ABA: INSERIR MANUALMENTE
elif aba == "inserir manualmente":
    st.subheader("➕ inserir novo disco manualmente")
    with st.form("form_manual"):
        m_artista = st.text_input("artista / banda")
        m_pais = st.text_input("país", value="Brasil")
        m_album = st.text_input("nome do álbum")
        m_ano = st.number_input("ano de lançamento", min_value=1900, max_value=2026, value=1975)
        m_spotify = st.text_input("link do álbum no Spotify", value="Spotify")
        m_colecao = st.selectbox("minha coleção", ["Sim", "Não"])
        
        st.markdown("nota da capa (1 a 5)")
        fb_man = st.feedback("stars", key="manual_stars")
        m_capa = (fb_man + 1) if fb_man is not None else 3
        
        st.markdown("nota das músicas (1 a 5)")
        fb_man_lik = st.feedback("stars", key="manual_stars_lik")
        m_lik = (fb_man_lik + 1) if fb_man_lik is not None else 4
        
        m_fav = st.text_input("música favorita")
            
        if st.form_submit_button("adicionar à coleção"):
            df_all = pd.read_csv("albums.csv", dtype=str)
            novo_registro = pd.DataFrame([{
                'Artist': str(m_artista),
                'Country': str(m_pais),
                'Album': str(m_album),
                'Released': str(int(m_ano)),
                'Spotify_Link': str(m_spotify),
                'Colecao': str(m_colecao),
                'Cover_Rating': str(int(m_capa)),
                'Liked_Tracks': str(int(m_lik)),
                'Favorite_Track': str(m_fav),
                'My_Review': ''
            }])
            df_atualizado = pd.concat([df_all, novo_registro], ignore_index=True)
            df_atualizado.to_csv("albums.csv", index=False)
            st.success(f"'{m_album}' adicionado com sucesso!")