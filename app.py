@st.cache_data
def load_data():
    if not os.path.exists("albums.csv"):
        st.error("⚠️ O arquivo 'albums.csv' não foi encontrado no GitHub. Envie a versão atualizada para a raiz do repositório.")
        return pd.DataFrame()
    
    # on_bad_lines='skip' evita que o app trave se encontrar alguma linha mal formatada
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