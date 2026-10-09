import streamlit as st
import json
import os

st.set_page_config(page_title="Hiệu Chỉnh La Bàn", layout="centered")

DATA_FILE = "huong_chuan.json"

# Danh sách 24 sơn hướng (Mỗi sơn chiếm 15 độ)
SON_HUONG_24 = [
    "Tý", "Quý", "Sửu", "Cấn", "Dần", "Giáp", "Mão", "Ất", 
    "Thìn", "Tốn", "Tỵ", "Bính", "Ngọ", "Đinh", "Mùi", "Khôn", 
    "Thân", "Canh", "Dậu", "Tân", "Tuất", "Càn", "Hợi", "Nhâm"
]

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
    new_name = st.text_input("Tên Vị Trí")
with col2:
    new_angle = st.number_input("Độ Chính Xác", min_value=0.0, max_value=360.0, step=0.1)

if st.button("Lưu Thông Tin"):
    if new_name:
        st.session_state.saved_angles[new_name] = new_angle
        save_data(st.session_state.saved_angles)
        st.rerun()

# Danh sach da luu
if st.session_state.saved_angles:
    st.write("Các Vị Trí Đã Lưu:")
    for name, angle in st.session_state.saved_angles.items():
        c1, c2 = st.columns([3, 1])
        c1.write(f"- {name}: {angle} độ")
        if c2.button("Xóa", key=f"del_{name}"):
            del st.session_state.saved_angles[name]
            save_data(st.session_state.saved_angles)
            st.rerun()

st.markdown("---")

# --- PHAN 2: TINH TOAN HUONG ---
st.header("2. Tính Toán Thực Tế")

# Chon huong
if st.session_state.saved_angles:
    options = ["Tự Nhập Bên Dưới..."] + list(st.session_state.saved_angles.keys())
    choice = st.selectbox("Chọn Hướng Đã Lưu:", options)
    
    if choice != "Tự Nhập Bên Dưới...":
        default_true_angle = st.session_state.saved_angles[choice]
    else:
        default_true_angle = 0.0
else:
    default_true_angle = 0.0

# 2 O nhap lieu thong so co ban
huong_chinh_xac = st.number_input("Hướng Chính Xác", min_value=0.0, max_value=360.0, value=float(default_true_angle), step=0.1)
huong_do_duoc = st.number_input("Hướng Đo Được", min_value=0.0, max_value=360.0, value=0.0, step=0.1)

st.write("") # Tao khoang trang

# --- PHAN CHON CHE DO ---
che_do = st.radio("Chọn chức năng:", ["Tìm Sơn", "Đo Hướng"], horizontal=True)

# Hien thi o nhap lieu hoac chon lua tuy thuoc vao che do
if che_do == "Đo Hướng":
    huong_can_do = st.number_input("Hướng La Bàn Đo", min_value=0.0, max_value=360.0, value=0.0, step=0.1)
else:
    son_can_tim = st.selectbox("Chọn 1 trong 24 Sơn:", SON_HUONG_24)

# Xu ly phep tinh
if st.button("Kết Quả", type="primary", use_container_width=True):
    chenh_lech = huong_chinh_xac - huong_do_duoc
    
    st.write("---")
    
    if che_do == "Đo Hướng":
        # Tinh toan huong thuc te tu so la ban
        ket_qua = (huong_can_do + chenh_lech) % 360
        index = int(((ket_qua + 7.5) % 360) / 15)
        son_huong = SON_HUONG_24[index]
        
        st.subheader(f"KẾT QUẢ: {ket_qua:.1f} độ - {son_huong}")
        
    else: # Che do "Tim Son"
        # Lay tam do cua Son tren thuc te (Vi du: Ty la 0 do)
        index_son = SON_HUONG_24.index(son_can_tim)
        tam_son_thuc_te = index_son * 15
        
        # Bien do cua Son la +- 7.5 do
        bat_dau_thuc_te = tam_son_thuc_te - 7.5
        ket_thuc_thuc_te = tam_son_thuc_te + 7.5
        
        # Ap dung do lech de ra so tren La ban
        bat_dau_la_ban = (bat_dau_thuc_te - chenh_lech) % 360
        ket_thuc_la_ban = (ket_thuc_thuc_te - chenh_lech) % 360
        
        st.subheader(f"KẾT QUẢ TÌM SƠN {son_can_tim.upper()}:")
        st.info(f"Từ **{bat_dau_la_ban:.1f} độ** đến **{ket_thuc_la_ban:.1f} độ**")
