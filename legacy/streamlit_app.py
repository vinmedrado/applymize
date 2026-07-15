"""
Applymize — Main Application
9 módulos + Auto-Apply + Campanha + Inteligência de Mercado + Score de Empregabilidade + A/B Test + Alertas + Relatório Semanal
"""
import sys, os, tempfile, json
import streamlit as st
from datetime import datetime, timedelta
import hashlib
from pathlib import Path
from datetime import datetime, date
from core.profile_store import (
    save_profile, load_profile, delete_profile,
    save_cv_profile, load_cv_profile, delete_cv_profile
)

sys.path.insert(0, str(Path(__file__).parent))

from core.auth import (
    user_exists, register_user, login_user, update_config,
    load_funnel, save_funnel, load_history, save_history,
    load_alerts, save_alerts, load_abtest, save_abtest,
    load_stats, save_stats, load_market, save_market,
)
from core.cv_parser import full_parse
from core.analyzer import (
    analyze_ats, analyze_job_match, optimize_cv, tailor_cv_for_job,
    gen_cover_letter, optimize_linkedin, gen_interview_prep,
    career_diagnosis, market_intelligence, gen_networking_email, get_search_terms,
)
from core.cv_exporter import generate_docx
from scrapers.scrapers import search_all
from automation.auto_apply import apply_gupy, run_campaign, get_company_intel
from intelligence.engine import (
    calc_employability_score, check_alerts, generate_weekly_report, abtest_compare,
)

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(page_title="Applymize", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');
:root{
  --bg:#080C16;--surface:#0F1524;--surface2:#161D2F;--surface3:#1C2540;
  --border:#1E2D4A;--border2:#2A3D60;
  --primary:#2563EB;--primary2:#1D4ED8;--accent:#06B6D4;
  --gold:#F59E0B;--success:#10B981;--warning:#F59E0B;--danger:#EF4444;
  --text:#F1F5F9;--text2:#94A3B8;--text3:#64748B;
  --glow:rgba(37,99,235,0.15);
}
*,*::before,*::after{box-sizing:border-box;}
html,body{background:var(--bg)!important;}
.stApp{background:var(--bg)!important;font-family:'DM Sans',sans-serif;color:var(--text);}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:var(--surface);}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:10px;}
[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border)!important;}
[data-testid="stSidebar"]>div{padding-top:0!important;}
.main .block-container{padding:1.5rem 2rem!important;max-width:1400px!important;}
h1,h2,h3,h4{font-family:'Syne',sans-serif!important;font-weight:800!important;letter-spacing:-0.02em;}
.stButton>button{
  background:linear-gradient(135deg,var(--primary),var(--primary2))!important;
  color:#fff!important;border:none!important;border-radius:10px!important;
  font-family:'Syne',sans-serif!important;font-weight:600!important;font-size:.88rem!important;
  padding:.55rem 1.2rem!important;transition:all .2s ease!important;
  box-shadow:0 2px 12px rgba(37,99,235,.3)!important;
}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 6px 24px rgba(37,99,235,.45)!important;}
.stTextInput>div>input,.stTextArea>div>textarea{
  background:var(--surface2)!important;border:1px solid var(--border)!important;
  color:var(--text)!important;border-radius:10px!important;
}
.stTextInput>div>input:focus,.stTextArea>div>textarea:focus{
  border-color:var(--primary)!important;box-shadow:0 0 0 3px var(--glow)!important;
}
.stSelectbox>div>div{background:var(--surface2)!important;border:1px solid var(--border)!important;color:var(--text)!important;border-radius:10px!important;}
[data-testid="stFileUploader"]{background:var(--surface2)!important;border:2px dashed var(--border2)!important;border-radius:14px!important;}
[data-testid="stFileUploader"]:hover{border-color:var(--primary)!important;}
.stProgress>div>div>div{background:linear-gradient(90deg,var(--primary),var(--accent))!important;border-radius:4px!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--surface2)!important;border-radius:12px!important;padding:4px!important;gap:2px!important;border:1px solid var(--border)!important;}
.stTabs [data-baseweb="tab"]{font-family:'Syne',sans-serif!important;font-weight:600!important;font-size:.82rem!important;color:var(--text2)!important;border-radius:8px!important;padding:.4rem .9rem!important;}
.stTabs [aria-selected="true"]{background:var(--primary)!important;color:#fff!important;box-shadow:0 2px 8px rgba(37,99,235,.4)!important;}
[data-testid="metric-container"]{background:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:12px!important;padding:1rem!important;}
.streamlit-expanderHeader{background:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:10px!important;font-family:'Syne',sans-serif!important;font-weight:600!important;}
hr{border-color:var(--border)!important;margin:1.2rem 0!important;}
.stSuccess{background:rgba(16,185,129,.08)!important;border-left-color:var(--success)!important;}
.stError{background:rgba(239,68,68,.08)!important;border-left-color:var(--danger)!important;}
.stWarning{background:rgba(245,158,11,.08)!important;border-left-color:var(--warning)!important;}
.stInfo{background:rgba(37,99,235,.08)!important;border-left-color:var(--primary)!important;}
.stCheckbox>label{color:var(--text2)!important;font-size:.87rem!important;}
/* Custom */
.am-logo{font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;background:linear-gradient(135deg,#fff 0%,#94C5FF 50%,var(--accent) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-1px;line-height:1;}
.am-tagline{font-size:.68rem;color:var(--text3);letter-spacing:3px;text-transform:uppercase;font-weight:500;}
.page-title{font-family:'Syne',sans-serif;font-size:1.7rem;font-weight:800;color:var(--text);letter-spacing:-.03em;margin-bottom:.2rem;}
.page-sub{color:var(--text2);font-size:.87rem;margin-bottom:1.5rem;}
.stat-card{background:var(--surface2);border:1px solid var(--border);border-radius:14px;padding:18px 20px;text-align:center;transition:all .2s;position:relative;overflow:hidden;}
.stat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--primary),var(--accent));}
.stat-card:hover{border-color:var(--border2);transform:translateY(-1px);}
.stat-value{font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;line-height:1;}
.stat-label{font-size:.75rem;color:var(--text3);text-transform:uppercase;letter-spacing:1px;margin-top:4px;}
.score-high{color:#10B981;}.score-mid{color:#F59E0B;}.score-low{color:#EF4444;}
.job-card{background:var(--surface2);border:1px solid var(--border);border-radius:14px;padding:18px 22px;margin-bottom:12px;transition:all .2s;position:relative;overflow:hidden;}
.job-card::after{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;background:linear-gradient(180deg,var(--primary),var(--accent));opacity:0;transition:opacity .2s;}
.job-card:hover{border-color:var(--border2);transform:translateX(3px);}
.job-card:hover::after{opacity:1;}
.job-title{font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;color:var(--text);}
.job-company{color:var(--accent);font-weight:500;font-size:.9rem;margin-top:2px;}
.job-meta{color:var(--text3);font-size:.8rem;margin-top:4px;}
.badge{display:inline-block;padding:2px 10px;border-radius:20px;font-size:.7rem;font-weight:700;font-family:'Syne',sans-serif;letter-spacing:.5px;}
.badge-gupy{background:rgba(16,185,129,.12);color:#10B981;border:1px solid rgba(16,185,129,.2);}
.badge-indeed{background:rgba(37,99,235,.12);color:#60A5FA;border:1px solid rgba(37,99,235,.2);}
.badge-catho{background:rgba(139,92,246,.12);color:#A78BFA;border:1px solid rgba(139,92,246,.2);}
.badge-infojobs{background:rgba(249,115,22,.12);color:#FB923C;border:1px solid rgba(249,115,22,.2);}
.badge-vagas{background:rgba(20,184,166,.12);color:#2DD4BF;border:1px solid rgba(20,184,166,.2);}
.badge-linkedin{background:rgba(14,165,233,.12);color:#38BDF8;border:1px solid rgba(14,165,233,.2);}
.tag{display:inline-block;padding:3px 10px;border-radius:20px;font-size:.75rem;font-weight:500;margin:2px;}
.tag-found{background:rgba(37,99,235,.12);color:#60A5FA;border:1px solid rgba(37,99,235,.25);}
.tag-missing{background:rgba(239,68,68,.1);color:#F87171;border:1px solid rgba(239,68,68,.25);}
.tag-tech{background:rgba(6,182,212,.1);color:#22D3EE;border:1px solid rgba(6,182,212,.25);}
.tag-soft{background:rgba(168,85,247,.1);color:#C084FC;border:1px solid rgba(168,85,247,.25);}
.match-high{background:rgba(16,185,129,.15);color:#10B981;border:1px solid rgba(16,185,129,.3);}
.match-mid{background:rgba(245,158,11,.15);color:#F59E0B;border:1px solid rgba(245,158,11,.3);}
.match-low{background:rgba(239,68,68,.12);color:#F87171;border:1px solid rgba(239,68,68,.25);}
.verdict-box{background:linear-gradient(135deg,rgba(37,99,235,.05),rgba(6,182,212,.05));border:1px solid rgba(37,99,235,.2);border-radius:14px;padding:18px 22px;border-left:3px solid var(--primary);}
.kanban-title{font-family:'Syne',sans-serif;font-weight:700;font-size:.78rem;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid var(--border);}
.kanban-card{background:var(--surface3);border:1px solid var(--border);border-radius:10px;padding:10px 12px;margin-bottom:8px;font-size:.83rem;transition:all .15s;}
.kanban-card:hover{border-color:var(--border2);transform:translateY(-1px);}
.step-dot{width:7px;height:7px;border-radius:50%;display:inline-block;}
.ghost-low{color:#10B981;font-weight:600;font-size:.78rem;}
.ghost-mid{color:#F59E0B;font-weight:600;font-size:.78rem;}
.ghost-high{color:#EF4444;font-weight:600;font-size:.78rem;}
.alert-card{background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:14px 18px;margin-bottom:10px;border-left:3px solid var(--gold);}
.emp-bar{height:10px;border-radius:5px;background:linear-gradient(90deg,var(--primary),var(--accent));transition:width .5s;}
.campaign-row{background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:12px 16px;margin-bottom:8px;}
.intel-card{background:var(--surface2);border:1px solid var(--border);border-radius:14px;padding:20px 24px;margin-bottom:12px;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# STATE
# ─────────────────────────────────────────
def _init():
    defs = {
        "logged_in":False,"user_config":None,"auth_password":"",
        "cv_data":load_cv_profile(),"ats_result":None,"optimized_cv":None,"tailored_cv":None,
        "job_terms":None,"jobs_found":[],"active_tab":"dashboard",
        "selected_job":None,"job_match_result":None,
        "cover_letter":None,"linkedin_opt":None,"interview_prep":None,
        "career_diag":None,"market_data":None,"networking_email":None,
        "funnel":None,"history":None,"alerts":None,"abtest":None,"stats":None,
        "campaign_results":[],"company_intel":None,"emp_score":None,
        "weekly_report":None,
    }
    for k,v in defs.items():
        if k not in st.session_state: st.session_state[k]=v

    profile = load_profile()
    if profile:
        if st.session_state.cv_data is None:
            st.session_state.cv_data = profile.get("cv_data")

        if st.session_state.ats_result is None:
            st.session_state.ats_result = profile.get("ats_result")

        if st.session_state.job_terms is None:
            st.session_state.job_terms = profile.get("job_terms")

        if st.session_state.emp_score is None:
            st.session_state.emp_score = profile.get("emp_score")
_init()

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def sc(s): return "high" if s>=70 else "mid" if s>=45 else "low"
def se(s): return "🟢" if s>=70 else "🟡" if s>=45 else "🔴"
def tags(items,cls): return " ".join(f'<span class="tag {cls}">{i}</span>' for i in (items or []))
def badge_src(src):
    m={"Gupy":"gupy","Indeed":"indeed","Catho":"catho","InfoJobs":"infojobs","Vagas.com":"vagas","LinkedIn":"linkedin"}
    return f'<span class="badge badge-{m.get(src,"gupy")}">{src}</span>'
def mbadge(s):
    cls="match-high" if s>=70 else "match-mid" if s>=45 else "match-low"
    return f'<span class="badge {cls}">⚡ {s}%</span>'
def gkey(): return st.session_state.user_config.get("groq_api_key","")
def score_ring(s,label=""):
    cls=sc(s); color={"high":"#10B981","mid":"#F59E0B","low":"#EF4444"}[cls]
    return f"""<div style="text-align:center">
  <div style="width:90px;height:90px;border-radius:50%;background:conic-gradient({color} {s}%,#1C2540 0%);
              display:flex;align-items:center;justify-content:center;margin:0 auto;box-shadow:0 0 20px {color}33">
    <div style="width:68px;height:68px;border-radius:50%;background:var(--surface2);
                display:flex;align-items:center;justify-content:center;flex-direction:column">
      <div style="font-family:Syne,sans-serif;font-weight:800;font-size:1.35rem;color:{color}">{s}</div>
      <div style="font-size:.55rem;color:var(--text3);letter-spacing:1px;text-transform:uppercase">{label}</div>
    </div>
  </div></div>"""

# ─────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────
def render_auth():
    c1,c2,c3=st.columns([1,1.4,1])
    with c2:
        st.markdown('<div style="text-align:center;padding:2rem 0 1.5rem"><div class="am-logo">Applymize</div><div class="am-tagline">Sua carreira. Com precisão de dados.</div></div>',unsafe_allow_html=True)
        t1,t2=st.tabs(["🔑  Entrar","✨  Criar Conta"])
        with t1:
            st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
            pwd=st.text_input("Senha",type="password",key="lp",placeholder="Digite sua senha")
            if st.button("Entrar →",use_container_width=True,key="btn_login"):
                cfg=login_user(pwd)
                if cfg: st.session_state.update(logged_in=True,user_config=cfg,auth_password=pwd); st.rerun()
                else: st.error("Senha incorreta.")
        with t2:
            st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
            uname=st.text_input("Seu nome",key="rn",placeholder="Ex: João Silva")
            gk=st.text_input("Groq API Key",type="password",key="rg",placeholder="gsk_...",help="Gratuita em console.groq.com")
            st.caption("🔗 [Obter chave gratuita](https://console.groq.com)")
            np=st.text_input("Criar senha",type="password",key="rp")
            cp=st.text_input("Confirmar senha",type="password",key="rc")
            if st.button("Criar Conta →",use_container_width=True,key="btn_reg"):
                if not all([uname,gk,np,cp]): st.error("Preencha todos os campos.")
                elif np!=cp: st.error("Senhas não coincidem.")
                elif len(np)<6: st.error("Mínimo 6 caracteres.")
                elif register_user(uname,np,gk): st.success("Conta criada! Faça login.")
                else: st.error("Erro ao criar conta.")

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
def render_sidebar():
    cfg=st.session_state.user_config
    with st.sidebar:
        st.markdown(f'<div style="padding:1.2rem .5rem .5rem"><div class="am-logo">Applymize</div><div class="am-tagline">v3 Premium</div></div>',unsafe_allow_html=True)
        st.markdown(f'<div style="color:var(--text3);font-size:.8rem;padding:0 .5rem .8rem">👤 {cfg.get("username","")}</div>',unsafe_allow_html=True)

        # Employability score mini
        if st.session_state.emp_score:
            s=st.session_state.emp_score.get("score",0)
            color={"high":"#10B981","mid":"#F59E0B","low":"#EF4444"}[sc(s)]
            st.markdown(f'<div style="padding:.5rem;background:var(--surface2);border:1px solid var(--border);border-radius:10px;margin-bottom:.8rem"><div style="font-size:.7rem;color:var(--text3);margin-bottom:4px">EMPREGABILIDADE</div><div style="background:var(--surface3);border-radius:4px;height:8px"><div style="width:{s}%;height:8px;border-radius:4px;background:linear-gradient(90deg,var(--primary),var(--accent))"></div></div><div style="font-family:Syne,sans-serif;font-weight:700;color:{color};font-size:.9rem;margin-top:4px">{s}/100 — {st.session_state.emp_score.get("level","")}</div></div>',unsafe_allow_html=True)

        st.divider()
        nav=[
            ("dashboard","🏠","Dashboard"),
            ("ats","🎯","Análise ATS"),
            ("jobs","🔍","Buscar Vagas"),
            ("match","⚡","Match por Vaga"),
            ("campaign","🚀","Modo Campanha"),
            ("cv","📄","CV Otimizado"),
            ("tailor","✂️","CV por Vaga"),
            ("letter","✉️","Carta de Apresentação"),
            ("linkedin","💼","LinkedIn"),
            ("interview","🎤","Prep Entrevista"),
            ("diagnosis","🧬","Diagnóstico de Carreira"),
            ("market","📊","Inteligência de Mercado"),
            ("networking","🤝","Networking Email"),
            ("funnel","📋","Funil de Candidaturas"),
            ("abtest","🔬","A/B Teste de CV"),
            ("alerts","🔔","Alertas de Vagas"),
            ("report","📈","Relatório Semanal"),
            ("settings","⚙️","Configurações"),
        ]
        for key,icon,label in nav:
            active=st.session_state.active_tab==key
            bg="rgba(37,99,235,.15)" if active else "transparent"
            border="1px solid rgba(37,99,235,.3)" if active else "1px solid transparent"
            color="#fff" if active else "var(--text2)"
            fw="700" if active else "500"
            st.markdown(f'<div style="background:{bg};border:{border};border-radius:9px;padding:6px 12px;margin-bottom:2px"><span style="color:{color};font-family:Syne,sans-serif;font-weight:{fw};font-size:.83rem">{icon} {label}</span></div>',unsafe_allow_html=True)
            if st.button(label,key=f"nav_{key}",use_container_width=True):
                st.session_state.active_tab=key; st.rerun()
        st.divider()
        if st.session_state.jobs_found:
            st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:var(--accent)">{len(st.session_state.jobs_found)}</div><div class="stat-label">Vagas encontradas</div></div>',unsafe_allow_html=True)
            st.markdown('<div style="height:8px"></div>',unsafe_allow_html=True)
        if st.button("🚪 Sair",use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

# ─────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────
def render_dashboard():
    st.markdown('<div class="page-title">🏠 Dashboard</div>',unsafe_allow_html=True)
    cfg=st.session_state.user_config
    hour=datetime.now().hour
    greeting="Bom dia" if hour<12 else "Boa tarde" if hour<18 else "Boa noite"
    st.markdown(f'<div class="page-sub">{greeting}, {cfg.get("username","")}! Aqui está um resumo da sua busca.</div>',unsafe_allow_html=True)

    funnel=st.session_state.funnel or load_funnel()
    st.session_state.funnel=funnel
    history=st.session_state.history or load_history()
    st.session_state.history=history

    total=sum(len(v) for v in funnel.values())
    aplicado=len(funnel.get("Aplicado",[]))
    entrevistas=len(funnel.get("Entrevista",[]))
    ofertas=len(funnel.get("Oferta",[]))

    c1,c2,c3,c4,c5=st.columns(5)
    with c1: st.markdown(f'<div class="stat-card"><div class="stat-value">{total}</div><div class="stat-label">No funil</div></div>',unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:var(--primary)">{aplicado}</div><div class="stat-label">Aplicadas</div></div>',unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:var(--gold)">{entrevistas}</div><div class="stat-label">Entrevistas</div></div>',unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:var(--success)">{ofertas}</div><div class="stat-label">Ofertas</div></div>',unsafe_allow_html=True)
    with c5:
        ats=st.session_state.ats_result
        cv_score=ats.get("score_geral",0) if ats else 0
        color={"high":"#10B981","mid":"#F59E0B","low":"#EF4444"}[sc(cv_score)] if cv_score else "var(--text3)"
        st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:{color}">{cv_score if cv_score else "—"}</div><div class="stat-label">Score CV</div></div>',unsafe_allow_html=True)

    st.markdown('<div style="height:16px"></div>',unsafe_allow_html=True)

    # Employability score
    if st.session_state.ats_result:
        emp=calc_employability_score(st.session_state.ats_result,funnel,history)
        st.session_state.emp_score=emp
        s=emp["score"]
        color={"high":"#10B981","mid":"#F59E0B","low":"#EF4444"}[sc(s)]
        tips_html = "".join(f'<div style="color:var(--text3);font-size:.82rem">→ {t}</div>' for t in emp["tips"][:2])
        st.markdown(f'<div class="verdict-box"><div style="display:flex;align-items:center;gap:16px"><div>{score_ring(s,"Emp.")}</div><div><div style="font-family:Syne,sans-serif;font-weight:800;font-size:1.2rem;color:{color}">{emp["level"]}</div><div style="color:var(--text2);font-size:.87rem;margin-top:4px">Score de Empregabilidade — calculado com base no CV, atividade e perfil</div>{tips_html}</div></div></div>',unsafe_allow_html=True)

    st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)

    # Quick actions
    st.markdown("**⚡ Ações Rápidas**")
    q1,q2,q3,q4,q5=st.columns(5)
    with q1:
        if st.button("🎯 Analisar CV",use_container_width=True): st.session_state.active_tab="ats";st.rerun()
    with q2:
        if st.button("🔍 Buscar Vagas",use_container_width=True): st.session_state.active_tab="jobs";st.rerun()
    with q3:
        if st.button("🚀 Iniciar Campanha",use_container_width=True): st.session_state.active_tab="campaign";st.rerun()
    with q4:
        if st.button("📊 Mercado",use_container_width=True): st.session_state.active_tab="market";st.rerun()
    with q5:
        if st.button("📈 Relatório",use_container_width=True): st.session_state.active_tab="report";st.rerun()

    # Alerts check
    if st.session_state.jobs_found and st.session_state.alerts:
        cv_kws=(st.session_state.ats_result or {}).get("palavras_chave_encontradas",[])
        triggered=check_alerts(st.session_state.jobs_found,st.session_state.alerts,cv_kws)
        if triggered:
            st.markdown(f'<div class="alert-card"><b style="color:var(--gold)">🔔 {len(triggered)} vaga(s) ativaram seus alertas!</b></div>',unsafe_allow_html=True)
            for t in triggered[:3]:
                j=t["job"]
                st.markdown(f'<div style="color:var(--text2);font-size:.87rem;padding:2px 0">⚡ {j.get("title","")} — {j.get("company","")} · {mbadge(t["match_score"])}</div>',unsafe_allow_html=True)

# ─────────────────────────────────────────
# ATS
# ─────────────────────────────────────────
def render_ats():
    st.markdown('<div class="page-title">🎯 Análise ATS</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Simulação real de sistemas ATS profissionais · Veredicto de RH sênior · Score de empregabilidade</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 1])
    uploaded = None

    with c1:
        if st.session_state.cv_data:
            st.success("Currículo carregado do perfil salvo.")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔄 Atualizar currículo", use_container_width=True):
                    delete_cv_profile()
                    st.session_state.cv_data = None
                    st.session_state.ats_result = None
                    st.session_state.job_terms = None
                    st.session_state.optimized_cv = None
                    st.session_state.tailored_cv = None
                    st.rerun()

            with col_b:
                if st.button("🧹 Limpar análise ATS", use_container_width=True):
                    st.session_state.ats_result = None
                    st.session_state.job_terms = None
                    st.session_state.emp_score = None
                    st.rerun()
        else:
            uploaded = st.file_uploader("Envie seu currículo (PDF ou DOCX)", type=["pdf", "docx"])

    with c2:
        target = st.text_input("Vaga alvo (opcional)", placeholder="Ex: Analista de Dados Pleno")

    if uploaded:
        with st.spinner("Extraindo conteúdo do currículo..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded.name).suffix) as tmp:
                tmp.write(uploaded.getbuffer())
                tmp_path = tmp.name

            cv_data = full_parse(tmp_path)
            os.unlink(tmp_path)

            if "error" in cv_data:
                st.error(cv_data["error"])
                return

            st.session_state.cv_data = cv_data
            st.session_state.ats_result = None
            st.session_state.job_terms = None
            st.session_state.optimized_cv = None
            st.session_state.tailored_cv = None
            save_cv_profile(cv_data)

        st.success("Currículo salvo com sucesso!")
        st.rerun()

    if not st.session_state.cv_data:
        st.info("Envie um currículo para iniciar a análise.")
        return

    if st.button("🔍 Analisar", type="primary", use_container_width=True):
        with st.spinner("Analisando com IA..."):
            cv_data = st.session_state.cv_data

            ats = analyze_ats(cv_data["raw_text"], gkey(), target)
            st.session_state.ats_result = ats
            st.session_state.optimized_cv = None

            terms = get_search_terms(cv_data["raw_text"], ats, gkey())
            st.session_state.job_terms = terms

            funnel = st.session_state.funnel or load_funnel()
            emp = calc_employability_score(ats, funnel, [])
            st.session_state.emp_score = emp

            save_profile(
                cv_data=st.session_state.cv_data,
                ats_result=ats,
                job_terms=terms,
                emp_score=emp
            )

        st.success("✅ Análise concluída!")
        st.rerun()

    if not st.session_state.ats_result: return
    ats=st.session_state.ats_result
    if ats.get("error"): st.error(ats.get("raw","")); return
    score=ats.get("score_geral",0)
    st.divider()
    c_sc,c_st=st.columns([1,3])
    with c_sc: st.markdown(score_ring(score,"ATS"),unsafe_allow_html=True)
    with c_st:
        compat=ats.get("compatibilidade_ats","")
        nivel=ats.get("nivel_perfil","")
        anos = ats.get("anos_experiencia_total", ats.get("anos_experiencia_estimados", ""))
        cc={"Alta":"#10B981","Média":"#F59E0B","Baixa":"#EF4444"}.get(compat,"var(--text)")
        r1,r2,r3,r4=st.columns(4)
        with r1: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:var(--accent)">{nivel}</div><div class="stat-label">Nível</div></div>',unsafe_allow_html=True)
        with r2: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:{cc}">{compat}</div><div class="stat-label">Compat. ATS</div></div>',unsafe_allow_html=True)
        with r3: st.markdown(f'<div class="stat-card"><div class="stat-value">{anos}</div><div class="stat-label">Anos exp.</div></div>',unsafe_allow_html=True)
        with r4: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:var(--text2)">{st.session_state.cv_data.get("word_count",0)}</div><div class="stat-label">Palavras</div></div>',unsafe_allow_html=True)
    if ats.get("resumo_executivo"):
        st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
        st.markdown(f'<div class="verdict-box"><b style="color:var(--accent);font-size:.75rem;letter-spacing:1px;text-transform:uppercase">Resumo Executivo</b><p style="margin:8px 0 0">{ats["resumo_executivo"]}</p></div>',unsafe_allow_html=True)
    st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
    with st.expander("📊 Pontuação Detalhada",expanded=True):
        for k,label in [("formatacao","Formatação"),("palavras_chave","Palavras-chave"),("experiencia_relevante","Experiência"),("resultados_quantificados","Resultados Quantificados"),("completude_secoes","Completude")]:
            v=ats.get("scores_detalhados",{}).get(k,0)
            color="#10B981" if v>=15 else "#F59E0B" if v>=10 else "#EF4444"
            cl,cb,cv2=st.columns([2,5,1])
            with cl: st.caption(label)
            with cb: st.progress(v/20)
            with cv2: st.markdown(f'<span style="color:{color};font-weight:700;font-size:.85rem">{v}/20</span>',unsafe_allow_html=True)
    ca,cb2,cc2=st.columns(3)
    with ca:
        st.markdown("#### ✅ Pontos Fortes")
        for p in ats.get("pontos_fortes",[]): st.markdown(f'<div style="color:var(--text2);font-size:.87rem;padding:4px 0;border-bottom:1px solid var(--border)">✦ {p}</div>',unsafe_allow_html=True)
    with cb2:
        st.markdown("#### 🚨 Problemas")
        for p in ats.get("problemas_criticos",[]): st.markdown(f'<div style="color:#F87171;font-size:.87rem;padding:4px 0;border-bottom:1px solid var(--border)">✗ {p}</div>',unsafe_allow_html=True)
    with cc2:
        st.markdown("#### 🔧 Melhorias")
        for m in ats.get("melhorias_prioritarias",[]): st.markdown(f'<div style="color:#FCD34D;font-size:.87rem;padding:4px 0;border-bottom:1px solid var(--border)">→ {m}</div>',unsafe_allow_html=True)
    st.markdown('<div style="height:8px"></div>',unsafe_allow_html=True)
    ck1,ck2=st.columns(2)
    with ck1:
        st.markdown("**🏷 Keywords Encontradas**")
        st.markdown(tags(ats.get("palavras_chave_encontradas",[]),"tag-found"),unsafe_allow_html=True)
    with ck2:
        st.markdown("**⚠️ Keywords Faltando**")
        st.markdown(tags(ats.get("palavras_chave_faltando",[]),"tag-missing"),unsafe_allow_html=True)
    st.markdown('<div style="height:8px"></div>',unsafe_allow_html=True)
    ct1,ct2=st.columns(2)
    with ct1:
        st.markdown("**💻 Tecnologias**")
        st.markdown(tags(ats.get("tecnologias_identificadas",[]),"tag-tech"),unsafe_allow_html=True)
    with ct2:
        st.markdown("**🤝 Soft Skills**")
        st.markdown(tags(ats.get("soft_skills",[]),"tag-soft"),unsafe_allow_html=True)
    if ats.get("gap_skills"):
        st.markdown('<div style="height:8px"></div>',unsafe_allow_html=True)
        st.markdown("**🎯 Gaps de Skills (para crescimento)**")
        st.markdown(tags(ats.get("gap_skills",[]),"tag-missing"),unsafe_allow_html=True)
    if ats.get("proximos_passos"):
        st.markdown('<div style="height:8px"></div>',unsafe_allow_html=True)
        st.markdown("**🗺 Próximos Passos Recomendados**")
        for p in ats.get("proximos_passos",[]): st.markdown(f"→ {p}")
    if ats.get("veredicto_rh"):
        st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
        st.markdown(f'<div class="verdict-box"><b style="color:var(--text2);font-size:.75rem;text-transform:uppercase">💬 Veredicto do Recrutador Sênior</b><p style="margin:8px 0 0;font-style:italic">"{ats["veredicto_rh"]}"</p></div>',unsafe_allow_html=True)
    st.markdown('<div style="height:16px"></div>',unsafe_allow_html=True)
    b1,b2,b3,b4,b5=st.columns(5)
    with b1:
        if st.button("📄 Otimizar CV",use_container_width=True): st.session_state.active_tab="cv";st.rerun()
    with b2:
        if st.button("🔍 Buscar Vagas",use_container_width=True): st.session_state.active_tab="jobs";st.rerun()
    with b3:
        if st.button("🧬 Diagnóstico",use_container_width=True): st.session_state.active_tab="diagnosis";st.rerun()
    with b4:
        if st.button("💼 LinkedIn",use_container_width=True): st.session_state.active_tab="linkedin";st.rerun()
    with b5:
        if st.button("📊 Mercado",use_container_width=True): st.session_state.active_tab="market";st.rerun()

# ─────────────────────────────────────────
# JOBS
# ─────────────────────────────────────────
def filtrar_vagas_recentes(jobs, dias=30):
    limite = datetime.now().date() - timedelta(days=dias)
    filtradas = []

    for job in jobs:
        posted = str(job.get("posted", "")).strip()
        if not posted:
            continue

        try:
            data_vaga = datetime.strptime(posted[:10], "%Y-%m-%d").date()
            if data_vaga >= limite:
                filtradas.append(job)
        except:
            continue

    return filtradas


def remover_duplicadas(jobs):
    unicas = {}
    for job in jobs:
        url = str(job.get("url", "")).strip()
        title = str(job.get("title", "")).strip().lower()
        company = str(job.get("company", "")).strip().lower()

        if url:
            chave = f"url::{url}"
        else:
            chave = f"title_company::{title}::{company}"

        if chave not in unicas:
            unicas[chave] = job

    return list(unicas.values())


def make_job_key(prefix, job, i):
    base = (
        str(job.get("url", "")) +
        "|" + str(job.get("title", "")) +
        "|" + str(job.get("company", "")) +
        "|" + str(i)
    )
    h = hashlib.md5(base.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}_{i}_{h}"

def render_jobs():
    st.markdown('<div class="page-title">🔍 Buscar Vagas</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">6 plataformas simultâneas · Ranking por compatibilidade · Ghost detector · Análise de empresa</div>',unsafe_allow_html=True)
    default_q=""
    if st.session_state.job_terms:
        t=st.session_state.job_terms.get("termos_busca",[])
        if t: default_q=t[0].get("termo","")
    c1,c2=st.columns([2,1])
    with c1: query=st.text_input("Cargo",value=default_q,placeholder="Ex: Analista de Dados")
    with c2: location=st.text_input("Localização",placeholder="Ex: São Paulo, Remoto")
    if st.session_state.job_terms:
        ts=st.session_state.job_terms.get("termos_busca",[])
        if len(ts)>1:
            st.caption("💡 Sugestões do perfil:")
            sc1,sc2,sc3,sc4=st.columns(4)
            for i,(t,col) in enumerate(zip(ts[:4],[sc1,sc2,sc3,sc4])):
                with col:
                    if st.button(f"{t['termo']} · {t['nivel']}",key=f"sug_{i}"): query=t["termo"]
    st.markdown("**Plataformas**")
    pc=st.columns(6)
    plats={"gupy":("Gupy",True),"indeed":("Indeed",True),"catho":("Catho",True),"infojobs":("InfoJobs",True),"vagas_com":("Vagas.com",True),"linkedin":("LinkedIn ⚠️",False)}
    selected=[]
    for i,(key,(name,default)) in enumerate(plats.items()):
        with pc[i]:
            if st.checkbox(name,value=default,key=f"p_{key}"): selected.append(key)
    cv_kws=[]
    if st.session_state.ats_result:
        cv_kws=st.session_state.ats_result.get("palavras_chave_encontradas",[])+st.session_state.ats_result.get("tecnologias_identificadas",[])
        st.caption(f"🎯 Match calculado com {len(cv_kws)} keywords do seu CV")
    cf1, cf2 = st.columns([1, 1])
    with cf1:
        dias_filtro = st.slider("Recência das vagas (dias)", 7, 90, 30, help="Filtro aplicado quando a plataforma informa data da vaga.")
    with cf2:
        manter_sem_data = st.checkbox("Manter vagas sem data", value=True, help="Recomendado: algumas plataformas não entregam data confiável.")

    if st.button("🔍 Buscar Agora",type="primary",use_container_width=True,disabled=not query):
        if not selected: st.warning("Selecione ao menos uma plataforma."); return
        with st.spinner(f"Buscando em {len(selected)} plataformas..."):
            jobs=search_all(query,location,selected,limit=15,cv_keywords=cv_kws)
            total_bruto=len(jobs)

            jobs=remover_duplicadas(jobs)
            total_unicas=len(jobs)

            recentes = filtrar_vagas_recentes(jobs, dias=dias_filtro)
            sem_data = [j for j in jobs if not str(j.get("posted", "")).strip()]

            if recentes:
                jobs = recentes + (sem_data if manter_sem_data else [])
            else:
                st.warning("Nenhuma vaga passou no filtro de recência. Mantendo resultados encontrados.")

            jobs=remover_duplicadas(jobs)
            st.session_state.jobs_found=jobs

        st.success(f"✅ {len(jobs)} vagas prontas ({total_bruto} brutas, {total_unicas} únicas).")
        st.rerun()
    if not st.session_state.jobs_found: return
    jobs=st.session_state.jobs_found
    st.divider()
    fc1,fc2,fc3,fc4=st.columns([2,2,1,1])
    with fc1:
        sources=list(set(j.get("source","") for j in jobs))
        sf=st.multiselect("Plataforma",sources,default=sources)
    with fc2: tf=st.text_input("Filtrar título",placeholder="Ex: Sênior")
    with fc3: gf=st.selectbox("Fantasma",["Todos","🟢 Baixa","🟡 Média","🔴 Alta"])
    with fc4: sortf=st.selectbox("Ordenar",["Match ↓","Plataforma","Empresa"])
    filtered=[j for j in jobs if (not sf or j.get("source") in sf) and (not tf or tf.lower() in j.get("title","").lower()) and (gf=="Todos" or j.get("ghost_level","").endswith(gf.split()[-1]))]
    if sortf=="Plataforma": filtered.sort(key=lambda x:x.get("source",""))
    elif sortf=="Empresa": filtered.sort(key=lambda x:x.get("company",""))
    st.caption(f"Exibindo {len(filtered)} de {len(jobs)} vagas")
    for i, job in enumerate(filtered):
        ms=job.get("match_score",0)
        ghost=job.get("ghost_level","🟢 Baixa")
        gcls="ghost-high" if "Alta" in ghost else "ghost-mid" if "Média" in ghost else "ghost-low"
        meta=" · ".join(p for p in [job.get("location",""),job.get("modality","")] if p) or "Localização não informada"
        st.markdown(f"""<div class="job-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">
    <div style="flex:1">
      <div class="job-title">{job.get("title","")}</div>
      <div class="job-company">{job.get("company","Empresa não informada")}</div>
      <div class="job-meta">{meta}</div>
    </div>
    <div style="text-align:right;flex-shrink:0">{badge_src(job.get("source",""))}
      <div style="margin-top:6px">{mbadge(ms)}</div>
      <div style="margin-top:4px"><span class="{gcls}">👻 {ghost}</span></div>
    </div>
  </div>{"".join(f'<div style="color:#EF4444;font-size:.75rem;margin-top:2px">⚠️ {f}</div>' for f in job.get("ghost_flags",[]))}
</div>""",unsafe_allow_html=True)
        bc1,bc2,bc3,bc4=st.columns(4)
        url=job.get("url","")
        with bc1:
            if url: st.markdown(f"[🔗 Ver vaga]({url})")
        with bc2:
            if st.button("⚡ Match",key=make_job_key("m", job, i)):
                job["description"] = job.get("description") or ""; st.session_state.selected_job=job; st.session_state.job_match_result=None
                st.session_state.active_tab="match"; st.rerun()
        with bc3:
            if st.button("🏢 Empresa",key=make_job_key("ci", job, i)):
                with st.spinner("Buscando dados da empresa..."):
                    intel=get_company_intel(job.get("company",""))
                    st.session_state.company_intel=intel
                st.info(intel.get("summary",""))
        with bc4:
            if st.button("📋 Funil",key=make_job_key("f", job, i)):
                fn=st.session_state.funnel or load_funnel()
                fn["Interesse"].append({"title":job.get("title",""),"company":job.get("company",""),"url":url,"source":job.get("source",""),"match":ms,"added":datetime.now().strftime("%d/%m/%Y"),"notes":""})
                save_funnel(fn); st.session_state.funnel=fn; st.success("Adicionado!")
        st.markdown("---")

# ─────────────────────────────────────────
# MATCH
# ─────────────────────────────────────────
def render_match():
    st.markdown('<div class="page-title">⚡ Match por Vaga</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Cole qualquer descrição de vaga · Análise detalhada de compatibilidade · Ajustes cirúrgicos</div>',unsafe_allow_html=True)
    if not st.session_state.cv_data: st.info("Primeiro faça a Análise ATS."); return
    j=st.session_state.selected_job or {}
    c1,c2=st.columns(2)
    with c1: jt=st.text_input("Cargo",value=j.get("title",""),placeholder="Ex: Engenheiro de Dados")
    with c2: jc=st.text_input("Empresa",value=j.get("company",""),placeholder="Ex: Nubank")
    jd=st.text_area("Descrição da vaga",value=j.get("description",""),height=180,placeholder="Cole a descrição completa...")
    if not jd:
        st.warning("Essa vaga veio sem descrição. Cole a descrição se quiser uma análise mais precisa; dá para rodar só com o cargo também.")
    if st.button("⚡ Analisar Match",type="primary",use_container_width=True,disabled=not jt):
        with st.spinner("Analisando compatibilidade..."):
            r=analyze_job_match(st.session_state.cv_data["raw_text"], jd or jt, jt, jc, gkey())
            st.session_state.job_match_result=r
            st.session_state.selected_job={"title":jt,"company":jc,"description":jd,"url":""}
        st.rerun()
    if not st.session_state.job_match_result: return
    r=st.session_state.job_match_result
    if r.get("error"):
        st.error("Erro ao processar o match.")
        st.write(r)
        return
    ms=r.get("match_score",0); deve=r.get("deve_aplicar",True); motivo=r.get("motivo_decisao","")
    bc="#10B981" if deve else "#EF4444"
    bt="✅ RECOMENDADO APLICAR" if deve else "⚠️ APLICAÇÃO DE RISCO"
    st.markdown(f'<div style="background:rgba({("16,185,129" if deve else "239,68,68")},.1);border:1px solid {bc};border-radius:14px;padding:16px 24px;margin-bottom:16px;display:flex;align-items:center;gap:16px"><div style="font-family:Syne,sans-serif;font-weight:800;font-size:1.1rem;color:{bc}">{bt}</div><div style="color:var(--text2);font-size:.9rem">{motivo}</div></div>',unsafe_allow_html=True)
    s1,s2,s3,s4=st.columns(4)
    pc2={"Alta":"#10B981","Média":"#F59E0B","Baixa":"#EF4444"}.get(r.get("probabilidade_entrevista",""),"var(--text)")
    with s1: st.markdown(score_ring(ms,"Match"),unsafe_allow_html=True)
    with s2: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:var(--accent)">{r.get("nivel_compatibilidade","")}</div><div class="stat-label">Compatibilidade</div></div>',unsafe_allow_html=True)
    with s3: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:{pc2}">{r.get("probabilidade_entrevista","")}</div><div class="stat-label">Prob. Entrevista</div></div>',unsafe_allow_html=True)
    with s4:
        nok=len(r.get("requisitos_atendidos",[])); nf=len(r.get("requisitos_faltando",[]))
        st.markdown(f'<div class="stat-card"><div class="stat-value">{nok}/{nok+nf}</div><div class="stat-label">Requisitos</div></div>',unsafe_allow_html=True)
    st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
    mc1,mc2=st.columns(2)
    with mc1:
        st.markdown("**✅ Requisitos Atendidos**")
        for x in r.get("requisitos_atendidos",[]): st.markdown(f'<div style="color:#10B981;font-size:.87rem;padding:3px 0">✓ {x}</div>',unsafe_allow_html=True)
    with mc2:
        st.markdown("**❌ Requisitos Faltando**")
        for x in r.get("requisitos_faltando",[]): st.markdown(f'<div style="color:#F87171;font-size:.87rem;padding:3px 0">✗ {x}</div>',unsafe_allow_html=True)
    if r.get("ajustes_rapidos"):
        with st.expander("🔧 Ajustes Rápidos para Este CV",expanded=True):
            for x in r.get("ajustes_rapidos",[]): st.markdown(f"→ {x}")
            if r.get("adicionar_no_cv"):
                st.markdown("**Adicione ao CV:**")
                st.markdown(tags(r.get("adicionar_no_cv",[]),"tag-missing"),unsafe_allow_html=True)
    if r.get("dica_candidatura"):
        st.markdown(f'<div class="verdict-box" style="margin-top:12px"><b style="color:var(--accent);font-size:.75rem;text-transform:uppercase">💡 Dica</b><p style="margin:8px 0 0">{r["dica_candidatura"]}</p></div>',unsafe_allow_html=True)
    st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
    ab1,ab2,ab3,ab4=st.columns(4)
    with ab1:
        if st.button("✂️ CV Personalizado",use_container_width=True): st.session_state.active_tab="tailor";st.rerun()
    with ab2:
        if st.button("✉️ Carta de Apresentação",use_container_width=True): st.session_state.active_tab="letter";st.rerun()
    with ab3:
        if st.button("🎤 Prep Entrevista",use_container_width=True): st.session_state.active_tab="interview";st.rerun()
    with ab4:
        if st.button("📋 Adicionar ao Funil",use_container_width=True):
            fn=st.session_state.funnel or load_funnel()
            fn["Interesse"].append({"title":jt,"company":jc,"url":"","source":"Manual","match":ms,"added":datetime.now().strftime("%d/%m/%Y"),"notes":""})
            save_funnel(fn); st.session_state.funnel=fn; st.success("Adicionado!")

# ─────────────────────────────────────────
# CAMPAIGN MODE
# ─────────────────────────────────────────
def render_campaign():
    st.markdown('<div class="page-title">🚀 Modo Campanha</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Define critérios → sistema filtra e processa vagas em lote · Auto-candidatura no Gupy</div>',unsafe_allow_html=True)
    if not st.session_state.cv_data: st.info("Primeiro faça a Análise ATS e busque vagas."); return
    if not st.session_state.jobs_found: st.info("Primeiro busque vagas na aba 🔍 Buscar Vagas."); return
    jobs=st.session_state.jobs_found
    c1,c2,c3=st.columns(3)
    with c1: min_match=st.slider("Match mínimo (%)",50,90,70)
    with c2: max_ghost=st.slider("Ghost score máximo",0,80,40)
    with c3: max_per_day=st.slider("Máx. vagas por rodada",5,50,20)
    auto_apply=st.checkbox("Auto-candidatura no Gupy (experimental)",value=False,help="Tenta submeter automaticamente via Selenium. Gupy apenas.")
    cv_path=""
    if auto_apply:
        cv_upload=st.file_uploader("Envie o CV (PDF) para candidatura automática",type=["pdf"])
        if cv_upload:
            with tempfile.NamedTemporaryFile(delete=False,suffix=".pdf") as tmp:
                tmp.write(cv_upload.getbuffer()); cv_path=tmp.name
        email_auto=st.text_input("Email (para preenchimento automático)",placeholder="seu@email.com")
    filtered=[j for j in jobs if j.get("match_score",0)>=min_match and j.get("ghost_score",100)<=max_ghost][:max_per_day]
    st.markdown(f"**{len(filtered)} vagas elegíveis** com os critérios selecionados")
    if filtered:
        with st.expander("Ver vagas elegíveis",expanded=False):
            for j in filtered[:10]:
                st.markdown(f'<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border)"><span style="color:var(--text)">{j.get("title","")} — {j.get("company","")}</span><span>{mbadge(j.get("match_score",0))} {badge_src(j.get("source",""))}</span></div>',unsafe_allow_html=True)
    if st.button(f"🚀 Iniciar Campanha ({len(filtered)} vagas)",type="primary",use_container_width=True,disabled=not filtered):
        user_info={"email":email_auto if auto_apply else ""}
        progress=st.progress(0); status=st.empty()
        results=[]
        def cb(i,total,title,company):
            progress.progress((i+1)/max(total,1))
            status.caption(f"Processando: {title} — {company}")
        with st.spinner("Executando campanha..."):
            results=run_campaign(filtered,cv_path,user_info,min_match,max_ghost,max_per_day,auto_apply,cb)
            st.session_state.campaign_results=results
            fn=st.session_state.funnel or load_funnel()
            for r2 in results:
                fn["Aplicado"].append({"title":r2["title"],"company":r2["company"],"url":r2["url"],"source":r2["source"],"match":r2["match_score"],"added":datetime.now().strftime("%d/%m/%Y"),"notes":r2.get("apply_message","")})
            save_funnel(fn); st.session_state.funnel=fn
        progress.empty(); status.empty()
        success=[r for r in results if r.get("apply_status")=="success"]
        tracked=[r for r in results if r.get("apply_status")=="tracked"]
        st.success(f"✅ Campanha concluída! {len(success)} enviadas, {len(tracked)} adicionadas ao funil.")
    if st.session_state.campaign_results:
        st.divider()
        st.markdown("**Resultados da última campanha:**")
        for r2 in st.session_state.campaign_results:
            status_color={"success":"#10B981","tracked":"#F59E0B","partial":"#F59E0B","failed":"#EF4444","error":"#EF4444","skipped":"#64748B"}.get(r2.get("apply_status",""),"var(--text3)")
            st.markdown(f'<div class="campaign-row"><div style="display:flex;justify-content:space-between"><span style="color:var(--text)">{r2["title"]} — {r2["company"]}</span><span style="color:{status_color};font-weight:600;font-size:.85rem">{r2.get("apply_status","").upper()}</span></div><div style="color:var(--text3);font-size:.8rem;margin-top:4px">{r2.get("apply_message","")}</div></div>',unsafe_allow_html=True)

# ─────────────────────────────────────────
# CV OTIMIZADO
# ─────────────────────────────────────────
def render_cv():
    st.markdown('<div class="page-title">📄 CV Otimizado</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Reescrita completa baseada na análise ATS · Download em DOCX formatado</div>',unsafe_allow_html=True)
    if not st.session_state.ats_result: st.info("Primeiro faça a Análise ATS."); return
    ats=st.session_state.ats_result
    if not st.session_state.optimized_cv:
        st.markdown(f"Score atual: {se(ats.get('score_geral',0))} **{ats.get('score_geral',0)}/100**")
        for p in ats.get("problemas_criticos",[]): st.markdown(f"🔴 {p}")
        if st.button("✨ Gerar CV Otimizado",type="primary",use_container_width=True):
            with st.spinner("Reescrevendo CV com IA..."):
                opt=optimize_cv(st.session_state.cv_data["raw_text"],ats,gkey())
                st.session_state.optimized_cv=opt
            st.rerun()
    else:
        st.markdown("#### ✨ CV Otimizado")
        edited=st.text_area("",value=st.session_state.optimized_cv,height=500,key="cv_edit",label_visibility="collapsed")
        c1,c2,c3=st.columns(3)
        with c1:
            if st.button("📥 Baixar DOCX",type="primary",use_container_width=True):
                contact=st.session_state.cv_data.get("contact",{})
                with st.spinner("Gerando DOCX..."):
                    path=generate_docx(edited,contact)
                if path.startswith("Erro"): st.error(path)
                else:
                    with open(path,"rb") as f:
                        st.download_button("⬇️ Download",data=f.read(),file_name="cv_applymize.docx",mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        with c2:
            if st.button("🔄 Regenerar",use_container_width=True): st.session_state.optimized_cv=None;st.rerun()
        with c3:
            if st.button("✂️ Personalizar por Vaga",use_container_width=True): st.session_state.active_tab="tailor";st.rerun()

# ─────────────────────────────────────────
# CV TAILOR
# ─────────────────────────────────────────
def render_tailor():
    st.markdown('<div class="page-title">✂️ CV Personalizado por Vaga</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Adapta seu CV especificamente para cada vaga · Keywords da descrição incorporadas naturalmente</div>',unsafe_allow_html=True)
    if not st.session_state.cv_data: st.info("Primeiro faça a Análise ATS."); return
    j=st.session_state.selected_job or {}
    c1,c2=st.columns(2)
    with c1: jt=st.text_input("Cargo da vaga",value=j.get("title",""),placeholder="Ex: Data Engineer Sênior")
    with c2: jc=st.text_input("Empresa",value=j.get("company",""),placeholder="Ex: Itaú")
    jd=st.text_area("Descrição completa da vaga",value=j.get("description",""),height=160,placeholder="Cole a descrição aqui...")
    if st.button("✂️ Personalizar CV",type="primary",use_container_width=True,disabled=not(jt and jd)):
        kws=(st.session_state.job_match_result or {}).get("palavras_chave_vaga",[])
        with st.spinner("Personalizando CV para esta vaga..."):
            tailored=tailor_cv_for_job(st.session_state.cv_data["raw_text"],jt,jd,kws,gkey())
            st.session_state.tailored_cv=tailored
        st.rerun()
    if st.session_state.tailored_cv:
        st.divider()
        edited=st.text_area("CV Personalizado (editável):",value=st.session_state.tailored_cv,height=450,key="tailor_edit")
        tc1,tc2=st.columns(2)
        with tc1:
            if st.button("📥 Baixar DOCX",type="primary",use_container_width=True):
                contact=st.session_state.cv_data.get("contact",{})
                with st.spinner("Gerando DOCX..."):
                    path=generate_docx(edited,contact)
                if not path.startswith("Erro"):
                    with open(path,"rb") as f:
                        st.download_button("⬇️ Download",data=f.read(),file_name=f"cv_{jc or 'empresa'}_{jt or 'vaga'}.docx",mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                else: st.error(path)
        with tc2:
            if st.button("🔄 Regenerar",use_container_width=True): st.session_state.tailored_cv=None;st.rerun()

# ─────────────────────────────────────────
# COVER LETTER
# ─────────────────────────────────────────
def render_letter():
    st.markdown('<div class="page-title">✉️ Carta de Apresentação</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Gerada por IA para cada vaga específica · Nunca genérica · 4 tons disponíveis</div>',unsafe_allow_html=True)
    if not st.session_state.cv_data: st.info("Primeiro faça a Análise ATS."); return
    j=st.session_state.selected_job or {}
    c1,c2=st.columns(2)
    with c1: jt=st.text_input("Cargo",value=j.get("title",""),placeholder="Ex: Analista de Dados")
    with c2: jc=st.text_input("Empresa",value=j.get("company",""),placeholder="Ex: iFood")
    jd=st.text_area("Descrição (opcional)",value=j.get("description",""),height=100,placeholder="Cole a descrição para carta mais precisa...")
    tone=st.selectbox("Tom",["profissional","direto e confiante","entusiasta","formal"])
    if st.button("✉️ Gerar Carta",type="primary",use_container_width=True,disabled=not jt):
        with st.spinner("Escrevendo carta personalizada..."):
            letter=gen_cover_letter(st.session_state.cv_data["raw_text"],jt,jc,jd,gkey(),tone)
            st.session_state.cover_letter=letter
        st.rerun()
    if st.session_state.cover_letter:
        st.divider()
        edited=st.text_area("Edite se necessário:",value=st.session_state.cover_letter,height=320,key="letter_edit",label_visibility="collapsed")
        lc1,lc2=st.columns(2)
        with lc1: st.download_button("📥 Baixar .txt",data=edited,file_name=f"carta_{jc}_{jt}.txt",mime="text/plain")
        with lc2:
            if st.button("🔄 Regenerar",use_container_width=True): st.session_state.cover_letter=None;st.rerun()

# ─────────────────────────────────────────
# LINKEDIN
# ─────────────────────────────────────────
def render_linkedin():
    st.markdown('<div class="page-title">💼 LinkedIn Optimizer</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Headline · About · Skills · SEO · Score estimado</div>',unsafe_allow_html=True)
    if not st.session_state.cv_data: st.info("Primeiro faça a Análise ATS."); return
    if not st.session_state.linkedin_opt:
        if st.button("💼 Otimizar LinkedIn",type="primary",use_container_width=True):
            with st.spinner("Gerando otimizações..."):
                li=optimize_linkedin(st.session_state.cv_data["raw_text"],st.session_state.ats_result or {},gkey())
                st.session_state.linkedin_opt=li
            st.rerun()
        return
    li=st.session_state.linkedin_opt
    if li.get("error"):
        st.error("Erro ao otimizar LinkedIn.")
        st.write(li)
        if st.button("🔄 Tentar novamente"):
            st.session_state.linkedin_opt = None
            st.rerun()
        return
    sc_li=li.get("score_estimado",0)
    cs,ci=st.columns([1,3])
    with cs: st.markdown(score_ring(sc_li,"LinkedIn"),unsafe_allow_html=True)
    with ci:
        url_s=li.get("url_sugestao","")
        if url_s: st.markdown(f"**URL sugerida:** `linkedin.com/in/{url_s}`")
        st.markdown("**Top 10 Skills:**")
        st.markdown(tags(li.get("skills_top10",[]),"tag-tech"),unsafe_allow_html=True)
    st.divider()
    st.markdown("**🏷 Headline**")
    st.text_area("Principal:",value=li.get("headline",""),height=70,key="li_hl")
    for a in li.get("headline_alternativas",[]): st.markdown(f'<div style="color:var(--text2);font-size:.87rem;padding:2px 0;border-bottom:1px solid var(--border)">→ {a}</div>',unsafe_allow_html=True)
    st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
    st.markdown("**📝 Seção Sobre (About)**")
    about=li.get("about","")
    st.text_area("Cole no LinkedIn:",value=about,height=200,key="li_about")
    cl=len(about)
    st.markdown(f'<span style="color:{"#10B981" if cl<=2600 else "#EF4444"};font-size:.78rem">{cl}/2600 chars</span>',unsafe_allow_html=True)
    if li.get("palavras_chave_seo"):
        st.markdown('<div style="height:8px"></div>',unsafe_allow_html=True)
        st.markdown("**🔍 Keywords SEO**")
        st.markdown(tags(li.get("palavras_chave_seo",[]),"tag-found"),unsafe_allow_html=True)
    if li.get("dicas_perfil"):
        with st.expander("💡 Dicas de Perfil"):
            for d in li.get("dicas_perfil",[]): st.markdown(f"→ {d}")
    if st.button("🔄 Regenerar",use_container_width=True): st.session_state.linkedin_opt=None;st.rerun()

# ─────────────────────────────────────────
# INTERVIEW
# ─────────────────────────────────────────
def render_interview():
    st.markdown('<div class="page-title">🎤 Prep para Entrevista</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Perguntas reais de RH e técnicas · Dicas STAR · Armadilhas · Red flags</div>',unsafe_allow_html=True)
    if not st.session_state.cv_data: st.info("Primeiro faça a Análise ATS."); return
    j=st.session_state.selected_job or {}
    c1,c2=st.columns(2)
    with c1: jt=st.text_input("Cargo",value=j.get("title",""),placeholder="Ex: Analista de Dados",key="iv_t")
    with c2: jc=st.text_input("Empresa",value=j.get("company",""),placeholder="Ex: Magazine Luiza",key="iv_c")
    jd=st.text_area("Descrição (para perguntas técnicas precisas)",value=j.get("description",""),height=100,key="iv_d")
    if st.button("🎤 Gerar Prep",type="primary",use_container_width=True,disabled=not jt):
        with st.spinner("Gerando perguntas específicas..."):
            prep=gen_interview_prep(st.session_state.cv_data["raw_text"],jt,jc,jd,gkey())
            st.session_state.interview_prep=prep
        st.rerun()
    if not st.session_state.interview_prep: return
    prep=st.session_state.interview_prep
    if prep.get("error"):
        st.error("Erro ao gerar preparação de entrevista.")
        st.write(prep)
        return
    st.divider()
    st.markdown("#### 🤝 Perguntas de RH")
    for i,q in enumerate(prep.get("perguntas_rh",[])):
        with st.expander(f"**{i+1}. {q.get('pergunta','')}**",expanded=(i==0)):
            st.markdown(f'<div style="color:var(--text2);font-size:.87rem">💡 <b>Como responder:</b> {q.get("dica","")}</div>',unsafe_allow_html=True)
            if q.get("armadilha"): st.markdown(f'<div style="color:var(--warning);font-size:.82rem;margin-top:6px;font-style:italic">⚠️ Cuidado: {q["armadilha"]}</div>',unsafe_allow_html=True)
    st.markdown("#### 💻 Perguntas Técnicas")
    for i,q in enumerate(prep.get("perguntas_tecnicas",[])):
        with st.expander(f"**{i+1}. {q.get('pergunta','')}**"):
            ca2,cb3=st.columns(2)
            with ca2: st.markdown(f'<div style="color:var(--text2);font-size:.87rem">📚 {q.get("contexto","")}</div>',unsafe_allow_html=True)
            with cb3: st.markdown(f'<div style="color:var(--text2);font-size:.87rem">🎯 Nível: {q.get("nivel","")}</div>',unsafe_allow_html=True)
    st.divider()
    ec1,ec2=st.columns(2)
    with ec1:
        with st.expander("💰 Pretensão salarial"): st.markdown(prep.get("pretensao_dica",""))
        with st.expander("🔑 Maior fraqueza"): st.markdown(prep.get("fraqueza_sugerida",""))
    with ec2:
        with st.expander("❓ Perguntas para fazer à empresa"):
            for p in prep.get("perguntas_para_empresa",[]): st.markdown(f"→ {p}")
        with st.expander("🚫 O que NUNCA dizer"):
            for r in prep.get("red_flags",[]): st.markdown(f"✗ {r}")
    if prep.get("dica_geral"):
        st.markdown(f'<div class="verdict-box" style="margin-top:12px"><b style="color:var(--accent);font-size:.75rem;text-transform:uppercase">💡 Dica do Coach</b><p style="margin:8px 0 0">{prep["dica_geral"]}</p></div>',unsafe_allow_html=True)
    if st.button("🔄 Regenerar",use_container_width=True): st.session_state.interview_prep=None;st.rerun()

# ─────────────────────────────────────────
# CAREER DIAGNOSIS
# ─────────────────────────────────────────
def render_diagnosis():
    st.markdown('<div class="page-title">🧬 Diagnóstico de Carreira</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Posicionamento vs mercado · Gap para próximo nível · Plano de desenvolvimento · Salários reais</div>',unsafe_allow_html=True)
    if not st.session_state.cv_data: st.info("Primeiro faça a Análise ATS."); return
    target=st.text_input("Cargo que deseja alcançar",placeholder="Ex: Engenheiro de Dados Sênior")
    if st.button("🧬 Gerar Diagnóstico",type="primary",use_container_width=True,disabled=not target):
        with st.spinner("Analisando carreira e mercado..."):
            diag=career_diagnosis(st.session_state.cv_data["raw_text"],st.session_state.ats_result or {},target,gkey())
            st.session_state.career_diag=diag
        st.rerun()
    if not st.session_state.career_diag: return
    d=st.session_state.career_diag
    if d.get("error"): st.error("Erro ao processar."); return
    se_score=d.get("score_empregabilidade",0)
    dc1,dc2=st.columns([1,3])
    with dc1: st.markdown(score_ring(se_score,"Emp."),unsafe_allow_html=True)
    with dc2:
        st.markdown(f'<div style="font-family:Syne,sans-serif;font-weight:700;font-size:1rem;margin-bottom:8px">{d.get("posicao_mercado","")}</div>',unsafe_allow_html=True)
        dd1,dd2,dd3=st.columns(3)
        with dd1: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:var(--accent)">{d.get("meses_para_senior","")}</div><div class="stat-label">Meses p/ Sênior</div></div>',unsafe_allow_html=True)
        with dd2: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:#10B981;font-size:1rem">{d.get("salario_atual_mercado","")}</div><div class="stat-label">Salário Atual</div></div>',unsafe_allow_html=True)
        with dd3: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:var(--gold);font-size:1rem">{d.get("salario_senior_mercado","")}</div><div class="stat-label">Salário Sênior</div></div>',unsafe_allow_html=True)
    st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
    if d.get("gap_para_proximo_nivel"):
        st.markdown("**🎯 Gaps para o Próximo Nível**")
        st.markdown(tags(d.get("gap_para_proximo_nivel",[]),"tag-missing"),unsafe_allow_html=True)
    if d.get("plano_desenvolvimento"):
        st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
        st.markdown("**📋 Plano de Desenvolvimento**")
        for step in d.get("plano_desenvolvimento",[]):
            imp_color={"Alto":"#EF4444","Médio":"#F59E0B","Baixo":"#10B981"}.get(step.get("impacto",""),"var(--text)")
            st.markdown(f'<div class="intel-card" style="padding:14px 18px;margin-bottom:8px"><div style="display:flex;justify-content:space-between"><span style="font-weight:600">{step.get("acao","")}</span><span style="color:{imp_color};font-size:.82rem;font-weight:700">⬆ {step.get("impacto","")} impacto</span></div><div style="color:var(--text2);font-size:.83rem;margin-top:4px">⏱ {step.get("prazo","")} · 📚 {step.get("recurso","")}</div></div>',unsafe_allow_html=True)
    ra,rb=st.columns(2)
    with ra:
        if d.get("certificacoes_recomendadas"):
            st.markdown("**🏆 Certificações Recomendadas**")
            for c2 in d.get("certificacoes_recomendadas",[]): st.markdown(f"→ {c2}")
    with rb:
        if d.get("cursos_gratuitos"):
            st.markdown("**🆓 Cursos Gratuitos**")
            for c2 in d.get("cursos_gratuitos",[]): st.markdown(f"→ {c2}")
    if d.get("dica_aceleracao"):
        st.markdown(f'<div class="verdict-box" style="margin-top:12px"><b style="color:var(--accent);font-size:.75rem;text-transform:uppercase">🚀 Dica de Aceleração</b><p style="margin:8px 0 0">{d["dica_aceleracao"]}</p></div>',unsafe_allow_html=True)
    if st.button("🔄 Regenerar",use_container_width=True): st.session_state.career_diag=None;st.rerun()

# ─────────────────────────────────────────
# MARKET INTELLIGENCE
# ─────────────────────────────────────────
def render_market():
    st.markdown('<div class="page-title">📊 Inteligência de Mercado</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Demanda real · Faixa salarial · Empresas contratando · Skills emergentes · Tendências</div>',unsafe_allow_html=True)
    ats=st.session_state.ats_result
    default_cargo=""
    default_nivel="Pleno"
    if ats:
        cargos=ats.get("cargos_ideais",[])
        if cargos: default_cargo=cargos[0]
        default_nivel=ats.get("nivel_perfil","Pleno")
    mc1,mc2,mc3=st.columns(3)
    with mc1: cargo=st.text_input("Cargo",value=default_cargo,placeholder="Ex: Analista de Dados")
    with mc2: cidade=st.text_input("Cidade",placeholder="Ex: São Paulo")
    with mc3: nivel=st.selectbox("Nível",["Júnior","Pleno","Sênior","Especialista"],index=["Júnior","Pleno","Sênior","Especialista"].index(default_nivel) if default_nivel in ["Júnior","Pleno","Sênior","Especialista"] else 1)
    if st.button("📊 Analisar Mercado",type="primary",use_container_width=True,disabled=not cargo):
        with st.spinner("Coletando inteligência de mercado..."):
            data=market_intelligence(cargo,cidade,nivel,gkey())
            st.session_state.market_data=data
        st.rerun()
    if not st.session_state.market_data: return
    m=st.session_state.market_data
    if m.get("error"): st.error("Erro ao processar."); return
    st.divider()
    dem=m.get("demanda_atual","")
    tend=m.get("tendencia","")
    dem_color={"Alta":"#10B981","Média":"#F59E0B","Baixa":"#EF4444"}.get(dem,"var(--text)")
    tend_color={"Crescendo":"#10B981","Estável":"#F59E0B","Diminuindo":"#EF4444"}.get(tend,"var(--text)")
    ms1,ms2,ms3,ms4=st.columns(4)
    with ms1: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:{dem_color}">{dem}</div><div class="stat-label">Demanda</div></div>',unsafe_allow_html=True)
    with ms2: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:{tend_color}">{tend}</div><div class="stat-label">Tendência</div></div>',unsafe_allow_html=True)
    with ms3: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:#10B981;font-size:1rem">{m.get("salario_mediano","")}</div><div class="stat-label">Salário Mediano</div></div>',unsafe_allow_html=True)
    with ms4: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:var(--text2);font-size:1rem">{m.get("salario_minimo","")}–{m.get("salario_maximo","")}</div><div class="stat-label">Faixa Salarial</div></div>',unsafe_allow_html=True)
    st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
    ma,mb2=st.columns(2)
    with ma:
        if m.get("empresas_contratando"):
            st.markdown("**🏢 Empresas Contratando**")
            for e in m.get("empresas_contratando",[]): st.markdown(f"→ {e}")
        if m.get("setores_demandantes"):
            st.markdown('<div style="height:8px"></div>',unsafe_allow_html=True)
            st.markdown("**📁 Setores com Maior Demanda**")
            for s in m.get("setores_demandantes",[]): st.markdown(f"→ {s}")
    with mb2:
        if m.get("skills_mais_pedidas"):
            st.markdown("**⭐ Skills Mais Pedidas**")
            st.markdown(tags(m.get("skills_mais_pedidas",[]),"tag-tech"),unsafe_allow_html=True)
        if m.get("skills_emergentes"):
            st.markdown('<div style="height:8px"></div>',unsafe_allow_html=True)
            st.markdown("**🚀 Skills Emergentes**")
            st.markdown(tags(m.get("skills_emergentes",[]),"tag-soft"),unsafe_allow_html=True)
        if m.get("modalidades"):
            st.markdown('<div style="height:8px"></div>',unsafe_allow_html=True)
            st.markdown("**🏠 Modalidades de Trabalho**")
            mod=m.get("modalidades",{})
            for k,v in mod.items(): st.markdown(f"→ {k.capitalize()}: **{v}%**")
    if m.get("insight"):
        st.markdown(f'<div class="verdict-box" style="margin-top:12px"><b style="color:var(--accent);font-size:.75rem;text-transform:uppercase">💡 Insight de Mercado</b><p style="margin:8px 0 0">{m["insight"]}</p></div>',unsafe_allow_html=True)
    if m.get("melhor_momento_candidatura"):
        st.markdown(f'<div style="color:var(--text2);font-size:.87rem;margin-top:8px">📅 <b>Melhor momento:</b> {m["melhor_momento_candidatura"]}</div>',unsafe_allow_html=True)
    if st.button("🔄 Regenerar",use_container_width=True): st.session_state.market_data=None;st.rerun()

# ─────────────────────────────────────────
# NETWORKING
# ─────────────────────────────────────────
def render_networking():
    st.markdown('<div class="page-title">🤝 Networking Email</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Email personalizado para funcionários da empresa alvo · Pedido de indicação ou conversa</div>',unsafe_allow_html=True)
    if not st.session_state.cv_data: st.info("Primeiro faça a Análise ATS."); return
    nc1,nc2=st.columns(2)
    with nc1: company=st.text_input("Empresa alvo",placeholder="Ex: Nubank, iFood, PicPay")
    with nc2: role=st.text_input("Cargo que deseja",placeholder="Ex: Analista de Dados Pleno")
    contact=st.text_input("Nome do contato (opcional)",placeholder="Ex: João Silva — Data Engineer no LinkedIn")
    if st.button("✉️ Gerar Email de Networking",type="primary",use_container_width=True,disabled=not(company and role)):
        with st.spinner("Escrevendo email personalizado..."):
            email=gen_networking_email(st.session_state.cv_data["raw_text"],company,role,contact,gkey())
            st.session_state.networking_email=email
        st.rerun()
    if st.session_state.networking_email:
        st.divider()
        edited=st.text_area("Email (editável):",value=st.session_state.networking_email,height=280,key="net_edit",label_visibility="collapsed")
        nc_a,nc_b=st.columns(2)
        with nc_a: st.download_button("📥 Baixar .txt",data=edited,file_name=f"networking_{company}.txt",mime="text/plain")
        with nc_b:
            if st.button("🔄 Regenerar",use_container_width=True): st.session_state.networking_email=None;st.rerun()

# ─────────────────────────────────────────
# FUNNEL
# ─────────────────────────────────────────
def render_funnel():
    st.markdown('<div class="page-title">📋 Funil de Candidaturas</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Kanban visual · Acompanhe todas as candidaturas · Dados salvos localmente</div>',unsafe_allow_html=True)
    if st.session_state.funnel is None: st.session_state.funnel=load_funnel()
    fn=st.session_state.funnel
    with st.expander("➕ Adicionar Manualmente"):
        fa,fb,fc=st.columns(3)
        with fa: mt=st.text_input("Cargo",key="mt")
        with fb: mc=st.text_input("Empresa",key="mc")
        with fc: mu=st.text_input("Link",key="mu")
        ms2=st.selectbox("Status",list(fn.keys()),key="ms2")
        if st.button("Adicionar",key="madd"):
            if mt:
                fn[ms2].append({"title":mt,"company":mc,"url":mu,"source":"Manual","added":datetime.now().strftime("%d/%m/%Y"),"notes":""})
                save_funnel(fn); st.session_state.funnel=fn; st.rerun()
    st.divider()
    total=sum(len(v) for v in fn.values())
    ap=len(fn.get("Aplicado",[])); ent=len(fn.get("Entrevista",[])); of=len(fn.get("Oferta",[]))
    fs1,fs2,fs3,fs4=st.columns(4)
    with fs1: st.markdown(f'<div class="stat-card"><div class="stat-value">{total}</div><div class="stat-label">Total</div></div>',unsafe_allow_html=True)
    with fs2: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:var(--primary)">{ap}</div><div class="stat-label">Aplicadas</div></div>',unsafe_allow_html=True)
    with fs3: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:var(--gold)">{ent}</div><div class="stat-label">Entrevistas</div></div>',unsafe_allow_html=True)
    with fs4: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:var(--success)">{of}</div><div class="stat-label">Ofertas</div></div>',unsafe_allow_html=True)
    st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
    col_colors={"Interesse":"#2563EB","Aplicado":"#7C3AED","Entrevista":"#D97706","Oferta":"#059669","Recusado":"#DC2626"}
    cols=st.columns(5)
    for idx,(status,color) in enumerate(col_colors.items()):
        items=fn.get(status,[])
        with cols[idx]:
            st.markdown(f'<div class="kanban-title" style="color:{color}">● {status.upper()} ({len(items)})</div>',unsafe_allow_html=True)
            for i,item in enumerate(items):
                url2=item.get("url",""); ms3=item.get("match","")
                link_html=f'<a href="{url2}" target="_blank" style="color:var(--accent);font-size:.72rem">🔗</a>' if url2 else ""
                match_html=f'<span style="color:var(--success);font-size:.72rem">⚡{ms3}%</span>' if ms3 else ""
                st.markdown(f'<div class="kanban-card"><div style="font-weight:600;font-size:.83rem">{item.get("title","")[:28]}{"..." if len(item.get("title",""))>28 else ""}</div><div style="color:var(--text3);font-size:.75rem">{item.get("company","")}</div><div style="margin-top:4px;display:flex;gap:6px">{link_html}{match_html}</div><div style="color:var(--text3);font-size:.7rem">{item.get("added","")}</div></div>',unsafe_allow_html=True)
                oc1,oc2=st.columns(2)
                with oc1:
                    others=[s for s in fn.keys() if s!=status]
                    ns=st.selectbox("→",others,key=f"mv_{status}_{i}",label_visibility="collapsed")
                with oc2:
                    if st.button("Move",key=f"mvb_{status}_{i}"):
                        fn[ns].append(item); fn[status].pop(i)
                        save_funnel(fn); st.session_state.funnel=fn; st.rerun()
            if st.button(f"🗑 Limpar",key=f"cl_{status}",use_container_width=True):
                fn[status]=[]; save_funnel(fn); st.session_state.funnel=fn; st.rerun()

# ─────────────────────────────────────────
# A/B TEST
# ─────────────────────────────────────────
def render_abtest():
    st.markdown('<div class="page-title">🔬 A/B Teste de CV</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Compare 2 versões do seu CV · Veja qual tem maior match score nas vagas encontradas</div>',unsafe_allow_html=True)
    if not st.session_state.jobs_found: st.info("Primeiro busque vagas para ter base de comparação."); return
    ab=st.session_state.abtest or load_abtest()
    st.session_state.abtest=ab
    abt1,abt2=st.tabs(["📄 CV A (Versão Atual)","📄 CV B (Versão Alternativa)"])
    with abt1:
        cv_a=st.text_area("Cole o CV A:",value=ab.get("cv_a",""),height=300,key="ab_a")
    with abt2:
        cv_b=st.text_area("Cole o CV B (versão com alterações):",value=ab.get("cv_b",""),height=300,key="ab_b")
    if st.button("🔬 Executar Teste A/B",type="primary",use_container_width=True,disabled=not(cv_a and cv_b)):
        with st.spinner("Calculando match para ambas as versões..."):
            jobs=st.session_state.jobs_found[:20]
            from scrapers.scrapers import local_match
            import re as re2
            def get_kws(text):
                words=re2.findall(r'\b[A-Za-zÀ-ÿ]{4,}\b',text)
                return list(set(words))[:30]
            kws_a=get_kws(cv_a); kws_b=get_kws(cv_b)
            res_a=[{"match_score":local_match(j,kws_a)} for j in jobs]
            res_b=[{"match_score":local_match(j,kws_b)} for j in jobs]
            comparison=abtest_compare(res_a,res_b)
            ab["cv_a"]=cv_a; ab["cv_b"]=cv_b
            ab["results"]={"a":res_a,"b":res_b,"comparison":comparison}
            save_abtest(ab); st.session_state.abtest=ab
        st.rerun()
    if ab.get("results") and ab["results"].get("comparison"):
        comp=ab["results"]["comparison"]
        st.divider()
        winner=comp.get("winner","A")
        wcolor="#10B981"
        st.markdown(f'<div style="background:rgba(16,185,129,.1);border:1px solid #10B981;border-radius:14px;padding:16px 24px;text-align:center"><div style="font-family:Syne,sans-serif;font-weight:800;font-size:1.3rem;color:{wcolor}">🏆 CV {winner} é o VENCEDOR</div><div style="color:var(--text2);margin-top:4px">{comp.get("recommendation","")}</div><div style="color:var(--text3);font-size:.82rem;margin-top:4px">Confiança: {comp.get("confidence","")}</div></div>',unsafe_allow_html=True)
        st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
        ra2,rb2=st.columns(2)
        with ra2: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:{"#10B981" if winner=="A" else "var(--text2)"}">{comp.get("avg_a",0)}</div><div class="stat-label">Match Médio CV A</div></div>',unsafe_allow_html=True)
        with rb2: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:{"#10B981" if winner=="B" else "var(--text2)"}">{comp.get("avg_b",0)}</div><div class="stat-label">Match Médio CV B</div></div>',unsafe_allow_html=True)

# ─────────────────────────────────────────
# ALERTS
# ─────────────────────────────────────────
def render_alerts():
    st.markdown('<div class="page-title">🔔 Alertas de Vagas</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Configure alertas · Serão verificados automaticamente ao buscar vagas</div>',unsafe_allow_html=True)
    if st.session_state.alerts is None: st.session_state.alerts=load_alerts()
    alerts=st.session_state.alerts
    with st.expander("➕ Criar Novo Alerta",expanded=True):
        alc1,alc2=st.columns(2)
        with alc1: al_name=st.text_input("Nome do alerta",placeholder="Ex: Vagas Dados SP")
        with alc2: al_cargo=st.text_input("Cargo (contém)",placeholder="Ex: Dados, Analista")
        alc3,alc4=st.columns(2)
        with alc3: al_kws=st.text_input("Keywords adicionais (vírgula)",placeholder="Ex: Python, SQL")
        with alc4: al_match=st.slider("Match mínimo",50,90,70,key="al_match")
        if st.button("➕ Criar Alerta",use_container_width=True):
            if al_name:
                alerts.append({"name":al_name,"cargo":al_cargo,"keywords":[k.strip() for k in al_kws.split(",") if k.strip()],"min_match":al_match,"created":str(date.today())})
                save_alerts(alerts); st.session_state.alerts=alerts; st.success(f"Alerta '{al_name}' criado!"); st.rerun()
    st.divider()
    if not alerts: st.info("Nenhum alerta configurado ainda."); return
    st.markdown(f"**{len(alerts)} alerta(s) ativo(s)**")
    for i,alert in enumerate(alerts):
        st.markdown(f'<div class="alert-card"><div style="display:flex;justify-content:space-between;align-items:center"><div><b style="color:var(--gold)">{alert["name"]}</b><div style="color:var(--text2);font-size:.83rem;margin-top:2px">Cargo: {alert.get("cargo","qualquer")} · Match ≥ {alert.get("min_match",70)}% · Keywords: {", ".join(alert.get("keywords",[])[:3]) or "nenhuma"}</div></div></div></div>',unsafe_allow_html=True)
        if st.button(f"🗑 Remover",key=f"rm_alert_{i}"):
            alerts.pop(i); save_alerts(alerts); st.session_state.alerts=alerts; st.rerun()
    if st.session_state.jobs_found:
        cv_kws=(st.session_state.ats_result or {}).get("palavras_chave_encontradas",[])
        triggered=check_alerts(st.session_state.jobs_found,alerts,cv_kws)
        if triggered:
            st.markdown(f'<div style="height:12px"></div>',unsafe_allow_html=True)
            st.markdown(f"**🔔 {len(triggered)} vagas ativaram alertas:**")
            for t in triggered:
                j=t["job"]
                url3=j.get("url","")
                link=f"[🔗 Ver]({url3})" if url3 else ""
                st.markdown(f'<div style="padding:8px 0;border-bottom:1px solid var(--border)"><b>{j.get("title","")}</b> — {j.get("company","")} · {mbadge(t["match_score"])} · {badge_src(j.get("source",""))} {link}</div>',unsafe_allow_html=True)

# ─────────────────────────────────────────
# WEEKLY REPORT
# ─────────────────────────────────────────
def render_report():
    st.markdown('<div class="page-title">📈 Relatório Semanal</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Progresso da semana · Taxa de conversão · Score de empregabilidade · Próxima meta</div>',unsafe_allow_html=True)
    funnel=st.session_state.funnel or load_funnel()
    history=st.session_state.history or load_history()
    ats=st.session_state.ats_result or {}
    emp=st.session_state.emp_score or calc_employability_score(ats,funnel,history)
    if st.button("📈 Gerar Relatório",type="primary",use_container_width=True):
        report=generate_weekly_report(funnel,history,ats,emp)
        st.session_state.weekly_report=report
        st.rerun()
    if not st.session_state.weekly_report: return
    r=st.session_state.weekly_report
    st.divider()
    rr1,rr2,rr3,rr4,rr5=st.columns(5)
    with rr1: st.markdown(f'<div class="stat-card"><div class="stat-value">{r.get("total_no_funil",0)}</div><div class="stat-label">No Funil</div></div>',unsafe_allow_html=True)
    with rr2: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:var(--primary)">{r.get("aplicadas_semana",0)}</div><div class="stat-label">Semana</div></div>',unsafe_allow_html=True)
    with rr3: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:var(--gold)">{r.get("entrevistas",0)}</div><div class="stat-label">Entrevistas</div></div>',unsafe_allow_html=True)
    with rr4: st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:var(--success)">{r.get("ofertas",0)}</div><div class="stat-label">Ofertas</div></div>',unsafe_allow_html=True)
    with rr5:
        conv=r.get("taxa_conversao",0)
        cc={"high":"#10B981","mid":"#F59E0B","low":"#EF4444"}[sc(int(conv))]
        st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:{cc}">{conv}%</div><div class="stat-label">Conversão</div></div>',unsafe_allow_html=True)
    st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
    if r.get("destaque"):
        st.markdown(f'<div class="verdict-box"><b style="color:var(--accent);font-size:.75rem;text-transform:uppercase">✨ Destaque da Semana</b><p style="margin:8px 0 0;font-size:1rem">{r["destaque"]}</p></div>',unsafe_allow_html=True)
    if r.get("proxima_meta"):
        st.markdown(f'<div style="margin-top:12px;padding:14px 18px;background:var(--surface2);border:1px solid var(--border);border-radius:12px"><b style="color:var(--gold)">🎯 Próxima Meta</b><p style="margin:6px 0 0;color:var(--text2)">{r["proxima_meta"]}</p></div>',unsafe_allow_html=True)

# ─────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────
def render_settings():
    st.markdown('<div class="page-title">⚙️ Configurações</div>',unsafe_allow_html=True)
    cfg=st.session_state.user_config
    st.text_input("Nome",value=cfg.get("username",""),disabled=True)
    st.markdown("**🔑 Groq API Key**")
    cur=cfg.get("groq_api_key","")
    masked=cur[:8]+"..."+cur[-4:] if len(cur)>12 else "***"
    st.caption(f"Atual: `{masked}`")
    nk=st.text_input("Nova API Key (vazio = manter)",type="password")
    cp2=st.text_input("Senha atual (obrigatório)",type="password")
    if st.button("💾 Salvar",use_container_width=True):
        if not cp2: st.error("Informe a senha."); return
        updates={}
        if nk: updates["groq_api_key"]=nk
        if updates:
            if update_config(cp2,updates):
                st.success("Salvo!")
                new_cfg=login_user(cp2)
                if new_cfg: st.session_state.user_config=new_cfg
            else: st.error("Senha incorreta.")
        else: st.info("Nenhuma alteração.")
    st.divider()
    st.markdown("**ℹ️ Applymize Premium v3.0**")
    st.caption("Dados em `~/.applymize/` — nunca enviados a servidores externos.")
    st.caption("IA: LLaMA 3 70B via Groq API (gratuita)")
    st.markdown("🔗 [Obter Groq API Key](https://console.groq.com)")

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    if "cv_data" not in st.session_state:
        st.session_state.cv_data = load_cv_profile()

    if not st.session_state.logged_in:
        render_auth(); return
    render_sidebar()
    routes={
        "dashboard":render_dashboard,"ats":render_ats,"jobs":render_jobs,
        "match":render_match,"campaign":render_campaign,"cv":render_cv,
        "tailor":render_tailor,"letter":render_letter,"linkedin":render_linkedin,
        "interview":render_interview,"diagnosis":render_diagnosis,"market":render_market,
        "networking":render_networking,"funnel":render_funnel,"abtest":render_abtest,
        "alerts":render_alerts,"report":render_report,"settings":render_settings,
    }
    routes.get(st.session_state.active_tab,render_dashboard)()

if __name__=="__main__":
    main()
