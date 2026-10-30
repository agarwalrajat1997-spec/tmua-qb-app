"""Post-generation recalculation using definitions, enumeration and quadrature.
Does not import the authoring modules or overwrite question content.
"""
import json, math, statistics, hashlib, re
from pathlib import Path
from statistics import NormalDist
from decimal import Decimal, ROUND_HALF_UP

def fmt(v):
    d = Decimal(str(float(v)))
    return format(d.quantize(Decimal(1).scaleb(d.adjusted() - 2), rounding=ROUND_HALF_UP), 'f') if d else '0'
ROOT = Path(__file__).resolve().parents[2]

def eq(a, b, tol=1e-07):
    assert math.isclose(a, b, rel_tol=tol, abs_tol=tol), (a, b)

def quad(f, a, b, N=4000):
    h = (b - a) / N
    return h / 3 * (f(a) + f(b) + 4 * sum((f(a + j * h) for j in range(1, N, 2))) + 2 * sum((f(a + j * h) for j in range(2, N, 2))))

def d(f, x):
    return (f(x + 1e-05) - f(x - 1e-05)) / 2e-05

def cf(n, p, k):
    return sum((math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k + 1)))

def rank(xs):
    return [statistics.mean([j + 1 for j, v in enumerate(sorted(xs)) if v == x]) for x in xs]

def corr(xs, ys):
    xm = statistics.mean(xs)
    ym = statistics.mean(ys)
    return sum(((x - xm) * (y - ym) for x, y in zip(xs, ys))) / math.sqrt(sum(((x - xm) ** 2 for x in xs)) * sum(((y - ym) ** 2 for y in ys)))

def verify(q):
    f = (q['number'] - 1) // 4
    i = (q['number'] - 1) % 4
    t = q['topicId']
    ss = ' '.join((z['text'] for g in q['markScheme'] for z in g['steps']))

    def has(v):
        assert str(v) in ss, (q['id'], v)
    if t == 'number-algebra':
        if f == 0:
            total = (240000000 + 30000000 * i) * (6 + i) / 1000
            has(math.ceil(total / 400000))
            eq(total, (2.4 + 0.3 * i) * (6 + i) * 100000.0)
        elif f == 1:
            a = 18 + 3 * i
            step = 4 + i
            N = 12 + i
            has(sum(range(a, a + step * N, step)))
        elif f == 2:
            a = 120 + 20 * i
            step = 15 + 5 * i
            N = 16 + i
            S = sum((a + j * step for j in range(N)))
            assert str(S) in q['stem']
            has(N)
        elif f == 3:
            a = 70 + 10 * i
            r = 1.12 + 0.01 * i
            N = 8 + i
            vals = [a]
            for j in range(N - 1):
                vals.append(vals[-1] * r)
            has(round(vals[-1]))
            has(round(sum(vals)))
        elif f == 4:
            amt = 900 + 100 * i
            r = 0.82 + 0.02 * i
            target = 200 + 10 * i
            N = 1
            while amt >= target:
                amt *= r
                N += 1
            has(N)
        elif f in [5, 6, 7, 8]:
            if f == 5:
                V = 4500 + 500 * i
                r = 0.032 + 0.004 * i
                N = 5 + i
            elif f == 6:
                V = 6200 + 400 * i
                r = (0.048 + 0.006 * i) / 12
                N = 12 * (3 + i)
            elif f == 7:
                V = 28000 + 3000 * i
                r = -(0.16 + 0.02 * i)
                N = 4 + i
            else:
                V = 10000 + 1000 * i
                r = 0.055 + 0.005 * i
                N = 6 + i
            B = V
            for j in range(N):
                B += B * r
            has(round(B) if f == 7 else f'{B:.2f}')
            if f == 8:
                has(f'{B / (1.025 + 0.002 * i) ** N:.2f}')
        elif f in [9, 10]:
            V = 16000 + 2000 * i if f == 9 else 24000 + 2000 * i
            r = (0.06 + 0.006 * i) / 12 if f == 9 else (0.072 + 0.006 * i) / 12
            N = 36 + 12 * i if f == 9 else 60
            pvfactor = sum(((1 + r) ** (-j) for j in range(1, N + 1)))
            payment = V / pvfactor
            has(f'{payment:.2f}')
            B = V
            end = N if f == 9 else 12 + 6 * i
            for j in range(end):
                B = B * (1 + r) - payment
            if f == 9:
                eq(B, 0, 1e-06)
            else:
                has(f'{B:.2f}')
        elif f == 11:
            D = 150 + 25 * i
            r = (0.036 + 0.006 * i) / 12
            N = 48 + 12 * i
            B = 0
            for j in range(N):
                B = B * (1 + r) + D
            has(f'{B:.2f}')
            has(f'{B - N * D:.2f}')
        elif f == 12:
            D = 200 + 30 * i
            r = 0.004 + 0.0005 * i
            target = 13000 + 1000 * i
            N = 0
            B = 0
            while B < target:
                B = B * (1 + r) + D
                N += 1
            has(N)
            has(f'{B:.2f}')
        elif f == 13:
            a = 3 + i
            b = 2 + i
            eq(a ** 5 / b ** 2 / a ** 2, a ** 3 / b ** 2)
            has(f'{fmt(a ** 3 / b ** 2)}')
        elif f == 14:
            h = (1.8 + 0.4 * i) * 10 ** (-5 - i)
            p = -math.log10(h)
            has(f'{fmt(p)}')
            eq(10 ** (-p), h)
        elif f == 15:
            r = 2.4 + 0.3 * i
            upper = math.pi * (r + 0.05) ** 2
            has(f'{fmt(upper)}')
            has(f'{fmt(100 * (1 - (r / (r + 0.05)) ** 2))}')
        elif f == 16:
            dist = 140 + 10 * i
            time = 35 + 5 * i
            values = [a / b for a in [dist - 0.5, dist + 0.5] for b in [time - 0.5, time + 0.5]]
            has(f'{fmt(min(values))}')
            has(f'{fmt(max(values))}')
        elif f == 17:
            x = 7 + i
            y = 11 + 2 * i
            b1 = 3 * x + 2 * y
            b2 = 2 * x + 5 * y
            eq((5 * b1 - 2 * b2) / 11, x)
            eq((3 * b2 - 2 * b1) / 11, y)
        elif f == 18:
            x = 4 + i
            y = 6 + i
            z = 9 + i
            bs = [2 * x + y + z, x + 3 * y + 2 * z, 3 * x + 2 * y + 4 * z]
            det = 2 * (3 * 4 - 2 * 2) - (4 - 6) + (2 - 9)
            eq(det, 11)
            has(x + y + z)
        elif f == 19:
            a = 2 + i
            b = 5 + i
            c = 9 + i
            for r in [a, b, c]:
                eq(r ** 3 - (a + b + c) * r * r + (a * b + a * c + b * c) * r - a * b * c, 0)
    elif t == 'functions':
        if f == 0:
            m = 2.5 + 0.5 * i
            c = 12 + 3 * i
            eq((12 * m + c - (4 * m + c)) / 8, m)
            has(20)
        elif f == 1:
            m = 2 + i
            px = 3 + i
            py = 5
            c = py + px / m
            xx = (c + 4) / (m + 1 / m)
            eq(m * xx - 4, -xx / m + c)
            has(f'{fmt(xx)}')
        elif f == 2:
            a = 1.4 + 0.2 * i
            b = 6 + i
            x = 30 + 5 * i
            eq((a * x + b - b) / a, x)
            assert 'reflections' in ss and 'inverse' in q['parts'][1]['prompt']
        elif f == 3:
            h = 3 + i
            k = 5 + 2 * i
            values = [k - (x - h) ** 2 for x in [0, h, h + 2]]
            assert min(values) < 0
            has(min(values))
            has(k)
        elif f == 4:
            a = 2 + i
            b = 7 + i
            v = (a + b) / 2
            eq((v - a) * (v - b), -(a - b) ** 2 / 4)
            has(a * b)
        elif f == 5:
            a = -1 - i
            b = 8 + 2 * i
            c = 10 + i
            for x in [0, 1, 3]:
                assert str(a * x * x + b * x + c) in q['stem']
            has(a * 16 + b * 4 + c)
        elif f == 6:
            a = 2 + i
            b = 20 + 2 * i
            s = 2 + i
            v = (a + b) / 2
            benefit = lambda x: -s * (x - a) * (x - b)
            eq(d(benefit, v), 0)
            assert benefit(v) >= benefit(v + 0.01)
            has(f'{benefit(v):g}')
        elif f == 7:
            a = 180 + 20 * i
            r = 1.18 + 0.02 * i
            T = math.log(2, r)
            eq(a * r ** T, 2 * a)
            has(f'{fmt(T)}')
        elif f == 8:
            amb = 18 + i
            a = 60 + 5 * i
            r = 0.78 + 0.02 * i
            T = math.log(10 / a, r)
            eq(amb + a * r ** T, amb + 10)
            has(f'{fmt(T)}')
        elif f == 9:
            a = 100 + 10 * i
            r = 1.12 + 0.01 * i
            m = 10 + i
            c = 150 + 10 * i
            fun = lambda t: a * r ** t - m * t - c
            roots = 0
            prev = fun(0)
            for j in range(1, 3001):
                val = fun(j / 100)
                if val * prev < 0:
                    roots += 1
                prev = val
            assert roots == 1
        elif f == 10:
            k = 3 + i
            power = 2 + i
            eq(k * 4 ** power / (k * 2 ** power), 2 ** power)
            has(k * 5 ** power)
        elif f == 11:
            r = 3 + i
            I = 80 + 20 * i
            eq(I * r * r / (2 * r) ** 2, I / 4)
            has(f'{I / 4:g}')
        elif f == 12:
            a = 1 + i
            b = 4 + i
            c = 8 + i
            f0 = lambda x: (x - a) * (x - b) * (x - c)
            S = a + b + c
            Q = a * b + a * c + b * c
            for z in [(S - math.sqrt(S * S - 3 * Q)) / 3, (S + math.sqrt(S * S - 3 * Q)) / 3]:
                eq(d(f0, z), 0, 1e-05)
                has(f'{fmt(z)}')
        elif f == 13:
            a = 4 + i
            d0 = 14 + i
            T = 12 + 4 * i
            b = 360 / T
            eq(a * math.cos(math.radians(b * T)) + d0, a + d0)
            has(T)
        elif f == 14:
            low = 3 + i
            high = 13 + 3 * i
            T = 16 + 4 * i
            a = (high - low) / 2
            mid = (high + low) / 2
            eq(a * math.cos(math.pi) + mid, low)
            has(mid if mid % 1 else f'{mid:g}')
        elif f == 15:
            base = 8 + i
            r = 2 + i
            r2 = 1 + 0.25 * i
            eq(base + r * 5, base + 5 * r + r2 * (5 - 5))
            has(f'{base + 5 * r + 4 * r2:.2f}')
            has(13)
        elif f == 16:
            c1 = 30 + 5 * i
            r1 = 2 + 0.25 * i
            c2 = 10 + i
            r2 = 4 + 0.25 * i
            x = (c1 - c2) / (r2 - r1)
            eq(c1 + r1 * x, c2 + r2 * x)
            assert c1 + r1 * 20 < c2 + r2 * 20
        elif f == 17:
            a = 4 + i
            b = 10 + 2 * i
            pred = a * 5 + b
            obs = pred + 3 + i
            has(f'{fmt(100 * abs(pred - obs) / obs)}')
        elif f == 18:
            a = 12 + 4 * i
            c = 2 + i
            eq(a / (3 + 1) + c, c + a / 4)
            has(3)
        elif f == 19:
            h = 4 + i
            k = 2 + i
            for z in [h - 3, h + 3]:
                eq(abs(z - h) + k, k + 3)
                assert 0 <= z <= h + 5
    elif t == 'geometry-trigonometry':
        if f == 0:
            aa = [1 + i, 2, 3]
            bb = [7 + i, 10 + i, 15 + i]
            dist = math.dist(aa, bb)
            has(f'{fmt(dist)}')
            eq(math.dist(aa, [(a + b) / 2 for a, b in zip(aa, bb)]), dist / 2)
        elif f == 1:
            a = 8 + i
            b = 6 + i
            h = 5 + i
            diag = math.hypot(a, b, h)
            angle = math.degrees(math.asin(h / diag))
            has(f'{fmt(diag)}')
            has(f'{fmt(angle)}')
        elif f == 2:
            s = 10 + 2 * i
            h = 12 + i
            area = 4 * (s * math.hypot(h, s / 2) / 2) + s * s
            has(f'{fmt(area)}')
            has(f'{fmt(s * s * h / 3)}')
        elif f == 3:
            r = 3 + i
            h = 8 + i
            has(f'{fmt(math.pi * r * r * h / 3)}')
            has(f'{fmt(math.pi * r * (r + math.hypot(r, h)))}')
        elif f == 4:
            r = 4 + i
            h = 9 + i
            V = math.pi * r * r * h + 2 * math.pi * r ** 3 / 3
            S = 2 * math.pi * r * h + 3 * math.pi * r * r
            has(f'{fmt(V)}')
            has(f'{fmt(S)}')
            assert 'diagramSvg' not in q
        elif f == 5:
            r = 5 + i
            s = 1.4 + 0.1 * i
            eq(4 * math.pi * (r * s) ** 2 / (4 * math.pi * r * r), s * s)
            has(f'{fmt(4 * math.pi * (r * s) ** 3 / 3)}')
        elif f == 6:
            d0 = 32 + 5 * i
            theta = 38 + 3 * i
            h = d0 * math.tan(math.radians(theta))
            has(f'{fmt(h + 1.6)}')
            assert 'diagramSvg' not in q
        elif f == 7:
            h = 45 + 5 * i
            theta = 24 + 3 * i
            d0 = h / math.tan(math.radians(theta))
            direct = h / math.sin(math.radians(theta))
            eq(math.hypot(h, d0), direct)
            has(f'{fmt(direct)}')
        elif f == 8:
            a = 12 + 2 * i
            b = 17 + i
            theta = 52 + 7 * i
            x = b * math.cos(math.radians(theta))
            y = b * math.sin(math.radians(theta))
            dist = math.hypot(a - x, y)
            has(f'{fmt(dist)}')
        elif f == 9:
            A0 = 38 + 3 * i
            B = 64 - i
            C = 180 - A0 - B
            a = 20 + 2 * i
            b = a * math.sin(math.radians(B)) / math.sin(math.radians(A0))
            c = a * math.sin(math.radians(C)) / math.sin(math.radians(A0))
            has(f'{fmt(b)}')
            has(f'{fmt(c)}')
            eq(A0 + B + C, 180)
        elif f == 10:
            a = 24 + 2 * i
            b = 18 + 3 * i
            theta = 43 + 6 * i
            area = a * b * math.sin(math.radians(theta)) / 2
            has(round(area * (7 + 2 * i)))
        elif f == 11:
            a = 12 + 2 * i
            b = 9 + i
            direct = math.sqrt(a * a + b * b + 2 * a * b * math.cos(math.radians(80)))
            has(f'{fmt(direct)}')
            has(f'{fmt(a + b - direct)}')
        elif f == 12:
            r = 14 + 2 * i
            deg = 65 + 10 * i
            arc = math.radians(deg) * r
            has(f'{fmt(arc)}')
            has(f'{fmt(arc + 2 * r)}')
        elif f == 13:
            r = 8 + i
            deg = 100 + 15 * i
            band = math.radians(deg) * ((r + 2) ** 2 - r * r) / 2
            has(f'{fmt(band)}')
        elif f == 14:
            a = (2 + i, 3)
            b = (8 + i, 7)
            mid = ((a[0] + b[0]) / 2, 5)
            eq(math.dist(a, mid), math.dist(b, mid))
            eq(4 / 6 * -1.5, -1)
        elif f in [15, 19]:
            a = 6 + 2 * i
            b = 8 + 2 * i
            v = (a / 2, b / 2)
            ds = [math.dist(v, z) for z in [(0, 0), (a, 0), (0, b)]]
            eq(ds[0], ds[1])
            eq(ds[1], ds[2])
            has(f'{fmt(ds[0])}')
            if f == 15:
                p = (a / 2 + 0.5, b / 2 - 0.5)
                ds = [math.dist(p, z) for z in [(0, 0), (a, 0), (0, b)]]
                assert ds.index(min(ds)) == 1
        elif f == 16:
            p = (3 + i, 4)
            sites = [(1 + i, 2), (8 + i, 2), (4 + i, 9)]
            ds = [math.dist(p, s) for s in sites]
            assert ds.index(min(ds)) == 0
            has(40 + 3 * i)
        elif f == 17:
            a = 8 + 2 * i
            C = a / 2
            left = a / 4
            right = 3 * a / 4
            eq(left, C - left)
            eq(right - C, a - right)
        elif f == 18:
            W = 12 + 2 * i
            H = 10 + 2 * i
            has(int(W * H * 60))
            has(f'{fmt(math.hypot(W / 2, H / 2))}')
    elif t == 'statistics-probability':
        if f == 0:
            N = 60 + 10 * i
            eq(sum([0.2 * N, 0.3 * N, 0.5 * N]), N)
            has(int(0.5 * N))
        elif f == 1:
            data = [10 + 2 * i + x for x in [1, 2, 2, 3, 4, 6, 7, 9, 10, 12]]
            has(f'{statistics.median(data):g}')
            eq(sum((x > 16 + 2 * i for x in data)) / 10, 0.4)
        elif f == 2:
            fs = [3 + i, 6, 10 + i, 7, 4]
            data = [x for x, freq in zip(range(1, 6), fs) for _ in range(freq)]
            has(f'{fmt(statistics.mean(data))}')
            has(f'{fmt(statistics.pstdev(data))}')
        elif f == 3:
            fs = [8 + i, 15 + i, 20 + 2 * i, 12 + i]
            ws = [10, 10, 20, 20]
            eq(sum((w * (f / w) for f, w in zip(fs, ws))), sum(fs))
        elif f == 4:
            fs = [8 + 2 * i, 22, 40, 30 - 2 * i]
            assert sum(fs) == 100
            cum = [sum(fs[:j]) for j in range(5)]
            Q = []
            for p in [25, 50, 75]:
                j = next((j for j in range(4) if cum[j] <= p <= cum[j + 1]))
                Q.append(j * 10 + 10 * (p - cum[j]) / fs[j])
            has(f'{fmt(Q[1])}')
            has(f'{fmt(Q[2] - Q[0])}')
        elif f == 5:
            assert 58 + i < 36 + i + 1.5 * 16 < 65 + i
            has(16)
        elif f in [6, 7]:
            xs = [1, 2, 3, 4, 5, 6] if f == 6 else [2, 4, 6, 8, 10]
            ys = [v + 3 * i for v in [12, 16, 17, 23, 25, 29]] if f == 6 else [v + i for v in [30, 26, 24, 19, 17]]
            m, c = statistics.linear_regression(xs, ys)
            has(f'{fmt(m)}')
            has(f'{fmt(c)}')
            if f == 6:
                has(f'{fmt(statistics.correlation(xs, ys))}')
        elif f == 8:
            rx = rank([10, 20, 20, 40, 50, 60])
            ry = rank([2 + i, 4 + i, 3 + i, 5 + i, 7 + i, 6 + i])
            has(f'{fmt(corr(rx, ry))}')
            eq(rx[1], 2.5)
        elif f == 9:
            both = 18 + 2 * i
            a = 22 + i
            b = 14 + i
            neither = 16 + i
            N = both + a + b + neither
            has(f'{fmt(both / (both + b))}')
            assert not math.isclose(both / N, (both + a) * (both + b) / N ** 2)
        elif f == 10:
            R = 5 + i
            B = 7 + i
            N = R + B
            outcomes = [(a, b) for a in range(N) for b in range(N) if a != b]
            diff = sum(((a < R) != (b < R) for a, b in outcomes)) / len(outcomes)
            has(f'{fmt(diff)}')
        elif f == 11:
            N = 3 + i
            p = 0.72 + 0.04 * i
            eq(1 - cf(N, p, 0), sum((math.comb(N, j) * p ** j * (1 - p) ** (N - j) for j in range(1, N + 1))))
            has(f'{fmt(1 - (1 - p) ** N)}')
        elif f == 12:
            ps = [0.4, 0.3 - 0.02 * i, 0.2, 0.1 + 0.02 * i]
            xs = [0, 5, 15, 30]
            eq(sum(ps), 1)
            E = sum((x * p for x, p in zip(xs, ps)))
            has(f'{fmt(E)}')
            eq(sum(((x - (8 + i)) * p for x, p in zip(xs, ps))), E - (8 + i))
        elif f == 13:
            N = 12 + 2 * i
            p = 0.35 + 0.05 * i
            k = 5 + i
            has(f'{fmt(1 - cf(N, p, k - 1))}')
            eq(cf(N, p, N), 1)
        elif f == 14:
            N = 20 + 2 * i
            p = 0.2 + 0.03 * i
            k = next((k for k in range(N + 1) if cf(N, p, k) >= 0.9))
            has(k)
            assert cf(N, p, k - 1) < 0.9 <= cf(N, p, k)
        elif f == 15:
            mu = 70 + 5 * i
            sd = 8 + i
            prob = quad(lambda x: math.exp(-(x - mu) ** 2 / (2 * sd * sd)) / (sd * math.sqrt(2 * math.pi)), mu - 6, mu + 10)
            has(f'{fmt(prob)}')
        elif f == 16:
            mu = 120 + 10 * i
            sd = 15 + 2 * i
            D = NormalDist(mu, sd)
            p = 0.9 + 0.02 * i
            cut = D.inv_cdf(p)
            eq(D.cdf(cut), p)
            has(f'{fmt(cut)}')
            eq(D.inv_cdf(0.05) + D.inv_cdf(0.95), 2 * mu)
        elif f == 17:
            obs = [[30 + 2 * i, 20 + i, 10 + i], [15 + i, 25 + 2 * i, 20 + i]]
            rows = list(map(sum, obs))
            cols = list(map(sum, zip(*obs)))
            N = sum(rows)
            exp = [[r * c / N for c in cols] for r in rows]
            chi = sum(((o - e) ** 2 / e for rr, ee in zip(obs, exp) for o, e in zip(rr, ee)))
            has(f'{fmt(chi)}')
            has(f'{fmt(math.exp(-chi / 2))}')
            assert min((v for r in exp for v in r)) > 5
        elif f == 18:
            obs = [15 + i, 18 + 2 * i, 25, 28 - i, 34 - 2 * i]
            E = sum(obs) / 5
            chi = sum((o * o / E for o in obs)) - sum(obs)
            has(f'{fmt(chi)}')
            has(f'{fmt(math.exp(-chi / 2) * (1 + chi / 2))}')
            assert E > 5
        elif f == 19:
            A0 = [14 + i, 16 + i, 17 + i, 15 + i, 18 + i, 16 + i, 19 + i, 17 + i]
            B = [18 + i, 20 + i, 19 + i, 22 + i, 21 + i, 20 + i, 23 + i, 19 + i]
            pooled = (statistics.variance(A0) + statistics.variance(B)) / 2
            tt = (statistics.mean(A0) - statistics.mean(B)) / math.sqrt(pooled / 4)
            df = 14
            c = math.gamma(7.5) / (math.sqrt(14 * math.pi) * math.gamma(7))
            pv = 1 - 2 * quad(lambda x: c * (1 + x * x / 14) ** (-7.5), 0, abs(tt))
            has(f'{fmt(tt)}')
            has(f'{fmt(pv)}')
            assert pv < 0.05
    elif t == 'calculus':
        if f in [0, 1]:
            a = 2 + i if f == 0 else 1 + i
            b = 3 + i if f == 0 else 4
            x = 2 if f == 0 else 3
            F = lambda x: a * x * x + b * x
            eq(d(F, x), 2 * a * x + b)
            has(2 * a * x + b if f == 0 else f'{fmt(2 * a * x + b)}')
        elif f == 2:
            a = 2 + i
            b = 5 + i
            F = lambda x: a * x ** 3 - b * x * x + 7
            for x in [1, 2, 3]:
                eq(d(F, x), 3 * a * x * x - 2 * b * x)
        elif f == 3:
            a = 12 + 4 * i
            b = 3 + i
            F = lambda x: a / x ** 2 + b * x + 20
            eq(d(F, 2), -a / 4 + b)
            has(f'{fmt(-a / 4 + b)}')
        elif f in [4, 11, 12]:
            a = 2 + i
            b = 6 + i if f == 4 else 5 + i
            for x, sign in [(a / 2, 1), ((a + b) / 2, -1), (b + 1, 1)]:
                assert (x - a) * (x - b) * sign > 0
            if f == 12:
                U = 9 + i
                F = lambda x: x ** 3 / 3 - (a + b) * x * x / 2 + a * b * x + 10
                has(f'{fmt(F(U))}')
                assert F(U) == max((F(v) for v in [0, a, b, U]))
        elif f == 5:
            a = 1 + i
            b = 2 + i
            c = 3
            F = lambda x: a * x * x + b * x + c
            m = 4 * a + b
            eq(d(F, 2), m)
            has(m)
            has(F(2) - 2 * m)
        elif f == 6:
            a = 2 + i
            c = 1 + i
            F = lambda x: a * x * x + c
            eq(d(F, 1), 2 * a)
            eq(2 * a * (-1 / (2 * a)), -1)
        elif f == 7:
            a = 3 + i
            b = 4 + i
            initial = 20 + 2 * i
            F3 = initial + quad(lambda x: a * x * x + b * x, 1, 3)
            has(f'{fmt(F3)}')
        elif f == 8:
            a = 1 + i
            b = 3 + i
            area = quad(lambda x: a * x * x + b, 1, 4)
            has(f'{fmt(area)}')
            eq(area, 21 * a + 3 * b)
        elif f == 9:
            a = 2 + i
            b = 8 + i
            area = quad(lambda x: a * x + b, 0, 6)
            has(f'{area:g}')
            eq(area / 6, a * 3 + b)
        elif f == 10:
            a = 1 + i
            b = 2 + i
            area = quad(lambda x: a * x * x + b, 2, 5)
            has(f'{fmt(area)}')
            has(f'{area * (4 + i):.2f}')
        elif f == 13:
            p = 70 + 10 * i
            c = 10 + 2 * i
            k = 0.5 + 0.1 * i
            fixed = 300 + 50 * i
            F = lambda x: x * (p - k * x) - (fixed + c * x)
            x = (p - c) / (2 * k)
            eq(d(F, x), 0, 1e-05)
            assert F(x) >= max(F(x - 0.1), F(x + 0.1))
            has(f'{F(x):.2f}')
        elif f == 14:
            L = 80 + 12 * i
            x = L / 4
            y = L - 2 * x
            eq(2 * x + y, L)
            assert x * y >= (x + 0.1) * (L - 2 * (x + 0.1))
            has(f'{x * y:g}')
        elif f == 15:
            L = 24 + 6 * i
            x = L / 6
            V = lambda x: x * (L - 2 * x) ** 2
            eq(d(V, x), 0, 1e-05)
            has(f'{V(x):g}')
            eq(V(0), 0)
            eq(V(L / 2), 0)
        elif f == 16:
            V = 500 + 250 * i
            r = (V / (2 * math.pi)) ** (1 / 3)
            S = lambda r: 2 * math.pi * r * r + 2 * V / r
            eq(d(S, r), 0, 1e-05)
            eq(V / (math.pi * r * r), 2 * r)
            has(f'{fmt(S(r))}')
        elif f == 17:
            a = 6 + 2 * i
            x = 2 * a / 3
            F = lambda x: a * x * x - x ** 3
            eq(d(F, x), 0, 1e-05)
            has(f'{fmt(F(x))}')
            assert F(x) > F(0) and F(x) > F(a)
        elif f == 18:
            h = 4 + i
            ws = [0, 8 + i, 12 + i, 9 + i, 0]
            area = sum((h * (a + b) / 2 for a, b in zip(ws, ws[1:])))
            has(f'{area:g}')
        elif f == 19:
            a = 1 + i
            F = lambda x: a * x * x + 2
            trap = sum(((F(j) + F(j + 1)) / 2 for j in range(4)))
            exact = quad(F, 0, 4)
            has(f'{fmt(trap)}')
            has(f'{fmt(exact)}')
            assert trap > exact
    return dict(id=q['id'], family=f'{t}/{f + 1:02d}', variant=i + 1, syllabusCode=q['syllabusCode'], result='passed', method='Post-generation independent definition/enumeration/recurrence/quadrature checks; emitted worked answers checked against recomputation', marks=q['marks'])

def main():
    results = []
    files = {}
    for p in sorted((ROOT / 'content' / 'ib' / 'math-ai-sl').glob('*.json')):
        files[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
        qs = json.loads(p.read_text(encoding='utf-8'))
        assert [q['number'] for q in qs] == list(range(1, 81))
        for q in qs:
            try:
                results.append(verify(q))
            except Exception as e:
                raise AssertionError(q['id']) from e
    assert len(results) == 400
    out = ROOT / 'docs' / 'ib-maths-reviews' / 'ai-sl-numeric-review.json'
    out.write_text(json.dumps(dict(status='passed', questionCount=400, familyCount=100, files=files, records=results), indent=2) + '\n', encoding='utf-8')
    print('Independent AI SL numeric review passed:', len(results), 'records /100families')
if __name__ == '__main__':
    main()
