import streamlit as st
import pandas as pd
import json
import os
import random

# Хуудасны тохиргоо
st.set_page_config(page_title="GTIS Physics - Smart Exam System", page_icon="⚡", layout="wide")

VOCAB_FILE = "vocab_data.json"
USER_FILE = "user_data.json"
RESULT_FILE = "result_data.json"
EXAM_FILE = "exam_data.json"
EXAM_RESULT_FILE = "exam_result_data.json"

def load_data():
    if os.path.exists(VOCAB_FILE):
        with open(VOCAB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [
        {"category": "Оптик", "en": "Reflection", "mn": "Гэрлийн ойлт", "description": "Гэрлийн цацраг гадаргуугаас буцаж ойх үзэгдэл."},
        {"category": "Механик", "en": "Velocity", "mn": "Хурд", "description": "Нэгж хугацаан дахь шилжилт."},
        {"category": "Механик", "en": "Acceleration", "mn": "Хурдасгал", "description": "Хурдны өөрчлөлтийн хурдац."},
        {"category": "Цахилгаан", "en": "Current", "mn": "Гүйдэл", "description": "Цэнэгт бөөмсийн чиглэлт хөдөлгөөн."}
    ]

def save_data(vocab_list):
    with open(VOCAB_FILE, "w", encoding="utf-8") as f:
        json.dump(vocab_list, f, ensure_ascii=False, indent=4)

def load_results():
    if os.path.exists(RESULT_FILE):
        with open(RESULT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_results(results_dict):
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(results_dict, f, ensure_ascii=False, indent=4)

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        'bagsh': {'password': '1234', 'role': 'Багш', 'name': 'Батбилэг багш'},
        'suragch1': {'password': 'pass1', 'role': 'Сурагч', 'name': 'Сурагч Бат'},
        'suragch2': {'password': 'pass2', 'role': 'Сурагч', 'name': 'Сурагч Болд'}
    }

def save_users(users_dict):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users_dict, f, ensure_ascii=False, indent=4)

def load_exams():
    if os.path.exists(EXAM_FILE):
        with open(EXAM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_exams(exams_list):
    with open(EXAM_FILE, "w", encoding="utf-8") as f:
        json.dump(exams_list, f, ensure_ascii=False, indent=4)

def load_exam_results():
    if os.path.exists(EXAM_RESULT_FILE):
        with open(EXAM_RESULT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_exam_results(res_dict):
    with open(EXAM_RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(res_dict, f, ensure_ascii=False, indent=4)

# Инициализаци
if 'vocab' not in st.session_state:
    st.session_state.vocab = load_data()
if 'users' not in st.session_state:
    st.session_state.users = load_users()
if 'exams' not in st.session_state:
    st.session_state.exams = load_exams()
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None

# ---- НЭВТРЭХ ТӨЛӨВ Хадгалах ----
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
    st.title("⚡ Физикийн ухаалаг сургалтын систем")
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

# ---- НЭВТЭРСНИЙ ДАРААХ ХЭСЭГ ----
else:
    user = st.session_state.user_info
    
    with st.sidebar:
        st.title("⚡ Физикийн систем")
        st.success(f"👤 {user['name']}\n\nЭрх: **{user['role']}**")
        
        if user['role'] == 'Багш':
            menu_choice = st.radio(
                "📌 Багшийн цэс:",
                [
                    "➕ Нэг нэгээр үг нэмэх",
                    "✏️ Үг засах / 🗑️ Устгах",
                    "📁 Файлаар олон үг оруулах",
                    "📝 Шалгалт удирдах & Оруулах",
                    "🤖 AI тест генератор",
                    "👥 Хэрэглэгч удирдах",
                    "📊 Дүн шинжилгээ (Analytics)"
                ]
            )
        else:
            menu_choice = st.radio(
                "📌 Сурагчийн цэс:",
                [
                    "📝 Нэр томьёоны сорилт (10 тест)",
                    "📋 Бүлэг сэдвийн шалгалтууд",
                    "📖 Толь бичиг (Хайх & Эрэмбэлэх)"
                ]
            )

        st.divider()
        if st.button("🚪 Гарах (Log out)", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            if "user" in st.query_params:
                del st.query_params["user"]
            st.rerun()

    # --- БАГШИЙН ХЭСЭГ ---
    if user['role'] == 'Багш':
        st.title(f"👨‍🏫 Багшийн удирдлага: {menu_choice}")

        # 1. Нэг нэгээр үг нэмэх
        if menu_choice == "➕ Нэг нэгээр үг нэмэх":
            st.subheader("Физикийн шинэ нэр томьёо нэмэх")
            category = st.selectbox("Бүлэг сэдэв", ["Механик", "Цахилгаан соронзон", "Оптик", "Термодинамик", "Бусад"])
            en_word = st.text_input("Термин / Англи үг").strip()
            mn_word = st.text_input("Монгол утга").strip()
            desc_text = st.text_input("Товч тайлбар").strip()
            
            if st.button("💾 Үг нэмэх"):
                if en_word and mn_word:
                    st.session_state.vocab.append({
                        "category": category, 
                        "en": en_word, 
                        "mn": mn_word, 
                        "description": desc_text if desc_text else "-"
                    })
                    save_data(st.session_state.vocab)
                    st.success(f"'{en_word}' - '{mn_word}' амжилттай нэмэгдлээ!")
                else:
                    st.warning("Англи болон Монгол утгыг заавал бөглөнө үү.")

        # 2. Үг засах / Устгах
        elif menu_choice == "✏️ Үг засах / 🗑️ Устгах":
            st.subheader("Засах болон устгах жагсаалт")
            df_vocab = pd.DataFrame(st.session_state.vocab)
            df_vocab.insert(0, "Устгах", False)
            
            edited_df = st.data_editor(
                df_vocab, 
                use_container_width=True, 
                hide_index=False,
                key="vocab_table_editor"
            )
            
            col_del_btn, col_edit = st.columns(2)
            with col_del_btn:
                if st.button("🗑️ Чеклэсэн үгсийг устгах"):
                    survived_vocab = []
                    deleted_count = 0
                    for idx, row in edited_df.iterrows():
                        if not row["Устгах"]:
                            survived_vocab.append({
                                "category": row.get("category", "Бусад"),
                                "en": row["en"],
                                "mn": row["mn"],
                                "description": row["description"]
                            })
                        else:
                            deleted_count += 1
                    
                    if deleted_count > 0:
                        st.session_state.vocab = survived_vocab
                        save_data(st.session_state.vocab)
                        st.success(f"Нийт {deleted_count} үг устгагдлаа!")
                        st.rerun()
                    else:
                        st.warning("Устгах үгээ чеклэнэ үү.")

            with col_edit:
                st.markdown("### ✏️ Мөрийн дугаараар засах")
                edit_idx = st.number_input("Засах дугаар (Index)", min_value=1, max_value=max(len(st.session_state.vocab), 1), step=1)
                curr_item = st.session_state.vocab[edit_idx - 1]
                cat_list = ["Механик", "Цахилгаан соронзон", "Оптик", "Термодинамик", "Бусад"]
                cat_index = cat_list.index(curr_item.get("category", "Бусад")) if curr_item.get("category") in cat_list else 0
                
                new_cat = st.selectbox("Шинэ бүлэг сэдэв", cat_list, index=cat_index)
                new_en = st.text_input("Шинэ Англи үг", value=curr_item['en'])
                new_mn = st.text_input("Шинэ Монгол утга", value=curr_item['mn'])
                new_desc = st.text_area("Шинэ тайлбар", value=curr_item['description'])
                
                if st.button("Өөрчлөлтийг хадгалах"):
                    st.session_state.vocab[edit_idx - 1] = {
                        "category": new_cat,
                        "en": new_en.strip(),
                        "mn": new_mn.strip(),
                        "description": new_desc.strip()
                    }
                    save_data(st.session_state.vocab)
                    st.success(f"Амжилттай шинэчлэгдлээ!")
                    st.rerun()

        # 3. Файлаар олон үг оруулах
        elif menu_choice == "📁 Файлаар олон үг оруулах":
            st.subheader("Файлаар олон нэр томьёо оруулах")
            st.info("Файлын багануудын нэр: `category`, `en`, `mn`, `description` байхыг зөвлөж байна.")
            uploaded_file = st.file_uploader("Үгийн файл (CSV эсвэл Excel)", type=['csv', 'xlsx'])
            
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                    st.dataframe(df.head())
                    if st.button("📥 Эдгээр үгсийг системд хуулах"):
                        count = 0
                        for _, row in df.iterrows():
                            if 'en' in df.columns and 'mn' in df.columns:
                                cat = str(row['category']) if 'category' in df.columns and pd.notna(row['category']) else "Бусад"
                                desc = str(row['description']) if 'description' in df.columns and pd.notna(row['description']) else "-"
                                st.session_state.vocab.append({"category": cat, "en": str(row['en']), "mn": str(row['mn']), "description": desc})
                                count += 1
                        save_data(st.session_state.vocab)
                        st.success(f"Нийт {count} нэр томьёо амжилттай нэмэгдлээ!")
                except Exception as e:
                    st.error(f"Алдаа гарлаа: {e}")

        # 4. Шалгалт удирдах & Оруулах (Гараар болон файлаар)
        elif menu_choice == "📝 Шалгалт удирдах & Оруулах":
            st.subheader("📝 Бүлэг сэдвийн шалгалт үүсгэх")
            
            exam_mode = st.radio("Шалгалт оруулах хэлбэр:", ["Гараар асуулт шивэх", "📁 Файлаар олон асуулт оруулах (Excel/CSV)"])
            exam_title = st.text_input("Шалгалтын нэр (Жишээ нь: Оптикийн нэгдсэн шалгалт)").strip()
            exam_desc = st.text_area("Шалгалтын санамж / заавар").strip()

            if exam_mode == "Гараар асуулт шивэх":
                st.markdown("#### Асуулт нэмэх")
                if 'temp_exam_questions' not in st.session_state:
                    st.session_state.temp_exam_questions = []
                    
                q_text = st.text_input("Асуултын текст").strip()
                col_a, col_b = st.columns(2)
                with col_a:
                    opt1 = st.text_input("Сонголт A").strip()
                    opt2 = st.text_input("Сонголт B").strip()
                with col_b:
                    opt3 = st.text_input("Сонголт C").strip()
                    opt4 = st.text_input("Сонголт D").strip()
                
                correct_ans = st.selectbox("Зөв хариулт", [opt1, opt2, opt3, opt4] if opt1 else ["-"])
                
                if st.button("➕ Асуултыг жагсаалтад нэмэх"):
                    if q_text and correct_ans != "-":
                        st.session_state.temp_exam_questions.append({
                            "question": q_text,
                            "options": [opt1, opt2, opt3, opt4],
                            "correct": correct_ans
                        })
                        st.success("Асуулт нэмэгдлээ!")
                    else:
                        st.warning("Асуулт болон сонголтуудыг гүйцэд оруулна уу.")
                
                if st.session_state.temp_exam_questions:
                    st.write(f"Одоогоор цугларсан асуулт: {len(st.session_state.temp_exam_questions)}")
                    if st.button("🚀 Шалгалтыг нийтлэх"):
                        if exam_title:
                            new_exam = {
                                "id": str(random.randint(1000, 9999)),
                                "title": exam_title,
                                "description": exam_desc,
                                "questions": st.session_state.temp_exam_questions
                            }
                            st.session_state.exams.append(new_exam)
                            save_exams(st.session_state.exams)
                            st.session_state.temp_exam_questions = []
                            st.success(f"'{exam_title}' шалгалт амжилттай үүслээ!")
                            st.rerun()

            else:
                st.info("Файлын багана: `question`, `opt1`, `opt2`, `opt3`, `opt4`, `correct` нэртэй байх шаардлагатай.")
                uploaded_exam_file = st.file_uploader("Шалгалтын асуултын файл", type=['csv', 'xlsx'])
                if uploaded_exam_file is not None:
                    try:
                        df_ex = pd.read_csv(uploaded_exam_file) if uploaded_exam_file.name.endswith('.csv') else pd.read_excel(uploaded_exam_file)
                        st.dataframe(df_ex.head())
                        
                        if st.button("📥 Файлаас шалгалт шууд үүсгэх"):
                            if exam_title:
                                file_questions = []
                                for _, row in df_ex.iterrows():
                                    file_questions.append({
                                        "question": str(row['question']),
                                        "options": [str(row['opt1']), str(row['opt2']), str(row['opt3']), str(row['opt4'])],
                                        "correct": str(row['correct'])
                                    })
                                new_exam = {
                                    "id": str(random.randint(1000, 9999)),
                                    "title": exam_title,
                                    "description": exam_desc,
                                    "questions": file_questions
                                }
                                st.session_state.exams.append(new_exam)
                                save_exams(st.session_state.exams)
                                st.success(f"'{exam_title}' шалгалт файлаас амжилттай үүслээ!")
                            else:
                                st.warning("Шалгалтын нэрийг оруулна уу.")
                    except Exception as e:
                        st.error(f"Алдаа гарлаа: {e}")

        # 5. AI Тест генератор
        elif menu_choice == "🤖 AI тест генератор":
            st.subheader("🤖 AI ашиглан автоматаар тест бэлтгэх")
            st.write("Системд байгаа нэр томьёонууд дээр үндэслэн AI автоматаар тест үүсгэнэ.")
            
            ai_category = st.selectbox("Сэдэв сонгох:", ["Бүгд"] + list(set([v.get('category', 'Бусад') for v in st.session_state.vocab])))
            q_count = st.slider("Үүсгэх асуултын тоо:", min_value=3, max_value=10, value=5)
            ai_exam_title = st.text_input("AI Шалгалтын нэр", value=f"{ai_category}-н AI Тест")
            
            if st.button("✨ AI Тест генератордох"):
                filtered_vocab = st.session_state.vocab if ai_category == "Бүгд" else [v for v in st.session_state.vocab if v.get('category') == ai_category]
                
                if len(filtered_vocab) < 4:
                    st.warning("AI тест үүсгэхэд тухайн сэдэвт дор хаяж 4 үг байх шаардлагатай.")
                else:
                    selected_items = random.sample(filtered_vocab, min(q_count, len(filtered_vocab)))
                    generated_questions = []
                    
                    for item in selected_items:
                        wrong_items = random.sample([v for v in st.session_state.vocab if v['en'] != item['en']], min(3, len(st.session_state.vocab)-1))
                        opts = [item['mn']] + [w['mn'] for w in wrong_items]
                        random.shuffle(opts)
                        
                        generated_questions.append({
                            "question": f"'{item['en']}' гэсэн терминий монгол орчуулгыг сонгоно уу.",
                            "options": opts,
                            "correct": item['mn']
                        })
                    
                    st.session_state.ai_generated_exam = {
                        "id": str(random.randint(1000, 9999)),
                        "title": ai_exam_title,
                        "description": "AI загвараар автоматаар бэлтгэсэн тест.",
                        "questions": generated_questions
                    }
                    st.success("AI Тест амжилттай үүсгэгдлээ! Доорх хэсгээс хянана уу.")

            if 'ai_generated_exam' in st.session_state and st.session_state.ai_generated_exam:
                ai_ex = st.session_state.ai_generated_exam
                st.markdown(f"### 📋 Бэлэн болсон AI шалгалт: {ai_ex['title']}")
                for idx, q in enumerate(ai_ex['questions']):
                    st.write(f"**{idx+1}. {q['question']}** (Зөв хариу: {q['correct']})")
                
                if st.button("✅ Энэ шалгалтыг нийтэлж сурагчдад нээх"):
                    st.session_state.exams.append(ai_ex)
                    save_exams(st.session_state.exams)
                    st.session_state.ai_generated_exam = None
                    st.success("Шалгалт сурагчдад амжилттай нээгдлээ!")
                    st.rerun()

        # 6. Хэрэглэгч удирдах
        elif menu_choice == "👥 Хэрэглэгч удирдах":
            st.subheader("Шинэ хэрэглэгч бүртгэх")
            new_user = st.text_input("Логин нэр").strip().lower()
            new_pass = st.text_input("Нууц үг").strip()
            new_name = st.text_input("Бүтэн нэр").strip()
            new_role = st.selectbox("Эрх", ["Сурагч", "Багш"])
            
            if st.button("Хэрэглэгч бүртгэх"):
                if new_user and new_pass and new_name:
                    st.session_state.users[new_user] = {'password': new_pass, 'role': new_role, 'name': new_name}
                    save_users(st.session_state.users)
                    st.success(f"'{new_name}' амжилттай бүртгэгдлээ!")
                else:
                    st.warning("Бүх талбарыг бөглөнө үү.")

        # 7. Дүн шинжилгээ
        elif menu_choice == "📊 Дүн шинжилгээ (Analytics)":
            st.subheader("📈 Сурагчдын нэгдсэн дүнгийн тайлан")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("### 1. Нэр томьёоны сорилтын дүн")
                results = load_results()
                if not results:
                    st.info("Сорилтын дүн байхгүй.")
                else:
                    summary_data = []
                    for s_name, data_list in results.items():
                        summary_data.append({"Сурагч": s_name, "Өгсөн тоо": len(data_list), "Сүүлийн оноо": data_list[-1]['score']})
                    st.dataframe(pd.DataFrame(summary_data), use_container_width=True)

            with col_b:
                st.markdown("### 2. Бүлэг сэдвийн шалгалтын дүн")
                exam_res = load_exam_results()
                if not exam_res:
                    st.info("Шалгалтын дүн байхгүй.")
                else:
                    ex_summary = []
                    for s_key, ex_dict in exam_res.items():
                        for ex_title, score in ex_dict.items():
                            ex_summary.append({"Сурагч": s_key, "Шалгалт": ex_title, "Оноо": score})
                    st.dataframe(pd.DataFrame(ex_summary), use_container_width=True)

    # --- СУРАГЧИЙН ХЭСЭГ ---
    else:
        st.title(f"🎓 Сурагчийн хэсэг: {menu_choice}")

        # 1. 10 Тестийн сорилт
        if menu_choice == "📝 Нэр томьёоны сорилт (10 тест)":
            st.subheader("Физикийн нэр томьёоны сорилт (Тайлах яг 10 тест)")
            vocab_list = st.session_state.vocab
            
            if len(vocab_list) < 4:
                st.warning("Тест эхлэхэд дор хаяж 4 үг шаардлагатай.")
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
                        
                        results_db = load_results()
                        u_key = user['username']
                        if u_key not in results_db:
                            results_db[u_key] = []
                        results_db[u_key].append({"word": "10 тест", "score": ses['score']})
                        save_results(results_db)
                        
                        if st.button("Дахин өгөх"):
                            ses['active'] = False
                            st.rerun()

        # 2. Бүлэг сэдвийн шалгалт
        elif menu_choice == "📋 Бүлэг сэдвийн шалгалтууд":
            st.subheader("📋 Идэвхтэй шалгалтууд")
            exams = load_exams()
            if not exams:
                st.info("Одоогоор идэвхтэй шалгалт байхгүй байна.")
            else:
                exam_titles = [ex['title'] for ex in exams]
                chosen_exam_title = st.selectbox("Шалгалт сонгох:", exam_titles)
                selected_exam = next((ex for ex in exams if ex['title'] == chosen_exam_title), None)
                
                if selected_exam:
                    st.write(f"**Заавар:** {selected_exam['description']}")
                    with st.form(key=f"student_exam_{selected_exam['id']}"):
                        student_answers = []
                        for idx, q in enumerate(selected_exam['questions']):
                            st.markdown(f"**{idx+1}. {q['question']}**")
                            ans = st.radio("Хариулт:", q['options'], key=f"ex_q_{selected_exam['id']}_{idx}")
                            student_answers.append({"selected": ans, "correct": q['correct']})
                            
                        submit_exam = st.form_submit_button("Шалгалт дуусгах ба илгээх")
                        
                        if submit_exam:
                            score_count = sum([1 for item in student_answers if item['selected'] == item['correct']])
                            total_q = len(student_answers)
                            
                            st.success(f"Шалгалт амжилттай! Авсан оноо: {score_count}/{total_q}")
                            
                            exam_res_db = load_exam_results()
                            u_key = user['username']
                            if u_key not in exam_res_db:
                                exam_res_db[u_key] = {}
                            exam_res_db[u_key][selected_exam['title']] = f"{score_count}/{total_q}"
                            save_exam_results(exam_res_db)

        # 3. Толь бичиг
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
