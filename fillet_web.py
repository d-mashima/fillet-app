import streamlit as st
from sympy import symbols, Eq, solve
import math

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
    input[type=number], input[type=text] {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

def calc_optimal(w, d, c, convex, z, R, r):
    mt = 13 if z < 50 else 20
    wpz = max(math.floor((20 + (convex - 20) / 2) * 0.9), 12)
    if z >= 50:
        wpz = 20
    wp_init = wpz
    dp_init = wpz

    # 960 → 970 に変更
    a0 = math.floor(970 / (w + wpz))
    b0 = math.floor((1100 - mt * 2) / (d + wpz))

    # フィレット中心
    x, y = symbols('x y', real=True)
    mx = my = None
    if R and r:
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
    elif R:
        m = d / 2 - c
        center_x, center_y = 0, -R + w / 2
        eq = Eq((m - center_x)**2 + (y - center_y)**2, (R - c)**2)
        sols = solve(eq, y)
        for y_val in sols:
            if y_val.evalf() > 0:
                mx = m
                my = float(y_val.evalf())
                break
    elif r:
        n = w / 2 - c
        center_x, center_y = -r + d / 2, 0
        eq = Eq((x - center_x)**2 + (n - center_y)**2, (r - c)**2)
        sols = solve(eq, x)
        for x_val in sols:
            if x_val.evalf() > 0:
                mx = float(x_val.evalf())
                my = n
                break
    else:
        mx = d / 2 - c
        my = w / 2 - c

    if mx is None or my is None:
        return None

    def evaluate(a_ref, b_ref, unrestricted=False, force_wp=None):
        best = None
        wp_range = [force_wp] if force_wp else range(wp_init, wp_init + 4)
        dp_range = range(dp_init, dp_init + 4) if not unrestricted else range(1, int((1100 - mt * 2) / b_ref - d) + 1)

        for wp in wp_range:
            for dp in dp_range:
                if wp < 1 or dp < 1:
                    continue
                for a_ref_try in range(a_ref, math.floor(974 / (w + wp)) + 1):
                    a = min(a_ref_try, math.floor(974 / (w + wp)))
                    b = min(b_ref, math.floor((1100 - mt * 2) / (d + dp)))
                    if a == 0 or b == 0:
                        continue
                    wc = w + wp
                    dc = d + dp
                    ds = mt * 2 + (d + dp) * b
                    L = math.sqrt((mx - dc / 2) ** 2 + (my - wc / 2) ** 2) - c - 7
                    if L > 8:
                        score = a * b
                        if (best is None or score > best['score'] or (score == best['score'] and ds < best['ds'])):
                            best = dict(a=a, b=b, wp=wp, dp=dp, wc=wc, dc=dc, ds=ds, L=L, score=score)
        return best

    result = evaluate(a0, b0, unrestricted=False)
    return result
