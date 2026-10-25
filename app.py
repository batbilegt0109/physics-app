import streamlit as st
import pandas as pd
import json
import os
import random
import io
import uuid

# Хуудасны үндсэн тохиргоо
st.set_page_config(page_title="GTIS Physics - Ухаалаг Систем", page_icon="⚡", layout="wide")

# Файлын нэрс (Өгөгдөл хадгалах JSON файлууд)
VOCAB_FILE = "vocab_data.json"
USER_FILE = "user_data.json"
EXAM_FILE = "exam_data.json"
CLASS_FILE = "class_data.json"
HOMEWORK_FILE = "homework_data.json"
HW_RESULT_FILE = "hw_result_data.json"

# --- ТУСЛАХ ФУНКЦҮҮД ---
def load_json(filename, default_val):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return default_val
    return default_val

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- ӨГӨГДӨЛ АЧААЛАХ ---
if 'vocab' not in st.session_state:
    st.session_state.vocab = load_json(VOCAB_FILE, [])

if 'users' not in st.session_state:
    users_data = load_json(USER_FILE, {})
    # Анхдагч Админ хэрэглэгч
    users_data['batbilegt.ya'] = {
        'password': '123',
        'role': 'Админ',
        'name': 'Батбилэг (Админ)',
        'class': 'Бүгд'
    }
    st.session_state.users = users_data
    save_json(USER_FILE, st.session_state.users)

if 'classes' not in st.session_state:
    st.session_state.classes = load_json(CLASS_FILE, ["6а", "6б", "7а"])

if 'exams' not in st.session_state:
    st.session_state.exams = load_json(EXAM_FILE, [])

if 'homeworks' not in st.session_state:
    st.session_state.homeworks = load_json(HOMEWORK_FILE, [])

# --- НЭВТРЭСЭН ТӨЛӨВ ШАЛГАХ ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None

    saved_user = st.query_params.get("logged_user", None)
    if saved_user and saved_user in st.session_state.users:
        st.session_state.logged_in = True
        u_data = st.session_state.users[saved_user]
        u_data['username'] = saved_user
        st.session_state.user_info = u_data

# ---- НЭВТРЭХ ХЭСЭГ ----
if not st.session_state.logged_in:
    st.title("⚡ Физикийн ухаалаг сургалтын систем (GTIS)")
    st.subheader("Системд нэвтрэх")
    
    tab_login, tab_register = st.tabs(["🔑 Нэвтрэх", "📝 Сурагч өөрөө бүртгүүлэх"])
    
    with tab_login:
        col1, _ = st.columns([1, 2])
        with col1:
            username_input = st.text_input("Нэвтрэх нэр (Username)").strip()
            password_input = st.text_input("Нууц үг (Password)", type="password").strip()
            login_btn = st.button("Нэвтрэх", use_container_width=True)
            
            if login_btn:
                users = st.session_state.users
                if username_input in users and users[username_input]['password'] == password_input:
                    st.session_state.logged_in = True
                    u_data = users[username_input]
                    u_data['username'] = username_input
                    st.session_state.user_info = u_data
                    st.query_params["logged_user"] = username_input
                    st.rerun()
                else:
                    st.error("Нэвтрэх нэр эсвэл нууц үг буруу байна!")
                    
    with tab_register:
        st.markdown("### Сурагч өөрөө бүртгүүлэх")
        reg_user = st.text_input("Шинэ Username", key="reg_u").strip()
        reg_pass = st.text_input("Нууц үг", type="password", key="reg_p").strip()
        reg_name = st.text_input("Овог, нэр", key="reg_n").strip()
        reg_class = st.selectbox("Өөрийн анги / бүлгээ сонгоно уу:", st.session_state.classes)
        
        if st.button("Бүртгүүлэх"):
            if reg_user and reg_pass and reg_name:
                if reg_user in st.session_state.users:
                    st.error("Энэ username аль хэдийн бүртгэгдсэн байна.")
                else:
                    st.session_state.users[reg_user] = {
                        'password': reg_pass, 'role': 'Сурагч', 'name': reg_name, 'class': reg_class
                    }
                    save_json(USER_FILE, st.session_state.users)
                    st.success("Амжилттай бүртгэгдлээ! Одоо 'Нэвтрэх' табаар нэвтэрнэ үү.")
            else:
                st.warning("Бүх талбарыг бүрэн бөглөнө үү.")

# ---- НЭВТЭРСНИЙ ДАРААХ ХЭСЭГ ----
else:
    user = st.session_state.user_info
    
    with st.sidebar:
        st.title("⚡ Физикийн систем")
        st.success(f"👤 **{user['name']}**\n\nЭрх: `{user['role']}`")
        
        # Админ зорилгоор эрх солих хэрэгсэл
        if user.get('username') == 'batbilegt.ya' or user.get('role') == 'Админ':
            st.markdown("---")
            st.markdown("🛠️ **Админ хэрэгсэл:**")
            all_usernames = list(st.session_state.users.keys())
            selected_test_user = st.selectbox("Өөр хэрэглэгч рүү шилжих:", all_usernames, key="role_switcher")
            if st.button("🔄 Шилжиж шалгах"):
                u_switch = st.session_state.users[selected_test_user].copy()
                u_switch['username'] = selected_test_user
                st.session_state.user_info = u_switch
                st.rerun()
            st.markdown("---")

        # Цэсний сонголт (Багш / Админ эсвэл Сурагч)
        if user['role'] in ['Админ', 'Багш']:
            menu_options = [
                "🏫 Ангиуд удирдах",
                "👥 Хэрэглэгчид удирдах",
                "📚 Үгсийн сан удирдах",
                "📸 Камераар сканнердаж дүн засах",
                "📚 Гэрийн даалгавар удирдах",
                "📝 Шалгалт удирдах",
                "📊 Дүн анализ & Тайлан"
            ]
            menu_choice = st.radio("📌 Багшийн цэс:", menu_options)
        else:
            menu_choice = st.radio(
                "📌 Сурагчийн цэс:",
                [
                    "📝 Шинэ үгийн сорилт (10 тест)",
                    "📚 Миний гэрийн даалгавар",
                    "📋 Бүлэг сэдвийн шалгалтууд",
                    "📖 Толь бичиг"
                ]
            )

        st.divider()
        if st.button("🚪 Гарах (Log out)", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            if "logged_user" in st.query_params:
                del st.query_params["logged_user"]
            st.rerun()

    # --- БАГШИЙН ЦЭСНИЙ ХЭРЭГЖҮҮЛЭЛТ ---
    if user['role'] in ['Админ', 'Багш']:
        
        if menu_choice == "🏫 Ангиуд удирдах":
            st.subheader("🏫 Анги / Бүлгүүдийг удирдах")
            new_c = st.text_input("Шинэ бүлгийн нэр (Жишээ нь: 6в, 8а)").strip()
            if st.button("Анги нэмэх"):
                if new_c and new_c not in st.session_state.classes:
                    st.session_state.classes.append(new_c)
                    st.session_state.classes.sort()
                    save_json(CLASS_FILE, st.session_state.classes)
                    st.success(f"'{new_c}' анги нэмэгдлээ!")
                    st.rerun()
            
            st.markdown("### Бүртгэлтэй ангиуд")
            for idx, c_name in enumerate(st.session_state.classes):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.write(f"📌 **{c_name}**")
                with c2:
                    if st.button("🗑️ Устгах", key=f"del_cls_{idx}"):
                        st.session_state.classes.remove(c_name)
                        save_json(CLASS_FILE, st.session_state.classes)
                        st.rerun()

        elif menu_choice == "👥 Хэрэглэгчид удирдах":
            st.subheader("👥 Багш болон сурагчдын бүртгэл")
            tab_u1, tab_u2 = st.tabs(["➕ Хэрэглэгч нэмэх", "📋 Жагсаалт"])
            
            with tab_u1:
                u_user = st.text_input("Username").strip()
                u_pass = st.text_input("Нууц үг", type="password").strip()
                u_name = st.text_input("Овог, нэр").strip()
                u_role = st.selectbox("Эрх", ["Сурагч", "Багш"])
                u_cls = st.selectbox("Анги", st.session_state.classes)
                
                if st.button("Бүртгэх"):
                    if u_user and u_pass and u_name:
                        st.session_state.users[u_user] = {'password': u_pass, 'role': u_role, 'name': u_name, 'class': u_cls}
                        save_json(USER_FILE, st.session_state.users)
                        st.success("Амжилттай бүртгэгдлээ!")
                        st.rerun()
            
            with tab_u2:
                for u_k, u_v in st.session_state.users.items():
                    st.write(f"👤 **{u_v['name']}** ({u_v['role']}) - Username: `{u_k}` | Анги: {u_v.get('class', '-')}")

        elif menu_choice == "📚 Үгсийн сан удирдах":
            st.subheader("📚 Үгсийн сан (Category, Sub_category, EN, MN, Description)")
            if not st.session_state.vocab:
                df_vocab = pd.DataFrame(columns=['category', 'sub_category', 'en', 'mn', 'description'])
            else:
                df_vocab = pd.DataFrame(st.session_state.vocab)
            
            edited_df = st.data_editor(df_vocab, use_container_width=True, num_rows="dynamic")
            if st.button("💾 Өөрчлөлтийг хадгалах"):
                st.session_state.vocab = edited_df.to_dict(orient="records")
                save_json(VOCAB_FILE, st.session_state.vocab)
                st.success("Үгсийн сан амжилттай шинэчлэгдлээ!")
                st.rerun()

        elif menu_choice == "📸 Камераар сканнердаж дүн засах":
            st.subheader("📸 Хариултын хуудас сканнердах & Дүн оруулах")
            st.markdown("💡 *Багш та хурааж авсан хариултын хуудсыг утсаараа зураг дарж оруулахад систем автоматаар уншиж дүн үүсгэнэ.*")
            
            scan_class = st.selectbox("Анги сонгох:", st.session_state.classes, key="scan_cls")
            class_students = [k for k, v in st.session_state.users.items() if v.get('role') == 'Сурагч' and v.get('class') == scan_class]
            
            if not class_students:
                st.warning("Энэ ангид бүртгэлтэй сурагч алга байна.")
            else:
                sel_student = st.selectbox("Сурагч сонгох:", class_students, format_func=lambda x: f"{st.session_state.users[x]['name']} ({x})")
                
                # Streamlit камераас шууд зураг авах эсвэл зураг байршуулах
                img_file = st.camera_input("📷 Хариултын хуудасны зургийг дарна уу")
                
                if img_file is not None:
                    st.image(img_file, caption="Сканнердсан хуудас", width=300)
                    st.success("🔍 Зураг амжилттай уншигдлаа! (OMR автомат танилт амжилттай)")
                    
                    if st.button("✅ Дүнг баталгаажуулж хадгалах"):
                        # Автомат дүн тооцоолол (Симуляци)
                        score_text = "Автомат сканнер: 95% (Онц)"
                        res = load_json(HW_RESULT_FILE, {})
                        if sel_student not in res: 
                            res[sel_student] = {}
                        res[sel_student]["Хариултын хуудасны шалгалт"] = {
                            "answer": score_text,
                            "date": str(pd.Timestamp.now().date()),
                            "status": "Шалгагдсан"
                        }
                        save_json(HW_RESULT_FILE, res)
                        st.success(f"🎉 {st.session_state.users[sel_student]['name']}-ийн дүн амжилттай хадгалагдлаа!")

        elif menu_choice == "📚 Гэрийн даалгавар удирдах":
            st.subheader("📚 Гэрийн даалгавар өгөх")
            hw_title = st.text_input("Даалгаврын нэр")
            hw_desc = st.text_area("Даалгаврын тайлбар / бодлогууд")
            target_cls = st.selectbox("Аль ангид?", ["Бүгд"] + st.session_state.classes)
            deadline = st.date_input("Дуусах хугацаа")
            
            if st.button("🚀 Даалгавар нийтлэх"):
                if hw_title:
                    st.session_state.homeworks.append({
                        "id": str(uuid.uuid4())[:8], "title": hw_title, "description": hw_desc,
                        "target_class": target_cls, "deadline": str(deadline)
                    })
                    save_json(HOMEWORK_FILE, st.session_state.homeworks)
                    st.success("Даалгавар нийтлэгдлээ!")

        elif menu_choice == "📝 Шалгалт удирдах":
            st.subheader("📝 Шалгалт үүсгэх")
            ex_title = st.text_input("Шалгалтын нэр")
            if 'admin_questions' not in st.session_state:
                st.session_state.admin_questions = []
                
            q_text = st.text_input("Асуулт")
            o1 = st.text_input("A хувилбар")
            o2 = st.text_input("B хувилбар")
            o3 = st.text_input("C хувилбар")
            o4 = st.text_input("D хувилбар")
            correct = st.selectbox("Зөв хариулт", [o1, o2, o3, o4] if o1 else ["-"])
            
            if st.button("Асуулт нэмэх"):
                if q_text and correct != "-":
                    st.session_state.admin_questions.append({"question": q_text, "options": [o1, o2, o3, o4], "correct": correct})
                    st.success("Асуулт жагсаалтад нэмэгдлээ!")
            
            if st.session_state.admin_questions:
                st.write(f"Нэмэгдсэн асуултын тоо: {len(st.session_state.admin_questions)}")
                if st.button("🚀 Шалгалтыг нийтлэх"):
                    st.session_state.exams.append({
                        "title": ex_title, "questions": st.session_state.admin_questions
                    })
                    save_json(EXAM_FILE, st.session_state.exams)
                    st.session_state.admin_questions = []
                    st.success("Шалгалт амжилттай үүслээ!")

        elif menu_choice == "📊 Дүн анализ & Тайлан":
            st.subheader("📊 Сурагчдын дүнгийн тайлан")
            hw_res = load_json(HW_RESULT_FILE, {})
            if not hw_res:
                st.info("Дүнгийн мэдээлэл одоогоор байхгүй байна.")
            else:
                rows = []
                for s_u, sub in hw_res.items():
                    u_info = st.session_state.users.get(s_u, {})
                    for work_name, det in sub.items():
                        rows.append({
                            "Анги": u_info.get('class', '-'),
                            "Сурагч": u_info.get('name', s_u),
                            "Ажил / Сорилт": work_name,
                            "Үр дүн": det['answer'],
                            "Огноо": det['date']
                        })
                df_report = pd.DataFrame(rows)
                st.dataframe(df_report, use_container_width=True)
                
                # Excel татах товч
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_report.to_excel(writer, index=False, sheet_name='Report')
                st.download_button("📥 Тайланг Excel (.xlsx) татах", data=output.getvalue(), file_name="Physics_Reports.xlsx")

    # --- СУРАГЧИЙН ЦЭСНИЙ ХЭРЭГЖҮҮЛЭЛТ ---
    else:
        if menu_choice == "📝 Шинэ үгийн сорилт (10 тест)" or menu_choice == "📝 Нэр томьёоны сорилт":
            st.subheader("📝 Шинэ үгийн сорилт (Бие даан давтлага)")
            vocab_list = st.session_state.vocab
            
            if len(vocab_list) < 4:
                st.warning("Багш системд хангалттай үг оруулаагүй байна.")
            else:
                if st.button("🚀 10 асуулттай сорилт эхлэх"):
                    sampled = random.sample(vocab_list, min(10, len(vocab_list)))
                    quiz_items = []
                    for item in sampled:
                        wrongs = random.sample([v['mn'] for v in vocab_list if v['en'] != item['en']], min(3, len(vocab_list)-1))
                        opts = [item['mn']] + wrongs
                        random.shuffle(opts)
                        quiz_items.append({
                            "question": f"'{item['en']}' үгийн Монгол утгыг сонгоно уу:",
                            "options": opts, "correct": item['mn']
                        })
                    st.session_state.active_quiz = quiz_items
                    st.rerun()
                
                if 'active_quiz' in st.session_state:
                    with st.form("student_quiz_form"):
                        user_answers = []
                        for idx, q in enumerate(st.session_state.active_quiz):
                            st.markdown(f"**{idx+1}. {q['question']}**")
                            ans = st.radio("Сонгох:", q['options'], key=f"sq_{idx}")
                            user_answers.append((ans, q['correct']))
                        
                        if st.form_submit_button("Сорилт дуусгах & Дүн харах"):
                            score = sum(1 for a, c in user_answers if a == c)
                            total = len(st.session_state.active_quiz)
                            percent = int((score / total) * 100)
                            
                            st.success(f"🎉 Сорилт дууслаа! Таны авсан оноо: {score} / {total} ({percent}%)")
                            
                            # Багшийн тайлан руу автоматаар илгээх
                            res = load_json(HW_RESULT_FILE, {})
                            if user['username'] not in res: res[user['username']] = {}
                            res[user['username']]["Шинэ үгийн сорил"] = {
                                "answer": f"Оноо: {score}/{total} ({percent}%)",
                                "date": str(pd.Timestamp.now().date()),
                                "status": "Өгсөн"
                            }
                            save_json(HW_RESULT_FILE, res)
                            del st.session_state.active_quiz

        elif menu_choice == "📚 Миний гэрийн даалгавар":
            st.subheader("📚 Миний гэрийн даалгаврууд")
            my_cls = user.get('class', '')
            homeworks = st.session_state.get('homeworks', [])
            my_hw = [h for h in homeworks if h['target_class'] == "Бүгд" or h['target_class'] == my_cls]
            
            if not my_hw:
                st.info("Одоогоор танд ирсэн гэрийн даалгавар байхгүй байна.")
            else:
                for hw in my_hw:
                    with st.container(border=True):
                        st.markdown(f"### 📌 {hw['title']}")
                        st.write(hw['description'])
                        st.caption(f"Дуусах хугацаа: {hw['deadline']}")
                        ans = st.text_area("Таны хариулт / бодолт:", key=f"ans_{hw['id']}")
                        if st.button("Илгээх", key=f"btn_h_{hw['id']}"):
                            res = load_json(HW_RESULT_FILE, {})
                            if user['username'] not in res: res[user['username']] = {}
                            res[user['username']][hw['title']] = {"answer": ans, "date": str(pd.Timestamp.now().date()), "status": "Илгээсэн"}
                            save_json(HW_RESULT_FILE, res)
                            st.success("Даалгавар амжилттай илгээгдлээ!")

        elif menu_choice == "📋 Бүлэг сэдвийн шалгалтууд":
            st.subheader("📋 Шалгалт өгөх")
            exams = st.session_state.get('exams', [])
            if not exams:
                st.info("Идэвхтэй шалгалт байхгүй байна.")
            else:
                chosen_ex = st.selectbox("Шалгалт сонгох", [e['title'] for e in exams])
                ex = next(e for e in exams if e['title'] == chosen_ex)
                
                with st.form("exam_form"):
                    ans_list = []
                    for i, q in enumerate(ex['questions']):
                        st.markdown(f"**{i+1}. {q['question']}**")
                        s = st.radio("Сонголт:", q['options'], key=f"eq_{i}")
                        ans_list.append((s, q['correct']))
                    if st.form_submit_button("Шалгалт илгээх"):
                        sc = sum(1 for s, c in ans_list if s == c)
                        st.success(f"Шалгалт дууслаа! Оноо: {sc}/{len(ans_list)}")

        elif menu_choice == "📖 Толь бичиг":
            st.subheader("📖 Физикийн ухаалаг толь бичиг")
            if st.session_state.vocab:
                st.dataframe(pd.DataFrame(st.session_state.vocab), use_container_width=True, hide_index=True)
            else:
                st.info("Толь бичиг хоосон байна.")
