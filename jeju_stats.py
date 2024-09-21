import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(layout="wide", page_title="제주도 농지통계")

# CSS를 사용하여 기본 패딩 제거
st.markdown("""
    <style>
        .reportview-container .main .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
        .reportview-container .main {
            color: #333;
            background-color: white;
        }
        h1 {
            padding-top: 0rem;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

# 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_excel('landstats_1.xlsx', header=0, skiprows=[0])
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = ['지역', '(전)필지수', '(전)면적(ha)', '(답)필지수', '(답)면적', '(과)필지수', '(과)면적', '총 필지수', '총 면적']
    df = df.set_index('지역')
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

df = load_data()

# 제목
st.title('2023년 제주도 농지통계(토지대장 기준)')

# 데이터 출력
# st.subheader('원본 데이터')
st.dataframe(df)


# 전/답/과 면적 비교 (그룹 막대 그래프)
# st.subheader('지역별 전/답/과 면적 비교')
fig_group_area = go.Figure(data=[
    go.Bar(name='전', x=df.index, y=df['(전)면적(ha)']),
    go.Bar(name='답', x=df.index, y=df['(답)면적']),
    go.Bar(name='과', x=df.index, y=df['(과)면적'])
])
fig_group_area.update_layout(barmode='group', title='제주도 지역별 전/답/과 면적(ha)')
st.plotly_chart(fig_group_area, use_container_width=True)


# 전/답/과 필지수 비교 (그룹 막대 그래프)
# st.subheader('지역별 전/답/과 필지수 비교')
fig_group = go.Figure(data=[
    go.Bar(name='전', x=df.index, y=df['(전)필지수']),
    go.Bar(name='답', x=df.index, y=df['(답)필지수']),
    go.Bar(name='과', x=df.index, y=df['(과)필지수'])
])
fig_group.update_layout(barmode='group', title='제주도 지역별 전/답/과 필지수(건)')
st.plotly_chart(fig_group, use_container_width=True)


# # 지역별 비교 (면적과 건수를 따로 표시)
# st.subheader('제주도 전/답/과 필지수 & 면적')

# # 도시 선택
# regions = st.multiselect('도시 선택:', df.index.tolist(), default=df.index.tolist())
# comparison_df = df.loc[regions]

# # 면적 그래프
# # st.subheader('선택된 지역의 전/답/과 면적')
# fig_area = px.bar(comparison_df, x=comparison_df.index, y=['(전)면적(ha)', '(답)면적', '(과)면적'],
#                   title='선택된 지역의 전/답/과 면적(ha)',
#                   labels={'value': '면적 (ha)', 'variable': '구분'},
#                   barmode='group')
# st.plotly_chart(fig_area, use_container_width=True)

# # 필지수(건수) 그래프
# # st.subheader('선택된 지역의 전/답/과 필지수(건)')
# fig_count = px.bar(comparison_df, x=comparison_df.index, y=['(전)필지수', '(답)필지수', '(과)필지수'],
#                    title='선택된 지역의 전/답/과 필지수(건)',
#                    labels={'value': '필지수 (건)', 'variable': '구분'},
#                    barmode='group')
# st.plotly_chart(fig_count, use_container_width=True)


# Load data
@st.cache_data
def load_data():
    jeju_data = pd.read_excel('landstats_2_jeju.xlsx', header=1)
    seoguipo_data = pd.read_excel('landstats_3_seoguiposi.xlsx', header=1)
    
    # Extract only the 'dong' name from the '지역' column
    jeju_data['동'] = jeju_data['지역'].str.split().str[-1]
    seoguipo_data['동'] = seoguipo_data['지역'].str.split().str[-1]
    
    return jeju_data, seoguipo_data

jeju_data, seoguipo_data = load_data()

# Streamlit app
st.title('2023년 제주도 읍면동 별 전/답/과 통계')

# Select city
city = st.selectbox('도시를 선택하세요:', ['제주시', '서귀포시'])

if city == '제주시':
    data = jeju_data
else:
    data = seoguipo_data

# Select land type and statistic type
land_type = st.selectbox('토지 유형(전/답/과)을 선택하세요:', ['전', '답', '과'])
stat_type = st.selectbox('통계 유형(필지수/면적)을 선택하세요:', ['필지수', '면적'])

# Combine selections to get the column name
selected_stat = f'({land_type}){stat_type}'

# Create bar chart
fig = px.bar(data, x='동', y=selected_stat, title=f'{city} {land_type} {stat_type} 통계')
fig.update_xaxes(title_text='동')
st.plotly_chart(fig)

# Show data table
if st.checkbox('원본 데이터 보기'):
    st.write(data)

# Add some insights
st.subheader('통계 요약')
st.write(f'선택된 통계 ({selected_stat})의 평균: {data[selected_stat].mean():.2f}')
st.write(f'선택된 통계 ({selected_stat})의 최대값: {data[selected_stat].max():.2f}')
st.write(f'선택된 통계 ({selected_stat})의 최소값: {data[selected_stat].min():.2f}')

# Allow users to download the data
csv = data.to_csv(index=False)
st.download_button(
    label="CSV로 데이터 다운로드",
    data=csv,
    file_name=f"{city}_land_stats.csv",
    mime="text/csv",
)