import streamlit as st
import pandas as pd
import json
import os
import random
import io
import uuid

# Хуудасны тохиргоо
st.set_page_config(page_title="GTIS Advanced Physics System", page_icon="⚡", layout="wide")

# Файлын нэрс
VOCAB_FILE = "vocab_data.json"
USER_FILE = "user_data.json"
EXAM_FILE = "exam_data.json"
CLASS_FILE = "class_data.json"
HOMEWORK_FILE = "homework_data.json"
HW_RESULT_FILE = "hw_result_data.json"

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

# Dynamic Бааз өгөгдөл
if 'vocab' not in st.session_state:
    st.session_state.vocab = load_json(VOCAB_FILE, [])

if 'users' not in st.session_state:
    users_data = load_json(USER_FILE, {})
    users_data['batbilegt.ya'] = {
        'password': '123',
        'role': 'Админ',
        'name': 'batbilegt.ya',
        'class': 'Бүгд'
    }
    st.session_state.users = users_data
    save_json(USER_FILE, st.session_state.users)

if 'classes' not in st.session_state:
    st.session_state.classes = load_json(CLASS_FILE, [])

if 'exams' not in st.session_state:
    st.session_state.exams = load_json(EXAM_FILE, [])

if 'homeworks' not in st.session_state:
    st.session_state.homeworks = load_json(HOMEWORK_FILE, [])

# --- REFRESH ХИЙХЭД НЭВТРЭСЭН ТӨЛӨВХӨТ ТАХИЛЗАХ (Query Params) ---
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
        st.success(f"👤 **{user['name']}** ({user['role']})")
        
        # --- БАТТАЙ АДМИН ТЕСТ ХЭРЭГСЭЛ (Жинхэнэ админ байхад хэзээ ч алга болохгүй) ---
        if st.session_state.get('real_admin') == 'batbilegt.ya' or user.get('username') == 'batbilegt.ya' or user.get('role') == 'Админ':
            if not st.session_state.get('real_admin'):
                st.session_state.real_admin = 'batbilegt.ya'
                
            st.markdown("---")
            st.markdown("🛠️ **Админ тест хийх хэрэгсэл:**")
            all_usernames = list(st.session_state.users.keys())
            
            current_selected = user.get('username', 'batbilegt.ya')
            default_idx = all_usernames.index(current_selected) if current_selected in all_usernames else 0
            
            selected_test_user = st.selectbox("Өөр хэрэглэгч рүү шилжих:", all_usernames, index=default_idx, key="role_switcher")
            if st.button("🔄 Энэ эрх рүү шилжиж шалгах"):
                u_switch = st.session_state.users[selected_test_user].copy()
                u_switch['username'] = selected_test_user
                st.session_state.user_info = u_switch
                st.rerun()
                
            if user.get('username') != 'batbilegt.ya':
                if st.button("⬅️ Админ руу буцах", use_container_width=True):
                    admin_u = st.session_state.users['batbilegt.ya'].copy()
                    admin_u['username'] = 'batbilegt.ya'
                    st.session_state.user_info = admin_u
                    st.rerun()
            st.markdown("---")

        if user['role'] in ['Админ', 'Багш']:
            menu_options = [
                "🏫 Ангиуд удирдах",
                "📚 Үгсийн сан удирдах (Засах/Устгах/Импорт)",
                "📚 Гэрийн даалгавар (Гараар/Файлаар)",
                "📝 Шалгалт удирдах (Гараар/Файлаар)",
                "🤖 AI тест генератор",
                "📊 Дүн анализ, Архив & Excel"
            ]
            if user['role'] == 'Админ' or user.get('username') == 'batbilegt.ya':
                menu_options.insert(1, "👥 Багш & Сурагчдын бүртгэл удирдах")
                
            menu_choice = st.radio("📌 Багшийн цэс:", menu_options)
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
            if "logged_user" in st.query_params:
                del st.query_params["logged_user"]
            st.rerun()

    # --- БАГШИЙН / АДМИНЫ ЦЭС ---
    if user['role'] in ['Админ', 'Багш']:
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
            st.subheader("👥 Багш болон сурагчдын бүртгэл удирдах (Зөвхөн Админ)")
            t_u1, t_u2 = st.tabs(["➕ Шинэ Багш / Сурагч нэмэх", "📋 Бүртгэлтэй хэрэглэгчид"])
            
            with t_u1:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("#### 👨‍🏫 Шинэ Багш нэмэх")
                    b_user = st.text_input("Багшийн Username", key="b_u").strip()
                    b_pass = st.text_input("Нууц үг", type="password", key="b_p").strip()
                    b_name = st.text_input("Багшийн бүтэн нэр", key="b_n").strip()
                    if st.button("Багш бүртгэх"):
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
                    s_user = st.text_input("Сурагчийн Username", key="s_u").strip()
                    s_pass = st.text_input("Нууц үг", type="password", key="s_p").strip()
                    s_name = st.text_input("Сурагчийн нэр", key="s_n").strip()
                    s_cls = st.selectbox("Анги сонгох", st.session_state.classes if st.session_state.classes else ["Ангигүй"], key="s_cls_box")
                    if st.button("Сурагч бүртгэх"):
                        if s_user and s_pass and s_name:
                            if s_user in st.session_state.users:
                                st.error("Энэ username аль хэдийн бүртгэгдсэн байна!")
                            else:
                                st.session_state.users[s_user] = {'password': s_pass, 'role': 'Сурагч', 'name': s_name, 'class': s_cls}
                                save_json(USER_FILE, st.session_state.users)
                                st.success(f"Сурагч '{s_name}' амжилттай нэмэгдлээ!")
                                st.rerun()

            with t_u2:
                st.markdown("#### Бүртгэлтэй хэрэглэгчдийн жагсаалт")
                for u_key, u_val in list(st.session_state.users.items()):
                    with st.container(border=True):
                        st.write(f"🎭 **{u_val['role']}** | Username: `{u_key}` | Нэр: **{u_val['name']}** | Анги: **{u_val.get('class', '-')}**")
                        if u_key != 'batbilegt.ya' and u_key != user.get('username'):
                            if st.button("🗑️ Хэрэглэгч устгах", key=f"del_u_{u_key}"):
                                del st.session_state.users[u_key]
                                save_json(USER_FILE, st.session_state.users)
                                st.success("Хэрэглэгч устгагдлаа!")
                                st.rerun()

        elif menu_choice == "📚 Үгсийн сан удирдах (Засах/Устгах/Импорт)":
            st.subheader("📚 Үгсийн сан удирдах (5 багана: category, sub_category, en, mn, description)")
            
            tab_v1, tab_v2 = st.tabs(["✏️ Үгс харах, Засах & Устгах", "📥 Файлаар & Гараар оруулах"])
            
            with tab_v1:
                if not st.session_state.vocab:
                    df_vocab = pd.DataFrame(columns=['category', 'sub_category', 'en', 'mn', 'description'])
                else:
                    df_vocab = pd.DataFrame(st.session_state.vocab)
                
                st.markdown("💡 *Хүснэгт дээр шууд засна уу. Мөн мөр сонгоод Delete товчоор устгах боломжтой.*")
                edited_df = st.data_editor(df_vocab, use_container_width=True, num_rows="dynamic", key="vocab_editor")
                
                if st.button("💾 Өөрчлөлтийг хадгалах"):
                    st.session_state.vocab = edited_df.to_dict(orient="records")
                    save_json(VOCAB_FILE, st.session_state.vocab)
                    st.success("Үгсийн сан амжилттай шинэчлэгдлээ!")
                    st.rerun()

            with tab_v2:
                col_i1, col_i2 = st.columns(2)
                with col_i1:
                    st.markdown("#### Файлаар олон үг оруулах (CSV / Excel)")
                    up_file = st.file_uploader("5 баганатай файл сонгоно уу", type=['csv', 'xlsx'])
                    if up_file:
                        try:
                            df_import = pd.read_csv(up_file) if up_file.name.endswith('.csv') else pd.read_excel(up_file)
                            df_import.columns = [str(c).strip().lower() for c in df_import.columns]
                            req_cols = ['category', 'sub_category', 'en', 'mn', 'description']
                            if not all(c in df_import.columns for c in req_cols):
                                st.error("Файлд category, sub_category, en, mn, description гэсэн 5 багана заавал байх ёстой!")
                            else:
                                st.dataframe(df_import.head(), use_container_width=True)
                                if st.button("📥 Файлын үгсийг нэмэх"):
                                    for _, r in df_import.iterrows():
                                        st.session_state.vocab.append({
                                            "category": str(r['category']), "sub_category": str(r['sub_category']),
                                            "en": str(r['en']), "mn": str(r['mn']), "description": str(r['description'])
                                        })
                                    save_json(VOCAB_FILE, st.session_state.vocab)
                                    st.success("Үгс амжилттай нэмэгдлээ!")
                                    st.rerun()
                        except Exception as e:
                            st.error(f"Алдаа гарлаа: {e}")
                
                with col_i2:
                    st.markdown("#### Гараар нэг үг нэмэх")
                    c_cat = st.text_input("Бүлэг сэдэв", key="c_cat_input").strip()
                    c_sub = st.text_input("Дэд сэдэв", key="c_sub_input").strip()
                    c_en = st.text_input("Англи термин", key="c_en_input").strip()
                    c_mn = st.text_input("Монгол утга", key="c_mn_input").strip()
                    c_desc = st.text_area("Тайлбар", key="c_desc_input").strip()
                    if st.button("Үг нэмэх"):
                        if c_cat and c_sub and c_en and c_mn:
                            st.session_state.vocab.append({
                                "category": c_cat, "sub_category": c_sub, "en": c_en, "mn": c_mn, "description": c_desc or "-"
                            })
                            save_json(VOCAB_FILE, st.session_state.vocab)
                            st.success("Үг нэмэгдлээ!")
                            st.rerun()

        elif menu_choice == "📚 Гэрийн даалгавар (Гараар/Файлаар)":
            st.subheader("📚 Гэрийн даалгавар өгөх (Бүлэг, дэд сэдвээр)")
            
            hw_title = st.text_input("Даалгаврын гарчиг")
            hw_cat = st.text_input("Бүлэг сэдэв", key="hw_cat_inp")
            hw_sub = st.text_input("Дэд сэдэв", key="hw_sub_inp")
            target_cls = st.selectbox("Аль ангид өгөх вэ?", ["Бүгд"] + st.session_state.classes)
            deadline = st.date_input("Дуусах хугацаа")
            
            hw_tab1, hw_tab2 = st.tabs(["✍️ Гараар заавар бичих", "📁 Файлаар оруулах (Даалгаврын текст/файл)"])
            
            hw_desc = ""
            with hw_tab1:
                hw_desc = st.text_area("Даалгаврын дэлгэрэнгүй заавар / Бодлогууд")
            with hw_tab2:
                hw_file = st.file_uploader("Даалгаврын файл хавсаргах (txt, pdf, docx, csv, xlsx)", type=['txt', 'csv', 'xlsx'])
                if hw_file:
                    hw_desc += f"\n[Хавсаргасан файл: {hw_file.name}]"
            
            if st.button("🚀 Даалгавар нийтлэх"):
                if hw_title and hw_cat:
                    st.session_state.homeworks.append({
                        "id": str(uuid.uuid4())[:8],
                        "title": hw_title,
                        "category": hw_cat,
                        "sub_category": hw_sub,
                        "description": hw_desc,
                        "target_class": target_cls,
                        "deadline": str(deadline),
                        "status": "Идэвхтэй"
                    })
                    save_json(HOMEWORK_FILE, st.session_state.homeworks)
                    st.success("Даалгавар амжилттай нийтлэгдлээ!")

        elif menu_choice == "📝 Шалгалт удирдах (Гараар/Файлаар)":
            st.subheader("📝 Шалгалт үүсгэх ба удирдах")
            ex_title = st.text_input("Шалгалтын нэр")
            ex_cat = st.text_input("Бүлэг сэдэв", key="ex_cat_inp")
            ex_sub = st.text_input("Дэд сэдэв", key="ex_sub_inp")
            ex_desc = st.text_area("Шалгалтын заавар")
            
            ex_tab1, ex_tab2 = st.tabs(["✍️ Асуултуудыг гараар нэмэх", "📁 Файлаар асуулт импортлох"])
            
            if 'temp_q' not in st.session_state:
                st.session_state.temp_q = []
                
            with ex_tab1:
                q = st.text_input("Асуулт")
                o1 = st.text_input("A хувилбар")
                o2 = st.text_input("B хувилбар")
                o3 = st.text_input("C хувилбар")
                o4 = st.text_input("D хувилбар")
                correct = st.selectbox("Зөв хариулт", [o1, o2, o3, o4] if o1 else ["-"])
                if st.button("Асуулт нэмэх"):
                    if q and correct != "-":
                        st.session_state.temp_q.append({"question": q, "options": [o1, o2, o3, o4], "correct": correct})
                        st.success("Асуулт нэмэгдлээ!")
                if st.session_state.temp_q:
                    st.write(f"Одоогоор нэмэгдсэн асуултын тоо: {len(st.session_state.temp_q)}")
                    
            with ex_tab2:
                st.info("Файлын формат: `question`, `opt1`, `opt2`, `opt3`, `opt4`, `correct` багануудтай байх.")
                ex_file = st.file_uploader("Шалгалтын асуултын файл", type=['csv', 'xlsx'])
                if ex_file:
                    try:
                        df_ex = pd.read_csv(ex_file) if ex_file.name.endswith('.csv') else pd.read_excel(ex_file)
                        df_ex.columns = [str(c).strip().lower() for c in df_ex.columns]
                        if st.button("📥 Файлаас асуултуудыг ачаалах"):
                            for _, r in df_ex.iterrows():
                                st.session_state.temp_q.append({
                                    "question": str(r['question']),
                                    "options": [str(r['opt1']), str(r['opt2']), str(r['opt3']), str(r['opt4'])],
                                    "correct": str(r['correct'])
                                })
                            st.success("Асуултууд амжилттай орлоо!")
                    except Exception as e:
                        st.error(f"Алдаа: {e}")

            if st.session_state.temp_q and st.button("🚀 Шалгалтыг бүхлээр нь нийтлэх"):
                if ex_title:
                    st.session_state.exams.append({
                        "id": str(uuid.uuid4())[:8],
                        "title": ex_title,
                        "category": ex_cat,
                        "sub_category": ex_sub,
                        "description": ex_desc,
                        "questions": st.session_state.temp_q
                    })
                    save_json(EXAM_FILE, st.session_state.exams)
                    st.session_state.temp_q = []
                    st.success("Шалгалт амжилттай нийтлэгдлээ!")

        elif menu_choice == "🤖 AI тест генератор":
            st.subheader("🤖 AI тест генератор (Үгсийн сангаас автомат тест үүсгэх)")
            if len(st.session_state.vocab) < 4:
                st.warning("AI тест үүсгэхэд үгсийн санд дор хаяж 4 үг байх шаардлагатай.")
            else:
                sub_cats = list(set([v.get('sub_category', 'Бүгд') for v in st.session_state.vocab]))
                chosen_sub = st.selectbox("Аль дэд сэдвээр AI тест үүсгэх вэ?", ["Бүгд"] + sub_cats)
                
                filtered_vocab = st.session_state.vocab if chosen_sub == "Бүгд" else [v for v in st.session_state.vocab if v.get('sub_category') == chosen_sub]
                
                count = st.slider("Асуултын тоо", 3, 10, min(5, len(filtered_vocab)))
                ai_title = st.text_input("Тестийн нэр", value=f"AI сорилт ({chosen_sub})")
                
                if st.button("✨ AI Тест автоматаар үүсгэх"):
                    selected = random.sample(filtered_vocab, min(count, len(filtered_vocab)))
                    q_list = []
                    for item in selected:
                        wrong_pool = [v['mn'] for v in filtered_vocab if v['en'] != item['en']]
                        if len(wrong_pool) < 3:
                            wrong_pool = [v['mn'] for v in st.session_state.vocab if v['en'] != item['en']]
                        wrong = random.sample(wrong_pool, min(3, len(wrong_pool)))
                        opts = [item['mn']] + wrong
                        random.shuffle(opts)
                        q_list.append({
                            "question": f"'{item['en']}' Монгол утгыг сонгоно уу:",
                            "options": opts,
                            "correct": item['mn']
                        })
                    
                    st.session_state.exams.append({
                        "id": str(uuid.uuid4())[:8],
                        "title": ai_title,
                        "category": chosen_sub,
                        "sub_category": chosen_sub,
                        "description": "AI автомат үүсгэсэн сорилт",
                        "questions": q_list
                    })
                    save_json(EXAM_FILE, st.session_state.exams)
                    st.success("🤖 AI тест амжилттай үүсэж, шалгалтын жагсаалтад нэмэгдлээ!")

        elif menu_choice == "📊 Дүн анализ, Архив & Excel":
            st.subheader("📊 Дүн шинжилгээ, Үр дүн & Архивлалт")
            
            hw_res = load_json(HW_RESULT_FILE, {})
            if not hw_res:
                st.info("Одоогоор ирүүлсэн даалгавар байхгүй байна.")
            else:
                rows = []
                for s_u, sub in hw_res.items():
                    u_cls = st.session_state.users.get(s_u, {}).get('class', '-')
                    u_name = st.session_state.users.get(s_u, {}).get('name', s_u)
                    for h_t, det in sub.items():
                        rows.append({
                            "Анги": u_cls,
                            "Сурагч": u_name,
                            "Username": s_u,
                            "Даалгавар": h_t,
                            "Хариулт": det['answer'],
                            "Огноо": det['date'],
                            "Төлөв": det.get('status', 'Идэвхтэй')
                        })
                
                df_res = pd.DataFrame(rows)
                selected_cls = st.selectbox("Ангиар шүүх:", ["Бүх анги"] + sorted(list(df_res["Анги"].unique())))
                
                filtered_df = df_res if selected_cls == "Бүх анги" else df_res[df_res["Анги"] == selected_cls]
                st.dataframe(filtered_df, use_container_width=True)
                
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        filtered_df.to_excel(writer, index=False, sheet_name='Analytics')
                    st.download_button("📥 Дүнгийн тайланг Excel (.xlsx) татах", data=output.getvalue(), file_name="Physics_Analysis.xlsx")
                
                with col_d2:
                    if st.button("📁 Архивлах (Дууссан даалгавруудыг архивлах)"):
                        st.success("Үр дүн амжилттай архивлав.")

    # --- СУРАГЧИЙН ЦЭС ---
    else:
        elif menu_choice == "📝 Нэр томьёоны сорилт (10 тест)" or menu_choice == "📝 Нэр томьёоны сорилт":
            st.subheader("📝 Нэр томьёоны сорилт")
            vocab_list = st.session_state.vocab
            
            if len(vocab_list) < 4:
                st.warning("Багш хангалттай үг оруулаагүй байна.")
            else:
                categories = list(set([v.get('category', 'Бүгд') for v in vocab_list]))
                chosen_cat = st.selectbox("Бүлэг сэдэв сонгох:", ["Бүх бүлэг"] + categories)
                
                filtered_vocab = vocab_list if chosen_cat == "Бүх бүлэг" else [v for v in vocab_list if v.get('category') == chosen_cat]
                
                sub_cats = list(set([v.get('sub_category', 'Бүгд') for v in filtered_vocab]))
                chosen_sub = st.selectbox("Дэд сэдэв сонгох:", ["Бүх дэд сэдэв"] + sub_cats)
                
                if chosen_sub != "Бүх дэд сэдэв":
                    filtered_vocab = [v for v in filtered_vocab if v.get('sub_category') == chosen_sub]
                
                if len(filtered_vocab) < 4:
                    st.warning("Сонгосон сэдэвт хангалттай үг байхгүй байна (Дор хаяж 4 үг шаардлагатай).")
                else:
                    total_q_count = st.slider("Нийт асуултын тоо:", min_value=4, max_value=min(30, len(filtered_vocab)), value=min(10, len(filtered_vocab)))
                    
                    if st.button("🚀 Сорилт эхлэх"):
                        sampled = random.sample(filtered_vocab, total_q_count)
                        quiz_items = []
                        
                        mn_en_count = max(1, int(total_q_count * 0.3))
                        
                        for i in range(mn_en_count):
                            item = sampled[i]
                            wrongs = random.sample([v['en'] for v in filtered_vocab if v['en'] != item['en']], min(3, len(filtered_vocab)-1))
                            opts = [item['en']] + wrongs
                            random.shuffle(opts)
                            quiz_items.append({
                                "question": f"Монгол утга: '{item['mn']}' -> Англи терминийг сонгоно уу:",
                                "options": opts, "correct": item['en']
                            })
                        
                        for i in range(mn_en_count, total_q_count):
                            item = sampled[i]
                            wrongs = random.sample([v['mn'] for v in filtered_vocab if v['en'] != item['en']], min(3, len(filtered_vocab)-1))
                            opts = [item['mn']] + wrongs
                            random.shuffle(opts)
                            quiz_items.append({
                                "question": f"Англи термин: '{item['en']}' -> Монгол утгыг сонгоно уу:",
                                "options": opts, "correct": item['mn']
                            })
                        
                        st.session_state.active_quiz = quiz_items
                        st.session_state.quiz_start_time = pd.Timestamp.now()
                        st.rerun()
                    
                    if 'active_quiz' in st.session_state:
                        start_t = st.session_state.get('quiz_start_time', pd.Timestamp.now())
                        elapsed = int((pd.Timestamp.now() - start_t).total_seconds())
                        st.info(f"⏱️ Сорилт үргэлжлэх хугацаа: {elapsed // 60} минут {elapsed % 60} секунд")
                        
                        with st.form("quiz_form"):
                            user_answers = []
                            for idx, q in enumerate(st.session_state.active_quiz):
                                st.markdown(f"**{idx+1}. {q['question']}**")
                                ans = st.radio("Сонгох:", q['options'], key=f"q_ans_{idx}")
                                user_answers.append((ans, q['correct']))
                            
                            if st.form_submit_button("Сорилт дуусгах & Дүн харах"):
                                score = sum(1 for a, c in user_answers if a == c)
                                total = len(st.session_state.active_quiz)
                                percent = int((score / total) * 100)
                                st.success(f"🎉 Сорилт дууслаа! Таны авсан оноо: {score} / {total} ({percent}%)")
                                del st.session_state.active_quiz
                                if 'quiz_start_time' in st.session_state:
                                    del st.session_state.quiz_start_time

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
                        st.markdown(f"### 📌 {hw['title']} ({hw.get('category', '-')})")
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
            exams = st.session_state.get('exams', [])
            if not exams:
                st.info("Шалгалт алга.")
            else:
                chosen = st.selectbox("Шалгалт сонгох", [e['title'] for e in exams])
                ex = next(e for e in exams if e['title'] == chosen)
                st.write(f"**Бүлэг:** {ex.get('category', '-')} | **Дэд сэдэв:** {ex.get('sub_category', '-')}")
                st.write(ex.get('description', ''))
                
                with st.form("ex_f"):
                    ans_list = []
                    for i, q in enumerate(ex['questions']):
                        st.markdown(f"**{i+1}. {q['question']}**")
                        s = st.radio("Сонголт:", q['options'], key=f"ex_q_{i}")
                        ans_list.append((s, q['correct']))
                    if st.form_submit_button("Шалгалт илгээх"):
                        sc = sum(1 for s, c in ans_list if s == c)
                        st.success(f"Шалгалт дууслаа! Оноо: {sc}/{len(ans_list)}")

        elif menu_choice == "📖 Толь бичиг":
            st.subheader("📖 Толь бичиг")
            if st.session_state.vocab:
                st.dataframe(pd.DataFrame(st.session_state.vocab), use_container_width=True, hide_index=True)
            else:
                st.info("Толь бичиг хоосон байна.")
