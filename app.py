import streamlit as st
import pandas as pd
import json
import os
import random

# Хуудасны тохиргоо
st.set_page_config(page_title="GTIS Physics", page_icon="⚡", layout="wide")

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
        'bagsh': {'password': '1234', 'role': 'Багш', 'name': 'batbilegt.ya'},
        'suragch1': {'password': 'pass1', 'role': 'Сурагч', 'name': 'Сурагч 1'},
        'suragch2': {'password': 'pass2', 'role': 'Сурагч', 'name': 'Сурагч 2'}
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

if 'vocab' not in st.session_state:
    st.session_state.vocab = load_data()

if 'users' not in st.session_state:
    st.session_state.users = load_users()

if 'exams' not in st.session_state:
    st.session_state.exams = load_exams()

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
    st.title("⚡ Физикийн ухаалаг систем")
    st.subheader("Системд нэвтрэх")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        username_input = st.text_input("Нэвтрэх нэр (Username)").strip().lower()
        password_input = st.text_input("Нууц үг (Password)", type="password").strip()
        login_btn = st.button("Нэвтрэх")
        
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
        st.success(f"{user['name']} ({user['role']})")
        if st.button("Гарах (Log out)"):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            if "user" in st.query_params:
                del st.query_params["user"]
            st.rerun()

    st.title("⚡ Физикийн ухаалаг систем")
    
    # --- БАГШИЙН ЦЭС ---
    if user['role'] == 'Багш':
        st.header("👨‍🏫 Багшийн удирдлагын самбар")
        
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "➕ Нэг нэгээр үг нэмэх", 
            "✏️ Үг засах / 🗑️ Устгах", 
            "📁 Файлаар олон үг оруулах", 
            "📝 Шалгалт удирдах (Бүлэг сэдэв)",
            "👥 Хэрэглэгч удирдах",
            "📊 Дүн шинжилгээ (Analytics)"
        ])
        
        with tab1:
            st.subheader("Физикийн шинэ нэр томьёо нэмэх")
            category = st.selectbox("Бүлэг сэдэв", ["Механик", "Цахилгаан соронзон", "Оптик", "Термодинамик", "Бусад"], key="add_cat")
            en_word = st.text_input("Термин / Англи үг").strip()
            mn_word = st.text_input("Монгол утга").strip()
            desc_text = st.text_input("Товч тайлбар").strip()
            
            if st.button("Үг нэмэх"):
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
                    
        with tab2:
            st.subheader("Чек тэмдэглээд устгах эсвэл мөрийн дугаараар засах")
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
                        st.success(f"Нийт {deleted_count} үг амжилттай устгагдлаа!")
                        st.rerun()
                    else:
                        st.warning("Устгахын тулд ямар нэгэн үг чекэлж (чагталж) сонгоно уу.")

            with col_edit:
                st.markdown("### ✏️ Мөрийн дугаараар засах")
                edit_idx = st.number_input("Засах үгийн дугаар (Index)", min_value=1, max_value=max(len(st.session_state.vocab), 1), step=1)
                
                curr_item = st.session_state.vocab[edit_idx - 1]
                curr_cat = curr_item.get("category", "Бусад")
                cat_list = ["Механик", "Цахилгаан соронзон", "Оптик", "Термодинамик", "Бусад"]
                cat_index = cat_list.index(curr_cat) if curr_cat in cat_list else 0
                
                new_cat = st.selectbox("Шинэ бүлэг сэдэв", cat_list, index=cat_index, key="edit_cat")
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
                    st.success(f"{edit_idx}-р дугаартай үг амжилттай шинэчлэгдлээ!")
                    st.rerun()

        with tab3:
            st.subheader("Файлаар олон үг оруулах")
            st.info("Таны файлд 'category', 'en', 'mn', 'description' гэсэн баганууд байвал зохимжтой.")
            uploaded_file = st.file_uploader("Файлаа сонгох / чирж оруулах", type=['csv', 'xlsx'])
            
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                        
                    st.dataframe(df.head())
                    
                    if st.button("Эдгээр үгсийг системд хуулах"):
                        count = 0
                        for _, row in df.iterrows():
                            if 'en' in df.columns and 'mn' in df.columns:
                                cat = str(row['category']) if 'category' in df.columns and pd.notna(row['category']) else "Бусад"
                                desc = str(row['description']) if 'description' in df.columns and pd.notna(row['description']) else "-"
                                st.session_state.vocab.append({
                                    "category": cat,
                                    "en": str(row['en']),
                                    "mn": str(row['mn']),
                                    "description": desc
                                })
                                count += 1
                        save_data(st.session_state.vocab)
                        st.success(f"Нийт {count} нэр томьёо амжилттай нэмэгдлээ!")
                except Exception as e:
                    st.error(f"Алдаа гарлаа: {e}")

        with tab4:
            st.subheader("📝 Бүлэг сэдвийн шалгалт үүсгэх")
            exam_title = st.text_input("Шалгалтын нэр (Жишээ нь: Механикийн сорилт #1)").strip()
            exam_desc = st.text_area("Шалгалтын тухай заавар").strip()
            
            st.markdown("#### Асуултууд нэмэх")
            if 'temp_exam_questions' not in st.session_state:
                st.session_state.temp_exam_questions = []
                
            q_text = st.text_input("Асуулт").strip()
            opt1 = st.text_input("Сонголт A").strip()
            opt2 = st.text_input("Сонголт B").strip()
            opt3 = st.text_input("Сонголт C").strip()
            opt4 = st.text_input("Сонголт D").strip()
            correct_ans = st.selectbox("Зөв хариулт", [opt1, opt2, opt3, opt4])
            
            if st.button("Энэ асуултыг нэмэх"):
                if q_text and correct_ans:
                    st.session_state.temp_exam_questions.append({
                        "question": q_text,
                        "options": [opt1, opt2, opt3, opt4],
                        "correct": correct_ans
                    })
                    st.success("Асуулт нэмэгдлээ!")
                else:
                    st.warning("Асуулт болон зөв хариултыг заавал оруулна уу.")
            
            if st.session_state.temp_exam_questions:
                st.write(f"Одоогоор нэмэгдсэн асуултын тоо: {len(st.session_state.temp_exam_questions)}")
                if st.button("Шалгалтыг нийтлэх / хадгалах"):
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
                        st.warning("Шалгалтын нэрийг оруулна уу.")

        with tab5:
            st.subheader("Шинэ хэрэглэгч бүртгэх")
            new_user = st.text_input("Логин нэр").strip().lower()
            new_pass = st.text_input("Нууц үг").strip()
            new_name = st.text_input("Бүтэн нэр").strip()
            new_role = st.selectbox("Эрх", ["Сурагч", "Багш"], key="role_select")
            
            if st.button("Хэрэглэгч бүртгэх"):
                if new_user and new_pass and new_name:
                    st.session_state.users[new_user] = {'password': new_pass, 'role': new_role, 'name': new_name}
                    save_users(st.session_state.users)
                    st.success(f"'{new_name}' амжилттай бүртгэгдлээ!")
                else:
                    st.warning("Бүх талбарыг бөглөнө үү.")

        with tab6:
            st.subheader("📈 Сурагчдын сорилт болон шалгалтын нэгдсэн дүн")
            
            st.markdown("### 1. Шинэ үгийн сорилтын дүн (10 тест)")
            results = load_results()
            if not results:
                st.info("Шинэ үгийн сорилт өгсөн сурагч байхгүй байна.")
            else:
                summary_data = []
                for s_name, data_list in results.items():
                    total_tests = len(data_list)
                    correct_count = sum([d['score'] for d in data_list])
                    summary_data.append({"Сурагч": s_name, "Нийт өгсөн": total_tests, "Зөв хариулсан": correct_count})
                st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
                
            st.markdown("### 2. Бүлэг сэдвийн шалгалтын дүн")
            exam_res = load_exam_results()
            if not exam_res:
                st.info("Бүлэг сэдвийн шалгалт өгсөн сурагч байхгүй байна.")
            else:
                ex_summary = []
                for s_key, ex_dict in exam_res.items():
                    for ex_title, score in ex_dict.items():
                        ex_summary.append({"Сурагч": s_key, "Шалгалтын нэр": ex_title, "Оноо": score})
                st.dataframe(pd.DataFrame(ex_summary), use_container_width=True, hide_index=True)

    # --- СУРАГЧИЙН ЦЭС ---
    else:
        st.header("🎓 Сурагчийн суралцах болон сорилтын хэсэг")
        
        tab_s1, tab_s2, tab_s3 = st.tabs([
            "📝 Нэр томьёоны сорилт (10 тест)", 
            "📋 Бүлэг сэдвийн шалгалтууд", 
            "📖 Толь бичиг (Хайх & Эрэмбэлэх)"
        ])
        
        with tab_s1:
            st.subheader("Физикийн нэр томьёо сорих тест (Яг 10 асуулт)")
            vocab_list = st.session_state.vocab
            
            if len(vocab_list) < 4:
                st.warning("Тест ажиллахад дор хаяж 4 үг шаардлагатай.")
            else:
                # 10 тестээр хязгаарлах логик
                if 'exam_session' not in st.session_state:
                    st.session_state.exam_session = {
                        'active': False,
                        'questions': [],
                        'current_idx': 0,
                        'score': 0,
                        'answers_log': []
                    }
                
                ses = st.session_state.exam_session
                
                if not ses['active']:
                    if st.button("🚀 Шинэ сорилт эхлэх (10 тест)"):
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
                                # Тайлбар хэсгийг энд зориуд оруулаагүй тул харагдахгүй
                            })
                        ses['active'] = True
                        ses['questions'] = q_list
                        ses['current_idx'] = 0
                        ses['score'] = 0
                        ses['answers_log'] = []
                        st.rerun()
                else:
                    if ses['current_idx'] < len(ses['questions']):
                        q_num = ses['current_idx'] + 1
                        q = ses['questions'][ses['current_idx']]
                        
                        st.markdown(f"### Асуулт {q_num} / {len(ses['questions'])}")
                        st.markdown(f"Англи үг: **{q['en']}**")
                        # Тайлбар харагдахгүй байх шаардлагын дагуу тайлбарыг энд бичээгүй болно.
                        
                        ans = st.radio("Энэ үгийн Монгол утгыг сонгоно уу:", q['options'], key=f"radio_{q_num}")
                        
                        if st.button("Хариулах & Дараах"):
                            if ans == q['correct']:
                                ses['score'] += 1
                            ses['current_idx'] += 1
                            st.rerun()
                    else:
                        st.success(f"🎉 Сорилт амжилттай дууслаа! Таны авсан оноо: {ses['score']} / {len(ses['questions'])}")
                        
                        # Үр дүнг хадгалах
                        if 'results_db' not in st.session_state:
                            st.session_state.results_db = load_results()
                        
                        user_key = user['username']
                        if user_key not in st.session_state.results_db:
                            st.session_state.results_db[user_key] = []
                            
                        st.session_state.results_db[user_key].append({
                            "word": "10 тестын багц",
                            "score": ses['score']
                        })
                        save_results(st.session_state.results_db)
                        
                        if st.button("Дахин сорилт өгөх"):
                            ses['active'] = False
                            st.rerun()

        with tab_s2:
            st.subheader("📋 Багшийн оруулсан бүлэг сэдвийн шалгалтууд")
            exams = load_exams()
            if not exams:
                st.info("Одоогоор идэвхтэй шалгалт байхгүй байна.")
            else:
                exam_titles = [ex['title'] for ex in exams]
                chosen_exam_title = st.selectbox("Шалгалт сонгох", exam_titles)
                
                selected_exam = next((ex for ex in exams if ex['title'] == chosen_exam_title), None)
                
                if selected_exam:
                    st.write(f"**Заавар:** {selected_exam['description']}")
                    
                    with st.form(key=f"exam_form_{selected_exam['id']}_student"):
                        student_answers = []
                        for idx, q in enumerate(selected_exam['questions']):
                            st.markdown(f"**{idx+1}. {q['question']}**")
                            ans = st.radio("Хариулт сонгох:", q['options'], key=f"ex_q_{selected_exam['id']}_{idx}")
                            student_answers.append({"selected": ans, "correct": q['correct']})
                            
                        submit_exam = st.form_submit_button("Шалгалт илгээх")
                        
                        if submit_exam:
                            score_count = 0
                            for item in student_answers:
                                if item['selected'] == item['correct']:
                                    score_count += 1
                            total_q = len(student_answers)
                            percentage = round((score_count / total_q) * 100, 1) if total_q > 0 else 0
                            
                            st.success(f"Таны шалгалт амжилттай илгээгдлээ! Авсан оноо: {score_count}/{total_q} ({percentage}%)")
                            
                            # Шалгалтын дүнг хадгалах
                            if 'exam_results_db' not in st.session_state:
                                st.session_state.exam_results_db = load_exam_results()
                            
                            u_key = user['username']
                            if u_key not in st.session_state.exam_results_db:
                                st.session_state.exam_results_db[u_key] = {}
                                
                            st.session_state.exam_results_db[u_key][selected_exam['title']] = f"{score_count}/{total_q}"
                            save_exam_results(st.session_state.exam_results_db)

        with tab_s3:
            st.subheader("📖 Физикийн нэр томьёоны толь бичиг")
            search_query = st.text_input("🔍 Хайх үг (Англи эсвэл Монголоор)").strip().lower()
            sort_option = st.selectbox("Эрэмбэлэх хэлбэр:", ["Англи үгээр (A-Z)", "Монгол үгээр (А-Я)"], key="sort_dict")
            
            df_vocab = pd.DataFrame(st.session_state.vocab)
            
            if search_query:
                df_vocab = df_vocab[
                    df_vocab['en'].str.lower().str.contains(search_query) | 
                    df_vocab['mn'].str.lower().str.contains(search_query) |
                    df_vocab['description'].str.lower().str.contains(search_query)
                ]
            
            if sort_option == "Англи үгээр (A-Z)":
                df_vocab = df_vocab.sort_values(by='en', ascending=True)
            else:
                df_vocab = df_vocab.sort_values(by='mn', ascending=True)
                
            st.write(f"Нийт {len(df_vocab)} үг олдлоо.")
            st.dataframe(df_vocab, use_container_width=True, hide_index=True)
