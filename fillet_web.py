import streamlit as st
import math
from sympy import symbols, Eq, solve

st.set_page_config(page_title="簡易割付計算", layout="centered")

# 入力項目
w = float(st.text_input("短側寸法 w（製品巾）", "161"))
d = float(st.text_input("長側寸法 d（製品送り）", "161"))
c = float(st.text_input("フィレット半径 c", "4"))
convex_input = st.text_input("カットからの凸", "15")
R_input = st.text_input("長側半径 R (空欄の場合は直線として扱います)", "")
r_input = st.text_input("短側半径 r (空欄の場合は直線として扱います)", "")
has_inner_outer_lid = st.checkbox("内外嵌合蓋")

R = float(R_input) if R_input.strip() else None
r = float(r_input) if r_input.strip() else None
convex = float(convex_input)

# ===== 内外嵌合蓋の処理 =====
if has_inner_outer_lid:
    convex = 8.0

# ===== t の計算 =====
t = int((10 + convex / 2) * 0.9)

# ===== フィレット中心の計算関数 =====
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

# ===== 横取り判定 =====
def check_side_pick(a, b, dc, wc):
    alt_a = max(t, int(1100 / dc))
    alt_b = max(t, int(960 / wc))
    return alt_a * alt_b > a * b

# ===== ボタンが押されたら計算 =====
if st.button("計算する"):
    mx, my = calculate_fillet_center(w, d, c, R, r)

    if mx is not None:
        # 仮のキャビピッチ
        dc = d + 20
        wc = w + 20

        # フィレット距離 L の計算
        L = math.sqrt((mx - dc / 2) ** 2 + (my - wc / 2) ** 2) - c - 7

        # 幅採り数と送り採り数の計算
        a = max(t, int(960 / dc))
        b = max(t, int(1100 / wc))

        # dsの計算（型寸送り・参考値）
        ds = dc * a

        # 横取り判定
        side_pick = check_side_pick(a, b, dc, wc)
        side_pick_message = "横取りの可能性あり" if side_pick else "横取りの可能性なし"

        # 結果の表示
        st.success(f"フィレット中心の座標 (m, n)：({mx:.3f}, {my:.3f})")
        st.write(f"幅採り数: {a}")
        st.write(f"送り採り数: {b}")
        st.write(f"幅方向キャビピッチ (wc): {wc}")
        st.write(f"送り方向キャビピッチ (dc): {dc}")
        st.write(f"フィレット距離 L（ガイドボッチからの距離）: {L:.3f}")
        st.write(f"型寸送り (参考値) ds: {ds}")
        st.write(side_pick_message)
    else:
        st.error(f"計算に失敗しました。エラー詳細: {my}")
