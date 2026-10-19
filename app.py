import streamlit as st
import pandas as pd

# Хуудасны тохиргоо
st.set_page_config(page_title="🔐 Системд нэвтрэх", page_icon="⚡", layout="wide")

# Суурь хэрэглэгчдийн дата (Нэвтрэх нэр: Нууц үг, Эрх)
if 'users' not in st.session_state:
    st.session_state.users = {
        'bagsh': {'password': '1234', 'role': 'Багш', 'name': 'Үндсэн Багш'},
        'suragch1': {'password': 'pass1', 'role': 'Сурагч', 'name': 'Сурагч 1'},
        'suragch2': {'password': 'pass2', 'role': 'Сурагч', 'name': 'Сурагч 2'}
    }

# Суурь физик үгсийн сан
if 'vocab' not in st.session_state:
    st.session_state.vocab = [
        {"English term": "Reflection of light", "Монгол нэршил": "Гэрлийн ойлт", "added_by": "Систем"},
        {"English term": "Plane mirror", "Монгол нэршил": "Хавтгай толь", "added_by": "Систем"},
        {"English term": "Spherical mirrors", "Монгол нэршил": "Бөмбөлөг толь", "added_by": "Систем"}
    ]

# Нэвтрэх төлөв
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None

# ---- НЭВТРЭХ ХЭСЭГ ----
if not st.session_state.logged_in:
    st.title("📚 Физикийн ухаалаг систем")
    st.subheader("Системд нэвтрэх")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        username_input = st.text_input("Нэвтрэх нэр (Username)").strip().lower()
        password_input = st.text_input("Нууц үг (Password)", type="password").strip()
        login_btn = st.button("Нэвтрэх")
        
        if login_btn:
            if username_input in st.session_state.users and st.session_state.users[username_input]['password'] == password_input:
                st.session_state.logged_in = True
                st.session_state.user_info = st.session_state.users[username_input]
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

    # Дээд талын хэсэг
    st.title("⚡ Физикийн нэр томьёоны ухаалаг систем")
    
    # --- БАГШИЙН ЦЭС ---
    if user['role'] == 'Багш':
        st.header("👨‍🏫 Багшийн удирдлагын самбар")
        
        tab1, tab2, tab3 = st.tabs(["➕ Нэг нэгээр үг нэмэх", "📁 Файлаар (CSV/Excel) олон үг оруулах", "👥 Хэрэглэгч удирдах"])
        
        with tab1:
            st.subheader("Физикийн шинэ нэр томьёо нэмэх")
            en_word = st.text_input("Термин / Англи үг").strip()
            mn_word = st.text_input("Монгол тайлбар").strip()
            if st.button("Үг нэмэх"):
                if en_word and mn_word:
                    st.session_state.vocab.append({"en": en_word, "mn": mn_word, "added_by": user['name']})
                    st.success(f"'{en_word}' - '{mn_word}' үг амжилттай нэмэгдлээ!")
                else:
                    st.warning("Хоёр талын талбарыг хоёуланг нь бөглөнө үү.")
                    
        with tab2:
            st.subheader("Файлаар (CSV эсвэл Excel) олон үг зэрэг оруулах")
            st.info("Файл чинь 'en' (Англи үг) болон 'mn' (Монгол утга) гэсэн баганатай байх ёстой.")
            uploaded_file = st.file_uploader("Файлаа сонгох / чирж оруулах", type=['csv', 'xlsx'])
            
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                        
                    st.write("Оруулсан файлын урьдчилан харах хэсэг:")
                    st.dataframe(df.head())
                    
                    if st.button("Эдгээр үгсийг системд хуулах"):
                        count = 0
                        for _, row in df.iterrows():
                            if 'en' in df.columns and 'mn' in df.columns:
                                st.session_state.vocab.append({
                                    "en": str(row['en']),
                                    "mn": str(row['mn']),
                                    "added_by": user['name']
                                })
                                count += 1
                        st.success(f"Нийт {count} нэр томьёо амжилттай нэмэгдлээ!")
                except Exception as e:
                    st.error(f"Файл уншихад алдаа гарлаа: {e}")

        with tab3:
            st.subheader("Шинэ сурагч эсвэл багш нэмэх")
            new_user = st.text_input("Шинэ хэрэглэгчийн логин нэр").strip().lower()
            new_pass = st.text_input("Нууц үг").strip()
            new_name = st.text_input("Бүтэн нэр").strip()
            new_role = st.selectbox("Эрх", ["Сурагч", "Багш"])
            
            if st.button("Хэрэглэгч бүртгэх"):
                if new_user and new_pass and new_name:
                    st.session_state.users[new_user] = {'password': new_pass, 'role': new_role, 'name': new_name}
                    st.success(f"'{new_name}' ({new_role}) амжилттай бүртгэгдлээ!")
                else:
                    st.warning("Мэдээллийг бүрэн бөглөнө үү.")

    # --- СУРАГЧИЙН ЦЭС ---
    else:
        st.header("🎓 Сурагчийн суралцах хэсэг")

    # Нийт үгсийн жагсаалт харуулах
    st.divider()
    st.subheader("📖 Одоо байгаа физикийн нэр томьёонууд")
    st.table(pd.DataFrame(st.session_state.vocab))
