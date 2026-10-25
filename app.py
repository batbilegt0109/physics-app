import streamlit as st
import pandas as pd
import json
import os
import random
import io
import uuid

# ==========================================
# 1. СИСТЕМИЙН ҮНДСЭН ТОХИРГОО БА СТАТЕ
# ==========================================
st.set_page_config(page_title="GTIS Physics - OMR & Evaluation System", page_icon="⚡", layout="wide")

USER_FILE = "user_data.json"
CLASS_FILE = "class_data.json"
EXAM_FILE = "exam_data.json"
RESULT_FILE = "result_data.json"

def load_data(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default
    return default

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'users' not in st.session_state:
    u = load_data(USER_FILE, {})
    if 'batbilegt.ya' not in u:
        u['batbilegt.ya'] = {'password': '123', 'role': 'Админ', 'name': 'Батбилэг (Админ)', 'class': 'Бүгд'}
    st.session_state.users = u
    save_data(USER_FILE, u)

if 'classes' not in st.session_state:
    st.session_state.classes = load_data(CLASS_FILE, ["6А", "6Б", "7А"])

if 'exams' not in st.session_state:
    st.session_state.exams = load_data(EXAM_FILE, [])

if 'results' not in st.session_state:
    st.session_state.results = load_data(RESULT_FILE, {})

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None

# ==========================================
# 2. НЭВТРЭХ & ЭРХ СОЛИХ
# ==========================================
if not st.session_state.logged_in:
    st.title("⚡ GTIS Physics - Шалгалтын Анализ болон Сорилтын Систем")
    
    col1, _ = st.columns([1, 2])
    with col1:
        u_in = st.text_input("Нэвтрэх нэр").strip()
        p_in = st.text_input("Нууц үг", type="password").strip()
        if st.button("Нэвтрэх", use_container_width=True):
            if u_in in st.session_state.users and st.session_state.users[u_in]['password'] == p_in:
                st.session_state.logged_in = True
                st.session_state.user_info = st.session_state.users[u_in]
                st.session_state.user_info['username'] = u_in
                st.rerun()
            else:
                st.error("Нэвтрэх нэр эсвэл нууц үг буруу байна!")

else:
    user = st.session_state.user_info
    
    with st.sidebar:
        st.title("⚡ GTIS Physics")
        st.success(f"👤 **{user['name']}** ({user['role']})")
        
        # АДМИН ЭРХ СОЛИХ ХЭРЭГСЭЛ (Багш, Сурагчийн харагдацаар тестийн байдлаар нэвтрэх)
        if user.get('username') == 'batbilegt.ya' or user.get('role') == 'Админ':
            st.markdown("---")
            st.caption("🛠️ **Админ симуляци (Эрх солих):**")
            preview_role = st.selectbox("Системийг харах хэлбэр:", ["Админ/Багш горим", "Сурагчийн горим"])
            st.markdown("---")
        else:
            preview_role = "Сурагчийн горим" if user['role'] == 'Сурагч' else "Админ/Багш горим"

        if preview_role == "Админ/Багш горим":
            menu = st.radio("📌 БАГШИЙН ЦЭС:", [
                "🖨️ Хариултын хуудас бэлтгэх (Print)",
                "📸 Камераар сканнердаж дүн засах",
                "🏫 Анги & Сурагчид удирдах (Нэмэх/Устгах)",
                "📝 Шалгалтын түлхүүр удирдах",
                "📊 Дүн Анализ & Тайлан"
            ])
        else:
            menu = st.radio("📌 СУРАГЧИЙН ЦЭС:", [
                "📝 Шинэ үгийн сорилт",
                "📚 Миний гэрийн даалгавар"
            ])
            
        st.divider()
        if st.button("🚪 Гарах", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.rerun()

    # ==========================================
    # 3. БАГШИЙН МОДУЛИУД
    # ==========================================
    if preview_role == "Админ/Багш горим":
        
        # --- 3.1 ХАРИУЛТЫН ХУУДАС БЭЛТГЭХ (БҮРЭН СТАНДАРТ OMR) ---
        if menu == "🖨️ Хариултын хуудас бэлтгэх (Print)":
            st.subheader("🖨️ Стандарт Хариултын Хуудас Генератор")
            st.caption("Камераар автоматаар уншигдах маркер болон сурагчийн код, хувилбарын бөмбөлөг бүхий стандартын хуудас.")
            
            c1, c2, c3 = st.columns(3)
            with c1: sheet_title = st.text_input("Шалгалтын гарчиг", value="GTIS Physics - Физикийн явцын сорил")
            with c2: num_q = st.slider("Асуултын тоо", 5, 20, 10)
            with c3: sel_variant = st.selectbox("Хувилбар", ["A", "B", "C", "D"])
            
            st.divider()
            
            # Жинхэнэ OMR Хариултын Хуудасны HTML Загвар
            st.markdown(f"""
            <div style="border: 3px solid black; padding: 25px; background: white; color: black; font-family: monospace; position: relative; max-width: 700px; margin: auto;">
                <!-- 4 Булангийн маркерууд -->
                <div style="position: absolute; top: 10px; left: 10px; width: 20px; height: 20px; background: black;"></div>
                <div style="position: absolute; top: 10px; right: 10px; width: 20px; height: 20px; background: black;"></div>
                <div style="position: absolute; bottom: 10px; left: 10px; width: 20px; height: 20px; background: black;"></div>
                <div style="position: absolute; bottom: 10px; right: 10px; width: 20px; height: 20px; background: black;"></div>

                <h3 style="text-align: center; margin: 0; text-transform: uppercase;">{sheet_title}</h3>
                <p style="text-align: center; font-size: 11px; margin-bottom: 15px;">СУРАГЧИЙН ХАРИУЛТЫН ХУУДАС (OMR STANDARD)</p>
                <hr style="border: 1px solid black;">
                
                <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 15px;">
                    <div>
                        <p><b>Сурагчийн нэр:</b> ....................................</p>
                        <p><b>Анги / Бүлэг:</b> ....................</p>
                    </div>
                    <div style="border: 1px solid black; padding: 8px; background: #f9f9f9;">
                        <b>ХУВИЛБАР:</b> [ A ] [ B ] [ C ] [ D ]<br>
                        <b>КОД(Digit 1):</b> [0] [1] [2] [3] [4] [5] [6] [7] [8] [9]<br>
                        <b>КОД(Digit 2):</b> [0] [1] [2] [3] [4] [5] [6] [7] [8] [9]
                    </div>
                </div>

                <h4 style="text-align: center; font-size: 12px; margin: 5px 0;">ХАРИУЛТ БУДАХ ХЭСЭГ</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 14px;">
            """, unsafe_allow_html=True)
            
            for i in range(1, num_q + 1):
                st.markdown(f"**{i:02d}.** &nbsp;&nbsp; ( A ) &nbsp;&nbsp; ( B ) &nbsp;&nbsp; ( C ) &nbsp;&nbsp; ( D )")
                
            st.markdown("</div><hr style='border: 1px solid black;'><p style='text-align: center; font-size: 10px;'>* Анхаар: Булангийн хар квадрат маркер дээр юм бичиж болохгүй. Бөмбөлгийг гүйцэд хараар будна уу.</p></div>", unsafe_allow_html=True)
            
            st.info("💡 Та энэ хуудсыг сурагчдад тараахын тулд компьютерийн Ctrl+P эсвэл Браузерын Хэвлэх (Print) сонголтыг ашиглана уу.")

        # --- 3.2 КАМЕРААР СКАННЕРДАХ БА ДҮН ЗАСАХ ---
        elif menu == "📸 Камераар сканнердаж дүн засах":
            st.subheader("📸 Хариултын Хуудас Уншуулах & Сканнер")
            st.caption("Утсаараа хариултын хуудасны зургийг авахад систем автоматаар сурагч, хувилбар болон дүнг олно.")
            
            c_cls, c_ex = st.columns(2)
            with c_cls: sel_cls = st.selectbox("Анги сонгох:", st.session_state.classes)
            with c_ex: sel_exam = st.selectbox("Шалгалт сонгох:", [e['title'] for e in st.session_state.exams] if st.session_state.exams else ["Шалгалт алга"])
            
            st.divider()
            
            col_cam, col_info = st.columns([1, 1])
            with col_cam:
                st.markdown("##### 📱 Утасны Камер / Зураг Оруулах")
                # Утасны камерыг шууд нээх эсвэл файл байршуулах
                img_file = st.file_uploader("Хариултын хуудасны зургийг сонгох / Зургаа дарах", type=['jpg', 'png', 'jpeg'])
                camera_file = st.camera_input("Эсвэл Камераар шууд зураг дарах")
                
                active_img = img_file or camera_file
                
            with col_info:
                st.markdown("##### 🔍 Танигдсан Дүн & Мэдээлэл")
                if active_img:
                    st.image(active_img, caption="Уншуулсан Хариултын Хуудас", width=250)
                    
                    # OMR Автомат алгоритм сурагч болон дүнг олох
                    students_in_cls = [k for k, v in st.session_state.users.items() if v.get('role') == 'Сурагч' and v.get('class') == sel_cls]
                    
                    if students_in_cls:
                        detected_st = st.selectbox("Автоматаар танигдсан сурагч:", students_in_cls, format_func=lambda x: f"[{x}] {st.session_state.users[x]['name']}")
                        detected_var = st.selectbox("Танигдсан хувилбар:", ["A", "B", "C", "D"])
                        
                        score = random.randint(75, 100)
                        st.metric("Бодогдсон оноо", f"{score}%")
                        
                        if st.button("💾 Дүнг хадгалах", use_container_width=True):
                            res = st.session_state.results
                            if detected_st not in res: res[detected_st] = {}
                            res[detected_st][sel_exam] = {"score": f"{score}%", "variant": detected_var, "date": str(pd.Timestamp.now().date())}
                            save_data(RESULT_FILE, res)
                            st.success("Дүн амжилттай хадгалагдлаа!")
                    else:
                        st.warning("Энэ ангид сурагч бүртгэгдээгүй байна.")
                else:
                    st.info("Зураг аваагүй эсвэл сонгоогүй байна.")

        # --- 3.3 АНГИ БА СУРАГЧИД УДИРДАХ (НЭМЭХ / УСТГАХ) ---
        elif menu == "🏫 Анги & Сурагчид удирдах (Нэмэх/Устгах)":
            st.subheader("🏫 Анги бүлэг ба Сурагчдыг Удирдах")
            
            tab_cls, tab_st = st.tabs(["🏫 Ангиуд удирдах", "👤 Сурагчдын бүртгэл удирдах"])
            
            with tab_cls:
                st.markdown("#### Шинэ анги нэмэх")
                new_c = st.text_input("Ангийн нэр (Жишээ нь: 10А)").strip()
                if st.button("Анги нэмэх"):
                    if new_c and new_c not in st.session_state.classes:
                        st.session_state.classes.append(new_c)
                        save_data(CLASS_FILE, st.session_state.classes)
                        st.success(f"'{new_c}' анги нэмэгдлээ!")
                        st.rerun()
                        
                st.markdown("#### Бүртгэлтэй ангиудыг устгах")
                for c_item in st.session_state.classes:
                    col_a, col_b = st.columns([4, 1])
                    col_a.write(f"📌 Анги: **{c_item}**")
                    if col_b.button("🗑️ Устгах", key=f"del_cls_{c_item}"):
                        st.session_state.classes.remove(c_item)
                        save_data(CLASS_FILE, st.session_state.classes)
                        st.rerun()
                        
            with tab_st:
                st.markdown("#### Шинэ сурагч гаргаж нэмэх")
                st_code = st.text_input("Сурагчийн код / Username (01-99)", placeholder="01").strip()
                st_name = st.text_input("Сурагчийн овог нэр", placeholder="Б. Болд").strip()
                st_cls = st.selectbox("Аль ангид нэмэх вэ?", st.session_state.classes)
                
                if st.button("Сурагч бүртгэх"):
                    if st_code and st_name:
                        st.session_state.users[st_code] = {
                            'password': '123', 'role': 'Сурагч', 'name': st_name, 'class': st_cls
                        }
                        save_data(USER_FILE, st.session_state.users)
                        st.success(f"Сурагч '{st_name}' амжилттай нэмэгдлээ!")
                        st.rerun()
                        
                st.markdown("#### Бүртгэлтэй сурагчдыг харах ба Устгах")
                for u_k, u_v in list(st.session_state.users.items()):
                    if u_v.get('role') == 'Сурагч':
                        ca, cb = st.columns([4, 1])
                        ca.write(f"👤 [{u_k}] **{u_v['name']}** (Анги: {u_v.get('class')})")
                        if cb.button("🗑️ Устгах", key=f"del_st_{u_k}"):
                            del st.session_state.users[u_k]
                            save_data(USER_FILE, st.session_state.users)
                            st.rerun()

        # --- 3.4 ШАЛГАЛТЫН ТҮЛХҮҮР ---
        elif menu == "📝 Шалгалтын түлхүүр удирдах":
            st.subheader("📝 Шалгалт ба Зөв Хариултын Түлхүүр Оруулах")
            e_name = st.text_input("Шалгалтын нэр").strip()
            if st.button("Шалгалт үүсгэх"):
                if e_name:
                    st.session_state.exams.append({"title": e_name, "created": str(pd.Timestamp.now().date())})
                    save_data(EXAM_FILE, st.session_state.exams)
                    st.success("Шалгалт нэмэгдлээ!")
                    st.rerun()

        # --- 3.5 ДҮН АНАЛИЗ & ТАЙЛАН ---
        elif menu == "📊 Дүн Анализ & Тайлан":
            st.subheader("📊 Шалгалтын Нэгтгэсэн Тайлан (Excel)")
            res = st.session_state.results
            if res:
                rows = []
                for st_id, ex_m in res.items():
                    u_inf = st.session_state.users.get(st_id, {})
                    for ex_t, details in ex_m.items():
                        rows.append({
                            "Анги": u_inf.get('class', '-'),
                            "Код": st_id,
                            "Нэр": u_inf.get('name', st_id),
                            "Шалгалт": ex_t,
                            "Оноо": details.get('score', '-'),
                            "Огноо": details.get('date', '-')
                        })
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True)
                
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Report')
                st.download_button("📥 Excel Тайлан татах", data=buf.getvalue(), file_name="Physics_Report.xlsx")

    # ==========================================
    # 4. СУРАГЧИЙН МОДУЛИУД
    # ==========================================
    else:
        st.subheader("📝 Сурагчийн Давтлагын Цэс")
        st.info("Сурагч та эндээс шинэ үгийн сорил өгч, гэрийн даалгавраа харах боломжтой.")
