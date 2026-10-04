import os
import glob
import re
import math
import base64
import unicodedata
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ----------------- ตั้งค่าฟอนต์ภาษาไทยสำหรับ Matplotlib -----------------
# 1) โหลดไฟล์ฟอนต์ที่แนบมากับโปรเจกต์ (โฟลเดอร์ fonts/ เช่น Sarabun-Regular.ttf, Sarabun-Bold.ttf)
# 2) ถ้าไม่มี จะไล่หาฟอนต์ไทยที่มีในระบบทั้ง Windows / macOS / Linux
def setup_thai_font():
    font_dir = os.path.join(BASE_DIR, "fonts")
    if os.path.isdir(font_dir):
        for fp in glob.glob(os.path.join(font_dir, "*.ttf")) + glob.glob(os.path.join(font_dir, "*.otf")):
            try:
                fm.fontManager.addfont(fp)
            except Exception:
                pass

    thai_fonts = [
        'Sarabun', 'Noto Sans Thai', 'Noto Serif Thai',
        'Tahoma', 'Leelawadee UI', 'Leelawadee', 'Angsana New', 'Cordia New',
        'Thonburi', 'Ayuthaya',
        'Garuda', 'Loma', 'Waree', 'Norasi', 'Tlwg Typo', 'Tlwg Typist',
        'Segoe UI', 'DejaVu Sans'
    ]
    available_fonts = {f.name for f in fm.fontManager.ttflist}
    for font in thai_fonts:
        if font in available_fonts:
            plt.rcParams['font.family'] = font
            break
    plt.rcParams['axes.unicode_minus'] = False

setup_thai_font()

# ----------------- ตั้งค่าหน้าเพจ -----------------
st.set_page_config(
    page_title="POLI SPECTRA | แบบประเมินจุดยืนทางการเมือง",
    page_icon="🧭",
    layout="centered"
)

# ----------------- CSS สไตล์ UI สว่าง คลีน เน้นสีแดงพรีเมียม -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], * {
        font-family: 'Sarabun', sans-serif !important;
    }
    
    .stApp {
        background-color: #fafbfc !important;
        color: #1e293b !important;
    }
    
    /* Hero Banner โทนแดงพรีเมียมสว่าง */
    .hero-banner-red {
        background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 50%, #fecdd3 100%);
        border-radius: 20px;
        padding: 32px 24px;
        text-align: center;
        margin-bottom: 25px;
        border: 1px solid #fecdd3;
        box-shadow: 0 4px 20px rgba(225, 29, 72, 0.05);
    }
    
    .tag-badge-red {
        background-color: #ffe4e6;
        color: #e11d48;
        font-size: 13px;
        font-weight: 700;
        padding: 5px 14px;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 12px;
        border: 1px solid #fecdd3;
    }
    
    /* Main Card สีขาว สว่าง สบายตา */
    .main-card-light {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #f1f5f9;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
    }
    
    /* กล่องสรุปตัวเลข 15 ข้อด้านขวา */
    .metric-card-red {
        background: linear-gradient(145deg, #be123c 0%, #9f1239 100%);
        color: #ffffff !important;
        border-radius: 16px;
        padding: 28px 20px;
        text-align: center;
        box-shadow: 0 8px 22px rgba(190, 18, 60, 0.22);
    }
    
    /* ตัวหนังสือตัวเลือก Radio ให้ชัดเจน 100% ไม่จม */
    div[data-testid="stRadio"] label p {
        font-size: 15px !important;
        font-weight: 500 !important;
        color: #1e293b !important;
    }
    /* ===== หน้าคำถามแบบใหม่ ===== */
    .qh-live { display:flex; align-items:center; gap:8px; font-size:11.5px; font-weight:700; letter-spacing:1.2px; color:#be123c; padding-top:10px; }
    .qh-live-dot { width:9px; height:9px; border-radius:50%; background:#e11d48; display:inline-block; }
    .qh-right { display:flex; justify-content:flex-end; align-items:center; gap:12px; }
    .qh-right-text { text-align:right; line-height:1.35; }
    .qh-count { font-size:14px; font-weight:800; color:#0f172a; }
    .qh-remain { font-size:11.5px; color:#64748b; }
    .qh-badge {
        width:44px; height:44px; border-radius:14px; background:#ffe4e6; color:#be123c;
        display:flex; align-items:center; justify-content:center; font-size:20px; font-weight:800; flex:none;
    }
    .qp-card { background:#ffffff; border:1px solid #f1f5f9; border-radius:18px; padding:16px 16px 14px 16px; box-shadow:0 4px 18px rgba(0,0,0,0.04); margin:6px 0 18px 0; }
    .qp-track { width:100%; height:7px; background:#ffe4e6; border-radius:6px; overflow:hidden; }
    .qp-fill { height:100%; border-radius:6px; background:linear-gradient(90deg,#fb7185,#be123c); }
    .step-row { display:flex; gap:6px; margin-top:14px; overflow-x:auto; padding-bottom:4px; }
    .step-chip { flex:1 0 54px; background:#f8fafc; border-radius:10px; padding:7px 8px 6px 8px; color:#94a3b8; }
    .step-top { display:flex; justify-content:space-between; align-items:center; font-size:11px; font-weight:700; height:16px; }
    .step-bar { height:3px; border-radius:3px; background:#e2e8f0; margin-top:6px; }
    .step-dot { width:5px; height:5px; border-radius:50%; background:#cbd5e1; display:inline-block; }
    .step-chip.done { background:#fff1f2; color:#be123c; }
    .step-chip.done .step-bar { background:#e11d48; }
    .step-chip.cur { background:linear-gradient(135deg,#be123c 0%,#881337 100%); color:#ffffff; }
    .step-chip.cur .step-bar { background:#fecdd3; }
    .step-chip.cur .step-dot { background:#fecdd3; }
    .q-card { background:#ffffff; border:1px solid #f1f5f9; border-radius:20px; padding:22px 24px 16px 24px; box-shadow:0 4px 18px rgba(0,0,0,0.04); margin-bottom:14px; }
    .q-icon-chip { width:40px; height:30px; border-radius:15px; background:#ffe4e6; display:inline-flex; align-items:center; justify-content:center; }
    .q-count { font-size:13px; font-weight:700; color:#be123c; margin-top:16px; }
    .q-text { font-size:21px; font-weight:700; color:#0f172a; line-height:1.6; margin-top:6px; }
    .q-hint { font-size:13px; color:#64748b; margin-top:14px; }

    /* ===== การ์ดเดียวรวมคำถาม + ตัวเลือก + แถบปุ่ม ===== */
    .st-key-quizcard {
        background:#ffffff; border:1px solid #f1f5f9; border-radius:20px;
        padding:24px 24px 0 24px !important; box-shadow:0 4px 18px rgba(0,0,0,0.05);
        overflow:hidden; gap:0.6rem !important; counter-reset: opt;
    }
    .st-key-quizcard [class*="st-key-opt"] .stButton > button {
        counter-increment: opt;
        display:flex !important; align-items:center !important; justify-content:flex-start !important;
        gap:14px; text-align:left !important; width:100%;
        background:#ffffff !important; color:#1e293b !important;
        border:1px solid #f1f5f9 !important; border-radius:14px !important;
        padding:14px 16px !important; min-height:56px; height:auto !important;
        box-shadow:0 1px 4px rgba(0,0,0,0.03) !important; transition:all 0.15s ease;
    }
    .st-key-quizcard [class*="st-key-opt"] .stButton > button::before {
        content: counter(opt);
        width:28px; height:28px; border-radius:50%; flex:none;
        background:#ffe4e6; color:#be123c; font-size:12.5px; font-weight:700;
        display:flex; align-items:center; justify-content:center;
    }
    .st-key-quizcard [class*="st-key-opt"] .stButton > button > div { flex:1; text-align:left !important; justify-content:flex-start !important; }
    .st-key-quizcard [class*="st-key-opt"] .stButton > button p {
        text-align:left !important; margin:0 !important; font-size:15px !important; font-weight:500 !important; color:#1e293b !important; line-height:1.5;
    }
    .st-key-quizcard [class*="st-key-opt"] .stButton > button:hover { border-color:#fecdd3 !important; background:#fff7f8 !important; }
    .st-key-quizcard [class*="st-key-optsel"] .stButton > button,
    .st-key-quizcard [class*="st-key-optsel"] .stButton > button:hover {
        border-color:#e11d48 !important; background:#fff1f2 !important; box-shadow:0 4px 14px rgba(225,29,72,0.14) !important;
    }
    .st-key-quizcard [class*="st-key-optsel"] .stButton > button::before { background:linear-gradient(135deg,#e11d48 0%,#be123c 100%); color:#ffffff; }
    .st-key-quizcard [class*="st-key-optsel"] .stButton > button p { color:#881337 !important; font-weight:700 !important; }
    .st-key-quizfoot {
        background:#fff7f8; border-top:1px solid #ffe4e6;
        margin:12px -24px 0 -24px; width:calc(100% + 48px) !important; padding:16px 24px !important;
    }
    .save-note { text-align:right; font-size:12px; color:#94a3b8; padding-top:12px; }

    /* ปุ่มกดหลักโทนแดง */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 14px rgba(225, 29, 72, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%) !important;
        box-shadow: 0 6px 18px rgba(225, 29, 72, 0.35) !important;
        transform: translateY(-1px) !important;
    }
    div.stButton > button[kind="primary"]:disabled {
        background: #e2e8f0 !important;
        color: #94a3b8 !important;
        box-shadow: none !important;
        transform: none !important;
    }
    
    /* ปุ่มย้อนกลับ/ปุ่มรอง */
    div.stButton > button[kind="secondary"] {
        background-color: #ffffff !important;
        color: #475569 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        padding: 9px 20px !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #cbd5e1 !important;
        color: #0f172a !important;
        background-color: #f8fafc !important;
    }

    /* การ์ดบุคคลสำคัญ */
    .person-card-complete {
        background: #ffffff;
        border: 1px solid #f1f5f9;
        border-radius: 16px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
        margin-bottom: 15px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        min-height: 520px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .person-card-complete:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(225, 29, 72, 0.1);
    }
    
    /* กรอบรูปภาพ: บังคับให้ขนาดเท่ากัน 100% ทั้ง 3 ใบ */
    .person-img-wrapper {
        width: 100%;
        height: 220px !important;
        min-height: 220px !important;
        max-height: 220px !important;
        border-radius: 12px;
        overflow: hidden;
        margin: 12px 0;
        background-color: #f8fafc;
        border: 1px solid #f1f5f9;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .person-img-wrapper img {
        width: 100% !important;
        height: 100% !important;
        object-fit: cover !important;
        object-position: top center !important; /* จัดช่วงศีรษะให้อยู่ตรงกลางกรอบ */
        display: block;
    }
    
    .quote-box-red {
        font-size: 12.5px;
        color: #475569;
        background: #fff1f2;
        padding: 10px 12px;
        border-radius: 8px;
        border-left: 3px solid #e11d48;
        margin-top: 8px;
        text-align: left;
        line-height: 1.5;
        min-height: 104px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: flex-start;
        gap: 4px;
    }
    .fact-label { font-size: 11px; font-weight: 800; color: #be123c; letter-spacing: 0.3px; }
    .fact-text { font-size: 12.5px; color: #475569; }
    .stat-badge-red {
        background: #ffe4e6;
        color: #be123c;
        font-size: 11.5px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 12px;
        display: inline-block;
        margin-bottom: 4px;
    }
    
    /* แถบเปอร์เซ็นต์ความสอดคล้อง */
    .bar-track {
        width: 100%;
        height: 7px;
        background: #f1f5f9;
        border-radius: 6px;
        overflow: hidden;
        margin-top: 4px;
    }
    .bar-fill {
        height: 100%;
        border-radius: 6px;
        background: linear-gradient(90deg, #fb7185, #e11d48);
    }
    /* ===== สเปกตรัม 7 อุดมการณ์ + Affinity Index ===== */
    .spec-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 24px;
        border: 1px solid #f1f5f9;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.04);
        margin: 10px 0 24px 0;
    }
    .spec-title { color: #0f172a; font-size: 22px; font-weight: 800; line-height: 1.3; }
    .spec-sub { color: #64748b; font-size: 13.5px; margin-top: 4px; }
    .spec-main-chip {
        display: inline-block; margin-top: 10px;
        background: #fff1f2; color: #be123c; border: 1px solid #fecdd3;
        font-size: 12px; font-weight: 700; padding: 4px 12px; border-radius: 12px;
    }
    .spec-bar-wrap { position: relative; margin-top: 46px; }
    .spec-bar { display: flex; height: 34px; border-radius: 6px; overflow: hidden; }
    .spec-seg { flex: 1; }
    .spec-dot {
        position: absolute; top: 50%; width: 20px; height: 20px; border-radius: 50%;
        background: #ffffff; border: 5px solid #0f172a;
        transform: translate(-50%, -50%); box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    .spec-marker-label {
        position: absolute; top: -36px; transform: translateX(-50%);
        background: #1e293b; color: #ffffff; font-size: 12px; font-weight: 700;
        padding: 5px 12px; border-radius: 14px; white-space: nowrap;
    }
    .spec-labels { display: flex; margin-top: 8px; }
    .spec-lab { flex: 1; text-align: center; font-size: 11.5px; color: #64748b; padding: 3px 0; border-radius: 4px; }
    .spec-lab-active { background: #ffe4e6; color: #be123c; font-weight: 700; }
    .aff-box { background: #f8fafc; border: 1px solid #f1f5f9; border-radius: 16px; padding: 16px; margin-top: 22px; }
    .aff-box-title { font-size: 15px; font-weight: 700; color: #1e293b; }
    .aff-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 12px; }
    .aff-card { background: #ffffff; border-radius: 12px; padding: 12px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06); }
    .aff-head { display: flex; justify-content: space-between; gap: 6px; }
    .aff-name { font-size: 12px; font-weight: 700; color: #0f172a; line-height: 1.35; }
    .aff-val { font-size: 12px; font-weight: 700; }
    .aff-track { height: 6px; background: #e2e8f0; border-radius: 4px; overflow: hidden; margin: 8px 0 6px 0; }
    .aff-fill { height: 100%; border-radius: 4px; }
    .aff-level { font-size: 12px; font-weight: 700; }
    .aff-note { font-size: 11.5px; color: #64748b; line-height: 1.4; margin-top: 2px; }
    .aff-balance {
        background: linear-gradient(145deg, #be123c 0%, #881337 100%);
        color: #ffffff; border-radius: 12px; padding: 14px;
        display: flex; flex-direction: column; justify-content: center;
    }
    .aff-bal-kicker { font-size: 10px; letter-spacing: 1px; font-weight: 700; color: #fecdd3; }
    .aff-bal-title { font-size: 17px; font-weight: 800; margin: 4px 0 6px 0; line-height: 1.25; }
    .aff-bal-desc { font-size: 11.5px; line-height: 1.45; color: #ffe4e6; }
    /* ===== แกนสเปกตรัมหน้าแรก (ภาพนิ่ง) ===== */
    .cont-card {
        background: #ffffff;
        border: 1px solid #f1f5f9;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.04);
        margin-top: 24px;
    }
    .cont-kicker { display: flex; align-items: center; gap: 8px; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; color: #be123c; }
    .cont-kicker-dot { width: 8px; height: 8px; border-radius: 50%; background: #dc2626; }
    .cont-title { font-size: 28px; font-weight: 800; color: #0f172a; margin-top: 6px; line-height: 1.25; }
    .cont-sub { font-size: 13.5px; color: #64748b; margin-top: 6px; line-height: 1.55; max-width: 540px; }
    .cont-scroll { overflow-x: auto; margin-top: 18px; background: #f8fafc; border-radius: 16px; }
    .cont-stage { position: relative; display: flex; min-width: 620px; height: 310px; padding: 0 16px; }
    .cont-col { flex: 1; display: flex; flex-direction: column; align-items: center; }
    .cont-half { flex: 1; display: flex; flex-direction: column; align-items: center; width: 100%; }
    .cont-top { justify-content: flex-end; }
    .cont-bottom { justify-content: flex-start; }
    .cont-gap { height: 22px; flex: none; }
    .cont-axis {
        position: absolute; left: 30px; right: 30px; top: 50%; height: 18px; transform: translateY(-50%);
        background: linear-gradient(90deg, #1e3a8a 0%, #0284c7 40%, #475569 70%, #dc2626 100%);
        display: flex; align-items: center; justify-content: space-between; padding: 0 12px;
        color: #ffffff; font-size: 10px; font-weight: 800; letter-spacing: 1px;
    }
    .cont-axis::before {
        content: ""; position: absolute; left: -14px; top: 50%; transform: translateY(-50%);
        border-top: 14px solid transparent; border-bottom: 14px solid transparent; border-right: 16px solid #1e3a8a;
    }
    .cont-axis::after {
        content: ""; position: absolute; right: -14px; top: 50%; transform: translateY(-50%);
        border-top: 14px solid transparent; border-bottom: 14px solid transparent; border-left: 16px solid #dc2626;
    }
    .cont-icon { width: 46px; height: 46px; border-radius: 14px; display: flex; align-items: center; justify-content: center; margin: 8px 0; }
    .cont-en { font-size: 11.5px; font-weight: 800; letter-spacing: 0.3px; color: #1e293b; white-space: nowrap; }
    .cont-th { font-size: 10.5px; font-weight: 700; white-space: nowrap; margin-top: 1px; }
    .cont-dot { width: 12px; height: 12px; border-radius: 50%; border: 3px solid #0f172a; background: #ffffff; margin: 7px 0; }
    /* ===== การ์ดอธิบาย 7 อุดมการณ์ (หน้าแรก ภาพนิ่ง) ===== */
    .ideo-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(215px, 1fr)); gap: 14px; margin-top: 16px; }
    .ideo-card { background: #fff7f8; border: 1px solid #ffe4e6; border-radius: 18px; padding: 18px; display: flex; flex-direction: column; }
    .ideo-top { display: flex; justify-content: space-between; align-items: center; gap: 6px; }
    .ideo-tag { display: inline-flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 700; padding: 4px 10px 4px 7px; border-radius: 14px; line-height: 1.2; }
    .ideo-idx { font-size: 10.5px; color: #94a3b8; font-weight: 600; white-space: nowrap; }
    .ideo-th { font-size: 21px; font-weight: 800; color: #0f172a; margin-top: 14px; line-height: 1.25; }
    .ideo-en { font-size: 10.5px; font-weight: 800; letter-spacing: 0.6px; margin-top: 3px; }
    .ideo-desc { font-size: 12.5px; color: #475569; line-height: 1.6; margin-top: 10px; flex: 1; }
    .ideo-val { background: #ffffff; border: 1px solid #ffe4e6; border-radius: 12px; padding: 10px 12px; margin-top: 14px; }
    .ideo-val-title { font-size: 11px; font-weight: 800; color: #0f172a; }
    .ideo-val-text { font-size: 11.5px; color: #475569; margin-top: 5px; line-height: 1.5; }
    .ideo-insight { background: linear-gradient(145deg, #be123c 0%, #881337 100%); color: #ffffff; border-radius: 18px; padding: 20px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 8px 22px rgba(190, 18, 60, 0.22); }
    .ideo-insight-kicker { font-size: 10.5px; font-weight: 700; letter-spacing: 1.2px; color: #fecdd3; }
    .ideo-insight-title { font-size: 20px; font-weight: 800; margin-top: 8px; line-height: 1.3; }
    .ideo-insight-text { font-size: 12.5px; line-height: 1.65; color: #ffe4e6; margin-top: 10px; }
    /* ===== ปกหน้าแรก ===== */
    .cover-wrap { border-radius: 20px; overflow: hidden; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.18); line-height: 0; }
    .cover-wrap img { width: 100%; height: auto; display: block; }
</style>
""", unsafe_allow_html=True)

# ----------------- ฟังก์ชันดึงรูปภาพ Base64 -----------------
def _norm(s):
    # NFC ช่วยให้ชื่อไฟล์ภาษาไทยจาก macOS (NFD) เทียบกับข้อความในโค้ดได้ตรงกัน
    return unicodedata.normalize("NFC", s).strip().lower()

# ค่าเป็นสตริงเดียวหรือลิสต์ของชื่อไฟล์ (ไม่รวมนามสกุล) ที่ยอมรับได้
ALIAS_MAP = {
    "kaysone phomvihane": ["kaysone phomvihane", "kaysone", "phomvihane", "phomwihane", "kaysone phomwihane", "ไกสอน พมวิหาน", "ไกสอน", "ไกรสร พรหมวิหาร", "พรหมวิหาร", "พมวิหาน"],
    "ไกรสร พรหมวิหาร": ["kaysone phomvihane", "kaysone", "phomvihane", "phomwihane", "kaysone phomwihane", "ไกสอน พมวิหาน", "ไกสอน", "ไกรสร พรหมวิหาร", "พรหมวิหาร", "พมวิหาน"],
    "olof palme": "olof palme",
    "friedrich engels": "friedrich engels",
    "karl marx": "คาร์ล มาร์กซ์ (karl marx)",
    "คาร์ล มาร์กซ์": "คาร์ล มาร์กซ์ (karl marx)",
    "vladimir lenin": "วลาดีมีร์ เลนิน (vladimir lenin)",
    "วลาดีมีร์ เลนิน": "วลาดีมีร์ เลนิน (vladimir lenin)",
    "ho chi minh": "โฮจิมินห์ (ho chi minh)",
    "โฮจิมินห์": "โฮจิมินห์ (ho chi minh)",
    "mao zedong": "เหมา เจ๋อตง (mao zedong)",
    "เหมา เจ๋อตง": "เหมา เจ๋อตง (mao zedong)",
    # รองรับทั้งชื่อไฟล์เดิมที่สะกดผิด (markel) และชื่อที่ถูกต้อง (merkel)
    "angela merkel": ["angela merkel", "angela markel"],
    "angela markel": ["angela merkel", "angela markel"],
    "valéry giscard d'estaing": ["valéry giscard d'estaing", "valery giscard d'estaing", "giscard"],
    "valery giscard d'estaing": ["valéry giscard d'estaing", "valery giscard d'estaing", "giscard"],
    "tony blair": "โทนี แบลร์ (tony blair)",
    "โทนี แบลร์": "โทนี แบลร์ (tony blair)",
    "justin trudeau": "จัสติน ทรูโด (justin trudeau)",
    "จัสติน ทรูโด": "จัสติน ทรูโด (justin trudeau)",
    "jacinda ardern": "จาซินดา อาร์เดิร์น (jacinda ardern)",
    "จาซินดา อาร์เดิร์น": "จาซินดา อาร์เดิร์น (jacinda ardern)",
    "edmund burke": "edmund burke",
    "shinzo abe": "shinzo abe",
    "donald trump": "donald trump",
    "ชวน หลีกภัย": "ชวน หลีกภัย",
    "javier milei": "javier milei",
    "robert nozick": "robert nozick",
    "ron paul": "ron paul",
    "john rawls": "john rawls",
    "john locke": "john locke",
    "giovanni gentile": "โจวันนี เจตินเล (giovanni gentile)",
    "โจวันนี เจตินเล": "โจวันนี เจตินเล (giovanni gentile)",
    "benito mussolini": "benito mussolini (เบนิโต มุสโสลินี)",
    "เบนิโต มุสโสลินี": "benito mussolini (เบนิโต มุสโสลินี)",
    "adolf hitler": "adolf hitler (อดอล์ฟ ฮิตเลอร์)",
    "อดอล์ฟ ฮิตเลอร์": "adolf hitler (อดอล์ฟ ฮิตเลอร์)",
    "แอนโทนี กิดเดนส์": "แอนโทนี กิดเดนส์",
    "anthony giddens": "แอนโทนี กิดเดนส์"
}

def _plain(s):
    # ตัวพิมพ์เล็ก และตัดเครื่องหมายกำกับเสียงของอักษรละติน (é -> e) โดยไม่แตะวรรณยุกต์ไทย
    s = unicodedata.normalize("NFD", _norm(s))
    s = re.sub(r"[\u0300-\u036f]", "", s)
    return unicodedata.normalize("NFC", s)

def _key(s):
    # เหลือเฉพาะตัวอักษรไทย/อังกฤษ/ตัวเลข (ตัดช่องว่าง _ - วงเล็บ ฯลฯ) เพื่อเทียบชื่อไฟล์ให้ยืดหยุ่น
    return re.sub(r"[^0-9a-z\u0e00-\u0e7f]", "", _plain(s))

def _find_images_dir():
    for d in (os.path.join(BASE_DIR, "images"), "images"):
        if os.path.isdir(d):
            return d
    return None

def _find_image_path(name_key):
    img_dir = _find_images_dir()
    if not img_dir:
        return None
    files = [f for f in os.listdir(img_dir) if os.path.isfile(os.path.join(img_dir, f))]
    file_keys = {f: _key(os.path.splitext(f)[0]) for f in files}

    clean = _norm(name_key)
    no_paren = _norm(clean.split("(")[0])

    cands = [clean, no_paren]
    alias = ALIAS_MAP.get(no_paren)
    if alias:
        cands += alias if isinstance(alias, list) else [alias]
    cands += re.findall(r"\(([^)]+)\)", clean)  # ชื่อในวงเล็บ เช่น (Karl Marx)
    cand_keys = [k for k in dict.fromkeys(_key(c) for c in cands) if k]

    # 1) ชื่อตรงกันทั้งหมด
    for ck in cand_keys:
        for f, fk in file_keys.items():
            if ck == fk:
                return os.path.join(img_dir, f)

    # 2) ชื่อบางส่วนตรงกัน
    for ck in cand_keys:
        for f, fk in file_keys.items():
            if len(fk) >= 3 and (ck in fk or fk in ck):
                return os.path.join(img_dir, f)

    # 3) ใช้นามสกุลภาษาอังกฤษ (คำสุดท้ายที่ยาว >= 4 ตัวอักษร) ค้นหา
    words = re.findall(r"[a-z]{4,}", _plain(name_key))
    if words:
        sur = words[-1]
        for f, fk in file_keys.items():
            if sur in fk:
                return os.path.join(img_dir, f)
    return None

# cache เฉพาะการอ่านไฟล์ที่เจอแล้ว (ไม่ cache ค่า None เพื่อให้เจอรูปทันทีเมื่อเพิ่ม/เปลี่ยนชื่อไฟล์)
@st.cache_data(show_spinner=False)
def _read_image_b64(path, mtime):
    try:
        with open(path, "rb") as img_file:
            b64 = base64.b64encode(img_file.read()).decode()
    except Exception:
        return None
    ext = os.path.splitext(path)[1].replace(".", "").lower()
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "jfif": "jpeg", "pjpeg": "jpeg", "pjp": "jpeg", "svg": "svg+xml"}.get(ext, ext)
    return f"data:image/{mime};base64,{b64}"

def get_image_base64(name_key):
    path = _find_image_path(name_key)
    if not path:
        return None
    return _read_image_b64(path, os.path.getmtime(path))

# ----------------- คำถาม 15 ข้อตามโครงสร้างจริง -----------------
questions_15 = [
    {
        "id": 1,
        "code": "Q1",
        "shade": "คอมมิวนิสต์",
        "q": "รัฐควรให้ความสำคัญกับผลประโยชน์และความต้องการของส่วนรวมมากกว่าสิทธิในการถือครองทรัพย์สินและผลประโยชน์ส่วนบุคคล เพื่อสร้างสังคมที่ไม่มีการแก่งแย่งชนชั้น",
        "type": "scale"
    },
    {
        "id": 2,
        "code": "Q2",
        "shade": "คอมมิวนิสต์",
        "q": "ประชาชนควรร่วมกันทำงานและมีส่วนร่วมในการผลิตและแบ่งปันทรัพยากรหรือผลผลิตของประเทศอย่างเป็นธรรม",
        "type": "scale"
    },
    {
        "id": 3,
        "code": "Q3",
        "shade": "สังคมนิยม",
        "q": "การศึกษาและการรักษาพยาบาลทุกระดับ ควรเป็นสิทธิขั้นพื้นฐานที่ทุกคนต้องได้รับฟรี โดยรัฐเป็นผู้รับผิดชอบค่าใช้จ่ายทั้งหมด",
        "type": "scale"
    },
    {
        "id": 4,
        "code": "Q4",
        "shade": "สังคมนิยม",
        "q": "รัฐบาลควรเข้ามาแทรกแซงและควบคุมระบบเศรษฐกิจ (เช่น ควบคุมราคาสินค้า หรือกำหนดค่าแรงขั้นต่ำให้สูง) เพื่อป้องกันไม่ให้เกิดความเหลื่อมล้ำทางรายได้",
        "type": "scale"
    },
    {
        "id": 5,
        "code": "Q5",
        "shade": "เสรีนิยม",
        "q": "ประชาชนควรมีสิทธิแสดงความคิดเห็นทางการเมืองได้อย่างเสรี แม้ความคิดเห็นนั้นจะวิพากษ์วิจารณ์รัฐบาล",
        "type": "scale"
    },
    {
        "id": 6,
        "code": "Q6",
        "shade": "เสรีนิยม",
        "q": "รัฐไม่ควรจำกัดเสรีภาพของประชาชน เว้นแต่การกระทำนั้นจะก่อให้เกิดอันตรายต่อผู้อื่น",
        "type": "scale"
    },
    {
        "id": 7,
        "code": "Q7",
        "shade": "สายกลาง",
        "q": "การแก้ปัญหาประเทศที่ดีที่สุด คือการประนีประนอมและค่อยเป็นค่อยไป มากกว่าการยึดติดกับอุดมการณ์สุดโต่งข้างใดข้างหนึ่ง",
        "type": "scale"
    },
    {
        "id": 8,
        "code": "Q8",
        "shade": "สายกลาง",
        "q": "นโยบายรัฐไม่ควรตัดสินจากคำว่า 'ฝ่ายซ้าย' หรือ 'ฝ่ายขวา' แต่ควรวัดจากหลักฐานเชิงประจักษ์และความเป็นไปได้จริงในทางปฏิบัติ",
        "type": "scale"
    },
    {
        "id": 9,
        "code": "Q9",
        "shade": "อนุรักษ์นิยม",
        "q": "สังคมควรรักษาประเพณีและวัฒนธรรมดั้งเดิมไว้ มากกว่าการเปลี่ยนแปลงตามกระแสสมัยใหม่",
        "type": "scale"
    },
    {
        "id": 10,
        "code": "Q10",
        "shade": "อนุรักษ์นิยม",
        "q": "การเปลี่ยนแปลงโครงสร้างทางสังคมและการเมืองควรทำอย่างค่อยเป็นค่อยไป ไม่ควรเปลี่ยนแปลงอย่างรวดเร็วหรือรุนแรง",
        "type": "scale"
    },
    {
        "id": 11,
        "code": "Q11",
        "shade": "อิสระนิยม",
        "q": "รัฐบาลควรแทรกแซงเศรษฐกิจและการทำธุรกิจให้น้อยที่สุด ปล่อยให้เป็นเรื่องของกลไกตลาดเสรีและการแข่งขันอย่างเป็นธรรม",
        "type": "scale"
    },
    {
        "id": 12,
        "code": "Q12",
        "shade": "อิสระนิยม",
        "q": "ตราบใดที่การกระทำนั้นไม่ได้ละเมิดหรือสร้างความเดือดร้อนให้คนอื่น ประชาชนควรมีเสรีภาพในการตัดสินใจชีวิตตนเองอย่างเต็มที่ เช่น ความเชื่อ ร่างกาย",
        "type": "scale"
    },
    {
        "id": 13,
        "code": "Q13",
        "shade": "ฟาสซิสต์",
        "q": "เชื้อชาติที่มีอารยธรรมและศักยภาพเหนือกว่า ย่อมมีสิทธิ์โดยชอบธรรมในการนำพาหรือควบคุมประชากรอื่นเพื่อความก้าวหน้า",
        "type": "scale"
    },
    {
        "id": 14,
        "code": "Q14",
        "shade": "ฟาสซิสต์",
        "q": "ความมั่นคงของรัฐมีความสำคัญมากกว่าสิทธิและเสรีภาพของปัจเจกชน",
        "type": "scale"
    },
    {
        "id": 15,
        "code": "Q15",
        "shade": "ตัวตัดสิน",
        "q": "หากคุณมีโอกาสกำหนดรูปแบบการบริหารประเทศในรัฐบาลในฝันของคุณ คุณจะเลือกแนวทางใดต่อไปนี้มากที่สุด?",
        "type": "bonus"
    }
]

# ตัวเลือกข้อ 15
q15_options = [
    {
        "id": 1,
        "shade": "คอมมิวนิสต์",
        "text": "รัฐเข้ามาดูแลทรัพยากรและกิจการสำคัญของประเทศเป็นหลัก ลดความเหลื่อมล้ำด้านรายได้และทรัพย์สิน ให้ประชาชนมีความเสมอภาคสูง และการตัดสินใจทางเศรษฐกิจและการเมืองเป็นไปในทิศทางเดียวกันเพื่อประโยชน์ส่วนรวม"
    },
    {
        "id": 2,
        "shade": "สังคมนิยม",
        "text": "รัฐจัดสวัสดิการและบริการสาธารณะอย่างทั่วถึง ควบคุมหรือกำกับกิจการสำคัญบางส่วนเพื่อสร้างความเป็นธรรมทางเศรษฐกิจ เปิดให้ประชาชนมีส่วนร่วมทางการเมือง และพยายามลดความแตกต่างระหว่างกลุ่มคนในสังคม"
    },
    {
        "id": 3,
        "shade": "เสรีนิยม",
        "text": "รัฐคุ้มครองสิทธิและเสรีภาพของประชาชน เปิดโอกาสให้ทุกคนแข่งขันและแสดงความคิดเห็นได้อย่างเท่าเทียม ใช้ระบบเศรษฐกิจที่อาศัยตลาดเป็นสำคัญแต่มีมาตรการช่วยเหลือผู้ที่เสียเปรียบ และยึดหลักการปกครองที่ประชาชนมีส่วนร่วม"
    },
    {
        "id": 4,
        "shade": "สายกลาง",
        "text": "รัฐเลือกใช้นโยบายตามสถานการณ์ โดยผสมผสานการดูแลเศรษฐกิจของรัฐกับกลไกตลาด ให้ความสำคัญทั้งสิทธิเสรีภาพและความมั่นคง ส่งเสริมสวัสดิการในระดับที่เหมาะสม และเปิดพื้นที่ให้ความคิดเห็นที่แตกต่างสามารถอยู่ร่วมกันได้"
    },
    {
        "id": 5,
        "shade": "อนุรักษ์นิยม",
        "text": "รัฐให้ความสำคัญกับความมั่นคงของประเทศ ระเบียบวินัย และการรักษาขนบธรรมเนียมที่สังคมเห็นว่ามีคุณค่า สนับสนุนเศรษฐกิจที่เติบโตโดยอาศัยภาคเอกชนและครอบครัวเป็นกำลังสำคัญ พร้อมเปลี่ยนแปลงสิ่งต่างๆ อย่างค่อยเป็นค่อยไป"
    },
    {
        "id": 6,
        "shade": "อิสระนิยม",
        "text": "รัฐควรเข้าไปยุ่งเกี่ยวกับชีวิตและเศรษฐกิจของประชาชนให้น้อยที่สุด เปิดโอกาสให้แต่ละคนตัดสินใจและประกอบกิจการได้อย่างอิสระ ลดกฎระเบียบและภาษีที่ไม่จำเป็น และจำกัดอำนาจรัฐเพื่อคุ้มครองสิทธิและเสรีภาพของแต่ละบุคคล"
    },
    {
        "id": 7,
        "shade": "ฟาสซิสต์",
        "text": "รัฐรวมอำนาจในการกำหนดทิศทางประเทศไว้อย่างเข้มแข็ง ให้ความสำคัญกับความเป็นเอกภาพของชาติ วินัย และการเชื่อฟังอำนาจรัฐ ส่งเสริมเศรษฐกิจที่ตอบสนองเป้าหมายของชาติ และจำกัดความขัดแย้งทางการเมืองเพื่อรักษาความเป็นระเบียบและความมั่นคงของประเทศ"
    }
]

# เกณฑ์คะแนน
scale_scoring = {
    0.00: "ไม่เห็นด้วยอย่างยิ่ง",
    0.25: "ไม่เห็นด้วย",
    0.50: "เฉยๆ",
    1.00: "เห็นด้วย",
    2.00: "เห็นด้วยอย่างยิ่ง"
}

# คะแนนสูงสุดต่ออุดมการณ์: 2 ข้อ x 2 คะแนน + โบนัสข้อ 15 อีก 2 คะแนน
MAX_SHADE_SCORE = 6.0
BONUS_POINTS = 2.0

def level_text(score):
    """แปลงคะแนนจริงเป็นข้อความบอกระดับความสอดคล้อง (ไม่แสดงตัวเลขให้ผู้ใช้เห็น)"""
    if score >= 4:
        return "สอดคล้องสูงมาก"
    if score >= 3:
        return "สอดคล้องสูง"
    if score >= 2:
        return "สอดคล้องปานกลาง"
    if score >= 1:
        return "สอดคล้องเล็กน้อย"
    return "ไม่ค่อยสอดคล้อง"

# เปลี่ยนเป็น True ถ้าต้องการแสดงตัวเลขเปอร์เซ็นต์ในส่วนสเปกตรัม (ค่าเริ่มต้น: แสดงเป็นข้อความ)
SHOW_PERCENT = False

# ลำดับอุดมการณ์บนแถบสเปกตรัม (ซ้าย -> ขวา) และสีของแต่ละช่วง
SPECTRUM_ORDER = ["คอมมิวนิสต์", "สังคมนิยม", "เสรีนิยม", "สายกลาง", "อนุรักษ์นิยม", "อิสระนิยม", "ฟาสซิสต์"]
SPECTRUM_COLORS = {
    "คอมมิวนิสต์": "#9f1d1d",
    "สังคมนิยม": "#c4001d",
    "เสรีนิยม": "#0284c7",
    "สายกลาง": "#0f9488",
    "อนุรักษ์นิยม": "#0b2a8f",
    "อิสระนิยม": "#475569",
    "ฟาสซิสต์": "#dc2626"
}

# ข้อความสั้นใต้การ์ด: (เมื่อสอดคล้องตั้งแต่ระดับปานกลางขึ้นไป, เมื่อสอดคล้องน้อย)
AFFINITY_NOTES = {
    "คอมมิวนิสต์": ("เห็นพ้องกับการถือครองทรัพยากรร่วมกัน", "ไม่ค่อยเห็นด้วยกับการยกเลิกทรัพย์สินส่วนบุคคล"),
    "สังคมนิยม": ("เห็นพ้องต่อรัฐสวัสดิการ", "ไม่ค่อยเห็นด้วยกับการให้รัฐแทรกแซงเศรษฐกิจ"),
    "เสรีนิยม": ("เห็นพ้องกับสิทธิเสรีภาพและความเสมอภาค", "ให้น้ำหนักสิทธิเสรีภาพของปัจเจกไม่มากนัก"),
    "สายกลาง": ("เห็นพ้องกับการประนีประนอมและความเป็นไปได้จริง", "ไม่ค่อยเห็นด้วยกับแนวทางประนีประนอม"),
    "อนุรักษ์นิยม": ("เห็นพ้องกับการรักษาประเพณีและค่อยเป็นค่อยไป", "ไม่ค่อยเห็นด้วยกับการยึดประเพณีเดิม"),
    "อิสระนิยม": ("เห็นพ้องกับเสรีภาพส่วนบุคคลและตลาดเสรี", "ไม่ค่อยเห็นด้วยกับการลดบทบาทรัฐสุดขั้ว"),
    "ฟาสซิสต์": ("เห็นพ้องกับรัฐเข้มแข็งและเอกภาพของชาติ", "ปฏิเสธการรวมอำนาจเบ็ดเสร็จของรัฐ")
}

# การ์ดสรุปทิศทาง (Spectrum Balance): (หัวข้อ, คำอธิบาย) ตามอุดมการณ์ที่สอดคล้องสูงสุด
BALANCE_CARDS = {
    "คอมมิวนิสต์": ("ความเสมอภาคของส่วนรวม", "โน้มเอียงสู่การถือครองทรัพยากรร่วมกันและลดความแตกต่างทางชนชั้น"),
    "สังคมนิยม": ("รัฐสวัสดิการเพื่อความเป็นธรรม", "โน้มเอียงสู่การจัดสวัสดิการถ้วนหน้าและลดความเหลื่อมล้ำทางรายได้"),
    "เสรีนิยม": ("ก้าวหน้าแบบเสรี", "โน้มเอียงสู่ความยุติธรรมทางเศรษฐกิจและความเท่าเทียมสากล"),
    "สายกลาง": ("สมดุลแบบปฏิบัตินิยม", "โน้มเอียงสู่การผสมผสานตลาดเสรีกับสวัสดิการอย่างพอเหมาะ"),
    "อนุรักษ์นิยม": ("มั่นคงและค่อยเป็นค่อยไป", "โน้มเอียงสู่การรักษาประเพณีและเสถียรภาพของสังคม"),
    "อิสระนิยม": ("เสรีภาพปัจเจกสูงสุด", "โน้มเอียงสู่รัฐขนาดเล็กและกลไกตลาดเสรี"),
    "ฟาสซิสต์": ("รัฐเข้มแข็งและเอกภาพของชาติ", "โน้มเอียงสู่การรวมศูนย์อำนาจและให้ความมั่นคงของรัฐอยู่เหนือปัจเจก")
}

def spectrum_position(shade_scores, best_shade):
    """ตำแหน่ง (0-100%) บนแถบสเปกตรัม
    จุดจะอยู่ในช่วงของอุดมการณ์ที่สอดคล้องสูงสุดเสมอ และเขยิบไปทางข้างเคียงที่คะแนนสูงกว่า"""
    n = len(SPECTRUM_ORDER)
    i = SPECTRUM_ORDER.index(best_shade)
    best = shade_scores[best_shade]
    left = shade_scores[SPECTRUM_ORDER[i - 1]] if i > 0 else 0.0
    right = shade_scores[SPECTRUM_ORDER[i + 1]] if i < n - 1 else 0.0
    shift = 0.0 if best <= 0 else max(-1.0, min(1.0, (right - left) / best)) * 0.4
    return (i + 0.5 + shift) / n * 100

# ฐานข้อมูลแนวคิดและบุคคลสำคัญ (ตัดคำว่าเฉดออก ให้เป็นชื่ออุดมการณ์โดยตรง)
spectrum_master = {
    "คอมมิวนิสต์": {
        "title": "คอมมิวนิสต์ (Communism)",
        "desc": "มุ่งสร้างสังคมที่ยกเลิกความแตกต่างทางชนชั้น ถือครองทรัพยากรและปัจจัยการผลิตร่วมกันโดยสังคม แทนการให้เอกชนแสวงหากำไร เพื่อสร้างความเสมอภาคสัมบูรณ์",
        "thinker": {"name": "คาร์ล มาร์กซ์ (Karl Marx)", "role": "นักคิดคอมมิวนิสต์: วิเคราะห์ชนชั้นและระบบเศรษฐกิจร่วมกัน", "quote": "“ชนชั้นกรรมาชีพไม่มีสิ่งใดจะสูญเสียนอกจากโซ่ตรวนของพวกเขา”"},
        "leader": {"name": "วลาดีมีร์ เลนิน (Vladimir Lenin)", "role": "ผู้นำการปฏิวัติ: องค์กรพรรคที่มีวินัยเพื่อความเสมอภาค", "quote": "“เสรีภาพมีค่าเมื่อนำมาซึ่งความเสมอภาคของมวลชน”"},
        "overall": {"name": "โฮจิมินห์ (Ho Chi Minh)", "role": "ผู้นำคอมมิวนิสต์: ชาตินิยมปลดปล่อยและความเสมอภาคทางสังคม", "quote": "“ความเป็นอันหนึ่งอันเดียวกันของประชาชนคือพลังลดความเหลื่อมล้ำ”"}
    },
    "สังคมนิยม": {
        "title": "สังคมนิยม (Socialism)",
        "desc": "รัฐหรือสังคมส่วนรวมเป็นเจ้าของและกำกับดูแลปัจจัยการผลิตสำคัญ เพื่อจัดสวัสดิการถ้วนหน้า ลดความเหลื่อมล้ำทางรายได้ และกระจายผลประโยชน์อย่างเป็นธรรม",
        "thinker": {"name": "Friedrich Engels", "role": "นักคิดสังคมนิยม: วิเคราะห์โครงสร้างสังคมและความเสมอภาค", "quote": "“ความเป็นเจ้าของทรัพย์สินมีส่วนทำให้เกิดความไม่เสมอภาค”"},
        "leader": {"name": "Olof Palme", "role": "ผู้นำสังคมนิยม: รัฐสวัสดิการถ้วนหน้าและการลดความเหลื่อมล้ำ", "quote": "“สิทธิสวัสดิการของประชาชน คือรากฐานที่แท้จริงของประชาธิปไตย”"},
        "overall": {"name": "Kaysone Phomvihane", "role": "ผู้นำสังคมนิยม: การขับเคลื่อนสังคมเพื่อประโยชน์สุขส่วนรวม", "quote": "“สร้างสรรค์สังคมบนพื้นฐานความเป็นธรรมแก่ประชาชนทุกคน”"}
    },
    "เสรีนิยม": {
        "title": "เสรีนิยม (Liberalism)",
        "desc": "ให้ความสำคัญสูงสุดกับสิทธิและเสรีภาพของปัจเจกบุคคล ความเสมอภาคภายใต้กฎหมาย หลักนิติธรรม และการจำกัดอำนาจรัฐไม่ให้แทรกแซงประชาชนเกินจำเป็น",
        "thinker": {"name": "John Rawls", "role": "นักปรัชญาเสรีนิยม: ทฤษฎีความยุติธรรมและโอกาสเท่าเทียม", "quote": "“ความยุติธรรมเริ่มต้นจากโอกาสที่เท่าเทียมของผู้ด้อยโอกาสที่สุด”"},
        "leader": {"name": "Angela Merkel", "role": "ผู้นำเสรีนิยมสายกลาง: เสถียรภาพ นิติธรรม และความร่วมมือสากล", "quote": "“ยึดมั่นในคุณค่าเสรีนิยมประชาธิปไตยและหลักการที่เคารพซึ่งกันและกัน”"},
        "overall": {"name": "Valéry Giscard d'Estaing", "role": "ผู้นำเสรีนิยม: การปฏิรูปเพื่อขยายเสรีภาพของประชาชน", "quote": "“การปฏิรูปที่แท้จริงคือการเคารพสิทธิและเสรีภาพของปัจเจกบุคคล”"}
    },
    "สายกลาง": {
        "title": "สายกลาง (Centrism)",
        "desc": "จุดยืนที่ไม่ยึดติดกับขั้วอุดมการณ์สุดโต่ง เน้นการแก้ปัญหาได้จริงในทางปฏิบัติ (Pragmatism) ผสมผสานกลไกตลาดเสรีควบคู่กับการกำกับดูแลสวัสดิการอย่างสมดุล",
        "thinker": {"name": "แอนโทนี กิดเดนส์", "role": "นักคิดทางสายที่สาม: การก้าวข้ามขั้วดั้งเดิมในยุคโลกาภิวัตน์", "quote": "“รัฐไม่ควรแทรกแซงแบบซ้ายเก่า และไม่ควรปล่อยปละละเลยแบบขวาเก่า”"},
        "leader": {"name": "โทนี แบลร์ (Tony Blair)", "role": "ผู้นำ The Third Way: ผสานตลาดเสรีกับสวัสดิการสังคม", "quote": "“ยอมรับกลไกตลาดเสรีควบคู่กับการรักษาระบบสวัสดิการสังคม”"},
        "overall": {"name": "จัสติน ทรูโด (Justin Trudeau)", "role": "ผู้นำสายกลางปฏิบัติ: สมดุลสิทธิเสรีภาพกับการเติบโตทางเศรษฐกิจ", "quote": "“รักษาสมดุลความก้าวหน้าทางสังคมควบคู่กับเสถียรภาพเศรษฐกิจ”"}
    },
    "อนุรักษ์นิยม": {
        "title": "อนุรักษ์นิยม (Conservatism)",
        "desc": "ให้คุณค่ากับความมั่นคง เสถียรภาพ ระเบียบวินัย และการรักษาประเพณีวัฒนธรรมดั้งเดิม เชื่อว่าสังคมควรพัฒนาอย่างรอบคอบและค่อยเป็นค่อยไป",
        "thinker": {"name": "Edmund Burke", "role": "บิดาแห่งอนุรักษ์นิยม: รักษาสถาบัน ประเพณี และการเปลี่ยนแปลงค่อยเป็นค่อยไป", "quote": "“เคารพภูมิปัญญาดั้งเดิมและระเบียบแบบแผนที่ผ่านการทดสอบตามกาลเวลา”"},
        "leader": {"name": "Shinzo Abe", "role": "ผู้นำอนุรักษ์นิยม: เสถียรภาพทางเศรษฐกิจและความมั่นคงของชาติ", "quote": "“สร้างความเจริญเติบโตบนพื้นฐานความมั่นคงและเกียรติยศของชาติ”"},
        "overall": {"name": "ชวน หลีกภัย", "role": "ผู้นำอนุรักษ์นิยมไทย: ยึดมั่นระบบรัฐสภาและหลักนิติธรรม", "quote": "“ให้ความสำคัญสูงสุดกับกฎหมาย ความมั่นคง และเสถียรภาพของรัฐ”"}
    },
    "อิสระนิยม": {
        "title": "อิสระนิยม (Libertarianism)",
        "desc": "ให้ความสำคัญสูงสุดกับเสรีภาพของปัจเจกบุคคลและกรรมสิทธิ์ในทรัพย์สิน ลดบทบาทและการแทรกแซงของรัฐให้เหลือน้อยที่สุด และเชื่อมั่นในตลาดเสรีบริสุทธิ์",
        "thinker": {"name": "Robert Nozick", "role": "นักคิดอิสระนิยม: รัฐขนาดเล็กที่สุดเพื่อคุ้มครองสิทธิบุคคล", "quote": "“รัฐที่เล็กที่สุดคือรัฐเดียวที่มีความชอบธรรมในการคุ้มครองเสรีภาพ”"},
        "leader": {"name": "Javier Milei", "role": "ผู้นำอิสระนิยม: เสรีภาพตลาดบริสุทธิ์ ลดบทบาทภาครัฐ", "quote": "“เสรีภาพทางเศรษฐกิจและกรรมสิทธิ์เอกชนคือกุญแจสู่ความเจริญรุ่งเรือง”"},
        "overall": {"name": "Ron Paul", "role": "นักการเมืองอิสระนิยม: เสรีภาพปัจเจกและการจำกัดอำนาจรัฐ", "quote": "“เปิดพื้นที่ให้บุคคลกำหนดวิถีชีวิตและใช้อำนาจภายใต้กรอบกฎหมาย”"}
    },
    "ฟาสซิสต์": {
        "title": "ฟาสซิสต์ (Fascism)",
        "desc": "เน้นชาตินิยมสุดโต่ง ความเป็นหนึ่งเดียวของชาติ ระเบียบวินัยทางทหาร และการรวมศูนย์อำนาจเบ็ดเสร็จ โดยผลประโยชน์และความมั่นคงของรัฐอยู่เหนือปัจเจกชน",
        "thinker": {"name": "โจวันนี เจตินเล (Giovanni Gentile)", "role": "นักคิดฟาสซิสต์: เอกภาพแห่งชาติและระเบียบวินัยสูงสุด", "quote": "“เอกภาพของรัฐและความเป็นหนึ่งเดียวอยู่เหนือเสรีภาพส่วนบุคคล”"},
        "leader": {"name": "Benito Mussolini (เบนิโต มุสโสลินี)", "role": "ผู้นำฟาสซิสต์: รัฐรวมศูนย์และระเบียบวินัยเด็ดขาด", "quote": "“ทุกสิ่งรวมอยู่ในรัฐ ไม่มีสิ่งใดอยู่นอกเหนือรัฐ และไม่มีสิ่งใดต่อต้านรัฐได้”"},
        "overall": {"name": "Adolf Hitler (อดอล์ฟ ฮิตเลอร์)", "role": "ผู้นำเผด็จการ: ชาตินิยมสุดโต่งและระเบียบการทหาร", "quote": "“ความแข็งแกร่งของรัฐตั้งอยู่บนระเบียบวินัยและความเป็นหนึ่งเดียวสูงสุด”"}
    }
}

# ----------------- ฟังก์ชันคำนวณผล -----------------
def calculate_scores(answers):
    """คืนค่า (shade_scores, strong_counts, bonus_shade)
    - shade_scores: คะแนนรวมต่ออุดมการณ์ (ข้อ 1-14 + โบนัสข้อ 15)
    - strong_counts: จำนวนข้อที่ตอบ 'เห็นด้วยอย่างยิ่ง' ต่ออุดมการณ์ (ใช้ตัดสินกรณีเสมอ)
    - bonus_shade: อุดมการณ์ที่เลือกในข้อ 15 (None ถ้ายังไม่ได้เลือก)
    """
    shade_scores = {s: 0.0 for s in spectrum_master.keys()}
    strong_counts = {s: 0 for s in spectrum_master.keys()}

    for i in range(14):
        s_name = questions_15[i]["shade"]
        ans_val = float(answers.get(i, 0.50))
        shade_scores[s_name] += ans_val
        if ans_val >= 2.0:
            strong_counts[s_name] += 1

    bonus_idx = answers.get(14)
    bonus_shade = None
    if bonus_idx is not None:
        bonus_shade = q15_options[bonus_idx]["shade"]
        shade_scores[bonus_shade] += BONUS_POINTS
    return shade_scores, strong_counts, bonus_shade

def pick_best(shade_scores, strong_counts, bonus_shade):
    """เลือกอุดมการณ์ผู้ชนะ พร้อมกติกาตัดสินเมื่อคะแนนเสมอ
    1) คะแนนรวมสูงสุด
    2) ถ้าเสมอ -> อุดมการณ์ที่ผู้ใช้เลือกในข้อ 15 (ถ้าอยู่ในกลุ่มที่เสมอ)
    3) ถ้ายังเสมอ -> อุดมการณ์ที่ตอบ 'เห็นด้วยอย่างยิ่ง' มากกว่า
    4) ถ้ายังเสมออีก -> ตามลำดับในฐานข้อมูล
    """
    top = max(shade_scores.values())
    tied = [s for s, v in shade_scores.items() if abs(v - top) < 1e-9]
    if len(tied) == 1:
        return tied[0]
    if bonus_shade in tied:
        return bonus_shade
    best_strong = max(strong_counts[s] for s in tied)
    tied = [s for s in tied if strong_counts[s] == best_strong]
    return tied[0]

def _compact(html):
    # ตัดการขึ้นบรรทัด/ย่อหน้าออก เพื่อไม่ให้ Streamlit (Markdown) ตีความบรรทัดที่เยื้องเป็น code block
    return re.sub(r"\n\s*", "", html)

def render_spectrum_html(shade_scores, best_shade):
    pos = spectrum_position(shade_scores, best_shade)
    label_pos = min(max(pos, 12), 88)  # กันป้ายล้นขอบซ้าย/ขวา
    pos_text = f" ({pos:.1f}%)" if SHOW_PERCENT else ""

    segments = "".join(
        f'<div class="spec-seg" style="background:{SPECTRUM_COLORS[s]};"></div>' for s in SPECTRUM_ORDER
    )
    labels = "".join(
        f'<div class="spec-lab{" spec-lab-active" if s == best_shade else ""}">{s}</div>' for s in SPECTRUM_ORDER
    )

    ranked = sorted(SPECTRUM_ORDER, key=lambda s: (-shade_scores[s], s != best_shade))
    cards = ""
    for rank, s in enumerate(ranked, 1):
        score = shade_scores[s]
        pct = round(score / MAX_SHADE_SCORE * 100)
        color = SPECTRUM_COLORS[s]
        agree, disagree = AFFINITY_NOTES[s]
        note = agree if score >= 2 else disagree
        level = "สอดคล้องสูงสุด (Primary match)" if s == best_shade else level_text(score)
        val = f'<span class="aff-val" style="color:{color};">{pct}%</span>' if SHOW_PERCENT else ""
        cards += (
            '<div class="aff-card">'
            f'<div class="aff-head"><span class="aff-name">{rank}. {spectrum_master[s]["title"]}</span>{val}</div>'
            f'<div class="aff-track"><div class="aff-fill" style="width:{max(pct, 4)}%; background:{color};"></div></div>'
            f'<div class="aff-level" style="color:{color};">{level}</div>'
            f'<div class="aff-note">{note}</div>'
            '</div>'
        )

    bal_title, bal_desc = BALANCE_CARDS[best_shade]
    balance = (
        '<div class="aff-balance">'
        '<div class="aff-bal-kicker">SPECTRUM BALANCE</div>'
        f'<div class="aff-bal-title">{bal_title}</div>'
        f'<div class="aff-bal-desc">{bal_desc}</div>'
        '</div>'
    )

    html = f"""
    <div class="spec-card">
        <div class="spec-title">ตำแหน่งบนสเปกตรัมอุดมการณ์ 7 อุดมการณ์</div>
        <div class="spec-sub">การคำนวณตำแหน่งของคุณเทียบกับอุดมการณ์หลักทั้ง 7 แบบ</div>
        <div class="spec-main-chip">ตำแหน่งหลัก: {best_shade}</div>
        <div class="spec-bar-wrap">
            <div class="spec-marker-label" style="left:{label_pos:.1f}%;">พิกัดของคุณ{pos_text}</div>
            <div class="spec-bar">{segments}</div>
            <div class="spec-dot" style="left:{pos:.1f}%;"></div>
        </div>
        <div class="spec-labels">{labels}</div>
        <div class="aff-box">
            <div class="aff-box-title">ระดับความสอดคล้องกับแต่ละแนวคิด (Affinity Index)</div>
            <div class="aff-grid">{cards}{balance}</div>
        </div>
    </div>
    """
    return _compact(html)

# ไอคอนเส้นแบบสถิต (viewBox 24x24)
_ICON_PATHS = {
    "star": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "flame": '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
    "scale": '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>',
    "unlock": '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>'
}

# ลำดับซ้าย -> ขวา: โหนดคี่อยู่เหนือแกน โหนดคู่อยู่ใต้แกน
CONTINUUM_NODES = [
    {"en": "COMMUNISM", "th": "คอมมิวนิสต์", "pos": "top", "icon": "star", "fill": True, "tile": "#fee2e2", "ink": "#dc2626", "label": "#dc2626", "dot": "#1e3a8a"},
    {"en": "SOCIALISM", "th": "สังคมนิยม", "pos": "bottom", "icon": "users", "fill": False, "tile": "#fee2e2", "ink": "#f43f5e", "label": "#2563eb", "dot": "#2563eb"},
    {"en": "LIBERALISM", "th": "เสรีนิยม", "pos": "top", "icon": "flame", "fill": False, "tile": "#e0f2fe", "ink": "#0284c7", "label": "#0284c7", "dot": "#0ea5e9"},
    {"en": "MODERATE", "th": "สายกลาง", "pos": "bottom", "icon": "scale", "fill": False, "tile": "#ccfbf1", "ink": "#0f9488", "label": "#0f9488", "dot": "#0f9488"},
    {"en": "CONSERVATISM", "th": "อนุรักษ์นิยม", "pos": "top", "icon": "sun", "fill": False, "tile": "#fef3c7", "ink": "#d97706", "label": "#d97706", "dot": "#d97706"},
    {"en": "LIBERTARIANISM", "th": "อิสระนิยม", "pos": "bottom", "icon": "unlock", "fill": False, "tile": "#ffedd5", "ink": "#ea580c", "label": "#ea580c", "dot": "#ea580c"},
    {"en": "FASCISM", "th": "ฟาสซิสต์", "pos": "top", "icon": "shield", "fill": False, "tile": "#fee2e2", "ink": "#dc2626", "label": "#dc2626", "dot": "#dc2626"}
]

def render_continuum_html():
    cols = ""
    for n in CONTINUUM_NODES:
        fill = n["ink"] if n["fill"] else "none"
        svg = (
            f'<svg viewBox="0 0 24 24" width="24" height="24" fill="{fill}" stroke="{n["ink"]}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{_ICON_PATHS[n["icon"]]}</svg>'
        )
        icon = f'<div class="cont-icon" style="background:{n["tile"]};">{svg}</div>'
        text = f'<div class="cont-en">{n["en"]}</div><div class="cont-th" style="color:{n["label"]};">{n["th"]}</div>'
        dot = f'<div class="cont-dot" style="border-color:{n["dot"]};"></div>'
        if n["pos"] == "top":
            top, bottom = icon + text + dot, ""
        else:
            top, bottom = "", dot + text + icon
        cols += (
            '<div class="cont-col">'
            f'<div class="cont-half cont-top">{top}</div>'
            '<div class="cont-gap"></div>'
            f'<div class="cont-half cont-bottom">{bottom}</div>'
            '</div>'
        )

    html = f"""
    <div class="cont-card">
        <div class="cont-kicker"><span class="cont-kicker-dot"></span>SPECTRUM CONTINUUM VISUALIZER</div>
        <div class="cont-title">แกนสเปกตรัมการเมือง 7 อุดมการณ์</div>
        <div class="cont-sub">จากซ้ายสุดถึงขวาสุด เรียงอุดมการณ์ทางการเมืองผ่านสัญลักษณ์และปรัชญาการปกครอง</div>
        <div class="cont-scroll">
            <div class="cont-stage">
                <div class="cont-axis"><span>LEFT</span><span>RIGHT</span></div>
                {cols}
            </div>
        </div>
    </div>
    """
    return _compact(html)

# ----------------- การ์ดอธิบาย 7 อุดมการณ์ (หน้าแรก ภาพนิ่ง) -----------------
# คำอธิบายหลักดึงจาก spectrum_master ส่วนป้ายตำแหน่ง ชื่ออังกฤษ และค่านิยมหลักกำหนดไว้ที่นี่
IDEOLOGY_CARD_INFO = {
    "คอมมิวนิสต์": {"tag": "ซ้ายจัด (Far-Left)", "en": "COMMUNISM",
                    "values": ["ความเท่าเทียมสูงสุด", "ทรัพย์สินส่วนรวม", "ไร้ชนชั้น"]},
    "สังคมนิยม": {"tag": "ซ้าย (Left)", "en": "SOCIALISM / SOCIAL DEMOCRACY",
                  "values": ["รัฐสวัสดิการเข้มแข็ง", "ความเป็นธรรมทางสังคม", "ลดความเหลื่อมล้ำ"]},
    "เสรีนิยม": {"tag": "กลาง-ซ้าย (Center-Left)", "en": "LIBERALISM",
                 "values": ["สิทธิมนุษยชน", "สังคมเปิด", "เสรีภาพในการแสดงออก"]},
    "สายกลาง": {"tag": "สายกลาง (Centrist)", "en": "MODERATE / CENTRIST",
                "values": ["ความสมดุล", "ยึดหลักความเป็นจริง", "ประนีประนอม"]},
    "อนุรักษ์นิยม": {"tag": "กลาง-ขวา (Center-Right)", "en": "CONSERVATISM",
                     "values": ["เสถียรภาพทางสังคม", "จารีตประเพณี", "เปลี่ยนแปลงค่อยเป็นค่อยไป"]},
    "อิสระนิยม": {"tag": "ขวา (Right)", "en": "LIBERTARIANISM",
                  "values": ["รัฐขนาดเล็ก", "ตลาดเสรีสูงสุด", "กรรมสิทธิ์ส่วนบุคคล"]},
    "ฟาสซิสต์": {"tag": "ขวาจัด (Far-Right)", "en": "FASCISM / AUTHORITARIANISM",
                 "values": ["ชาตินิยมสุดโต่ง", "รัฐรวมศูนย์", "อำนาจรัฐเบ็ดเสร็จ"]},
}

def render_ideology_cards_html():
    nodes = {n["th"]: n for n in CONTINUUM_NODES}
    cards = ""
    for i, name in enumerate(SPECTRUM_ORDER, 1):
        n = nodes[name]
        info = IDEOLOGY_CARD_INFO[name]
        fill = n["ink"] if n["fill"] else "none"
        svg = (
            f'<svg viewBox="0 0 24 24" width="15" height="15" fill="{fill}" stroke="{n["ink"]}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{_ICON_PATHS[n["icon"]]}</svg>'
        )
        values = " • ".join(info["values"])
        cards += (
            '<div class="ideo-card">'
            '<div class="ideo-top">'
            f'<span class="ideo-tag" style="background:{n["tile"]}; color:{n["label"]};">{svg}{info["tag"]}</span>'
            f'<span class="ideo-idx">{i:02d} / 07</span>'
            '</div>'
            f'<div class="ideo-th">{name}</div>'
            f'<div class="ideo-en" style="color:{n["label"]};">{info["en"]}</div>'
            f'<div class="ideo-desc">{spectrum_master[name]["desc"]}</div>'
            '<div class="ideo-val">'
            '<div class="ideo-val-title">ค่านิยมหลัก</div>'
            f'<div class="ideo-val-text">{values}</div>'
            '</div>'
            '</div>'
        )

    cards += (
        '<div class="ideo-insight">'
        '<div class="ideo-insight-kicker">SPECTRUM INSIGHT</div>'
        '<div class="ideo-insight-title">ทำไมต้องมี 7 อุดมการณ์?</div>'
        '<div class="ideo-insight-text">การแบ่งแค่ “ซ้าย” หรือ “ขวา” ไม่พอจะอธิบายความคิดของคนได้ '
        'จึงเรียงอุดมการณ์เป็นสเปกตรัม เพื่อสะท้อนมุมมองที่ต่างกันตามประเด็นเศรษฐกิจ สิทธิเสรีภาพ และวัฒนธรรม</div>'
        '</div>'
    )
    return _compact(f'<div class="ideo-grid">{cards}</div>')

# ----------------- ธีมสีของหน้าผลลัพธ์ (เปลี่ยนตามสีอุดมการณ์บนแถบสเปกตรัม) -----------------
def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def _mix(h, other, t):
    """ผสมสี h กับ other โดย t คือสัดส่วนของ other (0-1)"""
    a, b = _hex_to_rgb(h), _hex_to_rgb(other)
    return "#%02x%02x%02x" % tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3))

def make_theme(color):
    r, g, b = _hex_to_rgb(color)
    return {
        "main": color,                       # สีหลัก (เท่ากับสีบนแถบสเปกตรัม)
        "text": _mix(color, "#000000", 0.25),  # สีตัวอักษรบนพื้นอ่อน
        "title": _mix(color, "#000000", 0.50), # สีหัวข้อใหญ่
        "deep": _mix(color, "#000000", 0.50),  # ปลายไล่สีของการ์ดเข้ม
        "tint1": _mix(color, "#ffffff", 0.94),
        "tint2": _mix(color, "#ffffff", 0.88),
        "tint3": _mix(color, "#ffffff", 0.78),
        "line": _mix(color, "#ffffff", 0.72),
        "soft": _mix(color, "#ffffff", 0.78),  # ตัวอักษรบนพื้นเข้ม
        "rgb": f"{r}, {g}, {b}",
    }

def theme_css(t):
    return f"""
<style>
    .hero-banner-red {{ background: linear-gradient(135deg, {t['tint1']} 0%, {t['tint2']} 50%, {t['tint3']} 100%); border-color: {t['line']}; box-shadow: 0 4px 20px rgba({t['rgb']}, 0.10); }}
    .tag-badge-red {{ background-color: {t['tint2']}; color: {t['text']}; border-color: {t['line']}; }}
    .stat-badge-red {{ background: {t['tint2']}; color: {t['text']}; }}
    .quote-box-red {{ background: {t['tint1']}; border-left-color: {t['main']}; }}
    .fact-label {{ color: {t['text']}; }}
    .person-card-complete:hover {{ box-shadow: 0 8px 24px rgba({t['rgb']}, 0.14); }}
    .spec-main-chip {{ background: {t['tint1']}; color: {t['text']}; border-color: {t['line']}; }}
    .spec-lab-active {{ background: {t['tint2']}; color: {t['text']}; }}
    .aff-balance {{ background: linear-gradient(145deg, {t['main']} 0%, {t['deep']} 100%); }}
    .aff-bal-kicker {{ color: {t['soft']}; }}
    .aff-bal-desc {{ color: {t['tint2']}; }}
</style>
"""

# ----------------- State Management -----------------
if "page" not in st.session_state: st.session_state.page = "home"
if "current_q" not in st.session_state: st.session_state.current_q = 0
if "answers" not in st.session_state: st.session_state.answers = {}

# =======================================================
# 1. หน้าแรก (Home Screen)
# =======================================================
if st.session_state.page == "home":
    # ปกหน้าแรก: วางไฟล์ภาพไว้ที่ assets/cover.jpg (ถ้าไม่มีไฟล์ จะใช้แบนเนอร์ตัวอักษรแทน)
    cover_path = os.path.join(BASE_DIR, "assets", "cover.jpg")
    cover_b64 = _read_image_b64(cover_path, os.path.getmtime(cover_path)) if os.path.isfile(cover_path) else None
    if cover_b64:
        st.markdown(f'<div class="cover-wrap"><img src="{cover_b64}" alt="POLI SPECTRA"></div>', unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="hero-banner-red">
                <span class="tag-badge-red">POLI SPECTRA</span>
                <h1 style="color:#881337; margin-top:8px; font-weight:700; font-size:32px;">ร่วมค้นหาจุดยืนทางการเมืองของคุณ</h1>
                <p style="color:#475569; font-size:15.5px; max-width:640px; margin:auto; line-height:1.65;">
                    ค้นพบจุดยืนและแนวคิดของคุณผ่านแบบทดสอบ 15 ข้อ ครอบคลุมอุดมการณ์ทางการเมือง พร้อมคำถามตัดสินรัฐบาลในฝัน ประมวลผลสู่บทบาทและบุคคลสำคัญทางประวัติศาสตร์
                </p>
            </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.8, 1.2])
    with col1:
        st.markdown("""
        <div class="main-card-light" style="height:100%;">
            <h4 style="margin-top:0; color:#0f172a; font-weight:700;">แบบประเมินจุดยืนทางการเมือง 15 ข้อ</h4>
            <p style="color:#64748b; font-size:14px; line-height:1.65;">
                • <b>ข้อ 1–14:</b> ประเมินระดับความคิดเห็นต่อประเด็นทางสังคมและเศรษฐกิจ<br>
                • <b>ข้อ 15:</b> ตัวตัดสินรูปแบบรัฐบาลในฝันที่คุณเห็นด้วยมากที่สุด
            </p>
            <div style="background:#fff1f2; padding:12px 14px; border-radius:12px; font-weight:600; color:#be123c; font-size:13.5px; border:1px solid #fecdd3; display:inline-block; margin-top:8px;">
                ⏱ 15 ข้อคำถาม • ใช้เวลาตอบประมาณ 3–4 นาที
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card-red">
            <h1 style="font-size:56px; margin:0; color:#ffffff; font-weight:800; line-height:1;">15</h1>
            <p style="color:#fecdd3; font-size:14px; margin-top:8px; margin-bottom:18px;">ข้อคำถามประเมินจุดยืน</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 เริ่มทำแบบทดสอบ", use_container_width=True, type="primary"):
            st.session_state.page = "quiz"
            st.session_state.current_q = 0
            st.session_state.answers = {}
            st.rerun()

    # แกนสเปกตรัม 7 อุดมการณ์ (ภาพนิ่ง)
    st.markdown(render_continuum_html(), unsafe_allow_html=True)

    # การ์ดอธิบาย 7 อุดมการณ์ (ภาพนิ่ง)
    st.markdown(render_ideology_cards_html(), unsafe_allow_html=True)

# =======================================================
# 2. หน้าคำถาม (Quiz Screen: สะอาดตา ไม่มีป้ายหมุดสีแดง)
# =======================================================
elif st.session_state.page == "quiz":
    q_idx = st.session_state.current_q
    q_data = questions_15[q_idx]
    total_q = len(questions_15)
    num = q_idx + 1
    pct = int(num / total_q * 100)
    remaining = total_q - num
    mins_left = max(1, math.ceil(remaining * 0.25))
    remain_text = f"เหลืออีก {remaining} ข้อ • ประเมินอีก ~{mins_left} นาที" if remaining > 0 else "ข้อสุดท้ายแล้ว"

    # ---------- แถบหัว: ปุ่มกลับ / สถานะ / ความคืบหน้า ----------
    h_back, h_live, h_right = st.columns([1.3, 2.0, 2.6])
    with h_back:
        if st.button("← กลับหน้าหลัก", use_container_width=True, type="secondary"):
            st.session_state.page = "home"
            st.rerun()
    with h_live:
        st.markdown(
            '<div class="qh-live"><span class="qh-live-dot"></span>LIVE QUESTIONNAIRE SESSION</div>',
            unsafe_allow_html=True
        )
    with h_right:
        st.markdown(_compact(f"""
        <div class="qh-right">
            <div class="qh-right-text">
                <div class="qh-count">ข้อ {num} จาก {total_q} ข้อ ({pct}%)</div>
                <div class="qh-remain">{remain_text}</div>
            </div>
            <div class="qh-badge">{num}</div>
        </div>
        """), unsafe_allow_html=True)

    # ---------- แถบความคืบหน้า + ชิปเลขข้อ ----------
    CHECK_SVG = ('<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#e11d48" stroke-width="2.4" '
                 'stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m8 12 3 3 5-6"/></svg>')
    chips = ""
    for i in range(total_q):
        cls = "done" if i < q_idx else ("cur" if i == q_idx else "")
        mark = CHECK_SVG if i < q_idx else '<span class="step-dot"></span>'
        chips += f'<div class="step-chip {cls}"><div class="step-top"><span>{i + 1:02d}</span>{mark}</div><div class="step-bar"></div></div>'
    st.markdown(_compact(f"""
    <div class="qp-card">
        <div class="qp-track"><div class="qp-fill" style="width:{pct}%;"></div></div>
        <div class="step-row">{chips}</div>
    </div>
    """), unsafe_allow_html=True)

    # ---------- การ์ดเดียวรวมคำถาม + ตัวเลือก + แถบปุ่ม ----------
    LANDMARK_SVG = ('<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="#be123c" stroke-width="2" '
                    'stroke-linecap="round" stroke-linejoin="round"><path d="M3 22h18"/><path d="M6 18v-7"/><path d="M10 18v-7"/>'
                    '<path d="M14 18v-7"/><path d="M18 18v-7"/><path d="M12 2 3 7v3h18V7z"/></svg>')
    hint = "โปรดเลือกระดับความเห็นของท่าน:" if q_data["type"] == "scale" else "เลือก 1 ใน 7 รูปแบบที่ตรงใจคุณที่สุด:"

    def _box(key):
        # container แบบมี key (Streamlit รุ่นใหม่) ถ้ารุ่นเก่าไม่รองรับให้ใช้ container ธรรมดา
        try:
            return st.container(key=key)
        except TypeError:
            return st.container()

    # เตรียมตัวเลือก: (ค่าที่เก็บ, ข้อความที่แสดง)
    if q_data["type"] == "scale":
        cur_ans = st.session_state.answers.get(q_idx, 0.50)
        st.session_state.answers[q_idx] = cur_ans
        # แสดงจาก "เห็นด้วยอย่างยิ่ง" -> "ไม่เห็นด้วยอย่างยิ่ง" (ค่าคะแนนยังเป็นของเดิม)
        option_list = [(v, scale_scoring[v]) for v in list(scale_scoring.keys())[::-1]]
    else:
        cur_ans = st.session_state.answers.get(q_idx)  # None ถ้ายังไม่เคยเลือก (ข้อ 15 ไม่ตั้งค่าเริ่มต้น)
        option_list = [(i, q15_options[i]["text"]) for i in range(len(q15_options))]

    with _box("quizcard"):
        st.markdown(_compact(f"""
        <div>
            <div class="q-icon-chip">{LANDMARK_SVG}</div>
            <div class="q-count">ข้อที่ {num} จาก {total_q}</div>
            <div class="q-text">“{q_data['q']}”</div>
            <div class="q-hint">{hint}</div>
        </div>
        """), unsafe_allow_html=True)

        # ตัวเลือก: ปุ่มเต็มความกว้าง แสดงเฉพาะข้อความ (ตัวที่เลือกใช้ key ขึ้นต้น optsel เพื่อไฮไลต์)
        for i, (val, label) in enumerate(option_list):
            selected = (cur_ans is not None and cur_ans == val)
            key = f"optsel_{q_idx}_{i}" if selected else f"opt_{q_idx}_{i}"
            if st.button(label, key=key, use_container_width=True):
                st.session_state.answers[q_idx] = val
                st.rerun()

        # แถบปุ่มด้านล่างในการ์ดเดียวกัน
        with _box("quizfoot"):
            b_prev, b_note, b_next = st.columns([0.6, 1.6, 2.6])
            with b_prev:
                if q_idx > 0 and st.button("←", use_container_width=True, type="secondary", key="btn_prev"):
                    st.session_state.current_q -= 1
                    st.rerun()
            with b_note:
                st.markdown('<div class="save-note">บันทึกอัตโนมัติเรียบร้อย</div>', unsafe_allow_html=True)
            with b_next:
                if q_idx < total_q - 1:
                    if st.button(f"บันทึกและทำข้อถัดไป (ข้อ {q_idx + 2}) →", type="primary", use_container_width=True, key="btn_next"):
                        st.session_state.current_q += 1
                        st.rerun()
                else:
                    q15_done = st.session_state.answers.get(q_idx) is not None
                    if st.button("ดูผลการประเมิน ➔", type="primary", use_container_width=True, disabled=not q15_done, key="btn_result"):
                        st.session_state.page = "result"
                        st.rerun()
            if q_idx == total_q - 1 and st.session_state.answers.get(q_idx) is None:
                st.caption("กรุณาเลือกรูปแบบรัฐบาลในฝันก่อนดูผลการประเมิน")

# =======================================================
# 3. หน้าผลลัพธ์ (Result Screen: ตัดคำว่าเฉดและคะแนนออก + รูปขนาดเท่ากัน)
# =======================================================
elif st.session_state.page == "result":
    # ถ้ายังไม่ได้ตอบข้อ 15 ให้กลับไปตอบก่อน
    if st.session_state.answers.get(14) is None:
        st.warning("ยังไม่ได้เลือกคำตอบข้อ 15 กรุณากลับไปตอบก่อนดูผลการประเมิน")
        if st.button("← กลับไปตอบข้อ 15", type="primary", use_container_width=True):
            st.session_state.page = "quiz"
            st.session_state.current_q = len(questions_15) - 1
            st.rerun()
        st.stop()

    shade_scores, strong_counts, bonus_shade = calculate_scores(st.session_state.answers)
    best_shade = pick_best(shade_scores, strong_counts, bonus_shade)
    profile_data = spectrum_master[best_shade]
    th = make_theme(SPECTRUM_COLORS[best_shade])  # ธีมสีตามอุดมการณ์ที่ได้
    st.markdown(theme_css(th), unsafe_allow_html=True)

    # ระดับความสอดคล้อง (ข้อความ) คำนวณจากคะแนนจริง ไม่แสดงตัวเลขให้ผู้ใช้เห็น
    level_scores = {s: level_text(v) for s, v in shade_scores.items()}
    best_level = level_scores[best_shade]

    # ส่วนหัวผลลัพธ์
    st.markdown(f"""
        <div class="hero-banner-red">
            <span class="tag-badge-red">POLITICAL SPECTRUM RESULT</span>
            <h1 style="color:{th['title']}; margin:8px 0 12px 0; font-size:32px; font-weight:800;">{profile_data['title']}</h1>
            <p style="color:#475569; font-size:15px; max-width:680px; margin:0 auto; line-height:1.65;">{profile_data['desc']}</p>
        </div>
    """, unsafe_allow_html=True)

    col_stat, col_chart = st.columns([1.2, 1.8])
    with col_stat:
        st.markdown("""
        <div class="main-card-light">
            <h4 style="margin-top:0; color:#0f172a; font-weight:700;">📊 สรุปความสอดคล้องกับอุดมการณ์</h4>
        """, unsafe_allow_html=True)

        # เรียงจากความสอดคล้องสูงไปต่ำ
        ranked = sorted(shade_scores.keys(), key=lambda s: (-shade_scores[s], s != best_shade))
        for s_name in ranked:
            is_best = (s_name == best_shade)
            color = th["text"] if is_best else "#64748b"
            weight = "700" if is_best else "500"
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; margin:10px 0; font-size:14.5px;">
                <span style="color:{color}; font-weight:{weight};">{'⭐ ' if is_best else '• '}{s_name}</span>
                <span style="color:{color}; font-weight:{weight};">{level_scores[s_name]}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="margin-top:16px; padding-top:12px; border-top:1px solid #f1f5f9; font-size:13.5px; color:#475569;">
                <b>รูปแบบที่เลือกในข้อตัดสิน:</b> <span style="color:{th['text']}; font-weight:600;">{bonus_shade}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_chart:
        # Spider Chart แสดงความสอดคล้อง
        radar_labels = list(shade_scores.keys())
        radar_values = list(shade_scores.values())

        radar_values_plot = radar_values + [radar_values[0]]

        N = len(radar_labels)
        angles = [n / float(N) * 2 * math.pi for n in range(N)]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(4.5, 4.2), subplot_kw=dict(polar=True), facecolor='#ffffff')
        ax.set_facecolor('#ffffff')
        ax.set_theta_offset(math.pi / 2)
        ax.set_theta_direction(-1)

        plt.xticks(angles[:-1], radar_labels, size=8.5, color='#1e293b', fontweight='bold')
        ax.set_rlabel_position(0)
        plt.yticks([1, 2, 3, 4, 5, 6], ["", "", "", "", "", ""], color="#94a3b8")
        plt.ylim(0, MAX_SHADE_SCORE)

        ax.plot(angles, radar_values_plot, linewidth=2.2, color=th['main'])
        ax.fill(angles, radar_values_plot, color=th['main'], alpha=0.25)

        ax.set_title("แผนภาพเปรียบเทียบระดับความสอดคล้อง", size=10, fontweight='bold', y=1.09, color=th['title'])
        st.pyplot(fig)
        plt.close(fig)  # คืนหน่วยความจำ ป้องกัน figure สะสมเมื่อ rerun ซ้ำ

    # ----------------- สเปกตรัม 7 อุดมการณ์ + Affinity Index -----------------
    st.markdown(render_spectrum_html(shade_scores, best_shade), unsafe_allow_html=True)

    # ----------------- การ์ดบุคคลสำคัญ 3 ท่าน (รูปภาพขนาดเท่ากัน 100%) -----------------
    st.markdown("### 🏛 นักคิดและบุคคลสำคัญที่สอดคล้องกับคุณ")
    st.caption(f"ตัวแทนทางความคิดทั้งด้านนักคิด ปรัชญา และผู้นำในกลุ่มแนวคิด: {best_shade}")

    p1 = profile_data["thinker"]
    p2 = profile_data["leader"]
    p3 = profile_data["overall"]

    # กติกา: 3 ท่านต้องมีนักคิดอย่างน้อย 1 และผู้นำอย่างน้อย 1 ส่วนท่านที่ 3 เป็นแบบใดก็ได้
    # ป้ายและหัวข้อกล่องล่างจึงดูจาก "ประเภทของบุคคลนั้น" ไม่ผูกกับลำดับช่อง
    # ถ้าในข้อมูลระบุ "type": "thinker" หรือ "leader" ไว้ในบุคคลนั้น จะใช้ค่านั้นก่อน มิฉะนั้นเดาจากคำขึ้นต้นของ role
    def person_type(person):
        t = person.get("type")
        if t in ("thinker", "leader"):
            return t
        if person["role"].startswith(("นักคิด", "นักปรัชญา", "บิดาแห่ง")):
            return "thinker"
        return "leader"

    CARD_LABELS = {
        "thinker": ("💡 นักคิดสำคัญ (Thinker)", "💡 แนวคิดโดยสรุป"),
        "leader": ("🏛️ ผู้นำ/นักการเมือง (Leader)", "🏛️ แนวทางโดยสรุป"),
    }
    three_cards = []
    for person in (p1, p2, p3):
        badge_title, fact_label = CARD_LABELS[person_type(person)]
        three_cards.append({"badge_title": badge_title, "fact_label": fact_label, "data": person})

    cols = st.columns(3)
    for idx, card in enumerate(three_cards):
        with cols[idx]:
            p = card["data"]
            fact_text = p["quote"].strip().strip('“”"')
            display_name = re.sub(r"\s*\(.*?\)", "", p["name"]).strip()  # ตัดวงเล็บเฉพาะตอนแสดงผล
            img_b64 = get_image_base64(p["name"])
            
            # บรรจุรูปภาพในกรอบ .person-img-wrapper บังคับขนาดกว้าง-ยาวและตัดขอบเท่ากันทุกรูปเป๊ะ
            if img_b64:
                img_tag = f'<div class="person-img-wrapper"><img src="{img_b64}"></div>'
            else:
                img_tag = f'<div class="person-img-wrapper" style="background:{th['tint1']}; border:1px dashed {th['line']}; color:{th['text']}; font-size:13px;">📷 รูป: {p["name"]}</div>'
            
            card_html = f"""
            <div class="person-card-complete">
                <div>
                    <div style="font-size:11px; font-weight:700; color:{th['text']}; margin-bottom:4px;">{card['badge_title']}</div>
                    <span class="stat-badge-red">{best_level}กับแนวคิดนี้</span>
                    <div style="margin:6px 0 2px 0; color:#0f172a; font-size:15px; font-weight:700; line-height:1.35; height:44px; display:flex; align-items:center; justify-content:center; text-align:center;">{display_name}</div>
                    <div style="font-size:12px; color:#64748b; min-height:52px; line-height:1.4;">{p['role']}</div>
                </div>
                {img_tag}
                <div class="quote-box-red"><div class="fact-label">{card['fact_label']}</div><div class="fact-text">{fact_text}</div></div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

    st.write("")
    if st.button("🔄 ทำแบบประเมินใหม่อีกครั้ง", use_container_width=True, type="secondary"):
        st.session_state.page = "home"
        st.session_state.answers = {}
        st.session_state.current_q = 0
        st.rerun()
