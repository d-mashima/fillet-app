import streamlit as st
import math
from sympy import symbols, Eq, solve

st.set_page_config(page_title="フィレット距離計算ツール", layout="centered")

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
st.markdown('<div class="title">幅採り数5のフィレット距離計算ツール</div>', unsafe_allow_html=True)

w = st.number_input("短側寸法 w（製品巾）", value=175.0)
d = st.number_input("長側寸法 d（製品送り）", value=175.0)
c = st.number_input("フィレット半径 c", value=5.0)
convex = st.number_input("カットからの凸", value=3.0)
z = st.number_input("全高 z", value=50.0)
max_width_limit = 970

# 固定値
mt = 20 if z >= 50 else 13
wpz = max(math.floor((20 + (convex - 20) / 2) * 0.9), 12)
if z >= 50:
    wpz = 20
wp_init = wpz
dp_init = wpz
a0 = 5
b0 = 5

# フィレット中心
mx = d / 2 - c
my = w / 2 - c

# ===== 計算 =====
def calculate():
    dp_limit = int((1100 - mt * 2) / b0 - d)
    min_ds_result = None

    for wp in range(12, 40):
        for dp in range(12, dp_limit + 1):
            wc = w + wp
            dc = d + dp
            ds = mt * 2 + dc * b0
            if ds > 1100 or a0 * wc > max_width_limit:
                continue
            L = math.sqrt((mx - dc / 2) ** 2 + (my - wc / 2) ** 2) - c - 7
            if L > 8:
                # dsが最小のものを選択
                if min_ds_result is None or ds < min_ds_result['ds']:
                    min_ds_result = {
                        'a': a0, 'b': b0, 'wp': wp, 'dp': dp,
                        'wc': wc, 'dc': dc, 'ds': ds, 'L': L,
                        'score': a0 * b0
                    }
    return min_ds_result

if st.button("計算する"):
    result = calculate()

    if result:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown("【最適化結果】")
        st.write(f"幅採り数 a = {result['a']}")
        st.write(f"送り採り数 b = {result['b']}")
        st.write(f"キャビピッチ wc = {result['wc']}")
        st.write(f"送りキャビピッチ dc = {result['dc']}")
        st.write(f"型寸送り ds（参考値） = {result['ds']}")
        st.write(f"ガイドボッチからの距離 L = {result['L']:.3f}")
        st.write(f"製品数（a×b）= {result['score']}")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("条件を満たす構成が見つかりませんでした。")

st.markdown('</div>', unsafe_allow_html=True)
