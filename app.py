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
    .album-cover {
        border-radius: 10px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.7);
        max-width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color: #ffffff; font-weight: 800;'>devia ouvir mais discos</h1>", unsafe_allow_html=True)
st.caption("sua coleção digital inspirada em vinis • acervo unificado")

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
        'Genres': 'geral',
        'Origin': 'Brasil',
        'List': 'Geral'
    }
    for col, val_padrao in colunas_obrigatorias.items():
        if col not in df.columns:
            df[col] = val_padrao

    df = df.drop_duplicates(subset=['Artist', 'Album'], keep='first').reset_index(drop=True)
    return df

# Função para buscar a capa oficial do álbum direto na API pública do iTunes
@st.cache_data
def buscar_capa_album(artist, album):
    try:
        termo = f"{artist} {album}"
        url = f"https://itunes.apple.com/search?term={urllib.parse.quote(termo)}&entity=album&limit=1"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                # Pega a imagem e aumenta a resolução para 600x600 pixels
                artwork = data['results'][0]['artworkUrl100']
                return artwork.replace('100x100b.jpg', '600x600bb.jpg').replace('100x100', '600x600')
    except Exception:
        pass
    return None

df_albums = load_data()

if df_albums.empty:
    st.stop()

if 'popup_ativo' not in st.session_state:
    st.session_state.popup_ativo = True

# Menu Lateral
st.sidebar.markdown("### 🎛️ menu")
aba = st.sidebar.radio("navegar", ["coleção & histórico", "álbum do dia", "estatísticas"])

# Pop-up do Álbum do Dia com Capa na Tela
if st.session_state.popup_ativo and aba == "coleção & histórico":
    today_seed = int(datetime.date.today().strftime("%Y%m%d"))
    album_hoje = df_albums.sample(1, random_state=today_seed).iloc[0]
    
    with st.expander("✨ **disco do dia em destaque (clique para fechar/abrir)**", expanded=True):
        col_pop1, col_pop2 = st.columns([1, 2])
        with col_pop1:
            st.markdown(f"### 💿 {album_hoje['Album']}")
            st.text(f"artista: {album_hoje['Artist']}")
            st.text(f"lançamento: {album_hoje['Released']}")
            
            # Busca e exibe a capa direto no site
            capa_url = buscar_capa_album(album_hoje['Artist'], album_hoje['Album'])
            if capa_url:
                st.image(capa_url, caption=album_hoje['Album'], use_column_width=True)
            else:
                st.info("💿 Capa indisponível no momento")
            
            query_sp = urllib.parse.quote(f"{album_hoje['Artist']} {album_hoje['Album']}")
            st.markdown(f"🎧 [ouvir álbum completo no Spotify](https://open.spotify.com/search/{query_sp})", unsafe_allow_html=True)
            
        with col_pop2:
            st.markdown("#### 🎯 registre sua audição")
            cov_p = st.slider("nota da capa (1 a 5)", 1, 5, int(album_hoje.get('Cover_Rating', 4)), key="pop_cov")
            tot_p = st.number_input("total de faixas", 1, 30, int(album_hoje.get('Total_Tracks', 10)), key="pop_tot")
            lik_p = st.number_input("faixas que gostou", 0, tot_p, int(album_hoje.get('Liked_Tracks', 8)), key="pop_lik")
            
            if st.button("salvar audição do dia", type="primary"):
                st.success("audição registrada com sucesso!")
                st.session_state.popup_ativo = False
                st.rerun()

# Aba de Coleção & Histórico
if aba == "coleção & histórico":
    st.markdown("---")
    st.markdown("### 📚 sua coleção de vinis & histórico")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        artistas_disponiveis = ["todos"] + sorted(df_albums['Artist'].dropna().astype(str).unique().tolist())
        filtro_artista = st.selectbox("filtrar por banda / artista", artistas_disponiveis)
    with col_f2:
        listas_disponiveis = ["todos"] + sorted(df_albums['List'].dropna().astype(str).unique().tolist())
        filtro_lista = st.selectbox("filtrar por lista / coleção", listas_disponiveis)
    with col_f3:
        anos_disponiveis = sorted(df_albums['Released'].dropna().unique().tolist())
        filtro_ano = st.selectbox("filtrar por ano de lançamento", ["todos"] + anos_disponiveis)

    df_filtrado = df_albums.copy()
    if filtro_artista != "todos":
        df_filtrado = df_filtrado[df_filtrado['Artist'] == filtro_artista]
    if filtro_lista != "todos":
        df_filtrado = df_filtrado[df_filtrado['List'] == filtro_lista]
    if filtro_ano != "todos":
        df_filtrado = df_filtrado[df_filtrado['Released'] == filtro_ano]

    st.caption(f"exibindo {len(df_filtrado)} discos no acervo com os filtros aplicados.")

    cols = st.columns(4)
    for idx, row in enumerate(df_filtrado.head(24).iterrows()):
        i, r = row
        col_atual = cols[idx % 4]
        with col_atual:
            st.markdown(f"""
                <div class="vinyl-card">
                    <b style="color: #ffffff; font-size: 16px;">{r['Album']}</b><br>
                    <span style="color: #a0a0a0; font-size: 14px;">{r['Artist']}</span><br>
                    <span style="color: #f59e0b; font-size: 12px;">📅 {r['Released']} | 🏷️ {r['List']}</span><br>
                    <hr style="border: 0.5px solid #333; margin: 8px 0;">
                    <span style="color: #1db954; font-size: 12px;">⭐ Capa: {r['Cover_Rating']}/5 | Aprov: {r['Liked_Tracks']}/{r['Total_Tracks']}</span>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("editar / ver detalhes", key=f"btn_{i}"):
                st.session_state.album_editando = i

    if 'album_editando' in st.session_state:
        st.markdown("---")
        st.subheader("✏️ detalhando e editando álbum selecionado")
        sel_idx = st.session_state.album_editando
        row_sel = df_albums.loc[sel_idx]
        
        c_ed1, c_ed2 = st.columns(2)
        with c_ed1:
            st.markdown(f"### {row_sel['Album']}")
            st.text(f"artista: {row_sel['Artist']}")
            st.text(f"ano: {row_sel['Released']}")
            st.text(f"lista de origem: {row_sel['List']}")
            
            # Exibe a capa oficial do álbum detalhado direto no seu site
            capa_detalhe = buscar_capa_album(row_sel['Artist'], row_sel['Album'])
            if capa_detalhe:
                st.image(capa_detalhe, caption=row_sel['Album'], width=300)
            
            query_spotify = urllib.parse.quote(f"{row_sel['Artist']} {row_sel['Album']}")
            st.markdown(f"🎧 [ouvir no Spotify](https://open.spotify.com/search/{query_spotify})", unsafe_allow_html=True)
            
        with c_ed2:
            nova_capa = st.slider("nota da capa (1 a 5)", 1, 5, int(row_sel['Cover_Rating']), key=f"c_ed_{sel_idx}")
            tot_f = st.number_input("total de músicas", 1, 30, int(row_sel['Total_Tracks']), key=f"t_ed_{sel_idx}")
            lik_f = st.number_input("músicas que gostou", 0, tot_f, int(row_sel['Liked_Tracks']), key=f"l_ed_{sel_idx}")
            fav_m = st.text_input("música favorita", value=str(row_sel['Favorite_Track']), key=f"f_ed_{sel_idx}")
            rev_m = st.text_area("suas anotações / resenha", value=str(row_sel['My_Review']), key=f"r_ed_{sel_idx}")
            
            nota_capa_conv = (nova_capa / 5.0) * 10.0
            prop_musicas = (lik_f / tot_f) if tot_f > 0 else 0
            nota_musicas_conv = prop_musicas * 10.0
            nota_final_calculada = (nota_musicas_conv * 0.70) + (nota_capa_conv * 0.30)
            
            st.info(f"🎯 **nota final calculada: {nota_final_calculada:.2f} / 10**")
            
            if st.button("salvar alterações no acervo", type="primary"):
                df_albums.loc[sel_idx, 'Cover_Rating'] = nova_capa
                df_albums.loc[sel_idx, 'Total_Tracks'] = tot_f
                df_albums.loc[sel_idx, 'Liked_Tracks'] = lik_f
                df_albums.loc[sel_idx, 'Favorite_Track'] = fav_m
                df_albums.loc[sel_idx, 'My_Review'] = rev_m
                df_albums.to_csv("albums.csv", index=False)
                st.success("salvo com sucesso!")
                del st.session_state.album_editando
                st.rerun()

elif aba == "álbum do dia":
    st.subheader("🎲 gerenciador diário & inserção manual")
    with st.form("form_manual"):
        st.markdown("### inserir novo disco manualmente")
        m_artista = st.text_input("artista / banda")
        m_album = st.text_input("nome do álbum")
        m_ano = st.number_input("ano de lançamento", min_value=1900, max_value=2026, value=1975)
        m_lista = st.text_input("coleção / lista de origem", value="manual")
        
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
                'Album': m_album,
                'Released': m_ano,
                'List': m_lista,
                'Cover_Rating': m_capa,
                'Total_Tracks': m_tot,
                'Liked_Tracks': m_lik,
                'Favorite_Track': m_fav,
                'My_Review': ''
            }])
            df_atualizado = pd.concat([df_albums, novo_registro], ignore_index=True)
            df_atualizado.to_csv("albums.csv", index=False)
            st.success(f"'{m_album}' adicionado com sucesso!")

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