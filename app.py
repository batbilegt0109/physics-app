# Энэ кодыг Google Colab эсвэл python орчинд ажиллуулна
import streamlit as st

# Хуудасны үндсэн тохиргоо
st.set_page_config(page_title="Миний Физикийн Апп", page_icon="📚")

# 1. Системд бүртгэлтэй хэрэглэгчид (Өөрөө хүссэнээрээ нэмж хасаж болно)
if "users" not in st.session_state:
    st.session_state.users = {
        "bagsh": {"password": "123", "role": "Багш", "name": "Үндсэн Багш"},
        "surgach1": {"password": "456", "role": "Сурагч", "name": "Билгүүн"},
        "surgach2": {"password": "789", "role": "Сурагч", "name": "Хүслэн"}
    }

# 2. Физикийн шинэ үгсийн сан
if "vocabulary" not in st.session_state:
    st.session_state.vocabulary = [
        {"term": "Inertia", "definition": "Инерци - Бие анхны төлөвөө хадгалах чанар"},
        {"term": "Velocity", "definition": "Хурд - Чиглэл бүхий хурдны хэмжээ"}
    ]

# --- НЭВТРЭХ ХЭСЭГ ---
st.title("🔐 Системд нэвтрэх")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.role = None

if not st.session_state.logged_in:
    username = st.text_input("Нэвтрэх нэр (Username)")
    password = st.text_input("Нууц үг (Password)", type="password")
    
    if st.button("Нэвтрэх"):
        if username in st.session_state.users and st.session_state.users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.session_state.role = st.session_state.users[username]["role"]
            st.rerun()
        else:
            st.error("Нэвтрэх нэр эсвэл нууц үг буруу байна!")
else:
    # --- ХЭРВЭЭ НЭВТРЭСЭН БОЛ ---
    user_info = st.session_state.users[st.session_state.current_user]
    st.sidebar.success(f"Тавтай морил, {user_info['name']} ({user_info['role']})")
    
    if st.sidebar.button("Гарах (Log out)"):
        st.session_state.logged_in = False
        st.rerun()

    # А. ХЭРВЭЭ БАГШ БОЛ
    if st.session_state.role == "Багш":
        st.header("👩‍🏫 Багшийн удирдлагын самбар")
        
        tab1, tab2 = st.tabs(["📚 Шинэ үг нэмэх", "👥 Хэрэглэгч удирдах (Нэмэх/Хасах)"])
        
        with tab1:
            st.subheader("Физикийн шинэ нэр томьёо нэмэх")
            new_t = st.text_input("Термин / Англи үг")
            new_d = st.text_input("Монгол тайлбар")
            if st.button("Үг нэмэх"):
                if new_t and new_d:
                    st.session_state.vocabulary.append({"term": new_t, "definition": new_d})
                    st.success(f"'{new_t}' амжилттай нэмэгдлээ!")
                else:
                    st.warning("Бүх талбарыг бөглөнө үү.")
            
            st.write("Одоо байгаа үгс:")
            st.write(st.session_state.vocabulary)
            
        with tab2:
            st.subheader("Шинэ сурагч эсвэл багш бүртгэх")
            new_user_name = st.text_input("Шинэ нэвтрэх нэр")
            new_pass = st.text_input("Шинэ нууц үг")
            new_role = st.selectbox("Эрх", ["Сурагч", "Багш"])
            full_name = st.text_input("Сурагчийн бүтэн нэр")
            
            if st.button("Хэрэглэгч бүртгэх"):
                if new_user_name and new_pass:
                    st.session_state.users[new_user_name] = {
                        "password": new_pass, 
                        "role": new_role, 
                        "name": full_name
                    }
                    st.success(f"'{full_name}' амжилттай бүртгэгдлээ!")

    # Б. ХЭРВЭЭ СУРАГЧ БОЛ
    elif st.session_state.role == "Сурагч":
        st.header("📖 Сурагчийн цэс: Шинэ үг цээжлэх")
        st.write("Багшийн оруулсан физикийн нэр томьёонууд:")
        
        for idx, item in enumerate(st.session_state.vocabulary):
            with st.expander(f"Карт #{idx+1}: {item['term']}"):
                if st.button(f"Тайлбар харах {idx}", key=f"btn_{idx}"):
                    st.info(item['definition'])