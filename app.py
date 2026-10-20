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
QUIZ_RESULT_FILE = "quiz_result_data.json"

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

# Session state
if 'vocab' not in st.session_state:
    st.session_state.vocab = load_json(VOCAB_FILE, [])
if 'users' not in st.session_state:
    st.session_state.users = load_json(USER_FILE, {
        'bagsh': {'password': '1234', 'role': 'Багш', 'name': 'Багш', 'class': 'Бүгд'}
    })
if 'classes' not in st.session_state:
    st.session_state.classes = load_json(CLASS_FILE, [])
if 'exams' not in st.session_state:
    st.session_state.exams = load_json(EXAM_FILE, [])
if 'homeworks' not in st.session_state:
    st.session_state.homeworks = load_json(HOMEWORK_FILE, [])
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None

# ---- НЭВТРЭХ ХЭСЭГ ----
if not st.session_state.logged_in:
    st.title("⚡ Физикийн ухаалаг сургалтын систем (GTIS)")
    st.subheader("Системд нэвтрэх")
    
    tab_login, tab_register = st.tabs(["🔑 Нэвтрэх", "📝 Сурагч бүртгүүлэх"])
    
    with tab_login:
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
                    st.rerun()
                else:
                    st.error("Нэвтрэх нэр эсвэл нууц үг буруу байна!")
                    
    with tab_register:
        st.markdown("### Сурагч өөрөө бүртгүүлэх")
        if not st.session_state.classes:
            st.warning("Багш одоогоор анги үүсгээгүй байна. Багштайгаа холбогдоно уу.")
        else:
            reg_user = st.text_input("Шинэ Username").strip().lower()
            reg_pass = st.text_input("Нууц үг", type="password").strip()
            reg_name = st.text_input("Овог, нэр").strip()
            reg_class = st.selectbox("Өөрийн анги / бүлгээ сонгоно уу:", st.session_state.classes)
            
            if st.button("Бүртгүүлэх"):
                if reg_user and reg_pass and reg_name:
                    if reg_user in st.session_state.users:
                        st.error("Энэ username аль хэдийн бүртгэгдсэн байна.")
                    else:
                        st.session_state.users[reg_user] = {
                            'password': reg_pass,
                            'role': 'Сурагч',
                            'name': reg_name,
                            'class': reg_class
                        }
                        save_json(USER_FILE, st.session_state.users)
                        st.success("Амжилттай бүртгэгдлээ! Одоо 'Нэвтрэх' хэсгээр нэвтэрнэ үү.")
                else:
                    st.warning("Бүх талбарыг бүрэн бөглөнө үү.")

# ---- НЭВТЭРСНИЙ ДАРААХ ХЭСЭГ ----
else:
    user = st.session_state.user_info
    
    with st.sidebar:
        st.title("⚡ Физикийн систем")
        # Зөвхөн багшийн нэр гарна
        disp_name = user['name'] if user['role'] == 'Багш' else f"{user['name']} ({user.get('class', '')})"
        st.success(f"👤 **{disp_name}**\n\nЭрх: **{user['role']}**")
        
        if user['role'] == 'Багш':
            menu_choice = st.radio(
                "📌 Багшийн цэс:",
                [
                    "🏫 Ангиуд удирдах",
                    "👥 Сурагч & Нууц үг удирдах",
                    "➕ Үгсийн сан ба Дэд сэдэв",
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
                elif new_c in st.session_state.classes:
                    st.warning("Энэ анги аль хэдийн бүртгэгдсэн байна.")
            
            st.divider()
            st.markdown("### Бүртгэлтэй ангиуд")
            if not st.session_state.classes:
                st.info("Анги байхгүй байна.")
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

        elif menu_choice == "👥 Сурагч & Нууц үг удирдах":
            st.subheader("👥 Сурагчдын бүртгэл удирдах")
            with st.expander("➕ Шинэ сурагч бүртгэх"):
                if not st.session_state.classes:
                    st.warning("Эхлээд анги үүсгэнэ үү.")
                else:
                    s_user = st.text_input("Username").strip().lower()
                    s_pass = st.text_input("Нууц үг", type="password").strip()
                    s_name = st.text_input("Сурагчийн нэр").strip()
                    s_class = st.selectbox("Анги", st.session_state.classes)
                    if st.button("Бүртгэх"):
                        if s_user and s_pass and s_name:
                            st.session_state.users[s_user] = {'password': s_pass, 'role': 'Сурагч', 'name': s_name, 'class': s_class}
                            save_json(USER_FILE, st.session_state.users)
                            st.success("Амжилттай бүртгэгдлээ!")
                            st.rerun()

            student_list = {k: v for k, v in st.session_state.users.items() if v['role'] == 'Сурагч'}
            for s_username, s_data in student_list.items():
                with st.container(border=True):
                    st.write(f"👤 **{s_data['name']}** | Username: `{s_username}` | Анги: **{s_data.get('class')}**")
                    c1, c2, c3 = st.columns([2, 2, 1])
                    with c1:
                        n_name = st.text_input("Нэр солих", value=s_data['name'], key=f"n_{s_username}")
                    with c2:
                        n_pass = st.text_input("Шинэ нууц үг", type="password", key=f"p_{s_username}")
                    with c3:
                        st.write("")
                        st.write("")
                        if st.button("💾 Хадгалах", key=f"s_{s_username}"):
                            st.session_state.users[s_username]['name'] = n_name
                            if n_pass:
                                st.session_state.users[s_username]['password'] = n_pass
                            save_json(USER_FILE, st.session_state.users)
                            st.success("Шинэчлэгдлээ!")
                            st.rerun()
                    if st.button("🗑️ Устгах", key=f"del_u_{s_username}"):
                        del st.session_state.users[s_username]
                        save_json(USER_FILE, st.session_state.users)
                        st.rerun()

        elif menu_choice == "➕ Үгсийн сан ба Дэд сэдэв":
            st.subheader("📚 Үгсийн сан ба Дэд сэдвүүд удирдах")
            t1, t2 = st.tabs(["Үг нэмэх (Үндсэн & Дэд сэдэв)", "Файлаар оруулах"])
            
            with t1:
                cat = st.text_input("Үндсэн бүлэг сэдэв (Жишээ нь: Оптик)").strip()
                sub_cat = st.text_input("Дэд сэдэв (Жишээ нь: Гэрлийн хугарал)").strip()
                en = st.text_input("Англи термин").strip()
                mn = st.text_input("Монгол утга").strip()
                desc = st.text_area("Тайлбар").strip()
                
                if st.button("Үг нэмэх"):
                    if cat and sub_cat and en and mn:
                        st.session_state.vocab.append({
                            "category": cat,
                            "sub_category": sub_cat,
                            "en": en,
                            "mn": mn,
                            "description": desc or "-"
                        })
                        save_json(VOCAB_FILE, st.session_state.vocab)
                        st.success("Үг нэмэгдлээ!")
                        st.rerun()
                    else:
                        st.warning("Бүх шаардлагатай талбарыг бөглөнө үү.")
                
                if st.session_state.vocab:
                    st.divider("Бүртгэлтэй үгс:")
                    st.dataframe(pd.DataFrame(st.session_state.vocab), use_container_width=True)

            with t2:
                up = st.file_uploader("Файл сонгох (category, sub_category, en, mn, description)", type=['csv', 'xlsx'])
                if up:
                    df_up = pd.read_csv(up) if up.name.endswith('.csv') else pd.read_excel(up)
                    if st.button("Файлаас хуулах"):
                        for _, r in df_up.iterrows():
                            st.session_state.vocab.append({
                                "category": str(r.get('category', 'Бусад')),
                                "sub_category": str(r.get('sub_category', 'Дэд сэдэв')),
                                "en": str(r['en']),
                                "mn": str(r['mn']),
                                "description": str(r.get('description', '-'))
                            })
                        save_json(VOCAB_FILE, st.session_state.vocab)
                        st.success("Амжилттай импортлогдлоо!")
                        st.rerun()

        elif menu_choice == "📚 Гэрийн даалгавар өгөх":
            st.subheader("📚 Ангид даалгавар өгөх")
            hw_title = st.text_input("Гарчиг")
            hw_desc = st.text_area("Даалгаврын утга")
            target_cls = st.selectbox("Анги", ["Бүгд"] + st.session_state.classes)
            deadline = st.date_input("Дуусах хугацаа")
            if st.button("Даалгавар илгээх"):
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
                count = st.slider("Асуултын тоо", 3, 10, 5)
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
            st.subheader("📝 Нэр томьёоны сорилт (Хугацаатай, 10 асуулт нэг дор)")
            vocab_list = st.session_state.vocab
            
            if len(vocab_list) < 4:
                st.warning("Багш хангалттай үг оруулаагүй байна.")
            else:
                # Дэд сэдвээр шүүх сонголт
                sub_cats = list(set([v.get('sub_category', 'Бүгд') for v in vocab_list]))
                chosen_sub = st.selectbox("Дэд сэдэв сонгох:", ["Бүгд"] + sub_cats)
                
                filtered_vocab = vocab_list if chosen_sub == "Бүгд" else [v for v in vocab_list if v.get('sub_category') == chosen_sub]
                
                if len(filtered_vocab) < 4:
                    st.warning("Энэ дээд сэдвэд хангалттай үг алга.")
                else:
                    if st.button("🚀 Сорилт эхлэх (3 минут)"):
                        # 3 Монгол->Англи (3 ширхэг), 7 Англи->Монгол (7 ширхэг)
                        sample_size = min(10, len(filtered_vocab))
                        sampled = random.sample(filtered_vocab, sample_size)
                        
                        quiz_items = []
                        # Эхний 3 нь Монгол -> Англи
                        mn_en_count = min(3, len(sampled))
                        for i in range(mn_en_count):
                            item = sampled[i]
                            wrongs = random.sample([v['en'] for v in filtered_vocab if v['en'] != item['en']], min(3, len(filtered_vocab)-1))
                            opts = [item['en']] + wrongs
                            random.shuffle(opts)
                            quiz_items.append({
                                "type": "mn_en",
                                "question": f"Монгол утгаас Англи терминийг сонгоно уу: '{item['mn']}'",
                                "options": opts,
                                "correct": item['en']
                            })
                        
                        # Үлдсэн нь Англи -> Монгол
                        for i in range(mn_en_count, len(sampled)):
                            item = sampled[i]
                            wrongs = random.sample([v['mn'] for v in filtered_vocab if v['en'] != item['en']], min(3, len(filtered_vocab)-1))
                            opts = [item['mn']] + wrongs
                            random.shuffle(opts)
                            quiz_items.append({
                                "type": "en_mn",
                                "question": f"Англи терминий Монгол утгыг сонгоно уу: '{item['en']}'",
                                "options": opts,
                                "correct": item['mn']
                            })
                        
                        st.session_state.active_quiz = quiz_items
                        st.rerun()
                    
                    if 'active_quiz' in st.session_state:
                        st.markdown("⏳ **Сорилт явагдаж байна... Бүх асуултад хариулаад доорх товчийг дарна уу.**")
                        with st.form("quiz_form"):
                            user_answers = []
                            for idx, q in enumerate(st.session_state.active_quiz):
                                st.markdown(f"**{idx+1}. {q['question']}**")
                                ans = st.radio("Сонгох:", q['options'], key=f"q_ans_{idx}")
                                user_answers.append((ans, q['correct']))
                            
                            sub_quiz = st.form_submit_button("Сорилт дуусгах & Дүн харах")
                            if sub_quiz:
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
