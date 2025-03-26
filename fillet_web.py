import streamlit as st
from sympy import symbols, Eq, solve
import math

# ページ設定
st.set_page_config(page_title="フィレット距離計算ツール", layout="centered")

# HTML風スタイル追加
st.markdown("""
<style>
    html, body {
        font-family: "メイリオ", "MS Pゴシック", sans-serif;
    }
    .block-container {
        max-width: 400px;
        padding-top: 1rem;
        margin: auto;
    }
    label {
        font-weight: bold;
        font-size: 12px !important;
    }
    input[type="number"] {
        text-align: center;
    }
    .stNumberInput > div > input {
        font-size: 12px !important;
        text-align: center !important;
    }
    .stTextInput > div > input {
        font-size: 12px !important;
        text-align: center !important;
    }
    .result-box {
        background-color: #dff0d8;
        border: 1px solid #c3e6cb;
        padding: 10px;
        border-radius: 6px;
        font-size: 12px;
    }
    .section-title {
        background-color: #005bac;
        color: white;
        padding: 6px;
        font-size: 14px;
        text-align: center;
        border-radius: 4px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">割り付け＋フィレット距離計算ツール</div>', unsafe_allow_html=True)

# ===== 入力 =====
w = st.number_input("短側寸法 w（製品巾）", value=100.0)
d = st.number_input("長側寸法 d（製品送り）", value=200.0)
c = st.number_input("フィレット半径 c", value=10.0)
convex = st.number_input("凸（convex）", value=10.0)
z = st.number_input("全高 z", value=40.0)
R_input = st.text_input("短側の円半径（R, 式①）", value="")
r_input = st.text_input("長側の円半径（r, 式②）", value="")

use_circle1 = R_input.strip() != ""
use_circle2 = r_input.strip() != ""

try:
    R = float(R_input) if use_circle1 else None
    r = float(r_input) if use_circle2 else None

    # ===== 割り付けロジック =====
    mt = 13 if z < 50 else 20
    wpz_base = (20 + (convex - 20) / 2) * 0.9
    wpz = max(math.floor(wpz_base), 12)
    if z >= 50:
        wpz = 20
    dp = wpz

    a = math.floor(960 / (wpz + w))
    wp = math.floor((960 % (wpz + w)) / a) + wpz
    b = math.floor((1100 - mt * 2) / (d + dp))

    wc = w + wp
    dc = d + dp

    st.markdown('<div class="section-title">計算結果</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="result-box">
        幅採り数 a = {a}<br>
        送り採り数 b = {b}<br>
        キャビピッチ wc = {wc}<br>
        キャビピッチ dc = {dc}<br>
    """, unsafe_allow_html=True)

    # ===== フィレット中心計算 =====
    x, y = symbols('x y', real=True)
    mx, my = None, None

    if use_circle1 and use_circle2:
        x1, y1 = 0.0, -R + w / 2
        x2, y2 = -r + d / 2, 0.0
        eq1 = Eq((x - x1)**2 + (y - y1)**2, (R - c)**2)
        eq2 = Eq((x - x2)**2 + (y - y2)**2, (r - c)**2)
        solutions = solve((eq1, eq2), (x, y), dict=True)
        for sol in solutions:
            if sol[x].evalf() > 0 and sol[y].evalf() > 0:
                mx = float(sol[x].evalf())
                my = float(sol[y].evalf())
                break
    elif use_circle1:
        m = d / 2 - c
        center_x, center_y = 0, -R + w / 2
        eq = Eq((m - center_x)**2 + (y - center_y)**2, (R - c)**2)
        sols = solve(eq, y)
        for y_val in sols:
            yf = y_val.evalf()
            if yf > 0:
                mx = m
                my = float(yf)
                break
    elif use_circle2:
        n = w / 2 - c
        center_x, center_y = -r + d / 2, 0
        eq = Eq((x - center_x)**2 + (n - center_y)**2, (r - c)**2)
        sols = solve(eq, x)
        for x_val in sols:
            xf = x_val.evalf()
            if xf > 0:
                mx = float(xf)
                my = n
                break
    else:
        mx = d / 2 - c
        my = w / 2 - c

    if mx is None or my is None:
        st.error("第1象限に有効なフィレット中心が見つかりませんでした。")
        st.stop()

    # ===== 新定義の L =====
    L = math.sqrt((mx - dc / 2) ** 2 + (my - wc / 2) ** 2) - c

    st.markdown(f"""
        フィレット中心 (mx, my) = ({mx:.3f}, {my:.3f})<br>
        距離 L = √((mx - dc/2)² + (my - wc/2)²) - c = {L:.3f}
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"エラーが発生しました: {str(e)}")
