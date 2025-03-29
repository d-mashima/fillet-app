import streamlit as st
import math
from sympy import symbols, Eq, solve

st.set_page_config(page_title="簡易割付計算", layout="centered")

# ===== スタイル =====
st.markdown('''
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
''', unsafe_allow_html=True)

# ===== 入力 =====
st.markdown('<div class="main">', unsafe_allow_html=True)
st.markdown('<div class="title">簡易割付計算</div>', unsafe_allow_html=True)

w = st.number_input("短側寸法 w（製品巾）", value=175.0)
d = st.number_input("長側寸法 d（製品送り）", value=175.0)
c = st.number_input("フィレット半径 c", value=5.0)
convex = st.number_input("カットからの凸", value=3.0)
z = st.number_input("全高 z", value=50.0)
has_inner_outer_lid = st.checkbox("内外嵌合蓋")
R_input = st.text_input("長側半径 R (空欄の場合は直線)", "")
r_input = st.text_input("短側半径 r (空欄の場合は直線)", "")
R = float(R_input) if R_input.strip() else None
r = float(r_input) if r_input.strip() else None
max_width_limit = 970

# 内外嵌合蓋がある場合、凸を8に固定
if has_inner_outer_lid:
    convex = 8.0

# ===== t 値の計算 =====
t = max(int((10 + convex / 2) * 0.9), 12)

# ===== フィレット中心の計算 =====
def calculate_fillet_center(w, d, c, R, r):
    x, y = symbols('x y', real=True)

    try:
        if R and r:
            # 円と円のフィレット
            x1, y1 = 0, -R + c
            x2, y2 = -r + c, 0
            eq1 = Eq((x - x1)**2 + (y - y1)**2, (R - c)**2)
            eq2 = Eq((x - x2)**2 + (y - y2)**2, (r - c)**2)
            solutions = solve((eq1, eq2), (x, y), dict=True)
            for sol in solutions:
                if sol[x] > 0 and sol[y] > 0:
                    return float(sol[x]), float(sol[y])

        elif R and not r:
            # 円と直線のフィレット
            x1, y1 = 0, -R + c
            m = d / 2 - c
            eq = Eq((m - x1)**2 + (y - y1)**2, (R - c)**2)
            solutions = solve(eq, y)
            for y_val in solutions:
                if y_val.evalf() > 0:
                    return m, float(y_val.evalf())

        elif not R and r:
            # 直線と円のフィレット
            x2, y2 = -r + c, 0
            n = w / 2 - c
            eq = Eq((x - x2)**2 + (n - y2)**2, (r - c)**2)
            solutions = solve(eq, x)
            for x_val in solutions:
                if x_val.evalf() > 0:
                    return float(x_val.evalf()), n

        else:
            # 直線と直線のフィレット
            mx = d / 2 - c
            my = w / 2 - c
            return mx, my

    except Exception as e:
        st.error(f"計算中にエラーが発生しました: {e}")
        return None, None

if st.button("計算する"):
    mx, my = calculate_fillet_center(w, d, c, R, r)

    if mx is not None and my is not None:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown("【フィレット中心の結果】")
        st.write(f"フィレット中心の座標 (m, n)：({mx:.3f}, {my:.3f})")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("フィレット中心の計算に失敗しました。")
