import os
import glob
import math
import base64
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ----------------- ตั้งค่าฟอนต์ภาษาไทยสำหรับ Matplotlib ให้แสดงผลได้ 100% -----------------
def setup_thai_font():
    thai_fonts = ['Tahoma', 'Leelawadee UI', 'Leelawadee', 'Angsana New', 'Cordia New', 'Segoe UI']
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    for font in thai_fonts:
        if font in available_fonts:
            plt.rcParams['font.family'] = font
            break
    plt.rcParams['axes.unicode_minus'] = False

setup_thai_font()

# ----------------- ตั้งค่าหน้าเพจ -----------------
st.set_page_config(
    page_title="แบบประเมินจุดยืนทางการเมือง 7 เฉด",
    page_icon="🧭",
    layout="centered"
)

# ----------------- CSS สไตล์ UI กรอบสวยงาม -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Sarabun', sans-serif !important; }
    
    .hero-banner {
        background: linear-gradient(135deg, #dbeafe 0%, #ede9fe 50%, #fce7f3 100%);
        border-radius: 20px;
        padding: 30px 20px;
        text-align: center;
        margin-bottom: 25px;
    }
    .main-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }
    .tag-badge {
        background-color: #e0f2fe;
        color: #0369a1;
        font-size: 13px;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 16px;
        display: inline-block;
        margin-bottom: 10px;
    }
    .info-box {
        background-color: #f0f7ff;
        border-left: 4px solid #2563eb;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 13.5px;
        color: #1e3a8a;
        margin-top: 14px;
        margin-bottom: 20px;
        line-height: 1.5;
    }
    .person-card-complete {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 480px;
    }
    .person-card-complete img {
        width: 100%;
        height: 185px;
        object-fit: cover;
        border-radius: 10px;
        margin: 10px 0;
    }
    .quote-box {
        font-size: 12px;
        color: #334155;
        background: #f8fafc;
        padding: 10px;
        border-radius: 8px;
        border-left: 3px solid #3b82f6;
        margin-top: 8px;
        text-align: left;
        line-height: 1.4;
    }
    .stat-badge {
        background: #eef2ff;
        color: #4338ca;
        font-size: 12px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 12px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- ฟังก์ชันดึงรูปภาพ Base64 -----------------
def get_image_base64(name_key):
    if not os.path.exists("images"):
        return None
    files = os.listdir("images")
    target_path = None
    clean_k = name_key.split("(")[0].strip().lower()
    
    for f in files:
        name_no_ext = os.path.splitext(f)[0].strip().lower()
        if name_key.strip().lower() == name_no_ext or clean_k == name_no_ext:
            target_path = os.path.join("images", f)
            break
            
    if not target_path:
        for f in files:
            name_no_ext = os.path.splitext(f)[0].strip().lower()
            if clean_k in name_no_ext or name_no_ext in clean_k:
                target_path = os.path.join("images", f)
                break

    if target_path and os.path.exists(target_path):
        try:
            with open(target_path, "rb") as img_file:
                b64 = base64.b64encode(img_file.read()).decode()
                ext = os.path.splitext(target_path)[1].replace(".", "").lower()
                if ext == "jpg": ext = "jpeg"
                return f"data:image/{ext};base64,{b64}"
        except Exception:
            return None
    return None

# ----------------- โหลดข้อมูลจากโฟลเดอร์ Excel/ -----------------
EXCEL_DIR = "Excel"

fallback_questions = [
    {"id": 1, "dim": "มิติที่ 01: แกนเศรษฐกิจ", "q": "รัฐควรลดการเก็บภาษีคนรวยและภาคธุรกิจเพื่อกระตุ้นการลงทุน", "ctx": "ประเมินแนวคิดเศรษฐกิจตลาดเสรีและการกระตุ้นการลงทุน", "dir": 1, "axis": "Econ"},
    {"id": 2, "dim": "มิติที่ 02: แกนเศรษฐกิจ", "q": "รัฐควรจัดสวัสดิการถ้วนหน้าให้ประชาชนทุกคนโดยไม่มีเงื่อนไข", "ctx": "วัดระดับการสนับสนุนรัฐสวัสดิการถ้วนหน้าเพื่อลดความเหลื่อมล้ำ", "dir": -1, "axis": "Econ"},
    {"id": 3, "dim": "มิติที่ 03: แกนเศรษฐกิจ", "q": "รัฐวิสาหกิจควรถูกแปรรูปเป็นของเอกชนเพื่อเพิ่มประสิทธิภาพ", "ctx": "วัดมุมมองต่อการแปรรูปรัฐวิสาหกิจและกลไกเอกชน", "dir": 1, "axis": "Econ"},
    {"id": 4, "dim": "มิติที่ 04: แกนเศรษฐกิจ", "q": "ค่าแรงขั้นต่ำควรถูกกำหนดโดยกลไกตลาดไม่ใช่กฎหมายบังคับ", "ctx": "ประเมินการปล่อยเสรีของกลไกตลาดแรงงาน", "dir": 1, "axis": "Econ"},
    {"id": 5, "dim": "มิติที่ 05: แกนเศรษฐกิจ", "q": "รัฐบาลควรเก็บภาษีมรดกในอัตราสูงเพื่อลดความเหลื่อมล้ำ", "ctx": "วัดการกระจายรายได้และการลดความเหลื่อมล้ำทางภาษี", "dir": -1, "axis": "Econ"},
    {"id": 6, "dim": "มิติที่ 06: แกนสังคม", "q": "การแต่งงานของบุคคลเพศเดียวกันควรได้รับการรับรองตามกฎหมาย", "ctx": "ประเมินสิทธิความหลากหลายและความก้าวหน้าทางวัฒนธรรม", "dir": -1, "axis": "Social"},
    {"id": 7, "dim": "มิติที่ 07: แกนสังคม", "q": "โทษประหารชีวิตควรถูกยกเลิกทั้งหมด", "ctx": "ประเมินคุณค่าสิทธิมนุษยชนสากลเทียบกับการลงโทษทางอาญา", "dir": -1, "axis": "Social"},
    {"id": 8, "dim": "มิติที่ 08: แกนสังคม", "q": "การรักษาความสงบเรียบร้อยและสถาบันหลักมีความสำคัญเหนือสิทธิการชุมนุม", "ctx": "สะท้อนแกนความคิดอนุรักษนิยมและความมั่นคงของรัฐ", "dir": 1, "axis": "Social"},
    {"id": 9, "dim": "มิติที่ 09: แกนสังคม", "q": "งบประมาณกองทัพควรได้รับการสนับสนุนอย่างเต็มที่เพื่อปกป้องความมั่นคง", "ctx": "วัดลำดับความสำคัญของความมั่นคงแห่งชาติและกองทัพ", "dir": 1, "axis": "Social"},
    {"id": 10, "dim": "มิติที่ 10: แกนสังคม", "q": "ผู้ว่าราชการจังหวัดทุกจังหวัดควรมาจากการเลือกตั้งโดยตรงของประชาชน", "ctx": "ประเมินการกระจายอำนาจสู่ท้องถิ่นเทียบกับการรวมศูนย์", "dir": -1, "axis": "Social"}
]

@st.cache_data
def load_all_models_from_excel():
    questions = []
    q_path = os.path.join(EXCEL_DIR, "02_คำถาม.xlsx")
    if os.path.exists(q_path):
        try:
            df_q = pd.read_excel(q_path)
            cols = [str(c).strip().lower() for c in df_q.columns]
            c_text = next((df_q.columns[i] for i, c in enumerate(cols) if any(k in c for k in ["question", "คำถาม", "โจทย์"])), None)
            c_dir = next((df_q.columns[i] for i, c in enumerate(cols) if any(k in c for k in ["dir", "ทิศทาง", "sign"])), None)
            c_axis = next((df_q.columns[i] for i, c in enumerate(cols) if any(k in c for k in ["axis", "แกน", "มิติ"])), None)
            if c_text:
                for idx, r in df_q.iterrows():
                    if idx >= 10: break
                    qid = idx + 1
                    q_dir = int(r[c_dir]) if c_dir and pd.notna(r[c_dir]) else fallback_questions[idx]["dir"]
                    q_ax = str(r[c_axis]) if c_axis and pd.notna(r[c_axis]) else fallback_questions[idx]["axis"]
                    questions.append({
                        "id": qid,
                        "dim": f"มิติที่ {qid:02d}: แกน{q_ax}",
                        "q": str(r[c_text]),
                        "ctx": f"ประเมินจุดยืนในมิติ{q_ax}",
                        "dir": q_dir,
                        "axis": "Econ" if qid <= 5 else "Social"
                    })
        except Exception:
            pass

    if len(questions) < 10:
        questions = fallback_questions

    # น้ำหนักแกนจาก 03_น้ำหนักแกน.xlsx
    w_path = os.path.join(EXCEL_DIR, "03_น้ำหนักแกน.xlsx")
    weights = {"econ": 0.5, "social": 0.5}
    if os.path.exists(w_path):
        try:
            df_w = pd.read_excel(w_path)
            nums = []
            for col in df_w.columns:
                for val in df_w[col]:
                    try:
                        f = float(val)
                        if 0.0 < f < 1.0: nums.append(f)
                    except: pass
            if len(nums) >= 2:
                weights["econ"] = nums[0]
                weights["social"] = nums[1]
        except Exception:
            pass

    # ตารางช่วงคะแนนตัดสินจาก 04_ตารางเฉด.xlsx
    shade_thresholds = [
        {"key": "far_left", "name": "คอมมิวนิสต์ (Communism)", "min": -2.00, "max": -1.43, "badge": "01 / 07 : ซ้ายจัด"},
        {"key": "left", "name": "สังคมนิยม (Socialism)", "min": -1.43, "max": -0.86, "badge": "02 / 07 : ซ้าย"},
        {"key": "center_left", "name": "เสรีนิยม (Liberalism)", "min": -0.86, "max": -0.29, "badge": "03 / 07 : กลาง-ซ้าย"},
        {"key": "center", "name": "สายกลาง (Centrism)", "min": -0.29, "max": 0.29, "badge": "04 / 07 : สายกลาง"},
        {"key": "center_right", "name": "อนุรักษ์นิยม (Conservatism)", "min": 0.29, "max": 0.86, "badge": "05 / 07 : กลาง-ขวา"},
        {"key": "right", "name": "อิสระนิยม (Libertarianism)", "min": 0.86, "max": 1.43, "badge": "06 / 07 : ขวา"},
        {"key": "far_right", "name": "ฟาสซิสต์ (Fascism)", "min": 1.43, "max": 2.00, "badge": "07 / 07 : ขวาจัด"}
    ]
    t_path = os.path.join(EXCEL_DIR, "04_ตารางเฉด.xlsx")
    if os.path.exists(t_path):
        try:
            df_t = pd.read_excel(t_path)
            for idx, r in df_t.iterrows():
                if idx < len(shade_thresholds):
                    row_nums = [float(v) for v in r if isinstance(v, (int, float))]
                    if len(row_nums) >= 2:
                        shade_thresholds[idx]["min"] = min(row_nums)
                        shade_thresholds[idx]["max"] = max(row_nums)
        except Exception:
            pass

    return questions, weights, shade_thresholds

# ฐานข้อมูลตัวแทนบุคคล 7 เฉด
spectrum_master = {
    "far_left": {
        "name": "คอมมิวนิสต์ (Communism)",
        "badge": "01 / 07 : ซ้ายจัด",
        "desc": "มุ่งสร้างสังคมที่ลดหรือยกเลิกความแตกต่างทางชนชั้น ถือครองทรัพยากรและปัจจัยการผลิตร่วมกันโดยสังคม แทนการให้เอกชนแสวงหากำไร",
        "decision": "มุ่งเน้นการปฏิรูปโครงสร้างทางเศรษฐกิจเพื่อความเสมอภาคสัมบูรณ์ ให้คุณค่ากับความเป็นธรรมทางชนชั้นและการรวมพลังของส่วนรวม",
        "card1_thinker": {"name": "คาร์ล มาร์กซ์ (Karl Marx)", "role": "นักคิดคอมมิวนิสต์: วิเคราะห์ชนชั้นและระบบเศรษฐกิจร่วมกัน", "quote": "“ชนชั้นกรรมาชีพไม่มีสิ่งใดจะสูญเสียนอกจากโซ่ตรวนของพวกเขา”"},
        "card2_leader": {"name": "วลาดีมีร์ เลนิน (Vladimir Lenin)", "role": "ผู้นำการปฏิวัติ: องค์กรพรรคที่มีวินัยเพื่อความเสมอภาค", "quote": "“เสรีภาพมีค่าเมื่อนำมาซึ่งความเสมอภาคของมวลชน”"},
        "card3_overall": {"name": "โฮจิมินห์ (Ho Chi Minh)", "role": "ผู้นำคอมมิวนิสต์: ชาตินิยมปลดปล่อยและความเสมอภาคทางสังคม", "quote": "“ความเป็นอันหนึ่งอันเดียวกันของประชาชนคือพลังลดความเหลื่อมล้ำ”"}
    },
    "left": {
        "name": "สังคมนิยม (Socialism)",
        "badge": "02 / 07 : ซ้าย",
        "desc": "สังคมส่วนรวมหรือรัฐเป็นเจ้าของปัจจัยการผลิตและการกระจายสินค้า เพื่อลดความเหลื่อมล้ำทางชนชั้น สร้างความเสมอภาค และกระจายความมั่งคั่งอย่างเป็นธรรม",
        "decision": "ตัดสินใจโดยคำนึงถึงสวัสดิการของคนส่วนใหญ่เป็นหลัก เชื่อมั่นในความร่วมมือและการเกื้อกูลกันในสังคม",
        "card1_thinker": {"name": "Friedrich Engels", "role": "นักคิดสังคมนิยม: วิเคราะห์โครงสร้างสังคมและความเสมอภาค", "quote": "“ความเป็นเจ้าของทรัพย์สินมีส่วนทำให้เกิดความไม่เสมอภาค”"},
        "card2_leader": {"name": "Olof Palme", "role": "ผู้นำสังคมนิยม: รัฐสวัสดิการถ้วนหน้าและการลดความเหลื่อมล้ำ", "quote": "“สิทธิสวัสดิการของประชาชน คือรากฐานที่แท้จริงของประชาธิปไตย”"},
        "card3_overall": {"name": "Kaysone Phomvihane", "role": "ผู้นำสังคมนิยม: การขับเคลื่อนสังคมเพื่อประโยชน์สุขส่วนรวม", "quote": "“สร้างสรรค์สังคมบนพื้นฐานความเป็นธรรมแก่ประชาชนทุกคน”"}
    },
    "center_left": {
        "name": "เสรีนิยม (Liberalism)",
        "badge": "03 / 07 : กลาง-ซ้าย",
        "desc": "ให้ความสำคัญกับเสรีภาพและสิทธิของปัจเจกบุคคล ความเสมอภาคภายใต้กฎหมาย หลักนิติธรรม และการจำกัดอำนาจรัฐไม่ให้แทรกแซงประชาชนเกินจำเป็น",
        "decision": "ยึดมั่นในสิทธิมนุษยชน เหตุผล และการเปิดกว้างทางความคิด ให้ความเคารพต่อความหลากหลายและการเลือกของแต่ละบุคคล",
        "card1_thinker": {"name": "John Rawls", "role": "นักปรัชญาเสรีนิยม: ทฤษฎีความยุติธรรมและโอกาสเท่าเทียม", "quote": "“ความยุติธรรมเริ่มต้นจากโอกาสที่เท่าเทียมของผู้ด้อยโอกาสที่สุด”"},
        "card2_leader": {"name": "Angela Markel", "role": "ผู้นำเสรีนิยมสายกลาง: เสถียรภาพ นิติธรรม และความร่วมมือสากล", "quote": "“ยึดมั่นในคุณค่าเสรีนิยมประชาธิปไตยและหลักการที่เคารพซึ่งกันและกัน”"},
        "card3_overall": {"name": "Valéry Giscard d'Estaing", "role": "ผู้นำเสรีนิยม: การปฏิรูปเพื่อขยายเสรีภาพของประชาชน", "quote": "“การปฏิรูปที่แท้จริงคือการเคารพสิทธิและเสรีภาพของปัจเจกบุคคล”"}
    },
    "center": {
        "name": "สายกลาง (Centrism)",
        "badge": "04 / 07 : สายกลาง",
        "desc": "จุดยืนกึ่งกลาง ปฏิเสธความสุดโต่งทั้งสองฝั่ง มุ่งเน้นการแก้ปัญหาได้จริงในทางปฏิบัติ (Pragmatism) ผ่านระบบเศรษฐกิจผสมและการประนีประนอม",
        "decision": "มีความยืดหยุ่นสูง ตัดสินใจตามข้อเท็จจริงและผลลัพธ์เชิงประจักษ์มากกว่าการยึดติดกับอุดมการณ์สุดโต่งด้านใดด้านหนึ่ง",
        "card1_thinker": {"name": "แอนโทนี กิดเดนส์", "role": "นักคิดทางสายที่สาม: การก้าวข้ามขั้วดั้งเดิมในยุคโลกาภิวัตน์", "quote": "“รัฐไม่ควรแทรกแซงแบบซ้ายเก่า และไม่ควรปล่อยปละละเลยแบบขวาเก่า”"},
        "card2_leader": {"name": "โทนี แบลร์ (Tony Blair)", "role": "ผู้นำ The Third Way: ผสานตลาดเสรีกับสวัสดิการสังคม", "quote": "“ยอมรับกลไกตลาดเสรีควบคู่กับการรักษาระบบสวัสดิการสังคม”"},
        "card3_overall": {"name": "จัสติน ทรูโด (Justin Trudeau)", "role": "ผู้นำสายกลางปฏิบัติ: สมดุลสิทธิเสรีภาพกับการเติบโตทางเศรษฐกิจ", "quote": "“รักษาสมดุลความก้าวหน้าทางสังคมควบคู่กับเสถียรภาพเศรษฐกิจ”"}
    },
    "center_right": {
        "name": "อนุรักษ์นิยม (Conservatism)",
        "badge": "05 / 07 : กลาง-ขวา",
        "desc": "คุณให้คุณค่ากับความมั่นคง เสถียรภาพ ประเพณี และสถาบันดั้งเดิม เชื่อว่าสังคมควรพัฒนาอย่างค่อยเป็นค่อยไป ไม่ใช่การปฏิวัติที่สุ่มเสี่ยงต่อความวุ่นวาย",
        "decision": "คุณเป็นคนรอบคอบ ระมัดระวังความเสี่ยง ให้ความสำคัญกับความปลอดภัยและความมั่นคงระยะยาวมากกว่าความเปลี่ยนแปลงที่ฉับพลัน",
        "card1_thinker": {"name": "Edmund Burke", "role": "บิดาแห่งอนุรักษ์นิยม: รักษาสถาบัน ประเพณี และการเปลี่ยนแปลงค่อยเป็นค่อยไป", "quote": "“เคารพภูมิปัญญาดั้งเดิมและระเบียบแบบแผนที่ผ่านการทดสอบตามกาลเวลา”"},
        "card2_leader": {"name": "Shinzo Abe", "role": "ผู้นำอนุรักษ์นิยม: เสถียรภาพทางเศรษฐกิจและความมั่นคงของชาติ", "quote": "“สร้างความเจริญเติบโตบนพื้นฐานความมั่นคงและเกียรติยศของชาติ”"},
        "card3_overall": {"name": "ชวน หลีกภัย", "role": "ผู้นำอนุรักษ์นิยมไทย: ยึดมั่นระบบรัฐสภาและหลักนิติธรรม", "quote": "“ให้ความสำคัญสูงสุดกับกฎหมาย ความมั่นคง และเสถียรภาพของรัฐ”"}
    },
    "right": {
        "name": "อิสระนิยม (Libertarianism)",
        "badge": "06 / 07 : ขวา",
        "desc": "ให้ความสำคัญสูงสุดกับเสรีภาพและกรรมสิทธิ์ในทรัพย์สิน ลดการแทรกแซงของรัฐให้เหลือน้อยที่สุด สนับสนุนตลาดเสรีบริสุทธิ์และความรับผิดชอบของปัจเจกบุคคล",
        "decision": "เชื่อมั่นในศักยภาพของปัจเจกชนและการแข่งขันอย่างเสรี ไม่ชอบการบังคับควบคุมหรือการแทรกแซงจากอำนาจรัฐ",
        "card1_thinker": {"name": "Robert Nozick", "role": "นักคิดอิสระนิยม: รัฐขนาดเล็กที่สุดเพื่อคุ้มครองสิทธิบุคคล", "quote": "“รัฐที่เล็กที่สุดคือรัฐเดียวที่มีความชอบธรรมในการคุ้มครองเสรีภาพ”"},
        "card2_leader": {"name": "Javier Milei", "role": "ผู้นำอิสระนิยม: เสรีภาพตลาดบริสุทธิ์ ลดบทบาทภาครัฐ", "quote": "“เสรีภาพทางเศรษฐกิจและกรรมสิทธิ์เอกชนคือกุญแจสู่ความเจริญรุ่งเรือง”"},
        "card3_overall": {"name": "Ron Paul", "role": "นักการเมืองอิสระนิยม: เสรีภาพปัจเจกและการจำกัดอำนาจรัฐ", "quote": "“เปิดพื้นที่ให้บุคคลกำหนดวิถีชีวิตและใช้อำนาจภายใต้กรอบกฎหมาย”"}
    },
    "far_right": {
        "name": "ฟาสซิสต์ (Fascism)",
        "badge": "07 / 07 : ขวาจัด",
        "desc": "ขบวนการทางการเมืองที่เน้นชาตินิยมสุดโต่งทางการทหาร การรวมศูนย์อำนาจเบ็ดเสร็จ และการให้ความสำคัญสูงสุดแก่ชาติเหนือปัจเจกบุคคล",
        "decision": "ให้ความสำคัญสูงสุดกับระเบียบวินัย ความเป็นหนึ่งเดียวของกลุ่ม และความเข้มแข็งเด็ดขาดของอำนาจผู้นำ",
        "card1_thinker": {"name": "โจวันนี เจตินเล (Giovanni Gentile)", "role": "นักคิดฟาสซิสต์: เอกภาพแห่งชาติและระเบียบวินัยสูงสุด", "quote": "“เอกภาพของรัฐและความเป็นหนึ่งเดียวอยู่เหนือเสรีภาพส่วนบุคคล”"},
        "card2_leader": {"name": "Benito Mussolini (เบนิโต มุสโสลินี)", "role": "ผู้นำฟาสซิสต์: รัฐรวมศูนย์และระเบียบวินัยเด็ดขาด", "quote": "“ทุกสิ่งรวมอยู่ในรัฐ ไม่มีสิ่งใดอยู่นอกเหนือรัฐ และไม่มีสิ่งใดต่อต้านรัฐได้”"},
        "card3_overall": {"name": "Adolf Hitler (อดอล์ฟ ฮิตเลอร์)", "role": "ผู้นำเผด็จการ: ชาตินิยมสุดโต่งและระเบียบการทหาร", "quote": "“ความแข็งแกร่งของรัฐตั้งอยู่บนระเบียบวินัยและความเป็นหนึ่งเดียวสูงสุด”"}
    }
}

# ----------------- State Management -----------------
if "page" not in st.session_state: st.session_state.page = "home"
if "current_q" not in st.session_state: st.session_state.current_q = 0
if "answers" not in st.session_state: st.session_state.answers = {}

questions, weights, thresholds = load_all_models_from_excel()

# =======================================================
# 1. หน้าแรก (Home Screen)
# =======================================================
if st.session_state.page == "home":
    st.markdown("""
        <div class="hero-banner">
            <span class="tag-badge">POLITICAL SPECTRUM MODEL • ฐานข้อมูล EXCEL</span>
            <h1 style="color:#0f172a; margin-top:8px; font-weight:700; font-size:30px;">คุณยืนอยู่จุดใดในทางการเมือง?</h1>
            <p style="color:#475569; font-size:15px; max-width:620px; margin:auto; line-height:1.6;">
                ค้นพบจุดยืนของคุณผ่านแบบจำลอง 2 แกน (เศรษฐกิจ และ สังคม) โดยดึงเกณฑ์และคำถามจากโฟลเดอร์ Excel ประมวลผลสู่ 7 เฉดอุดมการณ์
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.8, 1.2])
    with col1:
        st.markdown("""
        <div class="main-card">
            <h4 style="margin-top:0; color:#1e293b;">แบบประเมินจุดยืนทางการเมือง 10 ข้อ</h4>
            <p style="color:#64748b; font-size:14px; line-height:1.6;">
                วิเคราะห์คำตอบจากไฟล์ <b>02_คำถาม.xlsx</b> คำนวณค่าน้ำหนักผ่าน <b>03_น้ำหนักแกน.xlsx</b> และตัดสินผลลัพธ์ผ่าน <b>04_ตารางเฉด.xlsx</b>
            </p>
            <div style="background:#eff6ff; padding:12px; border-radius:10px; font-weight:600; color:#1d4ed8; font-size:13px;">
                ⏱ 10 ข้อคำถาม • ใช้เวลาทำประมาณ 3 นาที
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="main-card" style="text-align:center; background:#0f172a; color:white; padding:35px 20px;">
            <h1 style="font-size:52px; margin:0; color:#60a5fa; font-weight:700;">10</h1>
            <p style="color:#94a3b8; font-size:14px; margin-bottom:20px;">คำถามประเมินจุดยืน</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 เริ่มทำแบบทดสอบ", use_container_width=True, type="primary"):
            st.session_state.page = "quiz"
            st.session_state.current_q = 0
            st.session_state.answers = {}
            st.rerun()

# =======================================================
# 2. หน้าคำถาม (Quiz Screen: ไม่แสดงคะแนน)
# =======================================================
elif st.session_state.page == "quiz":
    q_idx = st.session_state.current_q
    q_data = questions[q_idx]

    c_back, c_prog = st.columns([1, 4])
    with c_back:
        if st.button("← หน้าแรก"):
            st.session_state.page = "home"
            st.rerun()
    with c_prog:
        st.progress((q_idx + 1) / len(questions))
        st.caption(f"ข้อที่ {q_idx + 1} จาก {len(questions)} ข้อ ({(q_idx + 1) * 10}%)")

    st.markdown(f"""
    <div class="main-card">
        <span class="tag-badge">🏛 {q_data['dim']}</span>
        <h4 style="color:#64748b; font-size:14px; margin:0;">ข้อที่ {q_idx + 1} จาก 10</h4>
        <h2 style="color:#0f172a; margin-top:8px; font-size:20px; line-height:1.5;">“{q_data['q']}”</h2>
        <div class="info-box">
            ℹ️ <b>บริบททางวิชาการ:</b> {q_data['ctx']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    opts = {
        2: "เห็นด้วยอย่างยิ่ง (Strongly Agree)",
        1: "เห็นด้วย (Agree)",
        0: "ไม่แน่ใจ / เป็นกลาง (Neutral)",
        -1: "ไม่เห็นด้วย (Disagree)",
        -2: "ไม่เห็นด้วยอย่างยิ่ง (Strongly Disagree)"
    }

    cur_ans = st.session_state.answers.get(q_idx, 0)
    choice = st.radio(
        "ระดับความคิดเห็น",
        list(opts.keys()),
        format_func=lambda x: opts[x],
        index=list(opts.keys()).index(cur_ans),
        label_visibility="collapsed"
    )
    st.session_state.answers[q_idx] = choice

    st.write("")
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if q_idx > 0 and st.button("← ย้อนกลับข้อก่อนหน้า", use_container_width=True):
            st.session_state.current_q -= 1
            st.rerun()
    with btn_col2:
        if q_idx < len(questions) - 1:
            if st.button(f"บันทึกและทำข้อถัดไป (ข้อ {q_idx + 2}) →", type="primary", use_container_width=True):
                st.session_state.current_q += 1
                st.rerun()
        else:
            if st.button("ดูผลการประเมิน ➔", type="primary", use_container_width=True):
                st.session_state.page = "result"
                st.rerun()

# =======================================================
# 3. หน้าผลลัพธ์ (Spider Chart เป็นภาษาไทย + ตัวแทนแนวคิดตรงกัน 100%)
# =======================================================
elif st.session_state.page == "result":
    econ_scores = []
    social_scores = []

    for i in range(10):
        ans = st.session_state.answers.get(i, 0)
        direction = questions[i]["dir"]
        score_item = ans * direction
        if i < 5:
            econ_scores.append(score_item)
        else:
            social_scores.append(score_item)

    econ_avg = sum(econ_scores) / len(econ_scores)        # แกนเศรษฐกิจ (-2.0 ถึง +2.0)
    social_avg = sum(social_scores) / len(social_scores)    # แกนสังคม (-2.0 ถึง +2.0)
    
    w_econ = weights.get("econ", 0.5)
    w_social = weights.get("social", 0.5)
    composite_score = (econ_avg * w_econ) + (social_avg * w_social)

    # ตัดสินผลลัพธ์ผ่านตัวเลขจริง
    matched_tier = thresholds[3]
    for t in thresholds:
        if t["min"] <= composite_score <= t["max"]:
            matched_tier = t
            break

    profile_data = spectrum_master[matched_tier["key"]]

    # แสดงผลหัวข้อ
    st.markdown(f"""
        <div class="hero-banner" style="padding:26px 20px;">
            <span class="tag-badge">ผลการประเมินและทำนายจุดยืนทางการเมือง</span>
            <p style="color:#64748b; font-size:13px; margin:4px 0;">POLITICAL SPECTRUM RESULT</p>
            <h2 style="color:#0f172a; margin:4px 0 8px 0; font-size:26px;">{matched_tier['name']}</h2>
            <div style="color:#2563eb; font-weight:600; font-size:15px;">{matched_tier['badge']} (คะแนนผสาน: {composite_score:+.2f})</div>
            <p style="color:#475569; font-size:14px; max-width:650px; margin:10px auto 0 auto; line-height:1.5;">{profile_data['desc']}</p>
        </div>
    """, unsafe_allow_html=True)

    col_stat, col_chart = st.columns([1.2, 1.8])
    with col_stat:
        st.markdown(f"""
        <div class="main-card">
            <h4 style="margin-top:0;">📊 สรุปจุดยืน 2 แกน</h4>
            <div style="margin:12px 0;">
                <div style="font-size:12px; color:#64748b;">1. แกนเศรษฐกิจ (Q1–Q5):</div>
                <div style="font-size:17px; font-weight:700; color:{'#2563eb' if econ_avg < 0 else '#dc2626'};">
                    {econ_avg:+.2f} ({'ซ้าย / สวัสดิการรวมหมู่' if econ_avg < 0 else 'ขวา / ตลาดเสรี-เอกชน'})
                </div>
            </div>
            <div style="margin:12px 0;">
                <div style="font-size:12px; color:#64748b;">2. แกนสังคม (Q6–Q10):</div>
                <div style="font-size:17px; font-weight:700; color:{'#2563eb' if social_avg < 0 else '#dc2626'};">
                    {social_avg:+.2f} ({'ก้าวหน้า / สิทธิเสรีภาพ' if social_avg < 0 else 'อนุรักษ์ / มั่นคง-จารีต'})
                </div>
            </div>
            <div style="margin-top:14px; padding-top:10px; border-top:1px solid #e2e8f0;">
                <div style="font-size:12px; color:#64748b;">ลักษณะการตัดสินใจของคุณ:</div>
                <div style="font-size:13px; color:#334155; margin-top:4px; line-height:1.4;">{profile_data['decision']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_chart:
        # ----------------- Spider Chart (ภาษาไทย 100%) -----------------
        # แกนรอบวงเป็น 7 แนวคิดอุดมการณ์ภาษาไทย
        radar_ideologies_th = [
            'คอมมิวนิสต์',
            'สังคมนิยม',
            'เสรีนิยม',
            'สายกลาง',
            'อนุรักษ์นิยม',
            'อิสระนิยม',
            'ฟาสซิสต์'
        ]

        # จุดกึ่งกลางของแต่ละเฉดบนสเกล [-2.0, +2.0]
        ideology_centers = {
            'คอมมิวนิสต์': -1.72,
            'สังคมนิยม': -1.15,
            'เสรีนิยม': -0.58,
            'สายกลาง': 0.00,
            'อนุรักษ์นิยม': 0.58,
            'อิสระนิยม': 1.15,
            'ฟาสซิสต์': 1.72
        }

        # คำนวณความสอดคล้อง (%) เทียบกับแต่ละแนวคิด
        vals = []
        for ideo in radar_ideologies_th:
            center_val = ideology_centers[ideo]
            distance = abs(composite_score - center_val)
            affinity = max(15.0, (1.0 - (distance / 3.8)) * 100.0)
            vals.append(affinity)
        
        vals += vals[:1] # ปิดลูปกราฟ
        
        N = len(radar_ideologies_th)
        angles = [n / float(N) * 2 * math.pi for n in range(N)]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(4.5, 4.2), subplot_kw=dict(polar=True))
        ax.set_theta_offset(math.pi / 2)
        ax.set_theta_direction(-1)
        
        # ป้ายชื่อแกนรอบวงเป็นภาษาไทย
        plt.xticks(angles[:-1], radar_ideologies_th, size=8.5, color='#1e293b', fontweight='bold')
        ax.set_rlabel_position(0)
        plt.yticks([25, 50, 75, 100], ["25%", "50%", "75%", "100%"], color="#94a3b8", size=6.5)
        plt.ylim(0, 100)
        
        # วาดเส้นและพื้นที่สีน้ำเงิน
        ax.plot(angles, vals, linewidth=2, color='#2563eb')
        ax.fill(angles, vals, color='#3b82f6', alpha=0.35)
        
        # หัวข้อกราฟภาษาไทย
        ax.set_title("ระดับความสอดคล้องกับ 7 แนวคิดทางการเมือง", size=10, fontweight='bold', y=1.09, color='#0f172a')
        
        st.pyplot(fig)

    # ----------------- แมตช์บุคคลทั้ง 3 คนตามเฉดอุดมการณ์เดียวกัน 100% -----------------
    st.markdown("### 🏛️ นักคิดและบุคคลสำคัญที่สอดคล้องกับคุณ")
    st.caption(f"ตัวแทนทางความคิดทั้งด้านนักคิด ปรัชญา และผู้นำในกลุ่มเฉด: {matched_tier['name']}")

    p1 = profile_data["card1_thinker"]  # นักคิดสำคัญ
    p2 = profile_data["card2_leader"]   # ผู้นำสำคัญ
    p3 = profile_data["card3_overall"]  # บุคคลตัวแทนภาพรวม

    three_cards = [
        {"badge_title": "💡 หัวข้อที่ 1: นักคิดสำคัญ (Thinker)", "match": "95% Alignment", "data": p1},
        {"badge_title": "🏛️ หัวข้อที่ 2: ผู้นำ/นักการเมือง (Leader)", "match": "93% Alignment", "data": p2},
        {"badge_title": "🧭 ภาพรวม: ตัวแทนอุดมการณ์", "match": "94% Alignment", "data": p3}
    ]

    cols = st.columns(3)
    for idx, card in enumerate(three_cards):
        with cols[idx]:
            p = card["data"]
            img_b64 = get_image_base64(p["name"])
            
            img_tag = f'<img src="{img_b64}">' if img_b64 else f'<div style="height:180px; background:#f1f5f9; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#64748b; font-size:13px; margin:10px 0;">📷 รูป: {p["name"]}</div>'
            
            card_html = f"""
            <div class="person-card-complete">
                <div>
                    <div style="font-size:11px; font-weight:700; color:#2563eb; margin-bottom:4px;">{card['badge_title']}</div>
                    <span class="stat-badge">{card['match']}</span>
                    <h4 style="margin:6px 0 2px 0; color:#0f172a; font-size:15px;">{p['name']}</h4>
                    <div style="font-size:12px; color:#64748b; min-height:36px; line-height:1.4;">{p['role']}</div>
                </div>
                {img_tag}
                <div class="quote-box">{p['quote']}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

    st.write("")
    if st.button("🔄 ทำแบบประเมินใหม่อีกครั้ง", use_container_width=True):
        st.session_state.page = "home"
        st.session_state.answers = {}
        st.session_state.current_q = 0
        st.rerun()