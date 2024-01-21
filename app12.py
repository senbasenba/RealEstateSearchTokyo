import streamlit as st
import pandas as pd
import sqlite3
import base64
import pydeck as pdk  # pydeckをマップ表示用に使用します

# 'backimage.jpg'があなたのStreamlitアプリと同じディレクトリにあると仮定します
BG_IMAGE_PATH = 'backimage.jpg'

# SQLite3データベースに接続します
conn = sqlite3.connect('sumodb8.db')

@st.cache_data()
def load_data():
    query = "SELECT * FROM sumodb8_table"
    try:
        data = pd.read_sql(query, conn)
        return data
    except sqlite3.DatabaseError as e:
        st.error(f"データベースエラー: {e}")
        return None

# 背景画像とグレーの背景色を設定する関数です
def add_bg_and_set_bg_color(bg_image_path):
    with open(bg_image_path, "rb") as file:
        bg_base64 = base64.b64encode(file.read()).decode('utf-8')
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bg_base64}");
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            background-color: #AAAAAA;  # グレー色の背景を設定
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# 与えられたデータ用にpydeckマップを生成する関数です
def generate_map(data, lat_col='latitude', lon_col='longitude'):
    if data.empty:
        # データがない場合、デフォルトビューを返します
        return pdk.Deck()
    
    view_state = pdk.ViewState(
        latitude=data[lat_col].mean(),
        longitude=data[lon_col].mean(),
        zoom=11,
        pitch=0
    )

    layer = pdk.Layer(
        'ScatterplotLayer',
        data=data,
        get_position=[lon_col, lat_col],
        get_color='[200, 30, 0, 160]',
        get_radius=200,  # ポイントのサイズを調整する場合はここを変更
        pickable=True,  # ポイントが選択可能かどうか
    )
    
    return pdk.Deck(layers=[layer], initial_view_state=view_state, map_style="mapbox://styles/mapbox/dark-v10")

def main():
    add_bg_and_set_bg_color(BG_IMAGE_PATH)
    st.sidebar.title("Real Estate Search Tokyo")
    data = load_data()
    # 本サイトの説明テキストを配置
    st.sidebar.text("ハイクラスペア向け賃貸情報サイトです")
    st.sidebar.text("物件は中央区、新宿区、渋谷区、千代田区にの絞られております。")

    if data is not None:
        selected_areas = st.sidebar.multiselect("ご希望のエリア", data['Area'].unique())
        budget_range = st.sidebar.slider('ご予算（万）', 15, 30, (17, 30))
        submit_button = st.sidebar.button('検索', key='search')

        if submit_button:
            if selected_areas:
                data = data[data['Area'].isin(selected_areas)]
            data = data[(data['cost'] >= budget_range[0]) & (data['cost'] <= budget_range[1])]

            st.write(f"絞り込んだ結果の数: {len(data)}")  # 絞り込んだ結果の数を表示します

            if not data.empty:
                # データセット内の実際の緯度と経度の列名に置き換えてください
                st.pydeck_chart(generate_map(data, lat_col='lat', lon_col='lon'))
                st.dataframe(data)  # 絞り込んだデータをデータフレームで表示します
            else:
                st.write("該当する物件が見つかりませんでした。")

if __name__ == '__main__':
    main()
