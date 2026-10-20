import streamlit as st
import pandas as pd
import json
import os
import random

# Хуудасны тохиргоо
st.set_page_config(page_title="GTIS Advanced Physics System", page_icon="⚡", layout="wide")

# Файлын нэрс
VOCAB_FILE = "vocab_data.json"
USER_FILE = "user_data.json"
RESULT_FILE = "result_data.json"
EXAM_FILE = "exam_data.json"
EXAM_RESULT_FILE = "exam_result_data.json"
CLASS_FILE = "class_data.json"
HOMEWORK_FILE = "homework_data.json"
HW_RESULT_FILE = "hw_result_data.json"

# --- ӨГӨГДӨЛ АЧАХ БА ХАДГАЛАХ ФУНКЦҮҮД ---
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

# Өгөгдлийг симулятор санах ойд ачаалах
if 'vocab' not in st.session_state:
    st.session_state.vocab = load_json(VOCAB_FILE, [
        {"category": "Оптик", "en": "Reflection", "mn": "Гэрлийн ойлт", "description": "Гэрлийн цацраг гадаргуугаас буцаж ойх үзэгдэл."},
        {"category": "Механик", "en": "Velocity", "mn": "Хурд", "description": "Нэгж хугацаан дахь шилжилт."}
    ])

if 'users' not in st.session_state:
    st.session_state.users = load_json(USER_FILE, {
        'bagsh': {'password': '1234', 'role': 'Багш', 'name': 'Батбилэг багш', 'class': 'Бүгд'},
        'suragch1': {'password': 'pass1', 'role': 'Сурагч', 'name': 'Бат (Сурагч)', 'class': '10а'},
        'suragch2': {'password': 'pass2', 'role': 'Сурагч', 'name': 'Болд (Сурагч)', 'class': '10б'}
    })

if 'classes' not in st.session_state:
    st.session_state.classes = load_json(CLASS_FILE, ["10а", "10б", "11а", "11б", "Гүнзгийрүүлсэн"])

if 'exams' not in st.session_state:
    st.session_state.exams = load_json(EXAM_FILE, [])

if 'homeworks' not in st.session_state:
    st.session_state.homeworks = load_json(HOMEWORK_FILE, [])

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None

# ---- РЕФРЭШ ХИЙХЭД ГАРАХГҮЙ БАЙХ ХЭСЭГ ----
params = st.query_params
if "user" in params and not st.session_state.logged_in:
    username = params["user"]
    users = st.session_state.users
    if username in users:
        st.session_state.logged_in = True
        st.session_state.user_info = users[username]
        st.session_state.user_info['username'] = username

# ---- НЭВТРЭХ ХЭСЭГ ----
if not st.session_state.logged_in:
    st.title("⚡ Физикийн ухаалаг сургалтын систем (GTIS)")
    st.subheader("Системд нэвтрэх")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        username_input = st.text_input("Нэвтрэх нэр (Username)").strip().lower()
        password_input = st.text_input("Нууц үг (Password)", type="password").strip()
        login_btn = st.button("Нэвтрэх", use_container_width=True)
        
        if login_btn:
            users = st.session_state.users
            if username_input in users and users[username_input]['password'] == password_input:
                st.session_state.logged_in = True
                st.session_state.user_info = users[username_input]
                st.session_state.user_info['username'] = username_input
                st.query_params["user"] = username_input
                st.rerun()
            else:
                st.error("Нэвтрэх нэр эсвэл нууц үг буруу байна!")
    with col2:
        st.info("💡 **Анхаарна уу:** Сурагчдын нууц үгийг зөвхөн багш систем дотроос удирдах боломжтой бөгөөд сурагч өөрөө өөрчлөх боломжгүй.")
    # --- БАГШИЙН ХЭСЭГ (Үргэлжлэл - 2-р хэсэг) ---
    if user['role'] == 'Багш':
        # 1. Ангиуд удирдах
        if menu_choice == "🏫 Ангиуд удирдах":
            st.subheader("Анги бүлгүүдийн жагсаалт ба нэмэх")
            new_class_name = st.text_input("Шинэ ангийн нэр (Жишээ нь: 10в, 12а)").strip()
            if st.button("➕ Анги нэмэх"):
                if new_class_name and new_class_name not in st.session_state.classes:
                    st.session_state.classes.append(new_class_name)
                    save_json(CLASS_FILE, st.session_state.classes)
                    st.success(f"'{new_class_name}' анги амжилттай нэмэгдлээ!")
                    st.rerun()
                else:
                    st.warning("Ангийн нэр хоосон эсвэл аль хэдийн үүссэн байна.")
            
            st.write("### Одоогийн ангиуд:")
            st.write(", ".join([f"**{c}**" for c in st.session_state.classes]))

        # 2. Сурагч & Нууц үг удирдах (Багш сурагчийн нууц үгийг шууд өөрчлөх боломжтой)
        elif menu_choice == "👥 Сурагч & Нууц үг удирдах":
            st.subheader("Сурагчдын бүртгэл болон нууц үг шинэчлэх")
            
            # Шинэ сурагч бүртгэх
            with st.expander("➕ Шинэ сурагч бүртгэх"):
                s_user = st.text_input("Сурагчийн нэвтрэх нэр (Username)").strip().lower()
                s_pass = st.text_input("Шинэ нууц үг").strip()
                s_name = st.text_input("Сурагчийн бүтэн нэр").strip()
                s_class = st.selectbox("Анги сонгох", st.session_state.classes)
                
                if st.button("Сурагч бүртгэх"):
                    if s_user and s_pass and s_name:
                        st.session_state.users[s_user] = {
                            'password': s_pass,
                            'role': 'Сурагч',
                            'name': s_name,
                            'class': s_class
                        }
                        save_json(USER_FILE, st.session_state.users)
                        st.success(f"'{s_name}' сурагч амжилттай бүртгэгдлээ!")
                        st.rerun()
                    else:
                        st.warning("Бүх талбарыг бүрэн бөглөнө үү.")

            st.divider()
            st.markdown("### 📋 Бүртгэлтэй сурагчдын жагсаалт ба Нууц үг солих")
            student_list = {k: v for k, v in st.session_state.users.items() if v['role'] == 'Сурагч'}
            
            if not student_list:
                st.info("Бүртгэлтэй сурагч байхгүй байна.")
            else:
                for s_username, s_data in student_list.items():
                    with st.container(border=True):
                        c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
                        with c1:
                            st.write(f"**Нэр:** {s_data['name']}")
                            st.caption(f"Username: `{s_username}`")
                        with c2:
                            st.write(f"**Анги:** {s_data.get('class', 'Тодорхойгүй')}")
                        with c3:
                            new_p = st.text_input(f"Шинэ нууц үг ({s_username})", type="password", key=f"pass_{s_username}")
                        with c4:
                            st.write("")
                            if st.button("💾 Шинэчлэх", key=f"btn_{s_username}"):
                                if new_p:
                                    st.session_state.users[s_username]['password'] = new_p
                                    save_json(USER_FILE, st.session_state.users)
                                    st.success(f"'{s_username}' нууц үг шинэчлэгдлээ!")
                                else:
                                    st.warning("Нууц үг хоосон байна.")

        # 3. Үгсийн сан удирдах
        elif menu_choice == "➕ Үгсийн сан удирдах":
            st.subheader("📚 Физикийн нэр томьёоны сан")
            sub_tab1, sub_tab2 = st.tabs(["Нэг нэгээр нэмэх / Засах", "Файлаар олон үг оруулах"])
            
            with sub_tab1:
                cat_list = ["Механик", "Цахилгаан соронзон", "Оптик", "Термодинамик", "Бусад"]
                c_col1, c_col2 = st.columns(2)
                with c_col1:
                    st.markdown("#### Шинэ үг нэмэх")
                    cat = st.selectbox("Бүлэг сэдэв", cat_list)
                    en = st.text_input("Англи термин").strip()
                    mn = st.text_input("Монгол утга").strip()
                    desc = st.text_area("Тайлбар").strip()
                    if st.button("Үг нэмэх"):
                        if en and mn:
                            st.session_state.vocab.append({"category": cat, "en": en, "mn": mn, "description": desc or "-"})
                            save_json(VOCAB_FILE, st.session_state.vocab)
                            st.success("Үг нэмэгдлээ!")
                            st.rerun()
                        else:
                            st.warning("Англи болон монгол утгыг оруулна уу.")
                with c_col2:
                    st.markdown("#### Одоогийн үгсийг устгах")
                    df_v = pd.DataFrame(st.session_state.vocab)
                    df_v.insert(0, "Устгах", False)
                    edited_v = st.data_editor(df_v, use_container_width=True, key="vocab_ed")
                    if st.button("Чеклэсэн үгсийг устгах"):
                        new_v = []
                        for idx, row in edited_v.iterrows():
                            if not row["Устгах"]:
                                new_v.append({"category": row.get("category", "Бусад"), "en": row["en"], "mn": row["mn"], "description": row["description"]})
                        st.session_state.vocab = new_v
                        save_json(VOCAB_FILE, st.session_state.vocab)
                        st.success("Устгагдлаа!")
                        st.rerun()
            
            with sub_tab2:
                st.info("Файлын формат: `category`, `en`, `mn`, `description` багануудтай байх.")
                up_file = st.file_uploader("Файл сонгох (CSV, Excel)", type=['csv', 'xlsx'])
                if up_file:
                    try:
                        df_up = pd.read_csv(up_file) if up_file.name.endswith('.csv') else pd.read_excel(up_file)
                        st.dataframe(df_up.head())
                        if st.button("Файлаас хуулах"):
                            count = 0
                            for _, r in df_up.iterrows():
                                if 'en' in df_up.columns and 'mn' in df_up.columns:
                                    st.session_state.vocab.append({
                                        "category": str(r.get('category', 'Бусад')),
                                        "en": str(r['en']),
                                        "mn": str(r['mn']),
                                        "description": str(r.get('description', '-'))
                                    })
                                    count += 1
                            save_json(VOCAB_FILE, st.session_state.vocab)
                            st.success(f"Нийт {count} үг нэмэгдлээ!")
                    except Exception as e:
                        st.error(f"Алдаа гарлаа: {e}")
    # --- БАГШИЙН ХЭСЭГ (Үргэлжлэл - 3-р хэсэг) ---
    elif user['role'] == 'Багш':
        # 4. Гэрийн даалгавар удирдах
        if menu_choice == "📚 Гэрийн даалгавар удирдах":
            st.subheader("📚 Гэрийн даалгавар үүсгэх ба хянах")
            hw_tab1, hw_tab2 = st.tabs(["Гэрийн даалгавар үүсгэх", "Гүйцэтгэлийг хянах"])
            
            with hw_tab1:
                hw_title = st.text_input("Даалгаврын гарчиг").strip()
                hw_desc = st.text_area("Даалгаврын дэлгэрэнгүй заавар, бодлогууд").strip()
                target_class = st.selectbox("Аль ангид зориулсан бэ?", ["Бүгд"] + st.session_state.classes)
                hw_deadline = st.date_input("Дуусах хугацаа")
                
                if st.button("📤 Даалгавар нийтлэх"):
                    if hw_title:
                        if 'homeworks' not in st.session_state:
                            st.session_state.homeworks = []
                        new_hw = {
                            "id": str(random.randint(1000, 9999)),
                            "title": hw_title,
                            "description": hw_desc,
                            "class": target_class,
                            "deadline": str(hw_deadline)
                        }
                        st.session_state.homeworks.append(new_hw)
                        save_json(HOMEWORK_FILE, st.session_state.homeworks)
                        st.success(f"'{hw_title}' даалгавар амжилттай нийтлэгдлээ!")
                    else:
                        st.warning("Даалгаврын гарчиг оруулна уу.")
            
            with hw_tab2:
                st.markdown("### Сурагчдын даалгавар гүйцэтгэлийн тайлан")
                hw_results = load_json(HW_RESULT_FILE, {})
                if not hw_results:
                    st.info("Одоогоор илгээсэн даалгавар байхгүй байна.")
                else:
                    hw_summary = []
                    for s_name, sub_dict in hw_results.items():
                        for h_title, details in sub_dict.items():
                            hw_summary.append({
                                "Сурагч": s_name,
                                "Даалгавар": h_title,
                                "Төлөв": details.get("status", "Илгээсэн"),
                                "Хариу тайлбар": details.get("answer", "-"),
                                "Огноо": details.get("date", "-")
                            })
                    st.dataframe(pd.DataFrame(hw_summary), use_container_width=True)

        # 5. Шалгалт удирдах
        elif menu_choice == "📝 Шалгалт удирдах":
            st.subheader("📝 Шалгалт үүсгэх ба удирдах")
            ex_title = st.text_input("Шалгалтын нэр").strip()
            ex_desc = st.text_area("Шалгалтын тайлбар, заавар").strip()
            
            if 'temp_questions' not in st.session_state:
                st.session_state.temp_questions = []
                
            st.markdown("#### Асуулт нэмэх")
            q_text = st.text_input("Асуулт").strip()
            o1 = st.text_input("Сонголт A").strip()
            o2 = st.text_input("Сонголт B").strip()
            o3 = st.text_input("Сонголт C").strip()
            o4 = st.text_input("Сонголт D").strip()
            correct_ans = st.selectbox("Зөв хариулт", [o1, o2, o3, o4] if o1 else ["-"])
            
            if st.button("➕ Асуулт нэмэх"):
                if q_text and correct_ans != "-":
                    st.session_state.temp_questions.append({
                        "question": q_text,
                        "options": [o1, o2, o3, o4],
                        "correct": correct_ans
                    })
                    st.success("Асуулт нэмэгдлээ!")
                else:
                    st.warning("Асуулт болон сонголтуудыг бүрэн оруулна уу.")
            
            if st.session_state.temp_questions:
                st.write(f"Нийт нэмэгдсэн асуулт: {len(st.session_state.temp_questions)}")
                if st.button("🚀 Шалгалтыг нийтлэх"):
                    if ex_title:
                        if 'exams' not in st.session_state:
                            st.session_state.exams = []
                        new_exam = {
                            "id": str(random.randint(1000, 9999)),
                            "title": ex_title,
                            "description": ex_desc,
                            "questions": st.session_state.temp_questions
                        }
                        st.session_state.exams.append(new_exam)
                        save_json(EXAM_FILE, st.session_state.exams)
                        st.session_state.temp_questions = []
                        st.success(f"'{ex_title}' шалгалт амжилттай үүслээ!")
                        st.rerun()
                    else:
                        st.warning("Шалгалтын нэрийг оруулна уу.")

# --- СУРАГЧИЙН ХЭСЭГ БОЛОН ТӨГСГӨЛ (4-р хэсэг) ---
    else:
        # 1. 10 Тестийн сорилт
        if menu_choice == "📝 Нэр томьёоны сорилт (10 тест)":
            st.subheader("📝 Физикийн нэр томьёоны сорилт (Яг 10 тест)")
            vocab_list = st.session_state.vocab
            
            if len(vocab_list) < 4:
                st.warning("Тест ажиллахад дор хаяж 4 үг шаардлагатай.")
            else:
                if 'exam_session' not in st.session_state:
                    st.session_state.exam_session = {'active': False, 'questions': [], 'current_idx': 0, 'score': 0}
                
                ses = st.session_state.exam_session
                
                if not ses['active']:
                    if st.button("🚀 Шинэ 10 тесттэй сорилт эхлэх"):
                        selected_vocab = random.sample(vocab_list, min(10, len(vocab_list)))
                        q_list = []
                        for item in selected_vocab:
                            wrong_items = random.sample([v for v in vocab_list if v['en'] != item['en']], min(3, len(vocab_list)-1))
                            options = [item['mn']] + [w['mn'] for w in wrong_items]
                            random.shuffle(options)
                            q_list.append({
                                'en': item['en'],
                                'correct': item['mn'],
                                'options': options
                                # Тайлбар хэсэг нууцлагдсан
                            })
                        ses['active'] = True
                        ses['questions'] = q_list
                        ses['current_idx'] = 0
                        ses['score'] = 0
                        st.rerun()
                else:
                    if ses['current_idx'] < len(ses['questions']):
                        q_num = ses['current_idx'] + 1
                        q = ses['questions'][ses['current_idx']]
                        
                        st.markdown(f"### Асуулт {q_num} / {len(ses['questions'])}")
                        st.markdown(f"Англи үг: **{q['en']}**")
                        
                        ans = st.radio("Монгол утгыг сонгоно уу:", q['options'], key=f"radio_{q_num}")
                        
                        if st.button("Хариулах & Дараах"):
                            if ans == q['correct']:
                                ses['score'] += 1
                            ses['current_idx'] += 1
                            st.rerun()
                    else:
                        st.success(f"🎉 Сорилт дууслаа! Оноо: {ses['score']} / {len(ses['questions'])}")
                        
                        results_db = load_json(RESULT_FILE, {})
                        u_key = user['username']
                        if u_key not in results_db:
                            results_db[u_key] = []
                        results_db[u_key].append({"word": "10 тест багц", "score": ses['score']})
                        save_json(RESULT_FILE, results_db)
                        
                        if st.button("Дахин сорилт өгөх"):
                            ses['active'] = False
                            st.rerun()

        # 2. Гэрийн даалгавар гүйцэтгэх
        elif menu_choice == "📚 Гэрийн даалгавар":
            st.subheader("📚 Миний гэрийн даалгаврууд")
            homeworks = st.session_state.get('homeworks', [])
            
            if not homeworks:
                st.info("Одоогоор идэвхтэй гэрийн даалгавар байхгүй байна.")
            else:
                for hw in homeworks:
                    if hw['class'] == "Бүгд" or hw['class'] == user.get('class'):
                        with st.container(border=True):
                            st.markdown(f"### 📌 {hw['title']}")
                            st.write(hw['description'])
                            st.caption(f"Дуусах хугацаа: {hw['deadline']}")
                            
                            hw_ans = st.text_area(f"Таны хариулт / Бодолт ({hw['title']})", key=f"ans_{hw['id']}")
                            if st.button("📤 Даалгавар илгээх", key=f"sub_{hw['id']}"):
                                if hw_ans:
                                    hw_res = load_json(HW_RESULT_FILE, {})
                                    if user['username'] not in hw_res:
                                        hw_res[user['username']] = {}
                                    hw_res[user['username']][hw['title']] = {
                                        "status": "Илгээсэн",
                                        "answer": hw_ans,
                                        "date": str(pd.Timestamp.now().date())
                                    }
                                    save_json(HW_RESULT_FILE, hw_res)
                                    st.success("Гэрийн даалгавар амжилттай илгээгдлээ!")
                                else:
                                    st.warning("Хариултаа бичнэ үү.")

        # 3. Бүлэг сэдвийн шалгалт өгөх
        elif menu_choice == "📋 Бүлэг сэдвийн шалгалтууд":
            st.subheader("📋 Идэвхтэй шалгалтууд")
            exams = st.session_state.get('exams', [])
            if not exams:
                st.info("Одоогоор багш шалгалт оруулаагүй байна.")
            else:
                exam_titles = [ex['title'] for ex in exams]
                chosen_ex = st.selectbox("Шалгалт сонгох:", exam_titles)
                selected_exam = next((ex for ex in exams if ex['title'] == chosen_ex), None)
                
                if selected_exam:
                    st.write(f"**Заавар:** {selected_exam['description']}")
                    with st.form(key=f"student_exam_{selected_exam['id']}"):
                        student_answers = []
                        for idx, q in enumerate(selected_exam['questions']):
                            st.markdown(f"**{idx+1}. {q['question']}**")
                            ans = st.radio("Хариулт:", q['options'], key=f"ex_q_{selected_exam['id']}_{idx}")
                            student_answers.append({"selected": ans, "correct": q['correct']})
                            
                        submit_exam = st.form_submit_button("Шалгалт дуусгах & Илгээх")
                        
                        if submit_exam:
                            score_count = sum([1 for item in student_answers if item['selected'] == item['correct']])
                            total_q = len(student_answers)
                            st.success(f"Шалгалт илгээгдлээ! Авсан оноо: {score_count}/{total_q}")
                            
                            exam_res_db = load_json(EXAM_RESULT_FILE, {})
                            u_key = user['username']
                            if u_key not in exam_res_db:
                                exam_res_db[u_key] = {}
                            exam_res_db[u_key][selected_exam['title']] = f"{score_count}/{total_q}"
                            save_json(EXAM_RESULT_FILE, exam_res_db)

        # 4. Толь бичиг
        elif menu_choice == "📖 Толь бичиг (Хайх & Эрэмбэлэх)":
            st.subheader("📖 Физикийн нэр томьёоны толь бичиг")
            search_query = st.text_input("🔍 Хайх үг").strip().lower()
            sort_option = st.selectbox("Эрэмбэлэх:", ["Англи үгээр (A-Z)", "Монгол үгээр (А-Я)"])
            
            df_vocab = pd.DataFrame(st.session_state.vocab)
            if search_query:
                df_vocab = df_vocab[
                    df_vocab['en'].str.lower().str.contains(search_query) | 
                    df_vocab['mn'].str.lower().str.contains(search_query)
                ]
            
            df_vocab = df_vocab.sort_values(by='en' if sort_option == "Англи үгээр (A-Z)" else 'mn')
            st.dataframe(df_vocab, use_container_width=True, hide_index=True)
