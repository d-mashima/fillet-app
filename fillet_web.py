import streamlit as st
import math
from sympy import symbols, Eq, solve

st.set_page_config(page_title="簡易割付計算", layout="centered")

# 入力項目
w = float(st.text_input("短側寸法 w（製品巾）", "161"))
d = float(st.text_input("長側寸法 d（製品送り）", "161"))
c = float(st.text_input("フィレット半径 c", "4"))
R_input = st.text_input("長側半径 R (空欄の場合は直線として扱います)", "")
r_input = st.text_input("短側半径 r (空欄の場合は直線として扱います)", "")

R = float(R_input) if R_input.strip() else None
r = float(r_input) if r_input.strip() else None

# フィレット中心の計算関数
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
                yf = y_val.evalf()
                if yf > 0:
                    return m, float(yf)

        elif not R and r:
            # 直線と円のフィレット
            x2, y2 = -r + c, 0
            n = w / 2 - c
            eq = Eq((x - x2)**2 + (n - y2)**2, (r - c)**2)
            solutions = solve(eq, x)
            for x_val in solutions:
                xf = x_val.evalf()
                if xf > 0:
                    return float(xf), n

        else:
            # 直線と直線のフィレット
            mx = d / 2 - c
            my = w / 2 - c
            return mx, my

    except Exception as e:
        return None, str(e)

# ボタンが押されたら計算
if st.button("計算する"):
    mx, my = calculate_fillet_center(w, d, c, R, r)

    if mx is not None:
        st.success(f"フィレット中心の座標 (m, n)：({mx:.3f}, {my:.3f})")
    else:
        st.error(f"計算に失敗しました。エラー詳細: {my}")
