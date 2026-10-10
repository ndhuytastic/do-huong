import streamlit as st
import json
import requests

st.set_page_config(page_title="Hiệu Chỉnh La Bàn", layout="centered")

# --- KẾT NỐI VỚI CLOUD JSONBIN ---
try:
    BIN_ID = st.secrets["BIN_ID"]
    API_KEY = st.secrets["API_KEY"]
except:
    st.error("❌ Chưa cấu hình API Key trong Streamlit Secrets!")
    st.stop()

URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {
    "X-Master-Key": API_KEY,
    "Content-Type": "application/json"
}

# Hàm Đọc dữ liệu từ Cloud (Có báo lỗi)
def load_data():
    try:
        response = requests.get(URL, headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("record", {})
        else:
            st.error(f"❌ Lỗi Tải Dữ Liệu: {response.status_code} - {response.text}")
            return {}
    except Exception as e:
        st.error(f"❌ Lỗi mạng khi tải: {e}")
        return {}

# Hàm Ghi dữ liệu lên Cloud (Có báo lỗi)
def save_data(data):
    try:
        response = requests.put(URL, json=data, headers=HEADERS)
        if response.status_code != 200:
            st.error(f"❌ Lỗi Lưu Dữ Liệu: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"❌ Lỗi mạng khi lưu: {e}")

# Danh sách 24 sơn hướng
SON_HUONG_24 = [
    "Tý", "Quý", "Sửu", "Cấn", "Dần", "Giáp", "Mão", "Ất", 
    "Thìn", "Tốn", "Tỵ", "Bính", "Ngọ", "Đinh", "Mùi", "Khôn", 
    "Thân", "Canh", "Dậu", "Tân", "Tuất", "Càn", "Hợi", "Nhâm"
]

# Khoi tao bien luu tru 
if "saved_angles" not in st.session_state:
    st.session_state.saved_angles = load_data()

st.title("Hiệu Chỉnh La Bàn")

# --- PHAN 1: QUAN LY HUONG CHUAN ---
st.header("1. Quản Lý")

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

if st.session_state.saved_angles:
    options = ["Tự Nhập Bên Dưới..."] + list(st.session_state.saved_angles.keys())
    choice = st.selectbox("Chọn Hướng Đã Lưu:", options)
    
    if choice != "Tự Nhập Bên Dưới...":
        default_true_angle = st.session_state.saved_angles[choice]
    else:
        default_true_angle = 0.0
else:
    default_true_angle = 0.0

huong_chinh_xac = st.number_input("Hướng Chính Xác", min_value=0.0, max_value=360.0, value=float(default_true_angle), step=0.1)
huong_do_duoc = st.number_input("Hướng Đo Được", min_value=0.0, max_value=360.0, value=0.0, step=0.1)

st.write("") 

che_do = st.radio("Chọn chức năng:", ["Tìm Sơn", "Đo Hướng"], horizontal=True)

if che_do == "Đo Hướng":
    huong_can_do = st.number_input("Hướng La Bàn Đo", min_value=0.0, max_value=360.0, value=0.0, step=0.1)
else:
    son_can_tim = st.selectbox("Chọn 1 trong 24 Sơn:", SON_HUONG_24)

if st.button("Kết Quả", type="primary", use_container_width=True):
    chenh_lech = huong_chinh_xac - huong_do_duoc
    st.write("---")
    
    if che_do == "Đo Hướng":
        ket_qua = (huong_can_do + chenh_lech) % 360
        index = int(((ket_qua + 7.5) % 360) / 15)
        son_huong = SON_HUONG_24[index]
        st.subheader(f"KẾT QUẢ: {ket_qua:.1f} độ - {son_huong}")
        
    else:
        index_son = SON_HUONG_24.index(son_can_tim)
        tam_son_thuc_te = index_son * 15
        
        bat_dau_thuc_te = tam_son_thuc_te - 7.5
        ket_thuc_thuc_te = tam_son_thuc_te + 7.5
        
        bat_dau_la_ban = (bat_dau_thuc_te - chenh_lech) % 360
        ket_thuc_la_ban = (ket_thuc_thuc_te - chenh_lech) % 360
        
        st.subheader(f"KẾT QUẢ TÌM SƠN {son_can_tim.upper()}:")
        st.write(f"Trên la bàn của bạn, sơn **{son_can_tim}** sẽ hiển thị nằm trong khoảng:")
        st.info(f"Từ **{bat_dau_la_ban:.1f} độ** đến **{ket_thuc_la_ban:.1f} độ**")
