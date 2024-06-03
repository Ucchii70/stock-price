import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title('米国株可視化アプリ')

st.sidebar.write("""
こちらは株価可視化ツールです。以下のオプションから表示日時を指定できます。
""")

st.sidebar.write("""
## 表示日数選択
""")
days = st.sidebar.slider('日数を指定してください。', 1, 365, 20)

st.write(f"""
### 過去 **{days}日間** の各社株価
""")

#2回目以降実行時キャッシュをクリアーすることで動作が軽くなる
@st.cache_data
def get_data(days,tickers):
    
    df = pd.DataFrame()
    
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])

        hist = tkr.history(period=f'{days}d')

        hist.index = hist.index.strftime('%d %B %Y')   

        hist = hist[['Close']]
        hist.columns = [company]

        hist = hist.T

        hist.index.name = 'Name'
        df = pd.concat([df,hist])
    return df
try:
    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    ymin, ymax = st.sidebar.slider(
        '範囲を指定してください。',
        0.0, 1500.0, (0.0, 1500.0)
    )

    tickers = {
        'Apple': 'AAPL',
        'Tesla': 'TSLA',
        'NVIDIA': 'NVDA',
        'Meta':  'Meta',
        'Alphabet': 'GOOG',
        'Microsoft': 'MSFT',
        'Netflix': 'NFLX',
        'Amazon': 'AMZN'
    }
    df = get_data(days,tickers)
    companies = st.multiselect(
        '会社名を選択してください。',
        list(df.index),
        ['Amazon', 'Tesla','Apple', 'NVIDIA', 'Meta', 'Alphabet', 'Microsoft', 'Netflix']
    )

    #companiesに何も入っていなかったらエラーを返す
    if not companies:
        st.error('少なくとも一社は選んで下さい。')
    else:
        data = df.loc[companies]
        st.write('### 株価（USD）',data.sort_index())
        data = data.T.reset_index()
        data = pd.melt(data,id_vars=['Date']).rename(
            columns = {'value': 'Stock Prices(USD)'}
        )

        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin,ymax])),
                color='Name:N'
            )
        )
        #streamlitに表示させるために記述、use_container_widthでグラフの枠に収まるように調整
        st.altair_chart(chart,use_container_width=True)

except:
    st.error(
        'エラーが発生しました。再更新してください。'
    )





