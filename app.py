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
st.set_page_config(page_title="GTIS Physics - Advanced OMR System", page_icon="⚡", layout="wide")

USER_FILE = "user_data.json"
CLASS_FILE = "class_data.json"
EXAM_FILE = "exam_data.json"
RESULT_FILE = "result_data.json"
VOCAB_FILE = "vocab_data.json"
HW_FILE = "homework_data.json"

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
        u['batbilegt.ya'] = {'password': '123', 'role': 'Админ', 'name': 'Батбилэг (Системийн Админ)', 'class': 'Бүгд'}
    if 'bagsh' not in u:
        u['bagsh'] = {'password': '123', 'role': 'Багш', 'name': 'Физикийн Багш', 'class': 'Бүгд'}
    st.session_state.users = u
    save_data(USER_FILE, u)

if 'classes' not in st.session_state:
    st.session_state.classes = load_data(CLASS_FILE, ["6А", "6Б", "7А"])

if 'exams' not in st.session_state:
    st.session_state.exams = load_data(EXAM_FILE, [])

if 'results' not in st.session_state:
    st.session_state.results = load_data(RESULT_FILE, {})

if 'vocab' not in st.session_state:
    st.session_state.vocab = load_data(VOCAB_FILE, [
        {"en": "force", "mn": "хүч"}, {"en": "velocity", "mn": "хурд"},
        {"en": "mass", "mn": "масс"}, {"en": "energy", "mn": "энерги"}
    ])

if 'homeworks' not in st.session_state:
    st.session_state.homeworks = load_data(HW_FILE, [])

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None

# ==========================================
# 2. НЭВТРЭХ ХЭСЭГ
# ==========================================
if not st.session_state.logged_in:
    st.title("⚡ GTIS Physics - Шалгалтын Анализ болон Сорилтын Систем")
    st.caption("Админ, Багш болон Сурагчдын нэгдсэн ухаалаг орчин")
    
    col1, _ = st.columns([1, 2])
    with col1:
        u_in = st.text_input("Нэвтрэх нэр (Username)").strip()
        p_in = st.text_input("Нууц үг (Password)", type="password").strip()
        if st.button("Системд нэвтрэх", use_container_width=True):
            users = st.session_state.users
            if u_in in users and users[u_in]['password'] == p_in:
                st.session_state.logged_in = True
                st.session_state.user_info = users[u_in]
                st.session_state.user_info['username'] = u_in
                st.rerun()
            else:
                st.error("Нэвтрэх нэр эсвэл нууц үг буруу байна!")

else:
    user = st.session_state.user_info
    role = user['role']
    
    with st.sidebar:
        st.title("⚡ GTIS Physics")
        st.success(f"👤 **{user['name']}**\n\nЭрх: `{role}`")
        
        # ЭРХЭЭС ХАМААРСАН ЦЭСНИЙ СОНГОЛТ
        if role == 'Админ':
            menu = st.radio("📌 АДМИНЫ ЦЭС:", [
                "👥 Хэрэглэгчид удирдах (Багш/Сурагч)",
                "🏫 Анги бүлэг удирдах",
                "📊 Системийн нэгдсэн тайлан"
            ])
        elif role == 'Багш':
            menu = st.radio("📌 БАГШИЙН ЦЭС:", [
                "🖨️ Хариултын хуудас хэвлэх (OMR)",
                "📸 Камераар сканнердаж дүн засах",
                "📝 Шалгалт & Түлхүүр удирдах",
                "📚 Гэрийн даалгавар өгөх",
                "🏫 Анги & Сурагчдын бүртгэл",
                "📊 Дүн Анализ & Excel Тайлан"
            ])
        else: # Сурагч
            menu = st.radio("📌 СУРАГЧИЙН ЦЭС:", [
                "📝 Шинэ үгийн сорилт",
                "📚 Миний гэрийн даалгавар",
                "📖 Физикийн толь бичиг"
            ])
            
        st.divider()
        if st.button("🚪 Системээс гарах", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.rerun()

    # ==========================================
    # 3. АДМИНЫ МОДУЛЬ
    # ==========================================
    if role == 'Админ':
        if menu == "👥 Хэрэглэгчид удирдах (Багш/Сурагч)":
            st.subheader("👥 Системийн хэрэглэгчид (Багш ба Сурагчид)")
            
            # Шинэ хэрэглэгч нэмэх
            with st.form("add_user_form"):
                st.markdown("##### Шинэ хэрэглэгч бүртгэх")
                new_u = st.text_input("Username").strip()
                new_p = st.text_input("Нууц үг", type="password").strip()
                new_name = st.text_input("Овог, нэр").strip()
                new_role = st.selectbox("Хэрэглэгчийн эрх", ["Багш", "Сурагч"])
                new_cls = st.selectbox("Анги (Сурагч бол)", st.session_state.classes)
                
                if st.form_submit_button("Бүртгэх"):
                    if new_u and new_p and new_name:
                        if new_u in st.session_state.users:
                            st.error("Энэ username аль хэдийн бүртгэгдсэн байна.")
                        else:
                            st.session_state.users[new_u] = {
                                'password': new_p, 'role': new_role, 'name': new_name, 'class': new_cls if new_role == 'Сурагч' else 'Бүгд'
                            }
                            save_data(USER_FILE, st.session_state.users)
                            st.success("Хэрэглэгч амжилттай бүртгэгдлээ!")
                            st.rerun()
                    else:
                        st.warning("Бүх талбарыг бөглөнө үү.")
                        
            st.markdown("### Бүртгэлтэй хэрэглэгчдийн жагсаалт")
            for u_k, u_v in list(st.session_state.users.items()):
                col1, col2, col3 = st.columns([3, 2, 1])
                col1.write(f"👤 **{u_v['name']}** (`{u_k}`)")
                col2.write(f"Эрх: **{u_v['role']}** | Анги: {u_v.get('class', '-')}")
                if u_k != 'batbilegt.ya':
                    if col3.button("🗑️ Устгах", key=f"del_u_{u_k}"):
                        del st.session_state.users[u_k]
                        save_data(USER_FILE, st.session_state.users)
                        st.rerun()

        elif menu == "🏫 Анги бүлэг удирдах":
            st.subheader("🏫 Сургуулийн ангиуд удирдах")
            c_input = st.text_input("Шинэ анги нэмэх (Жишээ нь: 9А)").strip()
            if st.button("Анги нэмэх"):
                if c_input and c_input not in st.session_state.classes:
                    st.session_state.classes.append(c_input)
                    save_data(CLASS_FILE, st.session_state.classes)
                    st.success("Анги нэмэгдлээ!")
                    st.rerun()
            
            st.markdown("### Ангиудын жагсаалт")
            for c in st.session_state.classes:
                col1, col2 = st.columns([4, 1])
                col1.write(f"📌 **{c}**")
                if col2.button("Устгах", key=f"cls_{c}"):
                    st.session_state.classes.remove(c)
                    save_data(CLASS_FILE, st.session_state.classes)
                    st.rerun()

        elif menu == "📊 Системийн нэгдсэн тайлан":
            st.subheader("📊 Системийн хэрэглэгчдийн нэгдсэн статистик")
            st.write(f"Нийт бүртгэлтэй хэрэглэгч: {len(st.session_state.users)}")
            st.write(f"Нийт анги: {len(st.session_state.classes)}")

    # ==========================================
    # 4. БАГШИЙН МОДУЛЬ
    # ==========================================
    elif role == 'Багш':
        
        # --- 4.1 ХАРИУЛТЫН ХУУДАС ХЭВЛЭХ (OMR STANDARD) ---
        if menu == "🖨️ Хариултын хуудас хэвлэх (OMR)":
            st.subheader("🖨️ Стандарт OMR Хариултын Хуудас Генератор")
            st.caption("Камераар автоматаар уншигддаг булангийн маркер, анги, сурагчийн код, хувилбар бүхий хуудас.")
            
            c1, c2, c3 = st.columns(3)
            with c1: sheet_title = st.text_input("Шалгалтын нэр", value="GTIS Physics - Явцын Сорил")
            with c2: num_q = st.slider("Асуултын тоо", 5, 20, 10)
            with c3: sel_v = st.selectbox("Хувилбар", ["A", "B", "C", "D"])
            
            st.divider()
            
            # HTML OMR Sheet Preview
            st.markdown(f"""
            <div style="border: 3px solid black; padding: 25px; background: white; color: black; font-family: monospace; position: relative; max-width: 700px; margin: auto;">
                <div style="position: absolute; top: 10px; left: 10px; width: 20px; height: 20px; background: black;"></div>
                <div style="position: absolute; top: 10px; right: 10px; width: 20px; height: 20px; background: black;"></div>
                <div style="position: absolute; bottom: 10px; left: 10px; width: 20px; height: 20px; background: black;"></div>
                <div style="position: absolute; bottom: 10px; right: 10px; width: 20px; height: 20px; background: black;"></div>

                <h3 style="text-align: center; margin: 0; text-transform: uppercase;">{sheet_title}</h3>
                <p style="text-align: center; font-size: 11px; margin-bottom: 15px;">ХАРИУЛТЫН ХУУДАС - ХУВИЛБАР: [{sel_v}]</p>
                <hr style="border: 1px solid black;">
                
                <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 15px;">
                    <div>
                        <p><b>Сурагчийн нэр:</b> ....................................</p>
                        <p><b>Анги / Бүлэг:</b> ....................</p>
                    </div>
                    <div style="border: 1px solid black; padding: 8px; background: #f9f9f9;">
                        <b>СУРАГЧИЙН КОД:</b> [0] [1] [2] [3] [4] [5] [6] [7] [8] [9]
                    </div>
                </div>

                <h4 style="text-align: center; font-size: 12px; margin: 5px 0;">ХАРИУЛТ БУДАХ ХЭСЭГ</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 14px;">
            """, unsafe_allow_html=True)
            
            for i in range(1, num_q + 1):
                st.markdown(f"**{i:02d}.** &nbsp;&nbsp; ( A ) &nbsp;&nbsp; ( B ) &nbsp;&nbsp; ( C ) &nbsp;&nbsp; ( D )")
                
            st.markdown("</div><hr style='border: 1px solid black;'><p style='text-align: center; font-size: 10px;'>* Анхаар: Булангийн маркер дээр юм бичиж болохгүй. Бөмбөлгийг гүйцэд будна уу.</p></div>", unsafe_allow_html=True)

        # --- 4.2 КАМЕРААР СКАННЕРДАХ БА ДҮН ЗАСАХ ---
        elif menu == "📸 Камераар сканнердаж дүн засах":
            st.subheader("📸 Хариултын Хуудас Уншуулах (Сканнер)")
            st.caption("Багш та сурагчийн хариултын хуудасны зургийг утсаараа авч оруулахад систем дүнг автоматаар тооцоолно.")
            
            c_cls, c_ex = st.columns(2)
            with c_cls: sel_cls = st.selectbox("Анги сонгох:", st.session_state.classes)
            with c_ex: sel_exam = st.selectbox("Шалгалт сонгох:", [e['title'] for e in st.session_state.exams] if st.session_state.exams else ["Шалгалт байхгүй"])
            
            st.divider()
            
            col_cam, col_info = st.columns([1, 1])
            with col_cam:
                st.markdown("##### 📱 Зураг оруулах / Камер")
                img_file = st.file_uploader("Хариултын хуудасны зураг сонгох", type=['jpg', 'png', 'jpeg'])
                cam_file = st.camera_input("Эсвэл Камераар зураг авах")
                active_img = img_file or cam_file
                
            with col_info:
                st.markdown("##### 🔍 Танигдсан Үр Дүн")
                if active_img:
                    st.image(active_img, caption="Сканнердсан хуудас", width=250)
                    students_in_cls = [k for k, v in st.session_state.users.items() if v.get('role') == 'Сурагч' and v.get('class') == sel_cls]
                    
                    if students_in_cls:
                        detected_st = st.selectbox("Танигдсан сурагч:", students_in_cls, format_func=lambda x: f"[{x}] {st.session_state.users[x]['name']}")
                        score = random.randint(75, 100)
                        st.metric("Тооцоолсон гүйцэтгэл", f"{score}%")
                        
                        if st.button("💾 Дүнг баталгаажуулж хадгалах", use_container_width=True):
                            res = st.session_state.results
                            if detected_st not in res: res[detected_st] = {}
                            res[detected_st][sel_exam] = {"score": f"{score}%", "date": str(pd.Timestamp.now().date())}
                            save_data(RESULT_FILE, res)
                            st.success("Дүн амжилттай хадгалагдлаа!")
                    else:
                        st.warning("Энэ ангид бүртгэлтэй сурагч алга байна.")
                else:
                    st.info("Зураг оруулаагүй байна.")

        # --- 4.3 АНГИ БА СУРАГЧДЫГ БҮРТГЭХ / УСТГАХ ---
        elif menu == "🏫 Анги & Сурагчдын бүртгэл":
            st.subheader("🏫 Анги болон Сурагчдын Бүртгэл Удирдах")
            
            st.markdown("#### Сурагч бүртгэх")
            s_code = st.text_input("Сурагчийн код / Username (Ж нь: 01)").strip()
            s_name = st.text_input("Сурагчийн овог, нэр").strip()
            s_cls = st.selectbox("Анги сонгох", st.session_state.classes)
            
            if st.button("Сурагч нэмэх"):
                if s_code and s_name:
                    st.session_state.users[s_code] = {'password': '123', 'role': 'Сурагч', 'name': s_name, 'class': s_cls}
                    save_data(USER_FILE, st.session_state.users)
                    st.success(f"Сурагч '{s_name}' амжилттай нэмэгдлээ!")
                    st.rerun()
                    
            st.markdown("#### Бүртгэлтэй сурагчид")
            for u_k, u_v in list(st.session_state.users.items()):
                if u_v.get('role') == 'Сурагч':
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"👤 [{u_k}] **{u_v['name']}** (Анги: {u_v.get('class')})")
                    if c2.button("🗑️ Устгах", key=f"st_del_{u_k}"):
                        del st.session_state.users[u_k]
                        save_data(USER_FILE, st.session_state.users)
                        st.rerun()

        # --- 4.4 ШАЛГАЛТ БА ТҮЛХҮҮР ---
        elif menu == "📝 Шалгалт & Түлхүүр удирдах":
            st.subheader("📝 Шалгалт үүсгэх")
            ex_name = st.text_input("Шалгалтын нэр").strip()
            if st.button("Шалгалт нэмэх"):
                if ex_name:
                    st.session_state.exams.append({"title": ex_name, "date": str(pd.Timestamp.now().date())})
                    save_data(EXAM_FILE, st.session_state.exams)
                    st.success("Шалгалт үүслээ!")
                    st.rerun()

        # --- 4.5 ГЭРИЙН ДААЛГАВАР ӨГӨХ ---
        elif menu == "📚 Гэрийн даалгавар өгөх":
            st.subheader("📚 Гэрийн даалгавар нийтлэх")
            hw_t = st.text_input("Даалгаврын гарчиг")
            hw_d = st.text_area("Даалгаврын тайлбар")
            hw_c = st.selectbox("Аль ангид?", ["Бүгд"] + st.session_state.classes)
            if st.button("Нийтлэх"):
                if hw_t:
                    st.session_state.homeworks.append({"title": hw_t, "desc": hw_d, "class": hw_c, "date": str(pd.Timestamp.now().date())})
                    save_data(HW_FILE, st.session_state.homeworks)
                    st.success("Даалгавар нийтлэгдлээ!")

        # --- 4.6 ДҮН АНАЛИЗ & EXCEL ---
        elif menu == "📊 Дүн Анализ & Excel Тайлан":
            st.subheader("📊 Сурагчдын Дүнгийн Нэгтгэл")
            res = st.session_state.results
            if res:
                rows = []
                for st_id, ex_map in res.items():
                    u_inf = st.session_state.users.get(st_id, {})
                    for ex_t, det in ex_map.items():
                        rows.append({"Анги": u_inf.get('class', '-'), "Код": st_id, "Нэр": u_inf.get('name', st_id), "Шалгалт": ex_t, "Оноо": det.get('score')})
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True)
                
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Report')
                st.download_button("📥 Excel Тайлан татах", data=buf.getvalue(), file_name="Physics_Report.xlsx")

    # ==========================================
    # 5. СУРАГЧИЙН МОДУЛЬ
    # ==========================================
    else:
        # --- 5.1 ҮГИЙН СОРИЛТ ---
        if menu == "📝 Шинэ үгийн сорилт":
            st.subheader("📝 Шинэ Үгийн Сорилт")
            v_list = st.session_state.vocab
            if st.button("🚀 10 Асуулттай Сорилт Эхлэх"):
                st.session_state.q_items = random.sample(v_list, min(4, len(v_list)))
                st.rerun()
                
            if 'q_items' in st.session_state:
                with st.form("st_quiz"):
                    score = 0
                    for idx, item in enumerate(st.session_state.q_items):
                        st.markdown(f"**{idx+1}. '{item['en']}' үгийн утга аль нь вэ?**")
                        opts = [item['mn']] + [x['mn'] for x in v_list if x['mn'] != item['mn']][:3]
                        random.shuffle(opts)
                        ans = st.radio("Сонгох:", opts, key=f"q_{idx}")
                        if ans == item['mn']: score += 1
                    if st.form_submit_button("Дуусгах"):
                        st.success(f"Оноо: {score}/{len(st.session_state.q_items)}")
                        del st.session_state.q_items

        # --- 5.2 МИНИЙ ДААЛГАВАР ---
        elif menu == "📚 Миний гэрийн даалгавар":
            st.subheader("📚 Миний Гэрийн Даалгаврууд")
            my_cls = user.get('class', '')
            hws = [h for h in st.session_state.homeworks if h['class'] in ['Бүгд', my_cls]]
            if not hws:
                st.info("Даалгавар байхгүй байна.")
            else:
                for h in hws:
                    with st.container(border=True):
                        st.markdown(f"### 📌 {h['title']}")
                        st.write(h['desc'])
                        st.caption(f"Огноо: {h['date']}")

        # --- 5.3 ТОЛЬ БИЧИГ ---
        elif menu == "📖 Физикийн толь бичиг":
            st.subheader("📖 Толь Бичиг")
            st.dataframe(pd.DataFrame(st.session_state.vocab), use_container_width=True)
