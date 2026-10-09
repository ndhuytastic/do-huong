import streamlit as st
import json
import os

st.set_page_config(page_title="Hiệu Chỉnh La Bàn", layout="centered")

DATA_FILE = "huong_chuan.json"

# Ham doc/ghi du lieu
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Khoi tao bien luu tru
if "saved_angles" not in st.session_state:
    st.session_state.saved_angles = load_data()

st.title("Hiệu Chỉnh La Bàn")

# --- PHAN 1: QUAN LY HUONG CHUAN ---
st.header("1. Quản Lý")

# Form them moi
col1, col2 = st.columns([2, 1])
with col1:
    new_name = st.text_input("Ten vi tri")
with col2:
    new_angle = st.number_input("Độ Chính Xác", min_value=0.0, max_value=360.0, step=0.1)

if st.button("Lưu Thông Tin"):
    if new_name:
        st.session_state.saved_angles[new_name] = new_angle
        save_data(st.session_state.saved_angles)
        st.rerun()

# Danh sach da luu
if st.session_state.saved_angles:
    st.write("Cac vi tri da luu:")
    for name, angle in st.session_state.saved_angles.items():
        c1, c2 = st.columns([3, 1])
        c1.write(f"- {name}: {angle} do")
        if c2.button("Xoa", key=f"del_{name}"):
            del st.session_state.saved_angles[name]
            save_data(st.session_state.saved_angles)
            st.rerun()

st.markdown("---")

# --- PHAN 2: TINH TOAN HUONG ---
st.header("2. Tính Toán Thực Tế")

# Chon huong
if st.session_state.saved_angles:
    options = ["Tu nhap so..."] + list(st.session_state.saved_angles.keys())
    choice = st.selectbox("Chọn Hướng Đã Lưu:", options)
    
    if choice != "Tu nhap so...":
        default_true_angle = st.session_state.saved_angles[choice]
    else:
        default_true_angle = 0.0
else:
    default_true_angle = 0.0

# 3 O nhap lieu
huong_chinh_xac = st.number_input("Hướng Chính Xác", min_value=0.0, max_value=360.0, value=float(default_true_angle), step=0.1)
huong_do_duoc = st.number_input("Hướng Đo Được", min_value=0.0, max_value=360.0, value=0.0, step=0.1)
huong_can_do = st.number_input("Hướng La Bàn Đo", min_value=0.0, max_value=360.0, value=0.0, step=0.1)

# Xu ly phep tinh
if st.button("Kết Quả", type="primary", use_container_width=True):
    # Tinh toan do lech va ap dung vao huong can do
    chenh_lech = huong_chinh_xac - huong_do_duoc
    ket_qua = (huong_can_do + chenh_lech) % 360
    
    st.write("---")
    st.subheader(f"KẾT QUẢ: {ket_qua:.1f} do")
