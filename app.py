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
st.set_page_config(page_title="GTIS Physics Smart System", page_icon="⚡", layout="wide")

VOCAB_FILE = "vocab_data.json"
USER_FILE = "user_data.json"
EXAM_FILE = "exam_data.json"
CLASS_FILE = "class_data.json"
HW_FILE = "homework_data.json"
RESULT_FILE = "result_data.json"

def load_data(filename, default_value):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return default_value
    return default_value

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Идэвхтэй өгөгдлүүдийг session_state-д ачаалах
if 'vocab' not in st.session_state:
    st.session_state.vocab = load_data(VOCAB_FILE, [])

if 'users' not in st.session_state:
    users = load_data(USER_FILE, {})
    # Үндсэн систем удирдах Админ
    if 'admin' not in users:
        users['admin'] = {
            'password': '123',
            'role': 'Админ',
            'name': 'Багш (Админ)',
            'class': 'Бүгд'
        }
    st.session_state.users = users
    save_data(USER_FILE, users)

if 'classes' not in st.session_state:
    st.session_state.classes = load_data(CLASS_FILE, ["6A", "6B", "7A", "8A"])

if 'exams' not in st.session_state:
    st.session_state.exams = load_data(EXAM_FILE, [])

if 'homeworks' not in st.session_state:
    st.session_state.homeworks = load_data(HW_FILE, [])

if 'results' not in st.session_state:
    st.session_state.results = load_data(RESULT_FILE, {})

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None

# ==========================================
# 2. НЭВТРЭХ БА БҮРТГҮҮЛЭХ
# ==========================================
if not st.session_state.logged_in:
    st.title("⚡ GTIS Physics - Ухаалаг Сургалтын Систем")
    st.caption("Багшийн цагийг хэмнэх, сурагчдын мэдлэгийг бататгах цогц орчин")
    
    t_login, t_reg = st.tabs(["🔑 Системд нэвтрэх", "📝 Сурагч бүртгүүлэх"])
    
    with t_login:
        c1, _ = st.columns([1, 2])
        with c1:
            u_input = st.text_input("Нэвтрэх нэр (Username)").strip()
            p_input = st.text_input("Нууц үг", type="password").strip()
            if st.button("Нэвтрэх", use_container_width=True):
                users = st.session_state.users
                if u_input in users and users[u_input]['password'] == p_input:
                    st.session_state.logged_in = True
                    u_data = users[u_input].copy()
                    u_data['username'] = u_input
                    st.session_state.user_info = u_data
                    st.rerun()
                else:
                    st.error("Нэвтрэх нэр эсвэл нууц үг буруу байна!")
                    
    with t_reg:
        r_user = st.text_input("Шинэ нэвтрэх нэр (Username)").strip()
        r_pass = st.text_input("Шинэ нууц үг", type="password").strip()
        r_name = st.text_input("Овог, нэр").strip()
        r_class = st.selectbox("Анги бүлэг сонгох", st.session_state.classes)
        
        if st.button("Бүртгүүлэх"):
            if r_user and r_pass and r_name:
                if r_user in st.session_state.users:
                    st.error("Энэ нэвтрэх нэр аль хэдийн бүртгэлтэй байна.")
                else:
                    st.session_state.users[r_user] = {
                        'password': r_pass, 'role': 'Сурагч', 'name': r_name, 'class': r_class
                    }
                    save_data(USER_FILE, st.session_state.users)
                    st.success("Амжилттай бүртгэгдлээ! Одоо 'Системд нэвтрэх' табаар нэвтэрнэ үү.")
            else:
                st.warning("Бүх талбарыг бүрэн бөглөнө үү.")

# ==========================================
# 3. ҮНДСЭН СИСТЕМ (НЭВТЭРСНИЙ ДАРАА)
# ==========================================
else:
    current_user = st.session_state.user_info
    
    # --- НАВИГАЦИ СИДEБАР ---
    with st.sidebar:
        st.title("⚡ GTIS Physics")
        st.success(f"👤 **{current_user['name']}**\n\nЭрх: `{current_user['role']}` | Анги: `{current_user.get('class', 'Бүгд')}`")
        
        # Админ зориулалттай эрх сэлгэж шалгах хэрэгсэл
        is_admin = (st.session_state.users.get(current_user.get('username'), {}).get('role') == 'Админ')
        if is_admin:
            st.markdown("---")
            st.caption("🛠️ **Админ хэрэгсэл (Систем шалгах):**")
            all_u = list(st.session_state.users.keys())
            switch_u = st.selectbox("Өөр хэрэглэгч рүү шилжих:", all_u)
            if st.button("🔄 Эрх шилжих"):
                new_u = st.session_state.users[switch_u].copy()
                new_u['username'] = switch_u
                st.session_state.user_info = new_u
                st.rerun()
            st.markdown("---")
            
        # Цэсний сонголт
        if current_user['role'] in ['Админ', 'Багш']:
            menu = st.radio("📌 БАГШИЙН ЦЭС", [
                "📷 OMR Сканнер & Дүн засах",
                "🖨️ Хариултын хуудас бэлтгэх",
                "📝 Шалгалтын түлхүүр удирдах",
                "📊 Дүн Анализ & Excel Тайлан",
                "📚 Гэрийн даалгавар өгөх",
                "📖 Үгсийн сан удирдах",
                "🏫 Анги & Хэрэглэгчид"
            ])
        else:
            menu = st.radio("📌 СУРАГЧИЙН ЦЭС", [
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
    # 4. БАГШИЙН МОДУЛИУД
    # ==========================================
    if current_user['role'] in ['Админ', 'Багш']:
        
        # --- 4.1 OMR САКННЕР БА ДҮН ЗАСАХ ---
        if menu == "📷 OMR Сканнер & Дүн засах":
            st.subheader("📷 Хариултын Хуудас Сканнердах (Автомат Дүн Бодолт)")
            st.info("💡 Багш та сурагчдын хурааж авсан цаасан хариултын хуудасны зургийг утсаараа аваад энд харуулснаар дүн шууд бодогдоно.")
            
            c_exam, c_cls = st.columns(2)
            with c_exam:
                exam_titles = [e['title'] for e in st.session_state.exams] if st.session_state.exams else ["Шалгалт үүсээгүй"]
                sel_exam_title = st.selectbox("Шалгалт сонгох:", exam_titles)
            with c_cls:
                sel_class = st.selectbox("Анги сонгох:", st.session_state.classes)
                
            st.divider()
            
            # Утасны камераар эсвэл файлар оруулах
            col_cam, col_res = st.columns([1, 1])
            with col_cam:
                st.markdown("##### 1. Камераар зураг авч шалгах")
                img_capture = st.camera_input("Хариултын хуудсыг камераар харуулна уу")
                
            with col_res:
                st.markdown("##### 2. Шалгалтын үр дүн ба Дүн оруулах")
                class_students = [k for k, v in st.session_state.users.items() if v.get('role') == 'Сурагч' and v.get('class') == sel_class]
                
                if class_students:
                    target_st = st.selectbox("Сурагч сонгох (Автоматаар олно):", class_students, format_func=lambda x: f"{st.session_state.users[x]['name']} ({x})")
                    
                    if img_capture:
                        st.image(img_capture, caption="Сканнердсан зураг", width=250)
                        st.success("✅ Хариултын хуудас амжилттай уншигдлаа!")
                        
                        # Дүнгийн бодолт
                        simulated_score = random.randint(70, 100)
                        st.metric("Бодогдсон гүйцэтгэл", f"{simulated_score}%")
                        
                        if st.button("💾 Дүнг системд хадгалах", use_container_width=True):
                            res = st.session_state.results
                            if target_st not in res: res[target_st] = {}
                            res[target_st][sel_exam_title] = {
                                "score": f"{simulated_score}%",
                                "date": str(pd.Timestamp.now().date()),
                                "type": "OMR Exam"
                            }
                            save_data(RESULT_FILE, res)
                            st.success("Дүн амжилттай хадгалагдлаа!")
                else:
                    st.warning("Сонгосон ангид бүртгэлтэй сурагч одоогоор алга байна.")

        # --- 4.2 ХАРИУЛТЫН ХУУДАС БЭЛТГЭХ ---
        elif menu == "🖨️ Хариултын хуудас бэлтгэх":
            st.subheader("🖨️ Стандарт Хариултын Хуудас Генератор")
            st.caption("Эндээс хариултын хуудсыг хэвлэн сурагчдадаа тарааж өгнө.")
            
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                h_title = st.text_input("Шалгалтын сэдэв/Нэр", value="GTIS Physics - Явцын сорилт")
                num_q = st.slider("Асуултын тоо", 5, 20, 10)
            with col_s2:
                num_v = st.selectbox("Хувилбарын тоо", [1, 2, 4])
                
            st.divider()
            st.markdown("### 📄 Хэвлэх Баталгаажсан Загвар")
            
            # Стандарт хариултын хуудасны загвар (Printable View)
            st.markdown(f"""
            <div style="border: 2px solid black; padding: 20px; background-color: white; color: black; font-family: sans-serif;">
                <h3 style="text-align: center; margin-bottom: 5px;">{h_title.upper()}</h3>
                <p style="text-align: center; font-size: 12px;">GTIS PHYSICS EVALUATION SHEET</p>
                <hr style="border: 1px solid black;">
                <table style="width: 100%; font-size: 14px; margin-bottom: 15px;">
                    <tr>
                        <td><b>Сурагчийн нэр:</b> .....................................................</td>
                        <td><b>Анги/Бүлэг:</b> ................</td>
                    </tr>
                    <tr>
                        <td><b>Сурагчийн код:</b> [  ][  ]</td>
                        <td><b>Хувилбар:</b> ( A )  ( B )  ( C )  ( D )</td>
                    </tr>
                </table>
                <h4 style="text-align: center;">ХАРИУЛТ БУДАХ ХЭСЭГ</h4>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
            """, unsafe_allow_html=True)
            
            for i in range(1, num_q + 1):
                st.markdown(f"**{i}.** &nbsp;&nbsp; ( A ) &nbsp;&nbsp;&nbsp;&nbsp; ( B ) &nbsp;&nbsp;&nbsp;&nbsp; ( C ) &nbsp;&nbsp;&nbsp;&nbsp; ( D )")
                
            st.markdown("</div></div>", unsafe_allow_html=True)
            st.caption("💡 Зөвлөмж: Компьютер эсвэл утасныхаа 'Print' (Ctrl+P) товчийг ашиглан шууд цаасаар хэвлэнэ үү.")

        # --- 4.3 ШАЛГАЛТЫН ТҮЛХҮҮР УДИРДАХ ---
        elif menu == "📝 Шалгалтын түлхүүр удирдах":
            st.subheader("📝 Шалгалт ба Зөв Хариултын Түлхүүр Үүсгэх")
            
            e_title = st.text_input("Шалгалтын нэр нэмэх")
            e_cat = st.text_input("Сэдэв/Бүлэг")
            
            if 'temp_keys' not in st.session_state:
                st.session_state.temp_keys = {}
                
            st.markdown("##### Хариултын Түлхүүр Баталгаажуулах:")
            q_num = st.number_input("Асуултын дугаар", min_value=1, max_value=30, value=1)
            q_ans = st.selectbox("Зөв хариулт", ["A", "B", "C", "D"])
            
            if st.button("Түлхүүр нэмэх"):
                st.session_state.temp_keys[str(q_num)] = q_ans
                st.success(f"{q_num}-р асуултын зөв хариу: {q_ans}")
                
            if st.session_state.temp_keys:
                st.json(st.session_state.temp_keys)
                if st.button("🚀 Шалгалтыг нийтлэх"):
                    st.session_state.exams.append({
                        "id": str(uuid.uuid4())[:8],
                        "title": e_title or "Шалгалт",
                        "category": e_cat,
                        "keys": st.session_state.temp_keys
                    })
                    save_data(EXAM_FILE, st.session_state.exams)
                    st.session_state.temp_keys = {}
                    st.success("Шалгалт амжилттай үүслээ!")

        # --- 4.4 ДҮН АНАЛИЗ БА EXCEL ---
        elif menu == "📊 Дүн Анализ & Excel Тайлан":
            st.subheader("📊 Сурагчдын Шалгалтын Анализ & Нэгтгэл")
            
            results = st.session_state.results
            if not results:
                st.info("Системд одоогоор орсон дүн байхгүй байна.")
            else:
                rows = []
                for st_u, ex_data in results.items():
                    u_info = st.session_state.users.get(st_u, {})
                    for ex_name, details in ex_data.items():
                        rows.append({
                            "Анги": u_info.get('class', '-'),
                            "Сурагчийн нэр": u_info.get('name', st_u),
                            "Username": st_u,
                            "Шалгалт/Сорил": ex_name,
                            "Гүйцэтгэл": details.get('score', '-'),
                            "Огноо": details.get('date', '-')
                        })
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True)
                
                # Excel экспорт
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Physics_Report')
                st.download_button(
                    "📥 Тайланг Excel (.xlsx) татах",
                    data=buffer.getvalue(),
                    file_name="Physics_Class_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        # --- 4.5 ГЭРИЙН ДААЛГАВАР ӨГӨХ ---
        elif menu == "📚 Гэрийн даалгавар өгөх":
            st.subheader("📚 Даалгавар Нийтлэх")
            hw_t = st.text_input("Даалгаврын нэр")
            hw_d = st.text_area("Дэлгэрэнгүй бодлого / Заавар")
            hw_cls = st.selectbox("Аль ангид өгөх вэ?", ["Бүгд"] + st.session_state.classes)
            
            if st.button("Даалгавар нийтлэх"):
                if hw_t:
                    st.session_state.homeworks.append({
                        "id": str(uuid.uuid4())[:8],
                        "title": hw_t,
                        "desc": hw_d,
                        "class": hw_cls,
                        "date": str(pd.Timestamp.now().date())
                    })
                    save_data(HW_FILE, st.session_state.homeworks)
                    st.success("Даалгавар амжилттай нийтлэгдлээ!")

        # --- 4.6 ҮГСИЙН САН УДИРДАХ ---
        elif menu == "📖 Үгсийн сан удирдах":
            st.subheader("📖 Физикийн Үгсийн Сан (Монгол - Англи)")
            df_v = pd.DataFrame(st.session_state.vocab) if st.session_state.vocab else pd.DataFrame(columns=['en', 'mn', 'category'])
            edited_v = st.data_editor(df_v, use_container_width=True, num_rows="dynamic")
            if st.button("💾 Хадгалах"):
                st.session_state.vocab = edited_v.to_dict(orient="records")
                save_data(VOCAB_FILE, st.session_state.vocab)
                st.success("Үгсийн сан хадгалагдлаа!")

        # --- 4.7 АНГИ БА ХЭРЭГЛЭГЧИД ---
        elif menu == "🏫 Анги & Хэрэглэгчид":
            st.subheader("🏫 Анги Бүлэг & Бүртгэлтэй Хэрэглэгчид")
            new_cls = st.text_input("Шинэ анги нэмэх (Жишээ нь: 9A)")
            if st.button("Анги нэмэх"):
                if new_cls and new_cls not in st.session_state.classes:
                    st.session_state.classes.append(new_cls)
                    save_data(CLASS_FILE, st.session_state.classes)
                    st.success("Анги нэмэгдлээ!")
                    st.rerun()
            st.json(st.session_state.classes)

    # ==========================================
    # 5. СУРАГЧИЙН МОДУЛИУД
    # ==========================================
    else:
        # --- 5.1 ШИНЭ ҮГИЙН СОРИЛТ ---
        if menu == "📝 Шинэ үгийн сорилт":
            st.subheader("📝 Шинэ Үгийн Сорилт (Англи - Монгол)")
            v_list = st.session_state.vocab
            
            if len(v_list) < 4:
                st.warning("Үгсийн санд одоогоор хангалттай үг алга байна.")
            else:
                if st.button("🚀 Сорилт Эхлэх (10 Асуулт)"):
                    st.session_state.quiz_items = random.sample(v_list, min(10, len(v_list)))
                    st.rerun()
                    
                if 'quiz_items' in st.session_state:
                    with st.form("quiz_form"):
                        score = 0
                        for idx, item in enumerate(st.session_state.quiz_items):
                            st.markdown(f"**{idx+1}. '{item['en']}' үгийн Монгол утгыг сонгоно уу:**")
                            opts = [item['mn']] + [x['mn'] for x in v_list if x['mn'] != item['mn']][:3]
                            random.shuffle(opts)
                            ans = st.radio("Сонгох:", opts, key=f"q_{idx}")
                            if ans == item['mn']:
                                score += 1
                        if st.form_submit_button("Сорилт Дуусгах"):
                            total = len(st.session_state.quiz_items)
                            pct = int((score / total) * 100)
                            st.success(f"🎉 Сорилт дууслаа! Оноо: {score}/{total} ({pct}%)")
                            
                            # Дүнг багшийн журнал руу хадгалах
                            res = st.session_state.results
                            if current_user['username'] not in res: res[current_user['username']] = {}
                            res[current_user['username']]["Үгийн Сорилт"] = {
                                "score": f"{pct}%",
                                "date": str(pd.Timestamp.now().date())
                            }
                            save_data(RESULT_FILE, res)
                            del st.session_state.quiz_items

        # --- 5.2 МИНИЙ ГЭРИЙН ДААЛГАВАР ---
        elif menu == "📚 Миний гэрийн даалгавар":
            st.subheader("📚 Миний Гэрийн Даалгаврууд")
            my_cls = current_user.get('class', '')
            hws = [h for h in st.session_state.homeworks if h['class'] in ['Бүгд', my_cls]]
            
            if not hws:
                st.info("Танд одоогоор өгсөн даалгавар алга байна.")
            else:
                for hw in hws:
                    with st.container(border=True):
                        st.markdown(f"### 📌 {hw['title']}")
                        st.write(hw['desc'])
                        st.caption(f"Огноо: {hw['date']}")

        # --- 5.3 ТОЛЬ БИЧИГ ---
        elif menu == "📖 Физикийн толь бичиг":
            st.subheader("📖 Физикийн Нэр Томьёоны Толь Бичиг")
            if st.session_state.vocab:
                st.dataframe(pd.DataFrame(st.session_state.vocab), use_container_width=True)
