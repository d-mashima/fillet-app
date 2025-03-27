import streamlit as st
from sympy import symbols, Eq, solve
import math

st.set_page_config(page_title="フィレット距離計算ツール", layout="centered")

# ========== スタイル ========== #
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

# ========== 最適化ロジック関数 ========== #
def calc_optimal(w, d, c, convex, z, R, r):
    mt = 13 if z < 50 else 20
    wpz = max(math.floor((20 + (convex - 20) / 2) * 0.9), 12)
    if z >= 50:
        wpz = 20
    wp_init = wpz
    dp_init = wpz
    a0 = math.floor(960 / (w + wpz))
    b0 = math.floor((1100 - mt * 2) / (d + wpz))

    # フィレット中心（式①,②が直線なら）
    x, y = symbols('x y', real=True)
    mx = d / 2 - c
    my = w / 2 - c
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

    # 候補評価関数
    def evaluate(a_ref, b_ref, unrestricted=False, force_wp=None):
        results = []
        wp_range = [force_wp] if force_wp else range(12, 40)
        dp_range = range(12, int((1100 - mt * 2) / b_ref - d) + 1) if unrestricted else range(dp_init, dp_init + 4)
        for wp in wp_range:
            for dp in dp_range:
                wc = w + wp
                dc = d + dp
                ds = mt * 2 + dc * b_ref
                if ds > 1100:
                    continue
                L = math.sqrt((mx - dc / 2) ** 2 + (my - wc / 2) ** 2) - c - 7
                if L > 8:
                    a = min(a_ref, math.floor(960 / (w + wp)))
                    b = min(b_ref, math.floor((1100 - mt * 2) / (d + dp)))
                    results.append({
                        'a': a, 'b': b, 'wp': wp, 'dp': dp,
                        'wc': wc, 'dc': dc, 'ds': ds, 'L': L,
                        'score': a * b
                    })
        return results

    # a0,b0 固定で自由探索（最優先）
    candidates = evaluate(a0, b0, unrestricted=True)

    # 次に a-1, b-1 を試す
    if a0 > 1:
        wp_eq = math.floor((960 - w * (a0 - 1)) / (a0 - 1))
        candidates += evaluate(a0 - 1, b0, unrestricted=True, force_wp=wp_eq)
    if b0 > 1:
        candidates += evaluate(a0, b0 - 1, unrestricted=True)

    if candidates:
        return max(candidates, key=lambda x: (x['b'], x['score'], -x['ds']))
    else:
        return None

# ========== 入力UI ========== #
st.markdown('<div class="main">', unsafe_allow_html=True)
st.markdown('<div class="title">割り付け＋フィレット距離計算ツール</div>', unsafe_allow_html=True)

w = st.number_input("短側寸法 w（製品巾）", value=100.0)
d = st.number_input("長側寸法 d（製品送り）", value=200.0)
c = st.number_input("フィレット半径 c", value=10.0)
convex = st.number_input("凸（convex）", value=15.0)
z = st.number_input("全高 z", value=16.0)
R_input = st.text_input("短側の円半径（R, 式①）", value="")
r_input = st.text_input("長側の円半径（r, 式②）", value="")

try:
    R = float(R_input) if R_input.strip() else None
    r = float(r_input) if r_input.strip() else None

    result_normal = calc_optimal(w, d, c, convex, z, R, r)
    result_rotated = calc_optimal(d, w, c, convex, z, r, R)

    if result_normal:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown("【最適化結果】")
        st.write(f"幅採り数 a = {result_normal['a']}")
        st.write(f"送り採り数 b = {result_normal['b']}")
        st.write(f"キャビピッチ wc = {result_normal['wc']}")
        st.write(f"キャビピッチ dc = {result_normal['dc']}")
        st.write(f"型寸送り ds = {result_normal['ds']}")
        st.write(f"フィレット距離 L = {result_normal['L']:.3f}")
        st.write(f"製品数（a×b）= {result_normal['score']}")
        st.markdown('<span style="color: green;">※Lが8以下を回避するよう最適化されました。</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if result_rotated and result_rotated['score'] > result_normal['score']:
            st.markdown(f'<div class="alert">※横取りの可能性あり（a×b = {result_rotated["score"]}）</div>', unsafe_allow_html=True)

    else:
        st.error("L > 8 を満たす割り付けが見つかりませんでした。")

except Exception as e:
    st.error(f"エラーが発生しました: {str(e)}")

st.markdown('</div>', unsafe_allow_html=True)