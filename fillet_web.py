import streamlit as st
import math

st.set_page_config(page_title="簡易割付計算", layout="centered")

# ===== スタイル =====
st.markdown("""
    <style>
    .main {
        max-width: 360px;
        margin: auto;
        background-color: white;
        padding: 20px 30px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        font-family: "メイリオ", sans-serif;
    }
    .title {
        background-color: #005bac;
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-size: 16px;
        text-align: center;
    }
    .section {
        background-color: #e9f5ff;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        font-size: 13px;
    }
    .alert {
        color: red;
        font-weight: bold;
        text-align: center;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ===== 入力 =====
st.markdown('<div class="main">', unsafe_allow_html=True)
st.markdown('<div class="title">簡易割付計算</div>', unsafe_allow_html=True)

w_input = st.text_input("短側寸法 w（製品巾）")
d_input = st.text_input("長側寸法 d（製品送り）")
c_input = st.text_input("フィレット半径 c")
convex_input = st.text_input("カットからの凸")
z_input = st.text_input("全高 z")
R_input = st.text_input("長側半径 R (空欄の場合は直線として扱います)")
r_input = st.text_input("短側半径 r (空欄の場合は直線として扱います)")
has_inner_outer_lid = st.checkbox("内外嵌合蓋")
max_width_limit = 970

# 入力値のバリデーション
def validate_input(value, name):
    if not value.strip():
        st.error(f"{name} が入力されていません。")
        st.stop()
    try:
        return float(value)
    except ValueError:
        st.error(f"{name} は数値で入力してください。")
        st.stop()

w = validate_input(w_input, "短側寸法 w")
d = validate_input(d_input, "長側寸法 d")
c = validate_input(c_input, "フィレット半径 c")
convex = validate_input(convex_input, "カットからの凸")
z = validate_input(z_input, "全高 z")

# 内外嵌合蓋がある場合、凸を8に固定
if has_inner_outer_lid:
    convex = 8.0

# Rとrの入力チェック（空欄の場合は直線として扱う）
use_circle1 = R_input.strip() != ""
use_circle2 = r_input.strip() != ""

R = float(R_input) if use_circle1 else None
r = float(r_input) if use_circle2 else None

# 固定値
mt = 20 if z >= 50 else 13
wpz = max(math.floor((20 + (convex - 20) / 2) * 0.9), 12)
if z >= 50:
    wpz = 20
wp_init = wpz
dp_init = wpz
a0 = math.floor(960 / (w + wpz))
b0 = math.floor((1100 - mt * 2) / (d + wpz))

# t値の計算
t = math.floor((10 + convex / 2) * 0.9)
additional_margin = 5 if has_inner_outer_lid else 0

# フィレット中心
mx = d / 2 - c
my = w / 2 - c

# ファイルに保存
file_path = '/mnt/data/simple_layout_tool_with_empty_defaults.py'
with open(file_path, 'w') as f:
    f.write(code)

file_path
