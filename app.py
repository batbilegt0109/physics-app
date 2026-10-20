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
RESULT_FILE = "result_data.json"
EXAM_FILE = "exam_data.json"
EXAM_RESULT_FILE = "exam_result_data.json"
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

# Session state инициализаци
if 'vocab' not in st.session_state:
    st.session_state.vocab = load_json(VOCAB_FILE, [])

if 'users' not in st.session_state:
    st.session_state.users = load_json(USER_FILE, {
        'bagsh': {'password': '1234', 'role': 'Багш', 'name': 'Үндсэн багш', 'grade': 'Бүгд', 'group': 'Бүгд'}
    })

if 'classes' not in st.session_state:
    st.session_state.classes = load_json(CLASS_FILE, ["6а", "6б", "6в", "7а", "7б", "10а"])

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
        st.success(f"👤 {user['name']}\n\nАнги: **{user.get('class', 'Багш')}**\nЭрх: **{user['role']}**")
        
        if user['role'] == 'Багш':
            menu_choice = st.radio(
                "📌 Багшийн цэс:",
                [
                    "🏫 Ангиуд удирдах",
                    "👥 Сурагчдын жагсаалт",
                    "➕ Үгсийн сан удирдах",
                    "📚 Гэрийн даалгавар өгөх",
                    "📝 Шалгалт удирдах",
                    "🤖 AI тест генератор",
                    "📊 Анги бүлгийн дүн анализ & Excel"
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
            st.subheader("🏫 Анги / Бүлгүүд үүсгэх (Жишээ нь: 6а, 6б, 6в, 7а)")
            new_c = st.text_input("Шинэ бүлгийн нэр").strip()
            if st.button("Анги нэмэх"):
                if new_c and new_c not in st.session_state.classes:
                    st.session_state.classes.append(new_c)
                    st.session_state.classes.sort()
                    save_json(CLASS_FILE, st.session_state.classes)
                    st.success(f"'{new_c}' анги амжилттай нэмэгдлээ!")
                    st.rerun()
            st.write("Бүртгэлтэй ангиуд:", ", ".join([f"**{c}**" for c in st.session_state.classes]))

        elif menu_choice == "👥 Сурагчдын жагсаалт":
            st.subheader("👥 Бүртгэлтэй сурагчдын жагсаалт")
            s_list = {k: v for k, v in st.session_state.users.items() if v['role'] == 'Сурагч'}
            if not s_list:
                st.info("Сурагч бүртгэгдээгүй байна.")
            else:
                rows = [{"Username": k, "Нэр": v['name'], "Бүлэг/Анги": v.get('class', '-')} for k, v in s_list.items()]
                df_s = pd.DataFrame(rows)
                st.dataframe(df_s, use_container_width=True)

        elif menu_choice == "➕ Үгсийн сан удирдах":
            st.subheader("📚 Үгсийн сан")
            cat = st.text_input("Бүлэг сэдэв (Оптик, Механик г.м)")
            en = st.text_input("Англи термин")
            mn = st.text_input("Монгол утга")
            desc = st.text_input("Товч тайлбар")
            if st.button("Үг нэмэх"):
                if cat and en and mn:
                    st.session_state.vocab.append({"category": cat, "en": en, "mn": mn, "description": desc or "-"})
                    save_json(VOCAB_FILE, st.session_state.vocab)
                    st.success("Үг нэмэгдлээ!")
                    st.rerun()
            st.dataframe(pd.DataFrame(st.session_state.vocab), use_container_width=True)

        elif menu_choice == "📚 Гэрийн даалгавар өгөх":
            st.subheader("📚 Ангид даалгавар өгөх (Жишээ нь: Нийт 6-р анги эсвэл 7-р ангид)")
            st.info("💡 Даалгаврыг ангийн түвшнээр (6-р анги) өгөх ба дүн шинжилгээ дээр 6а, 6б, 6в бүлгүүдээр ялгарч харагдана.")
            
            hw_title = st.text_input("Даалгаврын гарчиг")
            hw_desc = st.text_area("Даалгаврын заавар / бодлогууд")
            
            # Ангийн түвшнээр сонгох (6-р анги, 7-р анги г.м)
            grade_target = st.selectbox("Аль ангийн түвшинд өгөх вэ?", ["6-р анги", "7-р анги", "8-р анги", "9-р анги", "10-р анги", "Бүгд"])
            deadline = st.date_input("Дуусах хугацаа")
            
            if st.button("Даалгавар нийтлэх"):
                if hw_title:
                    st.session_state.homeworks.append({
                        "id": str(random.randint(1000, 9999)),
                        "title": hw_title,
                        "description": hw_desc,
                        "target_grade": grade_target,
                        "deadline": str(deadline)
                    })
                    save_json(HOMEWORK_FILE, st.session_state.homeworks)
                    st.success(f"'{hw_title}' даалгавар {grade_target}-ийн бүх бүлгүүдэд нийтлэгдлээ!")

        elif menu_choice == "📝 Шалгалт удирдах":
            st.subheader("📝 Бүлэг сэдвийн шалгалт үүсгэх")
            ex_title = st.text_input("Шалгалтын нэр")
            ex_desc = st.text_area("Заавар")
            
            if 'temp_q' not in st.session_state:
                st.session_state.temp_q = []
                
            q = st.text_input("Асуулт")
            o1, o2, o3, o4 = st.text_input("A"), st.text_input("B"), st.text_input("C"), st.text_input("D")
            correct = st.selectbox("Зөв хариулт", [o1, o2, o3, o4] if o1 else ["-"])
            
            if st.button("Асуулт нэмэх"):
                if q and correct != "-":
                    st.session_state.temp_q.append({"question": q, "options": [o1, o2, o3, o4], "correct": correct})
                    st.success("Асуулт нэмэгдлээ!")
            
            if st.session_state.temp_q and st.button("Шалгалт нийтлэх"):
                st.session_state.exams.append({"title": ex_title, "description": ex_desc, "questions": st.session_state.temp_q})
                save_json(EXAM_FILE, st.session_state.exams)
                st.session_state.temp_q = []
                st.success("Шалгалт нийтлэгдлээ!")

        elif menu_choice == "🤖 AI тест генератор":
            st.subheader("🤖 AI ашиглан тест үүсгэх")
            count = st.slider("Асуултын тоо", 3, 10, 5)
            if st.button("AI Тест генератордох"):
                if len(st.session_state.vocab) >= 4:
                    selected = random.sample(st.session_state.vocab, min(count, len(st.session_state.vocab)))
                    q_list = []
                    for item in selected:
                        wrong = random.sample([v['mn'] for v in st.session_state.vocab if v['en'] != item['en']], 3)
                        opts = [item['mn']] + wrong
                        random.shuffle(opts)
                        q_list.append({"question": f"'{item['en']}' гэсэн үгийн утга?", "options": opts, "correct": item['mn']})
                    st.session_state.exams.append({"title": "AI Сорилт", "description": "Автомат сорилт", "questions": q_list})
                    save_json(EXAM_FILE, st.session_state.exams)
                    st.success("AI сорилт амжилттай үүслээ!")

        elif menu_choice == "📊 Анги бүлгийн дүн анализ & Excel":
            st.subheader("📊 Анги, бүлгээр ялгасан дүн шинжилгээ")
            
            hw_res = load_json(HW_RESULT_FILE, {})
            users_db = st.session_state.users
            
            if not hw_res:
                st.info("Илгээсэн даалгавар байхгүй байна.")
            else:
                rows = []
                for s_user, sub in hw_res.items():
                    user_class = users_db.get(s_user, {}).get('class', 'Тодорхойгүй')
                    user_name = users_db.get(s_user, {}).get('name', s_user)
                    for h_title, det in sub.items():
                        rows.append({
                            "Бүлэг/Анги": user_class,
                            "Сурагч": user_name,
                            "Username": s_user,
                            "Даалгавар": h_title,
                            "Хариулт": det['answer'],
                            "Илгээсэн огноо": det['date']
                        })
                
                df_res = pd.DataFrame(rows)
                
                # Анги бүлгээр нь шүүж харах
                selected_cls = st.selectbox("Анализ хийх бүлгээ сонгоно уу:", ["Бүх бүлэг"] + sorted(list(df_res["Бүлэг/Анги"].unique())))
                
                if selected_cls != "Бүх бүлэг":
                    filtered_df = df_res[df_res["Бүлэг/Анги"] == selected_cls]
                else:
                    filtered_df = df_res
                
                st.write(f"### 📋 {selected_cls} - Дүнгийн нэгтгэл")
                st.dataframe(filtered_df, use_container_width=True)
                
                # Excel рүү татах
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_res.to_excel(writer, index=False, sheet_name='Нийт_Дүн')
                    for cls_name, group_df in df_res.groupby("Бүлэг/Анги"):
                        group_df.to_excel(writer, index=False, sheet_name=f"Анги_{cls_name}")
                        
                processed_data = output.getvalue()
                
                st.download_button(
                    label="📥 Бүх бүлгийн тайланг Excel (.xlsx) файлаар татах",
                    data=processed_data,
                    file_name="Physics_Class_Analysis.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    # --- СУРАГЧИЙН ЦЭС ---
    else:
        if menu_choice == "📝 Нэр томьёоны сорилт (10 тест)":
            st.subheader("📝 Нэр томьёоны сорилт (Яг 10 тест, Тайлбар нуугдсан)")
            vocab_list = st.session_state.vocab
            if len(vocab_list) < 4:
                st.warning("Багш үгсийн сан оруулаагүй байна.")
            else:
                if 'quiz_idx' not in st.session_state:
                    st.session_state.quiz_idx = 0
                    st.session_state.quiz_score = 0
                    st.session_state.quiz_q = random.sample(vocab_list, min(10, len(vocab_list)))
                
                idx = st.session_state.quiz_idx
                q_list = st.session_state.quiz_q
                
                if idx < len(q_list):
                    item = q_list[idx]
                    wrong = random.sample([v['mn'] for v in vocab_list if v['en'] != item['en']], min(3, len(vocab_list)-1))
                    opts = [item['mn']] + wrong
                    random.shuffle(opts)
                    
                    st.write(f"### Асуулт {idx+1} / {len(q_list)}")
                    st.markdown(f"Англи үг: **{item['en']}**")
                    ans = st.radio("Монгол утгыг сонгоно уу:", opts, key=f"r_{idx}")
                    
                    if st.button("Хариулах & Дараах"):
                        if ans == item['mn']:
                            st.session_state.quiz_score += 1
                        st.session_state.quiz_idx += 1
                        st.rerun()
                else:
                    st.success(f"Сорилт дууслаа! Оноо: {st.session_state.quiz_score} / {len(q_list)}")
                    if st.button("Дахин өгөх"):
                        del st.session_state.quiz_idx
                        st.rerun()

        elif menu_choice == "📚 Миний гэрийн даалгавар":
            st.subheader(f"📚 {user.get('class', '')} бүлгийн гэрийн даалгаврууд")
            homeworks = st.session_state.get('homeworks', [])
            my_class = user.get('class', '') # Жишээ нь: 6а
            
            # Сурагчийн ангийн түвшинг тодорхойлох (Жишээ нь 6а -> 6-р анги)
            my_grade = my_class[0] + "-р анги" if len(my_class) > 0 and my_class[0].isdigit() else "Бүгд"
            
            filtered_hw = [
                hw for hw in homeworks 
                if hw.get('target_grade') == "Бүгд" or hw.get('target_grade') == my_grade or hw.get('target_grade') == my_class
            ]
            
            if not filtered_hw:
                st.info("Таны ангид одоогоор даалгавар байхгүй байна.")
            else:
                for hw in filtered_hw:
                    with st.container(border=True):
                        st.markdown(f"### 📌 {hw['title']}")
                        st.write(hw['description'])
                        st.caption(f"Дуусах хугацаа: {hw['deadline']}")
                        
                        ans_text = st.text_area("Таны хариулт / бодолт:", key=f"hw_ans_{hw['id']}")
                        if st.button("Илгээх", key=f"hw_btn_{hw['id']}"):
                            if ans_text:
                                hw_res = load_json(HW_RESULT_FILE, {})
                                if user['username'] not in hw_res:
                                    hw_res[user['username']] = {}
                                hw_res[user['username']][hw['title']] = {
                                    "status": "Илгээсэн",
                                    "answer": ans_text,
                                    "date": str(pd.Timestamp.now().date())
                                }
                                save_json(HW_RESULT_FILE, hw_res)
                                st.success("Даалгавар амжилттай илгээгдлээ!")

        elif menu_choice == "📋 Бүлэг сэдвийн шалгалтууд":
            exams = st.session_state.get('exams', [])
            if not exams:
                st.info("Шалгалт байхгүй байна.")
            else:
                titles = [e['title'] for e in exams]
                chosen = st.selectbox("Шалгалт сонгох", titles)
                ex = next(e for e in exams if e['title'] == chosen)
                
                with st.form("exam_form"):
                    answers = []
                    for i, q in enumerate(ex['questions']):
                        st.markdown(f"**{i+1}. {q['question']}**")
                        sel = st.radio("Сонголт:", q['options'], key=f"eq_{i}")
                        answers.append((sel, q['correct']))
                    if st.form_submit_button("Шалгалт илгээх"):
                        score = sum(1 for s, c in answers if s == c)
                        st.success(f"Шалгалт дууслаа! Оноо: {score}/{len(answers)}")

        elif menu_choice == "📖 Толь бичиг":
            st.subheader("📖 Толь бичиг")
            if st.session_state.vocab:
                st.dataframe(pd.DataFrame(st.session_state.vocab), use_container_width=True, hide_index=True)
            else:
                st.info("Үгсийн сан хоосон байна.")
