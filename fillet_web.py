
import math

# 入力値
w = 175.0
d = 175.0
c = 5.0
convex = 3.0
z = 50.0
has_inner_outer_lid = False
max_width_limit = 975

# 内外嵌合蓋がある場合、凸を8に固定
if has_inner_outer_lid:
    convex = 8.0

# 固定値
mt = 20 if z >= 50 else 13
wpz = max(math.floor((20 + (convex - 20) / 2) * 0.9), 12)
if z >= 50:
    wpz = 20

# フィレット中心の計算
mx = d / 2 - c
my = w / 2 - c

# 初期化
a0 = math.floor(max_width_limit / (w + wpz))
b0 = math.floor((1100 - mt * 2) / (d + wpz))

# 最適化関数
def optimize_adjusted(a_ref, b_ref):
    best = None
    wp_range = range(1, int(max_width_limit / a_ref - w) + 1)
    dp_limit = int((1100 - mt * 2) / b_ref - d)
    dp_range = range(1, dp_limit + 1)

    for wp in wp_range:
        for dp in dp_range:
            if wp < 1 or dp < 1:
                continue
            a = min(a_ref, math.floor(max_width_limit / (w + wp)))
            b = min(b_ref, math.floor((1100 - mt * 2) / (d + dp)))
            if a == 0 or b == 0:
                continue
            wc = w + wp
            dc = d + dp
            ds = mt * 2 + (d + dp) * b
            L = math.sqrt((mx - dc / 2) ** 2 + (my - wc / 2) ** 2) - c - 7
            if L > 8:
                score = a * b
                if (best is None or
                    score > best['score'] or
                    (score == best['score'] and ds < best['ds'])):
                    best = {
                        'a': a, 'b': b, 'wp': wp, 'dp': dp,
                        'wc': wc, 'dc': dc, 'ds': ds, 'L': L,
                        'score': score
                    }
    return best

# 最適化実行
result_adjusted = optimize_adjusted(a0, b0)

# 横取り判定
a = result_adjusted['a']
wc = result_adjusted['wc']
horizontal_check = a * wc <= max_width_limit

# 出力
print("最適化結果:", result_adjusted)
print("横取り判定 (True=OK / False=NG):", horizontal_check)
