import streamlit as st
import pandas as pd
import json
import os
import random
import io

# Хуудасны тохиргоо
st.set_page_config(page_title="GTIS Advanced Physics System", page_icon="⚡", layout="wide")

# Файлын нэрс
VOCAB_FILE = "vocab_data.json"
USER_FILE = "user_data.json"
EXAM_FILE = "exam_data.json"
CLASS_FILE = "class_data.json"
HOMEWORK_FILE = "homework_data.json"
HW_RESULT_FILE = "hw_result_data.json"
SESSION_FILE = "session_data.json"

# --- ФУНКЦҮҮД ---
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

# Session state ба Нэвтрэлтийн төлөвийг хадгалах
if 'vocab' not in st.session_state:
    st.session_state.vocab = load_json(VOCAB_FILE, [])

if 'users' not in st.session_state:
    st.session_state.users = load_json(USER_FILE, {
        'admin': {'password': '123', 'role': 'Багш', 'name': 'Админ Багш', 'class': 'Бүгд'}
    })

if 'classes' not in st.session_state:
    st.session_state.classes = load_json(CLASS_FILE, [])

if 'exams' not in st.session_state:
    st.session_state.exams = load_json(EXAM_FILE, [])

if 'homeworks' not in st.session_state:
    st.session_state.homeworks = load_json(HOMEWORK_FILE, [])

# Рефреш хийхэд нэвтрэлт арилахгүй байх логик
saved_session = load_json(SESSION_FILE, None)
if 'logged_in' not in st.session_state:
    if saved_session and saved_session.get('username') in st.session_state.users:
        st.session_state.logged_in = True
        st.session_state.user_info = st.session_state.users[saved_session['username']]
        st.session_state.user_info['username'] = saved_session['username']
    else:
        st.session_state.logged_in = False
        st.session_state.user_info = None

# ---- НЭВТРЭХ ХЭСЭГ ----
if not st.session_state.logged_in:
    st.title("⚡ Физикийн ухаалаг сургалтын систем (GTIS)")
    st.subheader("Системд нэвтрэх")
    
    tab_login, tab_register = st.tabs(["🔑 Нэвтрэх", "📝 Сурагч өөрөө бүртгүүлэх"])
    
    with tab_login:
        col1, _ = st.columns([1, 2])
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
                    save_json(SESSION_FILE, {'username': username_input})
                    st.rerun()
                else:
                    st.error("Нэвтрэх нэр эсвэл нууц үг буруу байна!")
                    
    with tab_register:
        st.markdown("### Сурагч өөрөө бүртгүүлэх хэсэг")
        reg_user = st.text_input("Шинэ Username").strip().lower()
        reg_pass = st.text_input("Нууц үг", type="password").strip()
        reg_name = st.text_input("Овог, нэр").strip()
        
        cls_options = st.session_state.classes if st.session_state.classes else ["Анги хараахан үүсээгүй"]
        reg_class = st.selectbox("Өөрийн анги / бүлгээ сонгоно уу:", cls_options)
        
        if st.button("Бүртгүүлэх"):
            if reg_user and reg_pass and reg_name:
                if reg_user in st.session_state.users:
                    st.error("Энэ username аль хэдийн бүртгэгдсэн байна.")
                else:
                    st.session_state.users[reg_user] = {
                        'password': reg_pass,
                        'role': 'Сурагч',
                        'name': reg_name,
                        'class': reg_class if reg_class != "Анги хараахан үүсээгүй" else "Тодорхойгүй"
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
        st.success(f"👤 **{user['name']}**\n\nЭрх: **{user['role']}**\nАнги: **{user.get('class', '-')}**")
        
        if user['role'] == 'Багш':
            menu_choice = st.radio(
                "📌 Багшийн цэс:",
                [
                    "🏫 Ангиуд удирдах",
                    "👥 Багш & Сурагчдын бүртгэл удирдах",
                    "➕ Үгсийн сан (5 баганатай импорт)",
                    "📚 Гэрийн даалгавар өгөх",
                    "📝 Шалгалт удирдах",
                    "🤖 AI тест генератор",
                    "📊 Дүн анализ & Excel"
                ]
            )
        else:
            menu_choice = st.radio(
                "📌 Сурагчийн цэс:",
                [
                    "📝 Нэр томьёоны сорилт (10 тест)",
                    "📚 Миний гэрийн даалгавар",
                    "📋 Бүлэг сэдвийн шалгалтууд",
                    "📖 Толь бичиг"
                ]
            )

        st.divider()
        if st.button("🚪 Гарах (Log out)", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
            st.rerun()

    # --- БАГШИЙН ЦЭС ---
    if user['role'] == 'Багш':
        if menu_choice == "🏫 Ангиуд удирдах":
            st.subheader("🏫 Анги / Бүлгүүдийг удирдах")
            new_c = st.text_input("Шинэ бүлгийн нэр (Жишээ нь: 6а, 6б, 7а)").strip()
            if st.button("Анги нэмэх"):
                if new_c and new_c not in st.session_state.classes:
                    st.session_state.classes.append(new_c)
                    st.session_state.classes.sort()
                    save_json(CLASS_FILE, st.session_state.classes)
                    st.success(f"'{new_c}' анги нэмэгдлээ!")
                    st.rerun()
            
            st.divider()
            st.markdown("### Бүртгэлтэй ангиуд")
            if not st.session_state.classes:
                st.info("Одоогоор бүртгэлтэй анги байхгүй байна.")
            else:
                for idx, c_name in enumerate(st.session_state.classes):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.write(f"📌 **{c_name}**")
                    with c2:
                        if st.button("🗑️ Устгах", key=f"del_cls_{idx}"):
                            st.session_state.classes.remove(c_name)
                            save_json(CLASS_FILE, st.session_state.classes)
                            st.rerun()

        elif menu_choice == "👥 Багш & Сурагчдын бүртгэл удирдах":
            st.subheader("👥 Хэрэглэгчдийн бүртгэл болон Username, Нэр, Нууц үг засах")
            
            t_user1, t_user2 = st.tabs(["➕ Шинэ Багш / Сурагч нэмэх", "⚙️ Бүртгэлтэй хэрэглэгчдийг засах"])
            
            with t_user1:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("#### 👨‍🏫 Шинэ Багш нэмэх")
                    b_user = st.text_input("Багшийн Username", key="b_u").strip().lower()
                    b_pass = st.text_input("Нууц үг", type="password", key="b_p").strip()
                    b_name = st.text_input("Багшийн бүтэн нэр", key="b_n").strip()
                    if st.button("Багш нэмэх"):
                        if b_user and b_pass and b_name:
                            if b_user in st.session_state.users:
                                st.error("Энэ username аль хэдийн бүртгэгдсэн байна!")
                            else:
                                st.session_state.users[b_user] = {'password': b_pass, 'role': 'Багш', 'name': b_name, 'class': 'Бүгд'}
                                save_json(USER_FILE, st.session_state.users)
                                st.success(f"Багш '{b_name}' амжилттай нэмэгдлээ!")
                                st.rerun()
                
                with col_b:
                    st.markdown("#### 🧑‍🎓 Шинэ Сурагч нэмэх")
                    s_user = st.text_input("Сурагчийн Username", key="s_u").strip().lower()
                    s_pass = st.text_input("Нууц үг", type="password", key="s_p").strip()
                    s_name = st.text_input("Сурагчийн нэр", key="s_n").strip()
                    s_cls = st.selectbox("Анги сонгох", st.session_state.classes if st.session_state.classes else ["Ангигүй"])
                    if st.button("Сурагч нэмэх"):
                        if s_user and s_pass and s_name:
                            if s_user in st.session_state.users:
                                st.error("Энэ username аль хэдийн бүртгэгдсэн байна!")
                            else:
                                st.session_state.users[s_user] = {'password': s_pass, 'role': 'Сурагч', 'name': s_name, 'class': s_cls}
                                save_json(USER_FILE, st.session_state.users)
                                st.success(f"Сурагч '{s_name}' амжилттай нэмэгдлээ!")
                                st.rerun()

            with t_user2:
                st.markdown("#### Бүртгэлтэй хэрэглэгчдийн мэдээлэл засах (Username, Нэр, Нууц үг)")
                for u_key, u_val in list(st.session_state.users.items()):
                    with st.container(border=True):
                        st.write(f"🎭 **{u_val['role']}** | Одоогийн Username: `{u_key}` | Нэр: **{u_val['name']}**")
                        c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                        with c1:
                            new_username = st.text_input("Username засах", value=u_key, key=f"eu_{u_key}").strip().lower()
                        with c2:
                            edit_name = st.text_input("Шинэ нэр", value=u_val['name'], key=f"en_{u_key}")
                        with c3:
                            edit_pass = st.text_input("Шинэ нууц үг", type="password", placeholder="Солих бол бичнэ үү", key=f"ep_{u_key}")
                        
                        col_btn1, col_btn2 = st.columns([1, 1])
                        with col_btn1:
                            if st.button("💾 Хадгалах", key=f"save_{u_key}"):
                                if new_username and new_username != u_key:
                                    if new_username in st.session_state.users:
                                        st.error("Энэ username аль хэдийн бүртгэгдсэн байна!")
                                    else:
                                        # Шинэ username руу өгөгдлийг шилжүүлж хуучин key-г устгах
                                        st.session_state.users[new_username] = st.session_state.users[u_key]
                                        del st.session_state.users[u_key]
                                        u_key = new_username
                                
                                st.session_state.users[u_key]['name'] = edit_name
                                if edit_pass:
                                    st.session_state.users[u_key]['password'] = edit_pass
                                save_json(USER_FILE, st.session_state.users)
                                st.success("Мэдээлэл шинэчлэгдлээ!")
                                st.rerun()
                        with col_btn2:
                            if st.button("🗑️ Устгах", key=f"del_{u_key}"):
                                if len(st.session_state.users) <= 1:
                                    st.warning("Хамгийн сүүлийн хэрэглэгчийг устгах боломжгүй.")
                                else:
                                    del st.session_state.users[u_key]
                                    save_json(USER_FILE, st.session_state.users)
                                    st.success("Хэрэглэгч устгагдлаа!")
                                    st.rerun()

        elif menu_choice == "➕ Үгсийн сан (5 баганатай импорт)":
            st.subheader("📚 Үгсийн сан удирдах (Гаднаас 5 баганаар оруулах)")
            
            st.info("💡 **Файлын 5 баганын бүтэц заавал дараах нэртэй байна:**\n\n1. `category` (Бүлэг сэдэв)\n2. `sub_category` (Дэд сэдэв)\n3. `en` (Англи үг)\n4. `mn` (Монгол утга)\n5. `description` (Тайлбар)")
            
            t_v1, t_v2 = st.tabs(["Файлаар оруулах (CSV / Excel)", "Гараар нэмэх & Бааз цэвэрлэх"])
            
            with t_v1:
                up_file = st.file_uploader("5 баганатай CSV эсвэл Excel файл оруулна уу", type=['csv', 'xlsx'])
                if up_file:
                    try:
                        df_import = pd.read_csv(up_file) if up_file.name.endswith('.csv') else pd.read_excel(up_file)
                        req_cols = ['category', 'sub_category', 'en', 'mn', 'description']
                        
                        missing_cols = [c for c in req_cols if c not in df_import.columns]
                        if missing_cols:
                            st.error(f"Файлд шаардлагатай дараах баганууд байхгүй байна: {missing_cols}")
                        else:
                            st.dataframe(df_import.head(), use_container_width=True)
                            if st.button("📥 Файлын үгсийг бааз руу хуулах"):
                                added_count = 0
                                for _, r in df_import.iterrows():
                                    st.session_state.vocab.append({
                                        "category": str(r['category']),
                                        "sub_category": str(r['sub_category']),
                                        "en": str(r['en']),
                                        "mn": str(r['mn']),
                                        "description": str(r['description'])
                                    })
                                    added_count += 1
                                save_json(VOCAB_FILE, st.session_state.vocab)
                                st.success(f"Нийт {added_count} үг амжилттай нэмэгдлээ!")
                                st.rerun()
                    except Exception as e:
                        st.error(f"Файл уншихад алдаа гарлаа: {e}")

            with t_v2:
                c1, c2 = st.columns(2)
                with c1:
                    cat = st.text_input("Бүлэг сэдэв").strip()
                    sub_cat = st.text_input("Дэд сэдэв").strip()
                    en = st.text_input("Англи үг").strip()
                    mn = st.text_input("Монгол утга").strip()
                    desc = st.text_area("Тайлбар").strip()
                    if st.button("Гараар үг нэмэх"):
                        if cat and sub_cat and en and mn:
                            st.session_state.vocab.append({
                                "category": cat, "sub_category": sub_cat, "en": en, "mn": mn, "description": desc or "-"
                            })
                            save_json(VOCAB_FILE, st.session_state.vocab)
                            st.success("Үг нэмэгдлээ!")
                            st.rerun()
                
                with c2:
                    st.markdown("#### Баазад байгаа үгс цэвэрлэх")
                    st.write(f"Одоогийн үгсийн тоо: **{len(st.session_state.vocab)}**")
                    if st.button("⚠️ Бүх үгийг устгаж бааз цэвэрлэх"):
                        st.session_state.vocab = []
                        save_json(VOCAB_FILE, st.session_state.vocab)
                        st.success("Бааз бүрэн цэвэрлэгдлээ!")
                        st.rerun()

            if st.session_state.vocab:
                st.divider()
                st.markdown("### 📋 Баазад байгаа бүх үгс")
                st.dataframe(pd.DataFrame(st.session_state.vocab), use_container_width=True)

        elif menu_choice == "📚 Гэрийн даалгавар өгөх":
            st.subheader("📚 Ангид даалгавар өгөх")
            hw_title = st.text_input("Даалгаврын гарчиг")
            hw_desc = st.text_area("Даалгаврын заавар")
            target_cls = st.selectbox("Аль ангид өгөх вэ?", ["Бүгд"] + st.session_state.classes)
            deadline = st.date_input("Дуусах хугацаа")
            if st.button("Даалгавар нийтлэх"):
                if hw_title:
                    st.session_state.homeworks.append({
                        "id": str(random.randint(1000, 9999)),
                        "title": hw_title, "description": hw_desc, "target_class": target_cls, "deadline": str(deadline)
                    })
                    save_json(HOMEWORK_FILE, st.session_state.homeworks)
                    st.success("Даалгавар нийтлэгдлээ!")

        elif menu_choice == "📝 Шалгалт удирдах":
            st.subheader("📝 Шалгалт үүсгэх")
            ex_title = st.text_input("Шалгалтын нэр")
            ex_desc = st.text_area("Заавар")
            if 'temp_q' not in st.session_state: st.session_state.temp_q = []
            q = st.text_input("Асуулт")
            o1, o2, o3, o4 = st.text_input("A"), st.text_input("B"), st.text_input("C"), st.text_input("D")
            correct = st.selectbox("Зөв хариулт", [o1, o2, o3, o4] if o1 else ["-"])
            if st.button("Асуулт нэмэх"):
                if q and correct != "-":
                    st.session_state.temp_q.append({"question": q, "options": [o1, o2, o3, o4], "correct": correct})
                    st.success("Нэмэгдлээ!")
            if st.session_state.temp_q and st.button("Шалгалт нийтлэх"):
                st.session_state.exams.append({"title": ex_title, "description": ex_desc, "questions": st.session_state.temp_q})
                save_json(EXAM_FILE, st.session_state.exams)
                st.session_state.temp_q = []
                st.success("Нийтлэгдлээ!")

        elif menu_choice == "🤖 AI тест генератор":
            st.subheader("🤖 AI тест үүсгэх")
            if len(st.session_state.vocab) >= 4:
                count = st.slider("Асуултын тоо", 3, 10, min(5, len(st.session_state.vocab)))
                if st.button("AI Тест үүсгэх"):
                    selected = random.sample(st.session_state.vocab, min(count, len(st.session_state.vocab)))
                    q_list = []
                    for item in selected:
                        wrong = random.sample([v['mn'] for v in st.session_state.vocab if v['en'] != item['en']], 3)
                        opts = [item['mn']] + wrong
                        random.shuffle(opts)
                        q_list.append({"question": f"'{item['en']}' утга?", "options": opts, "correct": item['mn']})
                    st.session_state.exams.append({"title": "AI Сорилт", "description": "Автомат", "questions": q_list})
                    save_json(EXAM_FILE, st.session_state.exams)
                    st.success("Үүслээ!")

        elif menu_choice == "📊 Дүн анализ & Excel":
            st.subheader("📊 Дүн шинжилгээ")
            hw_res = load_json(HW_RESULT_FILE, {})
            if hw_res:
                rows = []
                for s_u, sub in hw_res.items():
                    u_cls = st.session_state.users.get(s_u, {}).get('class', '-')
                    u_name = st.session_state.users.get(s_u, {}).get('name', s_u)
                    for h_t, det in sub.items():
                        rows.append({"Бүлэг": u_cls, "Сурагч": u_name, "Даалгавар": h_t, "Хариулт": det['answer'], "Огноо": det['date']})
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True)
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Analytics')
                st.download_button("📥 Excel татах", data=output.getvalue(), file_name="report.xlsx")
            else:
                st.info("Үр дүн байхгүй.")

    # --- СУРАГЧИЙН ЦЭС ---
    else:
        if menu_choice == "📝 Нэр томьёоны сорилт (10 тест)":
            st.subheader("📝 Нэр томьёоны сорилт (10 асуулт нэг дор)")
            vocab_list = st.session_state.vocab
            
            if len(vocab_list) < 4:
                st.warning("Багш хангалттай үг оруулаагүй байна.")
            else:
                sub_cats = list(set([v.get('sub_category', 'Бүгд') for v in vocab_list]))
                chosen_sub = st.selectbox("Дэд сэдэв сонгох:", ["Бүгд"] + sub_cats)
                
                filtered_vocab = vocab_list if chosen_sub == "Бүгд" else [v for v in vocab_list if v.get('sub_category') == chosen_sub]
                
                if len(filtered_vocab) < 4:
                    st.warning("Энэ дэд сэдэвт хангалттай үг байхгүй байна.")
                else:
                    if st.button("🚀 Сорилт эхлэх"):
                        sample_size = min(10, len(filtered_vocab))
                        sampled = random.sample(filtered_vocab, sample_size)
                        
                        quiz_items = []
                        mn_en_count = min(3, len(sampled))
                        
                        # 3 ширхэг Монгол -> Англи
                        for i in range(mn_en_count):
                            item = sampled[i]
                            wrongs = random.sample([v['en'] for v in filtered_vocab if v['en'] != item['en']], min(3, len(filtered_vocab)-1))
                            opts = [item['en']] + wrongs
                            random.shuffle(opts)
                            quiz_items.append({
                                "question": f"Монгол утга: '{item['mn']}' -> Англи терминийг сонгоно уу:",
                                "options": opts,
                                "correct": item['en']
                            })
                        
                        # 7 ширхэг Англи -> Монгол
                        for i in range(mn_en_count, len(sampled)):
                            item = sampled[i]
                            wrongs = random.sample([v['mn'] for v in filtered_vocab if v['en'] != item['en']], min(3, len(filtered_vocab)-1))
                            opts = [item['mn']] + wrongs
                            random.shuffle(opts)
                            quiz_items.append({
                                "question": f"Англи термин: '{item['en']}' -> Монгол утгыг сонгоно уу:",
                                "options": opts,
                                "correct": item['mn']
                            })
                        
                        st.session_state.active_quiz = quiz_items
                        st.rerun()
                    
                    if 'active_quiz' in st.session_state:
                        with st.form("quiz_form"):
                            user_answers = []
                            for idx, q in enumerate(st.session_state.active_quiz):
                                st.markdown(f"**{idx+1}. {q['question']}**")
                                ans = st.radio("Сонгох:", q['options'], key=f"q_ans_{idx}")
                                user_answers.append((ans, q['correct']))
                            
                            if st.form_submit_button("Сорилт дуусгах"):
                                score = sum(1 for a, c in user_answers if a == c)
                                st.success(f"🎉 Сорилт дууслаа! Таны авсан оноо: {score} / {len(st.session_state.active_quiz)}")
                                del st.session_state.active_quiz

        elif menu_choice == "📚 Миний гэрийн даалгавар":
            st.subheader("📚 Миний гэрийн даалгаврууд")
            homeworks = st.session_state.get('homeworks', [])
            my_cls = user.get('class', '')
            my_hw = [h for h in homeworks if h['target_class'] == "Бүгд" or h['target_class'] == my_cls]
            if not my_hw:
                st.info("Даалгавар байхгүй байна.")
            else:
                for hw in my_hw:
                    with st.container(border=True):
                        st.markdown(f"### 📌 {hw['title']}")
                        st.write(hw['description'])
                        st.caption(f"Хугацаа: {hw['deadline']}")
                        ans = st.text_area("Хариулт:", key=f"ans_{hw['id']}")
                        if st.button("Илгээх", key=f"btn_h_{hw['id']}"):
                            res = load_json(HW_RESULT_FILE, {})
                            if user['username'] not in res: res[user['username']] = {}
                            res[user['username']][hw['title']] = {"answer": ans, "date": str(pd.Timestamp.now().date())}
                            save_json(HW_RESULT_FILE, res)
                            st.success("Илгээгдлээ!")

        elif menu_choice == "📋 Бүлэг сэдвийн шалгалтууд":
            exams = st.session_state.get('exams', [])
            if not exams:
                st.info("Шалгалт алга.")
            else:
                chosen = st.selectbox("Шалгалт сонгох", [e['title'] for e in exams])
                ex = next(e for e in exams if e['title'] == chosen)
                with st.form("ex_f"):
                    ans_list = []
                    for i, q in enumerate(ex['questions']):
                        st.markdown(f"**{i+1}. {q['question']}**")
                        s = st.radio("Сонголт:", q['options'], key=f"ex_q_{i}")
                        ans_list.append((s, q['correct']))
                    if st.form_submit_button("Илгээх"):
                        sc = sum(1 for s, c in ans_list if s == c)
                        st.success(f"Оноо: {sc}/{len(ans_list)}")

        elif menu_choice == "📖 Толь бичиг":
            st.subheader("📖 Толь бичиг")
            if st.session_state.vocab:
                st.dataframe(pd.DataFrame(st.session_state.vocab), use_container_width=True, hide_index=True)
            else:
                st.info("Толь бичиг хоосон байна.")
