import os
import glob
import math
import base64
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ----------------- ตั้งค่าฟอนต์สำหรับ Matplotlib -----------------
def setup_thai_font():
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Liberation Sans', 'Tahoma', 'Leelawadee UI', 'Segoe UI']
    plt.rcParams['axes.unicode_minus'] = False

setup_thai_font()

# ----------------- ตั้งค่าหน้าเพจ -----------------
st.set_page_config(
    page_title="แบบประเมินจุดยืนทางการเมือง 7 อุดมการณ์",
    page_icon="🧭",
    layout="wide"  # ใช้ Wide layout เพื่อไม่ให้หน้าจอบนคอมโดนบีบแคบ
)

# ----------------- CSS สไตล์ Responsive UI (สมดุลทั้งคอมและมือถือ) -----------------
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
    
    /* ควบคุมขนาดคอนเทนเนอร์บนจอคอมให้กว้างพอดี ไม่หดแคบเป็นกล่องเล็ก */
    .block-container {
        max-width: 960px !important;
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        margin: 0 auto !important;
    }
    
    /* Hero Banner สว่างพรีเมียม */
    .hero-banner-red {
        background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 50%, #fecdd3 100%);
        border-radius: 20px;
        padding: 32px 24px;
        text-align: center;
        margin-bottom: 24px;
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
    
    /* การ์ดเนื้อหา */
    .main-card-light {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px 28px;
        border: 1px solid #f1f5f9;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
    }
    
    /* Radio ตัวเลือกคำถาม */
    div[data-testid="stRadio"] label p {
        font-size: 15px !important;
        font-weight: 500 !important;
        color: #1e293b !important;
        line-height: 1.5 !important;
    }
    div[data-testid="stRadio"] > div {
        background-color: #ffffff;
        padding: 12px 16px;
        border-radius: 12px;
        border: 1px solid #f1f5f9;
        gap: 12px !important;
    }

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
    
    /* ปุ่มย้อนกลับ */
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

    /* การ์ดบุคคลสำคัญ 3 ใบ สัดส่วนมาตรฐาน ไม่ยืดแบน */
    .person-card-complete {
        background: #ffffff;
        border: 1px solid #f1f5f9;
        border-radius: 16px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 490px;
        margin-bottom: 15px;
    }
    
    /* ปรับกรอบรูปภาพให้เท่ากัน 100% พร้อมล็อกตำแหน่งใบหน้า */
    .person-img-wrapper {
        width: 100%;
        aspect-ratio: 4 / 3;
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
        object-position: center 20% !important; /* จัดโฟกัสช่วงใบหน้าพอดี */
    }
    
    .quote-box-red {
        font-size: 13px;
        color: #475569;
        background: #fff1f2;
        padding: 10px 12px;
        border-radius: 8px;
        border-left: 3px solid #e11d48;
        margin-top: 8px;
        text-align: left;
        line-height: 1.45;
        min-height: 54px;
        display: flex;
        align-items: center;
    }
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
</style>
""", unsafe_allow_html=True)

# ----------------- ฟังก์ชันดึงรูปภาพ Base64 -----------------
def get_image_base64(name_key):
    if not os.path.exists("images"):
        return None
    files = os.listdir("images")
    target_path = None
    
    clean_k = name_key.strip().lower()
    no_paren = clean_k.split("(")[0].strip()
    
    alias_map = {
        "kaysone phomvihane": "kaysone phomvihane",
        "olof palme": "olof palme",
        "friedrich engels": "friedrich engels",
        "karl marx": "คาร์ล มาร์กซ์ (karl marx)",
        "คาร์ล มาร์กซ์": "คาร์ล มาร์กซ์ (karl marx)",
        "vladimir lenin": "วลาดีมีร์ เลนิน (vladimir lenin)",
        "วลาดีมีร์ เลนิน": "วลาดีมีร์ เลนิน (vladimir lenin)",
        "ho chi minh": "โฮจิมินห์ (ho chi minh)",
        "โฮจิมินห์": "โฮจิมินห์ (ho chi minh)",
        "angela merkel": "angela markel",
        "angela markel": "angela markel",
        "tony blair": "โทนี แบลร์ (tony blair)",
        "โทนี แบลร์": "โทนี แบลร์ (tony blair)",
        "justin trudeau": "จัสติน ทรูโด (justin trudeau)",
        "จัสติน ทรูโด": "จัสติน ทรูโด (justin trudeau)",
        "edmund burke": "edmund burke",
        "shinzo abe": "shinzo abe",
        "ชวน หลีกภัย": "ชวน หลีกภัย",
        "javier milei": "javier milei",
        "robert nozick": "robert nozick",
        "ron paul": "ron paul",
        "john rawls": "john rawls",
        "valéry giscard d'estaing": "valéry giscard d'estaing",
        "giovanni gentile": "โจวันนี เจตินเล (giovanni gentile)",
        "โจวันนี เจตินเล": "โจวันนี เจตินเล (giovanni gentile)",
        "benito mussolini": "benito mussolini (เบนิโต มุสโสลินี)",
        "เบนิโต มุสโสลินี": "benito mussolini (เบนิโต มุสโสลินี)",
        "adolf hitler": "adolf hitler (อดอล์ฟ ฮิตเลอร์)",
        "อดอล์ฟ ฮิตเลอร์": "adolf hitler (อดอล์ฟ ฮิตเลอร์)",
        "แอนโทนี กิดเดนส์": "แอนโทนี กิดเดนส์"
    }

    search_target = alias_map.get(no_paren, no_paren)

    for f in files:
        name_no_ext = os.path.splitext(f)[0].strip().lower()
        if clean_k == name_no_ext or search_target == name_no_ext:
            target_path = os.path.join("images", f)
            break
            
    if not target_path:
        for f in files:
            name_no_ext = os.path.splitext(f)[0].strip().lower()
            if search_target in name_no_ext or name_no_ext in search_target:
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

# ----------------- คำถาม 15 ข้อตามโครงสร้างจริง -----------------
questions_15 = [
    {"id": 1, "code": "Q1", "shade": "คอมมิวนิสต์", "q": "รัฐควรให้ความสำคัญกับผลประโยชน์และความต้องการของส่วนรวมมากกว่าสิทธิในการถือครองทรัพย์สินและผลประโยชน์ส่วนบุคคล เพื่อสร้างสังคมที่ไม่มีการแก่งแย่งชนชั้น", "type": "scale"},
    {"id": 2, "code": "Q2", "shade": "คอมมิวนิสต์", "q": "ประชาชนควรร่วมกันทำงานและมีส่วนร่วมในการผลิตและแบ่งปันทรัพยากรหรือผลผลิตของประเทศอย่างเป็นธรรม", "type": "scale"},
    {"id": 3, "code": "Q3", "shade": "สังคมนิยม", "q": "การศึกษาและการรักษาพยาบาลทุกระดับ ควรเป็นสิทธิขั้นพื้นฐานที่ทุกคนต้องได้รับฟรี โดยรัฐเป็นผู้รับผิดชอบค่าใช้จ่ายทั้งหมด", "type": "scale"},
    {"id": 4, "code": "Q4", "shade": "สังคมนิยม", "q": "รัฐบาลควรเข้ามาแทรกแซงและควบคุมระบบเศรษฐกิจ (เช่น ควบคุมราคาสินค้า หรือกำหนดค่าแรงขั้นต่ำให้สูง) เพื่อป้องกันไม่ให้เกิดความเหลื่อมล้ำทางรายได้", "type": "scale"},
    {"id": 5, "code": "Q5", "shade": "เสรีนิยม", "q": "ประชาชนควรมีสิทธิแสดงความคิดเห็นทางการเมืองได้อย่างเสรี แม้ความคิดเห็นนั้นจะวิพากษ์วิจารณ์รัฐบาล", "type": "scale"},
    {"id": 6, "code": "Q6", "shade": "เสรีนิยม", "q": "รัฐไม่ควรจำกัดเสรีภาพของประชาชน เว้นแต่การกระทำนั้นจะก่อให้เกิดอันตรายต่อผู้อื่น", "type": "scale"},
    {"id": 7, "code": "Q7", "shade": "สายกลาง", "q": "การแก้ปัญหาประเทศที่ดีที่สุด คือการประนีประนอมและค่อยเป็นค่อยไป มากกว่าการยึดติดกับอุดมการณ์สุดโต่งข้างใดข้างหนึ่ง", "type": "scale"},
    {"id": 8, "code": "Q8", "shade": "สายกลาง", "q": "นโยบายรัฐไม่ควรตัดสินจากคำว่า 'ฝ่ายซ้าย' หรือ 'ฝ่ายขวา' แต่ควรวัดจากหลักฐานเชิงประจักษ์และความเป็นไปได้จริงในทางปฏิบัติ", "type": "scale"},
    {"id": 9, "code": "Q9", "shade": "อนุรักษ์นิยม", "q": "สังคมควรรักษาประเพณีและวัฒนธรรมดั้งเดิมไว้ มากกว่าการเปลี่ยนแปลงตามกระแสสมัยใหม่", "type": "scale"},
    {"id": 10, "code": "Q10", "shade": "อนุรักษ์นิยม", "q": "การเปลี่ยนแปลงโครงสร้างทางสังคมและการเมืองควรทำอย่างค่อยเป็นค่อยไป ไม่ควรเปลี่ยนแปลงอย่างรวดเร็วหรือรุนแรง", "type": "scale"},
    {"id": 11, "code": "Q11", "shade": "อิสระนิยม", "q": "รัฐบาลควรแทรกแซงเศรษฐกิจและการทำธุรกิจให้น้อยที่สุด ปล่อยให้เป็นเรื่องของกลไกตลาดเสรีและการแข่งขันอย่างเป็นธรรม", "type": "scale"},
    {"id": 12, "code": "Q12", "shade": "อิสระนิยม", "q": "ตราบใดที่การกระทำนั้นไม่ได้ละเมิดหรือสร้างความเดือดร้อนให้คนอื่น ประชาชนควรมีเสรีภาพในการตัดสินใจชีวิตตนเองอย่างเต็มที่ เช่น ความเชื่อ ร่างกาย", "type": "scale"},
    {"id": 13, "code": "Q13", "shade": "ฟาสซิสต์", "q": "เชื้อชาติที่มีอารยธรรมและศักยภาพเหนือกกว่า ย่อมมีสิทธิ์โดยชอบธรรมในการนำพาหรือควบคุมประชากรอื่นเพื่อความก้าวหน้า", "type": "scale"},
    {"id": 14, "code": "Q14", "shade": "ฟาสซิสต์", "q": "ความมั่นคงของรัฐมีความสำคัญมากกว่าสิทธิและเสรีภาพของปัจเจกชน", "type": "scale"},
    {"id": 15, "code": "Q15", "shade": "ตัวตัดสิน", "q": "หากคุณมีโอกาสกำหนดรูปแบบการบริหารประเทศในรัฐบาลในฝันของคุณ คุณจะเลือกแนวทางใดต่อไปนี้มากที่สุด?", "type": "bonus"}
]

q15_options = [
    {"id": 0, "shade": "คอมมิวนิสต์", "title": "รูปแบบที่ 1 : เน้นความเสมอภาคและรัฐดูแลส่วนรวมเป็นหลัก", "text": "รัฐเข้ามาดูแลทรัพยากรและกิจการสำคัญของประเทศเป็นหลัก ลดความเหลื่อมล้ำด้านรายได้และทรัพย์สิน ให้ประชาชนมีความเสมอภาคสูง และการตัดสินใจทางเศรษฐกิจและการเมืองเป็นไปในทิศทางเดียวกันเพื่อประโยชน์ส่วนรวม"},
    {"id": 1, "shade": "สังคมนิยม", "title": "รูปแบบที่ 2 : เน้นรัฐสวัสดิการถ้วนหน้าและลดช่องว่างทางชนชั้น", "text": "รัฐจัดสวัสดิการและบริการสาธารณะอย่างทั่วถึง ควบคุมหรือกำกับกิจการสำคัญบางส่วนเพื่อสร้างความเป็นธรรมทางเศรษฐกิจ เปิดให้ประชาชนมีส่วนร่วมทางการเมือง และพยายามลดความแตกต่างระหว่างกลุ่มคนในสังคม"},
    {"id": 2, "shade": "เสรีนิยม", "title": "รูปแบบที่ 3 : เน้นสิทธิเสรีภาพ ความเท่าเทียม และกลไกตลาดมีธรรมภิบาล", "text": "รัฐคุ้มครองสิทธิและเสรีภาพของประชาชน เปิดโอกาสให้ทุกคนแข่งขันและแสดงความคิดเห็นได้อย่างเท่าเทียม ใช้ระบบเศรษฐกิจที่อาศัยตลาดเป็นสำคัญแต่มีมาตรการช่วยเหลือผู้ที่เสียเปรียบ และยึดหลักการปกครองที่ประชาชนมีส่วนร่วม"},
    {"id": 3, "shade": "สายกลาง", "title": "รูปแบบที่ 4 : เน้นการประนีประนอม นโยบายผสมผสานตามสถานการณ์จริง", "text": "รัฐเลือกใช้นโยบายตามสถานการณ์ โดยผสมผสานการดูแลเศรษฐกิจของรัฐกับกลไกตลาด ให้ความสำคัญทั้งสิทธิเสรีภาพและความมั่นคง ส่งเสริมสวัสดิการในระดับที่เหมาะสม และเปิดพื้นที่ให้ความคิดเห็นที่แตกต่างสามารถอยู่ร่วมกันได้"},
    {"id": 4, "shade": "อนุรักษ์นิยม", "title": "รูปแบบที่ 5 : เน้นความมั่นคง ระเบียบวินัย และจารีตประเพณีอันดีงาม", "text": "รัฐให้ความสำคัญกับความมั่นคงของประเทศ ระเบียบวินัย และการรักษาขนบธรรมเนียมที่สังคมเห็นว่ามีคุณค่า สนับสนุนเศรษฐกิจที่เติบโตโดยอาศัยภาคเอกชนและครอบครัวเป็นกำลังสำคัญ พร้อมเปลี่ยนแปลงสิ่งต่างๆ อย่างค่อยเป็นค่อยไป"},
    {"id": 5, "shade": "อิสระนิยม", "title": "รูปแบบที่ 6 : เน้นตลาดเสรีบริสุทธิ์และจำกัดบทบาทรัฐให้น้อยที่สุด", "text": "รัฐควรเข้าไปยุ่งเกี่ยวกับชีวิตและเศรษฐกิจของประชาชนให้น้อยที่สุด เปิดโอกาสให้แต่ละคนตัดสินใจและประกอบกิจการได้อย่างอิสระ ลดกฎระเบียบและภาษีที่ไม่จำเป็น และจำกัดอำนาจรัฐเพื่อคุ้มครองสิทธิและเสรีภาพของแต่ละบุคคล"},
    {"id": 6, "shade": "ฟาสซิสต์", "title": "รูปแบบที่ 7 : เน้นเอกภาพแห่งชาติ รวมศูนย์อำนาจ และระเบียบวินัยเข้มงวด", "text": "รัฐรวมอำนาจในการกำหนดทิศทางประเทศไว้อย่างเข้มแข็ง ให้ความสำคัญกับความเป็นเอกภาพของชาติ วินัย และการเชื่อฟังอำนาจรัฐ ส่งเสริมเศรษฐกิจที่ตอบสนองเป้าหมายของชาติ และจำกัดความขัดแย้งทางการเมืองเพื่อรักษาความเป็นระเบียบและความมั่นคงของประเทศ"}
]

scale_scoring = {
    0.00: "ไม่เห็นด้วยอย่างยิ่ง",
    0.25: "ไม่เห็นด้วย",
    0.50: "เฉยๆ",
    1.00: "เห็นด้วย",
    2.00: "เห็นด้วยอย่างยิ่ง"
}

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
        "leader": {"name": "Angela Markel", "role": "ผู้นำเสรีนิยมสายกลาง: เสถียรภาพ นิติธรรม และความร่วมมือสากล", "quote": "“ยึดมั่นในคุณค่าเสรีนิยมประชาธิปไตยและหลักการที่เคารพซึ่งกันและกัน”"},
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

# ----------------- State Management -----------------
if "page" not in st.session_state: st.session_state.page = "home"
if "current_q" not in st.session_state: st.session_state.current_q = 0
if "answers" not in st.session_state: st.session_state.answers = {}

# =======================================================
# 1. หน้าแรก (Home Screen)
# =======================================================
if st.session_state.page == "home":
    st.markdown("""
        <div class="hero-banner-red">
            <span class="tag-badge-red">POLITICAL SPECTRUM MODEL</span>
            <h1 style="color:#881337; margin:8px 0; font-weight:700; font-size:32px;">คุณยืนอยู่จุดใดในทางการเมือง?</h1>
            <p style="color:#475569; font-size:15px; margin:auto; line-height:1.6; max-width:640px;">
                ค้นพบจุดยืนและแนวคิดของคุณผ่านแบบทดสอบ 15 ข้อ ครอบคลุมอุดมการณ์ทางการเมือง พร้อมคำถามตัดสินรัฐบาลในฝัน
            </p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1.8, 1.2])
    with c1:
        st.markdown("""
        <div class="main-card-light" style="height:100%;">
            <h4 style="margin-top:0; color:#0f172a; font-weight:700; font-size:18px;">แบบประเมินจุดยืนทางการเมือง 15 ข้อ</h4>
            <p style="color:#64748b; font-size:14.5px; line-height:1.6;">
                • <b>ข้อ 1–14:</b> ประเมินระดับความคิดเห็นต่อประเด็นทางสังคมและเศรษฐกิจ<br>
                • <b>ข้อ 15:</b> ตัวตัดสินรูปแบบรัฐบาลในฝันที่คุณเห็นด้วยมากที่สุด
            </p>
            <div style="background:#fff1f2; padding:8px 14px; border-radius:12px; font-weight:600; color:#be123c; font-size:13px; border:1px solid #fecdd3; display:inline-block; margin-top:8px;">
                ⏱ ใช้เวลาตอบประมาณ 3 นาที
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="main-card-light" style="text-align:center; background:#be123c; color:white; padding:30px 20px; border:none;">
            <div style="font-size:54px; font-weight:800; color:#ffffff; line-height:1;">15</div>
            <div style="color:#fecdd3; font-size:14px; margin-top:8px;">คำถามประเมินจุดยืน</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 เริ่มทำแบบทดสอบ", use_container_width=True, type="primary"):
            st.session_state.page = "quiz"
            st.session_state.current_q = 0
            st.session_state.answers = {}
            st.rerun()

# =======================================================
# 2. หน้าคำถาม (Quiz Screen: กว้างพอดีตา ไม่หดแคบ)
# =======================================================
elif st.session_state.page == "quiz":
    q_idx = st.session_state.current_q
    q_data = questions_15[q_idx]

    c_back, c_prog = st.columns([1.2, 4.8])
    with c_back:
        if st.button("← หน้าแรก", use_container_width=True, type="secondary"):
            st.session_state.page = "home"
            st.rerun()
    with c_prog:
        st.progress((q_idx + 1) / len(questions_15))
        st.caption(f"ข้อที่ {q_idx + 1} จาก {len(questions_15)} ข้อ ({int((q_idx + 1) / len(questions_15) * 100)}%)")

    # การ์ดคำถามแบบกว้างพอดีตา
    st.markdown(f"""
    <div class="main-card-light">
        <div style="color:#64748b; font-size:14px; font-weight:500;">ข้อที่ {q_idx + 1} จาก {len(questions_15)}</div>
        <h3 style="color:#0f172a; margin: 12px 0 16px 0; font-size:21px; line-height:1.6; font-weight:700;">“{q_data['q']}”</h3>
    """, unsafe_allow_html=True)

    if q_data["type"] == "scale":
        st.markdown("<div style='font-weight:600; color:#334155; margin-bottom:12px; font-size:14.5px;'>เลือกระดับความคิดเห็นของคุณ:</div>", unsafe_allow_html=True)
        cur_ans = st.session_state.answers.get(q_idx, 0.50)
        choice = st.radio(
            "ระดับความคิดเห็น",
            list(scale_scoring.keys()),
            format_func=lambda x: scale_scoring[x],
            index=list(scale_scoring.keys()).index(cur_ans),
            label_visibility="collapsed"
        )
        st.session_state.answers[q_idx] = choice
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # ข้อ 15
        st.markdown("<div style='font-weight:600; color:#be123c; margin-bottom:12px; font-size:15px;'>เลือก 1 รูปแบบที่ตรงกับแนวทางในฝันของคุณมากที่สุด:</div>", unsafe_allow_html=True)
        cur_ans = st.session_state.answers.get(q_idx, 0)
        choice_idx = st.radio(
            "เลือกแนวทางของรัฐบาลในฝัน",
            range(len(q15_options)),
            format_func=lambda i: f"【{q15_options[i]['title']}】\n{q15_options[i]['text']}",
            index=cur_ans,
            label_visibility="collapsed"
        )
        st.session_state.answers[q_idx] = choice_idx
        st.markdown("</div>", unsafe_allow_html=True)

    btn_col1, btn_col2 = st.columns([1, 1.5])
    with btn_col1:
        if q_idx > 0 and st.button("← ย้อนกลับ", use_container_width=True, type="secondary"):
            st.session_state.current_q -= 1
            st.rerun()
    with btn_col2:
        if q_idx < len(questions_15) - 1:
            if st.button("ข้อถัดไป →", type="primary", use_container_width=True):
                st.session_state.current_q += 1
                st.rerun()
        else:
            if st.button("ดูผลการประเมิน ➔", type="primary", use_container_width=True):
                st.session_state.page = "result"
                st.rerun()

# =======================================================
# 3. หน้าผลลัพธ์ (Result Screen: แบ่งสัดส่วน 2 ฝั่งสวยงาม)
# =======================================================
elif st.session_state.page == "result":
    shade_scores = {
        "คอมมิวนิสต์": 0.0,
        "สังคมนิยม": 0.0,
        "เสรีนิยม": 0.0,
        "สายกลาง": 0.0,
        "อนุรักษ์นิยม": 0.0,
        "อิสระนิยม": 0.0,
        "ฟาสซิสต์": 0.0
    }

    for i in range(14):
        q = questions_15[i]
        s_name = q["shade"]
        ans_val = st.session_state.answers.get(i, 0.50)
        shade_scores[s_name] += float(ans_val)

    q15_selected_idx = st.session_state.answers.get(14, 0)
    bonus_shade = q15_options[q15_selected_idx]["shade"]
    shade_scores[bonus_shade] += 2.0

    best_shade = max(shade_scores, key=shade_scores.get)
    profile_data = spectrum_master[best_shade]

    # ส่วนหัวผลลัพธ์
    st.markdown(f"""
        <div class="hero-banner-red">
            <span class="tag-badge-red">POLITICAL SPECTRUM RESULT</span>
            <h1 style="color:#881337; margin:8px 0 12px 0; font-size:32px; font-weight:800;">{profile_data['title']}</h1>
            <p style="color:#475569; font-size:15px; max-width:680px; margin:0 auto; line-height:1.65;">{profile_data['desc']}</p>
        </div>
    """, unsafe_allow_html=True)

    # แบ่ง 2 คอลัมน์: ฝั่งซ้ายสรุปผล ฝั่งขวากราฟเรดาร์
    col_stat, col_chart = st.columns([1.1, 1.3])
    with col_stat:
        st.markdown("""
        <div class="main-card-light" style="height:100%;">
            <h4 style="margin-top:0; color:#0f172a; font-weight:700;">📊 สรุปความสอดคล้องกับอุดมการณ์</h4>
        """, unsafe_allow_html=True)

        for s_name in shade_scores.keys():
            is_best = (s_name == best_shade)
            color = "#e11d48" if is_best else "#64748b"
            weight = "700" if is_best else "500"
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; margin:10px 0; font-size:14.5px;">
                <span style="color:{color}; font-weight:{weight};">{'⭐ ' if is_best else '• '}{s_name}</span>
                <span style="color:{color}; font-weight:{weight};">{'สอดคล้องสูงสุด' if is_best else 'ทั่วไป'}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="margin-top:16px; padding-top:12px; border-top:1px solid #f1f5f9; font-size:13.5px; color:#475569;">
                <b>รูปแบบที่เลือกในข้อตัดสิน:</b> <span style="color:#be123c; font-weight:600;">{bonus_shade}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_chart:
        st.markdown("""
        <div class="main-card-light" style="display:flex; flex-direction:column; align-items:center;">
            <div style="font-weight:700; color:#0f172a; font-size:15px; margin-bottom:8px;">📊 แผนภาพเปรียบเทียบระดับความสอดคล้อง</div>
        """, unsafe_allow_html=True)
        
        radar_labels_en = [
            'Communism', 'Socialism', 'Liberalism', 'Centrism',
            'Conservatism', 'Libertarianism', 'Fascism'
        ]
        radar_values = list(shade_scores.values())
        radar_labels_plot = radar_labels_en + [radar_labels_en[0]]
        radar_values_plot = radar_values + [radar_values[0]]

        N = len(radar_labels_en)
        angles = [n / float(N) * 2 * math.pi for n in range(N)]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(4.0, 3.6), subplot_kw=dict(polar=True), facecolor='#ffffff')
        ax.set_facecolor('#ffffff')
        ax.set_theta_offset(math.pi / 2)
        ax.set_theta_direction(-1)

        plt.xticks(angles[:-1], radar_labels_plot[:-1], size=8, color='#334155', fontweight='bold')
        ax.set_rlabel_position(0)
        plt.yticks([1, 2, 3, 4, 5, 6], ["", "", "", "", "", ""], color="#94a3b8")
        plt.ylim(0, 6)

        ax.plot(angles, radar_values_plot, linewidth=2.2, color='#e11d48')
        ax.fill(angles, radar_values_plot, color='#fb7185', alpha=0.35)

        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

    # ----------------- การ์ดบุคคลสำคัญ 3 ท่าน -----------------
    st.markdown("### 🏛 นักคิดและบุคคลสำคัญที่สอดคล้องกับคุณ")
    st.caption(f"ตัวแทนทางความคิดทั้งด้านนักคิด ปรัชญา และผู้นำในกลุ่มแนวคิด: {best_shade}")

    p1 = profile_data["thinker"]
    p2 = profile_data["leader"]
    p3 = profile_data["overall"]

    three_cards = [
        {"badge_title": "💡 หัวข้อที่ 1: นักคิดสำคัญ (Thinker)", "match": "96% Alignment", "data": p1},
        {"badge_title": "🏛️ หัวข้อที่ 2: ผู้นำ/นักการเมือง (Leader)", "match": "94% Alignment", "data": p2},
        {"badge_title": "🧭 ภาพรวม: ตัวแทนอุดมการณ์", "match": "95% Alignment", "data": p3}
    ]

    cols = st.columns(3)
    for idx, card in enumerate(three_cards):
        with cols[idx]:
            p = card["data"]
            img_b64 = get_image_base64(p["name"])
            
            if img_b64:
                img_tag = f'<div class="person-img-wrapper"><img src="{img_b64}"></div>'
            else:
                img_tag = f'<div class="person-img-wrapper" style="background:#fff1f2; border:1px dashed #fecdd3; color:#be123c; font-size:13px;">📷 รูป: {p["name"]}</div>'
            
            card_html = f"""
            <div class="person-card-complete">
                <div>
                    <div style="font-size:11px; font-weight:700; color:#e11d48; margin-bottom:4px;">{card['badge_title']}</div>
                    <span class="stat-badge-red">{card['match']}</span>
                    <h4 style="margin:6px 0 2px 0; color:#0f172a; font-size:16px; font-weight:700;">{p['name']}</h4>
                    <div style="font-size:12px; color:#64748b; line-height:1.4;">{p['role']}</div>
                </div>
                {img_tag}
                <div class="quote-box-red">{p['quote']}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

    st.write("")
    if st.button("🔄 ทำแบบประเมินใหม่อีกครั้ง", use_container_width=True, type="secondary"):
        st.session_state.page = "home"
        st.session_state.answers = {}
        st.session_state.current_q = 0
        st.rerun()
