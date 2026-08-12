import streamlit as st
import pandas as pd
import plotly.express as px

# ページ基本設定
st.set_page_config(
    page_title="HR Analytics - 離職要因分析ダッシュボード",
    layout="wide"
)

st.title("📊 HR Analytics: 離職要因分析ダッシュボード")
st.caption("IBM HR Analytics データセットを活用したプロトタイプ")

# データ読み込み
@st.cache_data
def load_data():
    df = pd.read_csv("WA_Fn-UseC_-HR-Employee-Attrition.csv")
    df['Attrition_Flag'] = df['Attrition'].apply(lambda x: 1 if x == 'Yes' else 0)
    return df

try:
    df = load_data()
except Exception as e:
    st.error("データファイル 'WA_Fn-UseC_-HR-Employee-Attrition.csv' が読み込めませんでした。同階層に配置されているか確認してください。")
    st.stop()

# サイドバーフィルター
st.sidebar.header("🔍 フィルター設定")
selected_dept = st.sidebar.multiselect(
    "部門 (Department)",
    options=df["Department"].unique(),
    default=df["Department"].unique()
)
selected_overtime = st.sidebar.multiselect(
    "残業の有無 (OverTime)",
    options=df["OverTime"].unique(),
    default=df["OverTime"].unique()
)

filtered_df = df[
    (df["Department"].isin(selected_dept)) &
    (df["OverTime"].isin(selected_overtime))
]

# メイン表示（タブ分け）
tab1, tab2 = st.tabs(["📈 全社離職サマリー", "🔍 離職要因ディープダイブ"])

with tab1:
    total_emp = len(filtered_df)
    attrition_cnt = filtered_df['Attrition_Flag'].sum()
    attrition_rate = (attrition_cnt / total_emp * 100) if total_emp > 0 else 0
    avg_income = filtered_df['MonthlyIncome'].mean() if total_emp > 0 else 0
    avg_years = filtered_df['YearsAtCompany'].mean() if total_emp > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("総従業員数", f"{total_emp:,} 人")
    col2.metric("離職者数", f"{attrition_cnt:,} 人")
    col3.metric("離職率", f"{attrition_rate:.1f} %")
    col4.metric("平均月収", f"${avg_income:,.0f}")
    col5.metric("平均勤続年数", f"{avg_years:.1f} 年")

    st.markdown("---")
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("職種別 離職率")
        role_summary = filtered_df.groupby("JobRole")["Attrition_Flag"].agg(['count', 'mean']).reset_index()
        role_summary['離職率(%)'] = role_summary['mean'] * 100
        fig_role = px.bar(
            role_summary.sort_values(by="離職率(%)", ascending=True),
            x="離職率(%)", y="JobRole", orientation='h',
            text_auto='.1f', color="離職率(%)", color_continuous_scale="Reds"
        )
        st.plotly_chart(fig_role, use_container_width=True)

    with col_g2:
        st.subheader("残業有無による離職率比較")
        ot_summary = filtered_df.groupby("OverTime")["Attrition_Flag"].agg(['count', 'mean']).reset_index()
        ot_summary['離職率(%)'] = ot_summary['mean'] * 100
        fig_ot = px.bar(
            ot_summary, x="OverTime", y="離職率(%)",
            color="OverTime", text_auto='.1f',
            color_discrete_map={'Yes': '#EF553B', 'No': '#636EFA'}
        )
        st.plotly_chart(fig_ot, use_container_width=True)

with tab2:
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.subheader("仕事満足度と離職率")
        sat_summary = filtered_df.groupby("JobSatisfaction")["Attrition_Flag"].mean().reset_index()
        sat_summary["離職率(%)"] = sat_summary["Attrition_Flag"] * 100
        fig_sat = px.bar(
            sat_summary, x="JobSatisfaction", y="離職率(%)",
            labels={"JobSatisfaction": "仕事の満足度 (1:低い ~ 4:高い)"},
            text_auto='.1f'
        )
        st.plotly_chart(fig_sat, use_container_width=True)

    with col_d2:
        st.subheader("離職の有無と月収分布")
        fig_inc = px.box(
            filtered_df, x="Attrition", y="MonthlyIncome",
            color="Attrition",
            labels={"Attrition": "離職有無", "MonthlyIncome": "月収($)"}
        )
        st.plotly_chart(fig_inc, use_container_width=True)
