import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")

if not BACKEND_URL:
    st.error("BACKEND_URL is not set in environment variables.")
    st.stop()


@st.cache_resource
def _http_session():
    import requests
    s = requests.Session()
    return s


st.set_page_config(
    page_title="Vendor Decision Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(79, 70, 229, 0.2);
    }

    .main-header h1 {
        color: white;
        font-size: 2.25rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
    }

    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
    }

    .metric-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    .metric-card:hover {
        border-color: #c7d2fe;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.1);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4f46e5;
    }

    .metric-label {
        color: #6b7280;
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .insight-card {
        background: #eff6ff;
        border-left: 4px solid #3b82f6;
        border-radius: 0 10px 10px 0;
        padding: 1.25rem 1.5rem;
        margin: 0.75rem 0;
    }

    .assumption-card {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        border-radius: 0 10px 10px 0;
        padding: 1.25rem 1.5rem;
        margin: 0.75rem 0;
    }

    .risk-card {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        border-radius: 0 10px 10px 0;
        padding: 1.25rem 1.5rem;
        margin: 0.75rem 0;
    }

    .gap-card {
        background: #faf5ff;
        border-left: 4px solid #a855f7;
        border-radius: 0 10px 10px 0;
        padding: 1.25rem 1.5rem;
        margin: 0.75rem 0;
    }

    .tradeoff-card {
        background: #ecfdf5;
        border-left: 4px solid #10b981;
        border-radius: 0 10px 10px 0;
        padding: 1.25rem 1.5rem;
        margin: 0.75rem 0;
    }

    .card-text {
        color: #1f2937;
        font-size: 0.95rem;
        line-height: 1.6;
        margin: 0;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #f3f4f6;
        padding: 6px;
        border-radius: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 18px;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background: #4f46e5 !important;
        color: white !important;
    }

    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: #4f46e5;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #4338ca;
    }

    section[data-testid="stSidebar"] .stButton > button:disabled {
        background: #d1d5db;
        color: #9ca3af;
    }

    [data-testid="stFileUploader"] {
        background: #f5f3ff;
        border: 2px dashed #c4b5fd;
        border-radius: 12px;
        padding: 1rem;
    }

    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e5e7eb;
    }

    .section-header h2 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 600;
        color: #111827;
    }

    .section-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
    }

    .stChatMessage {
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }

    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    .analyzing-text {
        animation: pulse 2s ease-in-out infinite;
        color: #4f46e5;
        font-weight: 600;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ──
st.session_state.setdefault("analysis", None)
st.session_state.setdefault("messages", [])
st.session_state.setdefault("analysis_in_flight", False)
st.session_state.setdefault("chat_in_flight", False)

# ── Header ──
st.markdown("""
<div class="main-header">
    <h1>🎯 Vendor Decision Intelligence</h1>
    <p>Surface facts, assumptions, risks, and trade-offs — without recommendations</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("### 📁 Upload Documents")
    
    files = st.file_uploader(
        "Drop your vendor files here",
        type=["csv", "xlsx", "pdf"],
        accept_multiple_files=True,
        help="Supported: CSV, Excel, PDF"
    )
    
    if files:
        st.markdown(f"**{len(files)} file(s) selected**")
        for f in files:
            size_kb = len(f.getvalue()) / 1024
            icon = "📊" if f.name.endswith(('.csv', '.xlsx')) else "📄"
            st.markdown(f"{icon} `{f.name}` ({size_kb:.1f} KB)")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        analyze_clicked = st.button(
            "🚀 Analyze",
            disabled=st.session_state.analysis_in_flight or not files,
            use_container_width=True
        )
    with col2:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.analysis = None
            st.session_state.messages = []
            st.session_state.analysis_in_flight = False
            st.session_state.chat_in_flight = False
            st.rerun()

    if analyze_clicked:
        st.session_state.analysis_in_flight = True
        
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        try:
            progress_placeholder.progress(0, "Preparing files...")
            
            payload = []
            for i, f in enumerate(files):
                f.seek(0)
                payload.append(("files", (f.name, f.read(), f.type)))
                progress_placeholder.progress(
                    int((i + 1) / len(files) * 30),
                    f"Reading {f.name}..."
                )
            
            progress_placeholder.progress(35, "Sending to backend...")
            status_placeholder.markdown(
                '<p class="analyzing-text">🔍 Analyzing documents...</p>',
                unsafe_allow_html=True
            )
            
            r = _http_session().post(
                f"{BACKEND_URL}/analyze",
                files=payload,
                timeout=120
            )
            
            progress_placeholder.progress(90, "Processing results...")
            
            if r.status_code == 200:
                st.session_state.analysis = r.json()
                st.session_state.messages = [{
                    "role": "assistant",
                    "content": (
                        "Hey! Your documents have been analyzed successfully. "
                        "I'm ready to help you explore the vendor data — "
                        "feel free to ask me about risks, pricing, trade-offs, "
                        "or anything else you'd like to dig into!"
                    )
                }]
                progress_placeholder.progress(100, "Complete!")
                status_placeholder.success("✅ Analysis ready!")
            else:
                status_placeholder.error(f"Analysis failed ({r.status_code})")
                
        except Exception as e:
            status_placeholder.error(f"Error: {e}")
        finally:
            st.session_state.analysis_in_flight = False

# ── Landing page ──
if not st.session_state.analysis:
    st.markdown("")
    _left, _center, _right = st.columns([1, 3, 1])
    with _center:
        st.markdown("### Welcome to Decision Intelligence")
        st.caption("Transform vendor documents into actionable insights")
        st.markdown("")
        steps = {
            "📁  **Upload Documents**": "CSV, Excel, or PDF vendor files",
            "🔍  **Extract Facts**": "AI identifies key data points",
            "💡  **Surface Insights**": "Assumptions, risks, and trade-offs",
            "💬  **Ask Questions**": "Interactive exploration of data",
        }
        for title, desc in steps.items():
            st.markdown(f"{title}  \n{desc}")
        st.markdown("")
        st.info("Upload files in the sidebar and click **Analyze** to get started.")
    st.stop()

# ── Extract data ──
result = st.session_state.analysis
facts = result.get("facts", [])
analysis = result.get("analysis", {})
vendor_data = result.get("vendor_data", [])


def extract_text(item):
    if isinstance(item, dict):
        return next(iter(item.values()))
    return item


# ── Chart helpers ──
PRIMARY_BAR_COLOR = '#6366f1'

VENDOR_PALETTE = [
    '#6366f1', '#10b981', '#f59e0b', '#ef4444', '#3b82f6',
    '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#84cc16',
]

METRIC_PALETTE = [
    '#6366f1', '#10b981', '#f59e0b', '#ef4444', '#3b82f6',
    '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#84cc16',
]


@st.cache_data(show_spinner=False)
def _facts_df(facts_raw: list):
    import pandas as pd
    df = pd.DataFrame(facts_raw)
    if df.empty or "value" not in df.columns:
        return df.iloc[0:0] if not df.empty else df
    df["value_numeric"] = pd.to_numeric(df["value"], errors="coerce")
    return df.dropna(subset=["value_numeric"])


@st.cache_data(show_spinner=False)
def _numeric_attributes(df) -> list[str]:
    if df is None or getattr(df, "empty", True):
        return []
    if "attribute" not in df.columns:
        return []
    return sorted([str(a) for a in df["attribute"].dropna().unique().tolist()])


def _base_layout(**overrides):
    base = dict(
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff',
        font=dict(family='Inter, sans-serif', color='#1f2937'),
        margin=dict(t=60, b=60, l=60, r=30),
    )
    base.update(overrides)
    return base


def create_bar_chart(df, attribute: str):
    import plotly.graph_objects as go

    subset = df[df["attribute"] == attribute]
    if subset.empty or subset["entity_name"].nunique() < 2:
        return None

    vendors = subset["entity_name"].tolist()
    values = subset["value_numeric"].tolist()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=vendors,
        y=values,
        marker=dict(color=PRIMARY_BAR_COLOR, line=dict(width=0), cornerradius=6),
        text=[f"{v:,.2f}" for v in values],
        textposition='outside',
        textfont=dict(color='#374151', size=12),
        hovertemplate='<b>%{x}</b><br>%{y:,.2f}<extra></extra>'
    ))

    nice_title = attribute.replace('_', ' ').title()
    fig.update_layout(**_base_layout(
        title=dict(text=f"<b>{nice_title}</b> by Vendor",
                   font=dict(size=18, color='#111827')),
        xaxis=dict(
            title='',
            gridcolor='#f3f4f6',
            linecolor='#e5e7eb',
            tickfont=dict(color='#374151', size=12),
        ),
        yaxis=dict(
            title=dict(text=nice_title, font=dict(color='#6b7280', size=13)),
            gridcolor='#f3f4f6',
            linecolor='#e5e7eb',
            tickfont=dict(color='#374151', size=12),
        ),
        margin=dict(t=80, b=60, l=80, r=40),
        showlegend=False,
        bargap=0.3,
    ))
    return fig


def create_grouped_bar(df):
    import plotly.graph_objects as go

    if df.empty or df["entity_name"].nunique() < 2:
        return None

    pivot = df.pivot_table(
        index='entity_name', columns='attribute',
        values='value_numeric', aggfunc='mean'
    ).fillna(0)

    if pivot.empty:
        return None

    fig = go.Figure()
    for i, col in enumerate(pivot.columns):
        nice_col = col.replace('_', ' ').title()
        fig.add_trace(go.Bar(
            name=nice_col,
            x=pivot.index.tolist(),
            y=pivot[col].tolist(),
            marker_color=METRIC_PALETTE[i % len(METRIC_PALETTE)],
            hovertemplate=f'<b>%{{x}}</b><br>{nice_col}: %{{y:,.2f}}<extra></extra>',
        ))

    fig.update_layout(**_base_layout(
        title=dict(text="<b>All Metrics</b> by Vendor",
                   font=dict(size=18, color='#111827')),
        barmode='group',
        xaxis=dict(tickfont=dict(color='#374151', size=12),
                   gridcolor='#f3f4f6'),
        yaxis=dict(tickfont=dict(color='#374151', size=12),
                   gridcolor='#f3f4f6'),
        legend=dict(font=dict(color='#374151', size=11),
                    orientation='h', yanchor='bottom', y=-0.25,
                    xanchor='center', x=0.5),
        margin=dict(t=80, b=80, l=80, r=40),
        bargap=0.25,
        bargroupgap=0.1,
    ))
    return fig


# ── Tabs ──
tabs = st.tabs([
    "📊 Dashboard",
    "📋 Facts",
    "💡 Insights",
    "⚠️ Assumptions & Gaps",
    "🎯 Trade-offs & Risks",
    "💬 Chat",
    "📁 Documents"
])

# ── Dashboard ──
with tabs[0]:
    st.markdown(
        '<div class="section-header">'
        '<div class="section-icon" style="background: linear-gradient(135deg, #6366f1, #8b5cf6);">📊</div>'
        '<h2>Decision Dashboard</h2></div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(facts)}</div>
            <div class="metric-label">Facts Extracted</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        vendors = set(f.get("entity_name", "") for f in facts)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(vendors)}</div>
            <div class="metric-label">Vendors Analyzed</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(analysis.get("insights", []))}</div>
            <div class="metric-label">Key Insights</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(analysis.get("risks", []))}</div>
            <div class="metric-label">Risks Identified</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    df = _facts_df(facts)
    attrs = _numeric_attributes(df)

    if not attrs:
        st.info("📉 Not enough comparable numeric data to visualize.")
    else:
        chart_col1, chart_col2 = st.columns([3, 1])

        with chart_col2:
            st.markdown("**Chart Type**")
            chart_type = st.radio(
                "Chart Type",
                ["Bar Chart", "Grouped Bars"],
                label_visibility="collapsed"
            )

            if chart_type == "Bar Chart":
                st.markdown("**Select Metric**")
                selected_attr = st.selectbox(
                    "Metric", options=attrs, index=0,
                    label_visibility="collapsed"
                )

        with chart_col1:
            if chart_type == "Bar Chart":
                fig = create_bar_chart(df, selected_attr)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data for comparison.")
            elif chart_type == "Grouped Bars":
                fig = create_grouped_bar(df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data for grouped comparison.")

# ── Facts ──
with tabs[1]:
    st.markdown(
        '<div class="section-header">'
        '<div class="section-icon" style="background: linear-gradient(135deg, #10b981, #14b8a6);">📋</div>'
        '<h2>Extracted Facts</h2></div>',
        unsafe_allow_html=True
    )

    if facts:
        import pandas as pd
        facts_df = pd.DataFrame(facts)

        col1, col2 = st.columns([3, 1])
        with col2:
            if "entity_name" in facts_df.columns:
                vendor_filter = st.multiselect(
                    "Filter by Vendor",
                    options=facts_df["entity_name"].unique().tolist(),
                    default=[]
                )
                if vendor_filter:
                    facts_df = facts_df[facts_df["entity_name"].isin(vendor_filter)]

        st.dataframe(
            facts_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "entity_name": st.column_config.TextColumn("Vendor", width="medium"),
                "attribute": st.column_config.TextColumn("Attribute", width="medium"),
                "value": st.column_config.NumberColumn("Value", format="%.2f"),
                "source": st.column_config.TextColumn("Source", width="medium")
            }
        )
    else:
        st.info("📭 No structured facts extracted from documents.")

# ── Insights ──
with tabs[2]:
    st.markdown(
        '<div class="section-header">'
        '<div class="section-icon" style="background: linear-gradient(135deg, #3b82f6, #0ea5e9);">💡</div>'
        '<h2>Key Insights</h2></div>',
        unsafe_allow_html=True
    )

    insights = analysis.get("insights", [])
    if insights:
        for i in insights:
            text = extract_text(i)
            st.markdown(
                f'<div class="insight-card"><p class="card-text">{text}</p></div>',
                unsafe_allow_html=True
            )
    else:
        st.info("💭 No insights generated yet.")

# ── Assumptions & Gaps ──
with tabs[3]:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="section-header">'
            '<div class="section-icon" style="background: linear-gradient(135deg, #f59e0b, #eab308);">⚠️</div>'
            '<h2>Assumptions</h2></div>',
            unsafe_allow_html=True
        )

        assumptions = analysis.get("assumptions", [])
        if assumptions:
            for a in assumptions:
                text = extract_text(a)
                st.markdown(
                    f'<div class="assumption-card"><p class="card-text">{text}</p></div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("✅ No assumptions identified.")

    with col2:
        st.markdown(
            '<div class="section-header">'
            '<div class="section-icon" style="background: linear-gradient(135deg, #d946ef, #a855f7);">❓</div>'
            '<h2>Information Gaps</h2></div>',
            unsafe_allow_html=True
        )

        gaps = analysis.get("missing_information", [])
        if gaps:
            for g in gaps:
                text = extract_text(g)
                st.markdown(
                    f'<div class="gap-card"><p class="card-text">{text}</p></div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("✅ No information gaps identified.")

# ── Trade-offs & Risks ──
with tabs[4]:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="section-header">'
            '<div class="section-icon" style="background: linear-gradient(135deg, #10b981, #22c55e);">⚖️</div>'
            '<h2>Trade-offs</h2></div>',
            unsafe_allow_html=True
        )

        tradeoffs = analysis.get("tradeoffs", [])
        if tradeoffs:
            for t in tradeoffs:
                text = extract_text(t)
                st.markdown(
                    f'<div class="tradeoff-card"><p class="card-text">{text}</p></div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("📊 No trade-offs identified.")

    with col2:
        st.markdown(
            '<div class="section-header">'
            '<div class="section-icon" style="background: linear-gradient(135deg, #ef4444, #f97316);">🚨</div>'
            '<h2>Risks</h2></div>',
            unsafe_allow_html=True
        )

        risks = analysis.get("risks", [])
        if risks:
            for r in risks:
                text = extract_text(r)
                st.markdown(
                    f'<div class="risk-card"><p class="card-text">{text}</p></div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("✅ No risks identified.")

# ── Chat ──
with tabs[5]:
    st.markdown(
        '<div class="section-header">'
        '<div class="section-icon" style="background: linear-gradient(135deg, #8b5cf6, #a855f7);">💬</div>'
        '<h2>Guided Exploration</h2></div>',
        unsafe_allow_html=True
    )

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if len(st.session_state.messages) <= 1:
        st.markdown("**Suggested questions:**")
        suggested = [
            "What are the main risks with these vendors?",
            "Which assumptions should I verify first?",
            "What information gaps exist in this data?",
            "Compare the trade-offs between vendors",
            "Are there any compliance concerns?",
        ]
        scols = st.columns(len(suggested))
        for idx, sq in enumerate(suggested):
            with scols[idx]:
                if st.button(sq, key=f"sq_{idx}", use_container_width=True):
                    st.session_state["_pending_question"] = sq
                    st.rerun()

    pending_q = st.session_state.pop("_pending_question", None)
    q = st.chat_input("Ask about risks, assumptions, or trade-offs...")
    q = q or pending_q

    if q and not st.session_state.chat_in_flight:
        st.session_state.chat_in_flight = True

        with st.chat_message("user"):
            st.markdown(q)

        chat_context = {
            "facts": facts[:30],
            "insights": analysis.get("insights", [])[:5],
            "assumptions": analysis.get("assumptions", [])[:5],
            "risks": analysis.get("risks", [])[:5],
            "tradeoffs": analysis.get("tradeoffs", [])[:5]
        }

        try:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    r = _http_session().post(
                        f"{BACKEND_URL}/chat",
                        json={"question": q, "context": chat_context},
                        timeout=45
                    )

                reply = (
                    r.json().get("reply", "No response")
                    if r.status_code == 200
                    else f"Error ({r.status_code})"
                )
                st.markdown(reply)

            st.session_state.messages.extend([
                {"role": "user", "content": q},
                {"role": "assistant", "content": reply}
            ])

            st.rerun()

        except Exception as e:
            st.error(f"Chat failed: {e}")
        finally:
            st.session_state.chat_in_flight = False

# ── Documents ──
with tabs[6]:
    st.markdown(
        '<div class="section-header">'
        '<div class="section-icon" style="background: linear-gradient(135deg, #64748b, #475569);">📁</div>'
        '<h2>Source Documents</h2></div>',
        unsafe_allow_html=True
    )

    if vendor_data:
        for item in vendor_data:
            filename = item.get("filename", "Document")
            file_type = item.get("type", "unknown")
            icon = "📊" if file_type in ["csv", "excel"] else "📄"

            with st.expander(f"{icon} {filename}"):
                if file_type == "pdf":
                    preview = item.get("text_preview", "")
                    if preview:
                        st.text_area("Extracted Text", preview, height=200, disabled=True)
                    else:
                        st.warning(item.get("error", "No text extracted"))
                elif "sample" in item:
                    import pandas as pd
                    st.markdown(
                        f"**Rows:** {item.get('rows', 'N/A')} | "
                        f"**Columns:** {len(item.get('columns', []))}"
                    )
                    st.dataframe(
                        pd.DataFrame(item["sample"]),
                        use_container_width=True,
                        hide_index=True
                    )
                elif "error" in item:
                    st.error(item["error"])
    else:
        st.info("📭 No documents to display.")
