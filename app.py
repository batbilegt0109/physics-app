import streamlit as st
import pandas as pd
import json
import os
import random

# Хуудасны тохиргоо
st.set_page_config(page_title="Физикийн ухаалаг систем", page_icon="⚡", layout="wide")

VOCAB_FILE = "vocab_data.json"
USER_FILE = "user_data.json"

def load_data():
    if os.path.exists(VOCAB_FILE):
        with open(VOCAB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [
        {"en": "Reflection", "mn": "Гэрлийн ойлт", "description": "Гэрлийн цацраг гадаргуугаас буцаж ойх үзэгдэл."},
            ]

def save_data(vocab_list):
    with open(VOCAB_FILE, "w", encoding="utf-8") as f:
        json.dump(vocab_list, f, ensure_ascii=False, indent=4)

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        'bagsh': {'password': '1234', 'role': 'Багш', 'name': 'Үндсэн Багш'},
        'suragch1': {'password': 'pass1', 'role': 'Сурагч', 'name': 'Сурагч 1'},
        'suragch2': {'password': 'pass2', 'role': 'Сурагч', 'name': 'Сурагч 2'}
    }

def save_users(users_dict):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users_dict, f, ensure_ascii=False, indent=4)

if 'vocab' not in st.session_state:
    st.session_state.vocab = load_data()

if 'users' not in st.session_state:
    st.session_state.users = load_users()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None

# ---- НЭВТРЭХ ХЭСЭГ ----
if not st.session_state.logged_in:
    st.title("⚡ Физикийн нэр томьёоны ухаалаг систем")
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
                st.rerun()
            else:
                st.error("Нэвтрэх нэр эсвэл нууц үг буруу байна!")

# ---- НЭВТЭРСНИЙ ДАРААХ ХЭСЭГ ----
else:
    user = st.session_state.user_info
    
    # Зүүн талын цэс (Sidebar)
    with st.sidebar:
        st.success(f"Тавтай морил, {user['name']} ({user['role']})")
        if st.button("Гарах (Log out)"):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.rerun()

    st.title("⚡ Физикийн нэр томьёоны ухаалаг систем")
    
    # --- БАГШИЙН ЦЭС ---
    if user['role'] == 'Багш':
        st.header("👨‍🏫 Багшийн удирдлагын самбар")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "➕ Нэг нэгээр үг нэмэх", 
            "✏️ Үг засах / 🗑️ Устгах", 
            "📁 Файлаар олон үг оруулах", 
            "👥 Хэрэглэгч удирдах"
        ])
        
        with tab1:
            st.subheader("Физикийн шинэ нэр томьёо нэмэх")
            en_word = st.text_input("Термин / Англи үг").strip()
            mn_word = st.text_input("Монгол утга").strip()
            desc_text = st.text_input("Товч тайлбар").strip()
            
            if st.button("Үг нэмэх"):
                if en_word and mn_word:
                    st.session_state.vocab.append({
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
            
            # DataFrame руу хувиргахдаа устгах чек багана (Select) нэмэх
            df_vocab = pd.DataFrame(st.session_state.vocab)
            df_vocab.insert(0, "Устгах", False)
            
            # Хэрэглэгч хүснэгтээс чеклэх боломжтой болгох
            edited_df = st.data_editor(
                df_vocab, 
                use_container_width=True, 
                hide_index=False,
                key="vocab_table_editor"
            )
            
            col_del_btn, col_edit = st.columns(2)
            
            with col_del_btn:
                if st.button("🗑️ Чеклэсэн үгсийг устгах"):
                    # Чекийн True болгосон мөрүүдийг хасаад үлдсэнийг нь авна
                    survived_vocab = []
                    deleted_count = 0
                    for idx, row in edited_df.iterrows():
                        if not row["Устгах"]:
                            survived_vocab.append({
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
                new_en = st.text_input("Шинэ Англи үг", value=curr_item['en'])
                new_mn = st.text_input("Шинэ Монгол утга", value=curr_item['mn'])
                new_desc = st.text_area("Шинэ тайлбар", value=curr_item['description'])
                
                if st.button("Өөрчлөлтийг хадгалах"):
                    st.session_state.vocab[edit_idx - 1] = {
                        "en": new_en.strip(),
                        "mn": new_mn.strip(),
                        "description": new_desc.strip()
                    }
                    save_data(st.session_state.vocab)
                    st.success(f"{edit_idx}-р дугаартай үг амжилттай шинэчлэгдлээ!")
                    st.rerun()

        with tab3:
            st.subheader("Файлаар олон үг оруулах")
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
                                desc = str(row['description']) if 'description' in df.columns and pd.notna(row['description']) else "-"
                                st.session_state.vocab.append({
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

    # --- СУРАГЧИЙН ЦЭС ---
    else:
        st.header("🎓 Сурагчийн суралцах болон сорилтын хэсэг")
        
        tab_s1, tab_s2 = st.tabs(["📝 Нэр томьёоны сорилт (Тест)", "📖 Толь бичиг (Хайх & Эрэмбэлэх)"])
        
        with tab_s1:
            st.subheader("Физикийн мэдлэг сорих тест")
            vocab_list = st.session_state.vocab
            
            if len(vocab_list) < 4:
                st.warning("Тест ажиллахад дор хаяж 4 үг шаардлагатай.")
            else:
                if 'quiz_q' not in st.session_state:
                    st.session_state.quiz_q = None
                
                if st.button("Шинэ асуулт авах") or st.session_state.quiz_q is None:
                    correct_item = random.choice(vocab_list)
                    wrong_items = random.sample([v for v in vocab_list if v['en'] != correct_item['en']], min(3, len(vocab_list)-1))
                    options = [correct_item['mn']] + [w['mn'] for w in wrong_items]
                    random.shuffle(options)
                    
                    st.session_state.quiz_q = {
                        'en': correct_item['en'],
                        'correct': correct_item['mn'],
                        'options': options,
                        'desc': correct_item['description']
                    }
                
                q = st.session_state.quiz_q
                st.markdown(f"### Англи үг: **{q['en']}**")
                st.caption(f"Тайлбар: {q['desc']}")
                
                ans = st.radio("Энэ үгийн Монгол утгыг сонгоно уу:", q['options'], key="quiz_choice")
                
                if st.button("Хариу шалгах"):
                    if ans == q['correct']:
                        st.success("🎉 Зөв байна! Сайн байна.")
                    else:
                        st.error(f"❌ Буруу байна. Зөв хариулт нь: **{q['correct']}**")

        with tab_s2:
            st.subheader("📖 Физикийн нэр томьёоны толь бичиг")
            search_query = st.text_input("🔍 Хайх үг (Англи эсвэл Монголоор)").strip().lower()
            sort_option = st.selectbox("Эрэмбэлэх хэлбэр:", ["Англи үгээр (A-Z)", "Монгол үгээр (А-Я)"])
            
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
