import os, streamlit as st, pandas as pd, numpy as np
import plotly.express as px, plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="MSF 직원 피해 현황 2015–2025",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Noto+Sans+KR:wght@300;400;500;700&family=JetBrains+Mono:wght@400;600&display=swap');

html,body,[class*="css"]{
  font-family:'Noto Sans KR',sans-serif;
  background:#080c14;
  color:#dde3ee;
}

/* ── 헤더 ── */
.hero {
  position:relative;
  background:linear-gradient(135deg,#0d0000 0%,#1a0505 40%,#0a0f1e 100%);
  border-left:6px solid #e63946;
  border-bottom:1px solid #1e293b;
  padding:36px 40px 28px;
  margin-bottom:28px;
  border-radius:0 12px 12px 0;
  overflow:hidden;
}
.hero::before {
  content:'';
  position:absolute;
  top:-60px;right:-60px;
  width:300px;height:300px;
  background:radial-gradient(circle,rgba(230,57,70,0.08),transparent 70%);
  pointer-events:none;
}
.hero-label {
  font-family:'JetBrains Mono',monospace;
  font-size:0.68rem;
  color:#e63946;
  letter-spacing:3px;
  text-transform:uppercase;
  margin-bottom:8px;
}
.hero h1 {
  font-family:'Syne',sans-serif;
  font-size:2.2rem;
  font-weight:800;
  color:#fff;
  margin:0 0 8px;
  line-height:1.15;
  letter-spacing:-0.5px;
}
.hero p {
  color:#8a9ab8;
  font-size:0.82rem;
  font-family:'JetBrains Mono',monospace;
  margin:0;
}

/* ── KPI ── */
.kpi-wrap {
  background:linear-gradient(135deg,#111827,#0d1117);
  border:1px solid #1e293b;
  border-top:3px solid #e63946;
  border-radius:10px;
  padding:20px 22px;
  text-align:center;
  position:relative;
  overflow:hidden;
}
.kpi-wrap::after {
  content:'';
  position:absolute;
  bottom:0;left:0;right:0;
  height:2px;
  background:linear-gradient(90deg,transparent,rgba(230,57,70,0.3),transparent);
}
.kpi-lbl {
  font-family:'JetBrains Mono',monospace;
  font-size:0.62rem;
  color:#64748b;
  letter-spacing:1.5px;
  text-transform:uppercase;
  margin-bottom:6px;
}
.kpi-val {
  font-family:'Syne',sans-serif;
  font-size:2rem;
  font-weight:800;
  color:#e63946;
  line-height:1;
  margin-bottom:4px;
}
.kpi-sub {
  font-size:0.7rem;
  color:#475569;
}
.kpi-delta {
  font-family:'JetBrains Mono',monospace;
  font-size:0.68rem;
  color:#f59e0b;
  margin-top:4px;
}

/* ── 섹션 타이틀 ── */
.sec-title {
  font-family:'Syne',sans-serif;
  font-size:1.05rem;
  font-weight:700;
  color:#e2e8f0;
  border-left:4px solid #e63946;
  padding-left:12px;
  margin:24px 0 14px;
  letter-spacing:-0.2px;
}

/* ── 사건 카드 ── */
.incident-card {
  background:linear-gradient(135deg,#111827,#0d1117);
  border:1px solid #1e293b;
  border-left:4px solid #e63946;
  border-radius:0 10px 10px 0;
  padding:16px 20px;
  margin-bottom:10px;
  transition:border-color 0.2s,transform 0.2s;
}
.incident-card:hover {
  border-left-color:#f87171;
  transform:translateX(4px);
}
.inc-date {
  font-family:'JetBrains Mono',monospace;
  font-size:0.68rem;
  color:#64748b;
  margin-bottom:4px;
}
.inc-name {
  font-size:0.95rem;
  font-weight:700;
  color:#e2e8f0;
  margin-bottom:2px;
}
.inc-role {
  font-size:0.72rem;
  color:#94a3b8;
  margin-bottom:6px;
}
.inc-detail {
  font-size:0.79rem;
  color:#8a9ab8;
  line-height:1.6;
}
.inc-type {
  display:inline-block;
  background:#1e1e2e;
  border:1px solid #334155;
  border-radius:4px;
  padding:2px 8px;
  font-size:0.65rem;
  font-family:'JetBrains Mono',monospace;
  color:#f87171;
  margin-bottom:8px;
}
.inc-country {
  display:inline-block;
  background:#1a2744;
  border:1px solid #2a3f6f;
  border-radius:4px;
  padding:2px 8px;
  font-size:0.65rem;
  color:#93c5fd;
  margin-left:6px;
  margin-bottom:8px;
}

/* ── 출처 ── */
.src-bar {
  font-size:0.65rem;
  color:#334155;
  font-family:'JetBrains Mono',monospace;
  line-height:1.9;
  padding-top:16px;
  border-top:1px solid #1e293b;
  margin-top:8px;
}

#MainMenu,footer,header{visibility:hidden;}
.block-container{padding-top:1rem;}
</style>
""", unsafe_allow_html=True)

# ── 데이터 로드 ───────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
BG, PBG = "#080c14", "#111827"
RED = "#e63946"

@st.cache_data
def load():
    y = pd.read_csv(os.path.join(BASE,"msf_staff_yearly_stats.csv"))
    c = pd.read_csv(os.path.join(BASE,"msf_staff_by_country.csv"))
    i = pd.read_csv(os.path.join(BASE,"msf_staff_incidents.csv"))
    h = pd.read_csv(os.path.join(BASE,"msf_health_facility_attacks.csv"))
    for col in ["killed","wounded","kidnapped","total"]:
        y[col] = pd.to_numeric(y[col], errors="coerce")
    for col in ["killed","wounded","kidnapped"]:
        c[col] = pd.to_numeric(c[col], errors="coerce")
    i["date"] = pd.to_datetime(i["date"], errors="coerce")
    return y, c, i, h

yearly, by_country, incidents, health = load()

# ── 헤더 ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-label">Aid Worker Security · MSF Staff Protection</div>
  <h1>🏥 MSF 직원 피해 현황<br>2015 – 2025</h1>
  <p>구호 현장의 공격·사망·납치 기록 | 출처: Aid Worker Security Database · WHO SSA · MSF Official</p>
</div>
""", unsafe_allow_html=True)

# ── KPI ───────────────────────────────────────────────────────────────────────
y_valid = yearly.dropna(subset=["total"])
total_killed    = int(yearly["killed"].sum())
total_wounded   = int(yearly["wounded"].sum(skipna=True))
total_kidnapped = int(yearly["kidnapped"].sum(skipna=True))
total_incidents = int(y_valid["total"].sum())
worst_year_row  = yearly.loc[yearly["killed"].idxmax()]
pct_gaza_2024   = round(181/383*100, 1)

k1,k2,k3,k4,k5,k6 = st.columns(6)
for col, lbl, val, sub, delta in [
    (k1,"10년 총 사망",    f"{total_killed:,}","명 (2015~2024)","↑ 2024년 역대 최고"),
    (k2,"10년 총 부상",    f"{total_wounded:,}","명",""),
    (k3,"10년 총 납치",    f"{total_kidnapped:,}","명",""),
    (k4,"10년 총 피해",    f"{total_incidents:,}","건 (사망+부상+납치)",""),
    (k5,"최악의 해",       str(int(worst_year_row['year'])),"사망자 최다","2024: 383명"),
    (k6,"가자지구 비중",   f"{pct_gaza_2024}%","2024 전체 사망 중","가자지구 181/383명"),
]:
    col.markdown(
        f'<div class="kpi-wrap"><div class="kpi-lbl">{lbl}</div>'
        f'<div class="kpi-val">{val}</div><div class="kpi-sub">{sub}</div>'
        f'<div class="kpi-delta">{delta}</div></div>',
        unsafe_allow_html=True)

st.markdown("")

# ── 탭 ───────────────────────────────────────────────────────────────────────
t1,t2,t3,t4,t5 = st.tabs([
    "📈 연도별 추이", "🗺️ 국가별 현황", "🕯️ 사건 기록", "🏥 의료시설 공격", "📄 원시 데이터"])

LO = dict(
    template="plotly_dark",
    paper_bgcolor=BG,
    plot_bgcolor=PBG,
    margin=dict(l=10,r=10,t=30,b=10),
    font=dict(family="Noto Sans KR, sans-serif", size=11, color="#94a3b8"),
    xaxis=dict(gridcolor="#1e293b", zeroline=False),
    yaxis=dict(gridcolor="#1e293b", zeroline=False),
)

# ════════ TAB 1: 연도별 추이 ══════════════════════════════════════════════════
with t1:
    st.markdown('<div class="sec-title">연도별 인도주의 구호원 피해 추이 (2015–2025)</div>', unsafe_allow_html=True)

    # 스택 영역 차트
    y_melt = yearly.melt(id_vars="year", value_vars=["killed","wounded","kidnapped"],
                         var_name="유형", value_name="인원")
    y_melt["유형"] = y_melt["유형"].map({"killed":"사망","wounded":"부상","kidnapped":"납치"})
    y_melt = y_melt.dropna()
    fig1 = px.area(y_melt, x="year", y="인원", color="유형",
        color_discrete_map={"사망":RED,"부상":"#f59e0b","납치":"#457b9d"},
        labels={"year":"연도","인원":"피해자 수","유형":"유형"})
    fig1.update_layout(height=380,
        legend=dict(orientation="h", y=1.05, x=0),
        title=dict(text="연도별 사망·부상·납치 누적 추이", font=dict(size=13, color="#e2e8f0"), x=0))
    fig1.update_traces(hovertemplate="%{x}년 %{fullData.name}: %{y:,}명<extra></extra>")
    st.plotly_chart(fig1, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-title">연도별 사망자 수 (막대)</div>', unsafe_allow_html=True)
        y_bar = yearly.dropna(subset=["killed"])
        colors_bar = [RED if yr == 2024 else "#7f1d1d" for yr in y_bar["year"]]
        fig2 = go.Figure(go.Bar(
            x=y_bar["year"], y=y_bar["killed"],
            marker_color=colors_bar,
            text=y_bar["killed"], textposition="outside",
            hovertemplate="%{x}년<br>사망: %{y}명<extra></extra>"))
        fig2.update_layout(height=320,
            title=dict(text="연도별 사망자 수 (2024 역대 최고)", font=dict(size=12,color="#e2e8f0"),x=0),
            xaxis=dict(tickvals=list(y_bar["year"]), gridcolor="#1e293b"),
            yaxis=dict(title="명", gridcolor="#1e293b"))
        fig2.add_annotation(x=2024, y=383, text="🔴 역대 최고<br>383명", showarrow=True,
            arrowhead=2, arrowcolor=RED, font=dict(color=RED, size=10),
            ax=40, ay=-40)
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-title">전년 대비 사망자 증감률</div>', unsafe_allow_html=True)
        y_pct = yearly.dropna(subset=["killed"]).copy()
        y_pct["증감률"] = y_pct["killed"].pct_change() * 100
        y_pct = y_pct.dropna(subset=["증감률"])
        bar_clr = [RED if v > 0 else "#22c55e" for v in y_pct["증감률"]]
        fig3 = go.Figure(go.Bar(
            x=y_pct["year"], y=y_pct["증감률"].round(1),
            marker_color=bar_clr,
            text=y_pct["증감률"].round(1).astype(str) + "%",
            textposition="outside",
            hovertemplate="%{x}년<br>전년比 %{y:.1f}%<extra></extra>"))
        fig3.update_layout(height=320,
            title=dict(text="전년 대비 사망자 증감률 (%)", font=dict(size=12,color="#e2e8f0"),x=0),
            xaxis=dict(tickvals=list(y_pct["year"]), gridcolor="#1e293b"),
            yaxis=dict(title="%", gridcolor="#1e293b"))
        fig3.add_hline(y=0, line_dash="dot", line_color="#334155")
        st.plotly_chart(fig3, use_container_width=True)

    # 사망·부상·납치 3분할 서브플롯
    st.markdown('<div class="sec-title">유형별 10년 추이 비교</div>', unsafe_allow_html=True)
    fig4 = make_subplots(rows=1, cols=3,
        subplot_titles=["사망자 수","부상자 수","납치 건수"],
        shared_yaxes=False)
    for idx, (col_name, color, row, col) in enumerate([
        ("killed", RED, 1, 1),
        ("wounded", "#f59e0b", 1, 2),
        ("kidnapped", "#457b9d", 1, 3),
    ]):
        df_sub = yearly.dropna(subset=[col_name])
        fig4.add_trace(go.Scatter(
            x=df_sub["year"], y=df_sub[col_name],
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=6, color=color),
            fill="tozeroy", fillcolor=color.replace("#","rgba(").replace(")", ",0.08)") if "#" in color else color,
            hovertemplate=f"%{{x}}년: %{{y:,}}명<extra></extra>",
            showlegend=False), row=row, col=col)
    fig4.update_layout(
        template="plotly_dark", paper_bgcolor=BG, plot_bgcolor=PBG,
        height=280, margin=dict(l=10,r=10,t=40,b=10),
        font=dict(family="Noto Sans KR", size=10, color="#94a3b8"))
    for i in fig4['layout']['annotations']:
        i['font'] = dict(size=11, color="#94a3b8")
    st.plotly_chart(fig4, use_container_width=True)

# ════════ TAB 2: 국가별 현황 ══════════════════════════════════════════════════
with t2:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-title">2024년 국가별 사망자</div>', unsafe_allow_html=True)
        df24 = by_country[by_country["year"]==2024].sort_values("killed")
        fig5 = px.bar(df24, x="killed", y="country_kr", orientation="h",
            color="killed", color_continuous_scale=[[0,"#3b0f14"],[1,RED]],
            labels={"killed":"사망자 수","country_kr":"국가"},
            text="killed")
        fig5.update_layout(height=300, coloraxis_showscale=False,
            title=dict(text="2024년 사망자 상위국", font=dict(size=12,color="#e2e8f0"),x=0))
        fig5.update_traces(
            textposition="outside",
            hovertemplate="%{y}<br>사망: %{x}명<extra></extra>")
        st.plotly_chart(fig5, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-title">2023년 국가별 사망자</div>', unsafe_allow_html=True)
        df23 = by_country[by_country["year"]==2023].sort_values("killed")
        fig6 = px.bar(df23, x="killed", y="country_kr", orientation="h",
            color="killed", color_continuous_scale=[[0,"#1a1a3e"],[1,"#7c3aed"]],
            labels={"killed":"사망자 수","country_kr":"국가"},
            text="killed")
        fig6.update_layout(height=300, coloraxis_showscale=False,
            title=dict(text="2023년 사망자 상위국", font=dict(size=12,color="#e2e8f0"),x=0))
        fig6.update_traces(
            textposition="outside",
            hovertemplate="%{y}<br>사망: %{x}명<extra></extra>")
        st.plotly_chart(fig6, use_container_width=True)

    # 2023 vs 2024 나란히 비교
    st.markdown('<div class="sec-title">2023 vs 2024 국가별 사망자 비교</div>', unsafe_allow_html=True)
    all_countries = by_country["country_kr"].unique()
    compare_rows = []
    for ctry in all_countries:
        for yr in [2023, 2024]:
            row = by_country[(by_country["country_kr"]==ctry)&(by_country["year"]==yr)]
            compare_rows.append({
                "국가": ctry,
                "연도": str(yr),
                "사망자": int(row["killed"].values[0]) if len(row) else 0
            })
    df_cmp = pd.DataFrame(compare_rows)
    fig7 = px.bar(df_cmp, x="국가", y="사망자", color="연도", barmode="group",
        color_discrete_map={"2023":"#7c3aed","2024":RED},
        text="사망자")
    fig7.update_layout(height=340,
        legend=dict(orientation="h", y=1.08),
        title=dict(text="국가별 2023→2024 피해 변화", font=dict(size=12,color="#e2e8f0"),x=0))
    fig7.update_traces(
        textposition="outside",
        hovertemplate="%{x} %{fullData.name}년<br>사망: %{y}명<extra></extra>")
    st.plotly_chart(fig7, use_container_width=True)

    # 컨텍스트별 파이
    st.markdown('<div class="sec-title">분쟁 유형별 피해 비중 (2023–2024 합산)</div>', unsafe_allow_html=True)
    ctx = by_country.groupby("context")["killed"].sum().reset_index()
    ctx.columns = ["분쟁 유형","사망자 합계"]
    fig8 = px.pie(ctx, names="분쟁 유형", values="사망자 합계", hole=0.5,
        color_discrete_sequence=[RED,"#457b9d","#f59e0b"])
    fig8.update_layout(template="plotly_dark", paper_bgcolor=BG,
        height=300, margin=dict(l=10,r=10,t=10,b=10),
        legend=dict(orientation="h", y=-0.1))
    fig8.update_traces(
        textinfo="percent+label",
        hovertemplate="%{label}<br>사망: %{value}명<extra></extra>")
    st.plotly_chart(fig8, use_container_width=True)

# ════════ TAB 3: 사건 기록 ════════════════════════════════════════════════════
with t3:
    st.markdown('<div class="sec-title">🕯️ 확인된 주요 사건 기록 (MSF 공식 출처)</div>', unsafe_allow_html=True)

    # 필터
    fc1, fc2 = st.columns(2)
    with fc1:
        sel_country = st.multiselect(
            "국가 필터",
            options=sorted(incidents["country_kr"].unique()),
            default=sorted(incidents["country_kr"].unique()))
    with fc2:
        sel_type = st.multiselect(
            "사건 유형 필터",
            options=sorted(incidents["incident_type"].unique()),
            default=sorted(incidents["incident_type"].unique()))

    filtered = incidents[
        incidents["country_kr"].isin(sel_country) &
        incidents["incident_type"].isin(sel_type)
    ].sort_values("date", ascending=False)

    st.markdown(f"<p style='font-size:0.78rem;color:#64748b;margin-bottom:16px;'>총 {len(filtered)}건 표시 중</p>", unsafe_allow_html=True)

    for _, row in filtered.iterrows():
        date_str = row["date"].strftime("%Y년 %m월 %d일") if pd.notna(row["date"]) else "날짜 미상"
        src_link = f'<a href="{row["source_url"]}" target="_blank" style="color:#475569;text-decoration:none;">📎 {row["source"]}</a>'
        st.markdown(f"""
        <div class="incident-card">
          <div class="inc-date">{date_str}</div>
          <span class="inc-type">{row['incident_type']}</span>
          <span class="inc-country">{row['country_kr']}</span>
          <div class="inc-name">{row['name']}</div>
          <div class="inc-role">{row['role']}</div>
          <div class="inc-detail">{row['details']}</div>
          <div style="margin-top:8px;font-size:0.65rem;">{src_link}</div>
        </div>""", unsafe_allow_html=True)

    # 사건 유형별 도넛
    st.markdown('<div class="sec-title">사건 유형 분포</div>', unsafe_allow_html=True)
    type_cnt = incidents["incident_type"].value_counts().reset_index()
    type_cnt.columns = ["유형","건수"]
    fig_inc = px.pie(type_cnt, names="유형", values="건수", hole=0.5,
        color_discrete_sequence=[RED,"#f59e0b","#457b9d","#7c3aed","#22c55e"])
    fig_inc.update_layout(template="plotly_dark", paper_bgcolor=BG,
        height=300, margin=dict(l=10,r=10,t=10,b=10),
        legend=dict(orientation="h", y=-0.15, font=dict(size=10)))
    fig_inc.update_traces(textinfo="percent+label",
        hovertemplate="%{label}<br>%{value}건<extra></extra>")
    st.plotly_chart(fig_inc, use_container_width=True)

# ════════ TAB 4: 의료시설 공격 ═══════════════════════════════════════════════
with t4:
    st.markdown('<div class="sec-title">의료시설·구호 활동 공격 통계 (WHO SSA)</div>', unsafe_allow_html=True)

    hc1, hc2 = st.columns(2)
    with hc1:
        fig_h1 = go.Figure(go.Bar(
            x=health["year"].astype(str),
            y=health["total_attacks"],
            marker_color=[RED,"#f59e0b"],
            text=health["total_attacks"],
            textposition="outside",
            hovertemplate="%{x}년<br>공격 건수: %{y:,}건<extra></extra>"))
        fig_h1.update_layout(height=300,
            title=dict(text="연도별 의료시설 공격 건수", font=dict(size=12,color="#e2e8f0"),x=0),
            yaxis=dict(title="건수", gridcolor="#1e293b"))
        st.plotly_chart(fig_h1, use_container_width=True)

    with hc2:
        fig_h2 = go.Figure(go.Bar(
            x=health["year"].astype(str),
            y=health["deaths_from_attacks"],
            marker_color=["#7f1d1d","#991b1b"],
            text=health["deaths_from_attacks"],
            textposition="outside",
            hovertemplate="%{x}년<br>공격 관련 사망: %{y:,}명<extra></extra>"))
        fig_h2.update_layout(height=300,
            title=dict(text="공격 관련 사망자 수", font=dict(size=12,color="#e2e8f0"),x=0),
            yaxis=dict(title="명", gridcolor="#1e293b"))
        st.plotly_chart(fig_h2, use_container_width=True)

    # 맥락 설명 카드
    for yr, attacks, deaths, top in zip(
        health["year"], health["total_attacks"],
        health["deaths_from_attacks"], health["top_country"]):
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#111827,#0d1117);
          border:1px solid #1e293b;border-left:4px solid #f59e0b;
          border-radius:0 10px 10px 0;padding:18px 22px;margin-bottom:12px;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
            color:#f59e0b;letter-spacing:2px;margin-bottom:6px;">{yr}년</div>
          <div style="display:flex;gap:32px;flex-wrap:wrap;">
            <div><span style="font-size:1.6rem;font-family:'Syne',sans-serif;
              font-weight:800;color:#e63946;">{attacks:,}</span>
              <span style="font-size:0.75rem;color:#64748b;margin-left:6px;">건의 의료시설 공격</span></div>
            <div><span style="font-size:1.6rem;font-family:'Syne',sans-serif;
              font-weight:800;color:#f87171;">{deaths:,}</span>
              <span style="font-size:0.75rem;color:#64748b;margin-left:6px;">명 사망</span></div>
            <div><span style="font-size:0.75rem;color:#64748b;">최다 피해국: </span>
              <span style="font-size:0.85rem;font-weight:700;color:#e2e8f0;">{top}</span></div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#0d1117;border:1px solid #1e293b;border-radius:8px;
      padding:16px 20px;margin-top:8px;">
      <div style="font-size:0.8rem;color:#94a3b8;line-height:1.8;">
        ⚠️ <b style="color:#e2e8f0;">국제인도법(IHL) 위반:</b>
        의료시설·구호 차량·직원에 대한 의도적 공격은 제네바협약 및 로마규정상 전쟁범죄에 해당합니다.<br>
        📋 <b style="color:#e2e8f0;">UN 안보리 결의 2286(2016):</b>
        의료시설 공격 규탄 및 책임 추궁 촉구. MSF 쿤두즈 병원 폭격(2015) 이후 채택.
      </div>
    </div>""", unsafe_allow_html=True)

# ════════ TAB 5: 원시 데이터 ══════════════════════════════════════════════════
with t5:
    st.markdown('<div class="sec-title">📄 연도별 피해 통계</div>', unsafe_allow_html=True)
    st.dataframe(yearly.style.format(
        {"killed":"{:,.0f}","wounded":"{:,.0f}","kidnapped":"{:,.0f}","total":"{:,.0f}"},
        na_rep="—"), use_container_width=True, height=320)

    st.markdown('<div class="sec-title">📄 국가별 피해 현황</div>', unsafe_allow_html=True)
    st.dataframe(by_country.style.format(
        {"killed":"{:,.0f}","wounded":"{:,.0f}","kidnapped":"{:,.0f}"},
        na_rep="—"), use_container_width=True, height=300)

    st.markdown('<div class="sec-title">📄 주요 사건 기록</div>', unsafe_allow_html=True)
    st.dataframe(incidents[["date","country_kr","name","role","incident_type","details","source"]],
        use_container_width=True, height=300)

    st.markdown('<div class="sec-title">📄 의료시설 공격 통계</div>', unsafe_allow_html=True)
    st.dataframe(health, use_container_width=True, height=120)

# ── 하단 출처 ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div class="src-bar">
📎 Aid Worker Security Database (AWSD) 2025 &nbsp;|&nbsp;
WHO Surveillance System for Attacks on Healthcare (SSA) &nbsp;|&nbsp;
MSF Year in Review 2024 &nbsp;|&nbsp;
MSF Remembering Our Colleagues Killed in Gaza (msf.org) &nbsp;|&nbsp;
Doctors Without Borders USA (doctorswithoutborders.org) &nbsp;|&nbsp;
Wikipedia — Attacks on Humanitarian Workers &nbsp;|&nbsp;
MSF UK Annual Report 2025
</div>""", unsafe_allow_html=True)
