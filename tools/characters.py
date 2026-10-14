# Generador de los disfraces de SMUSH! (por nivel) y de sus capas animadas.
# Uso: python3 tools/characters.py <carpeta de salida>
#   - board5.html / big5.html / front_board.html: tableros para revisar
#   - rig.json: las capas que van en index.html como `const RIG = ...;` (pegar en una sola línea)
# Lee los marcianitos originales (ALIENS) de index.html y, de tools/front/, los de frente y el yeti (dibujos del usuario).
# Las coordenadas (u, v) van de 0 a 10 sobre la caja del cuerpo.
import re, json, math, sys
D = sys.argv[1]
s = open(__import__('os').path.join(__import__('os').path.dirname(__file__), '..', 'index.html')).read()
A = json.loads(re.search(r'^const ALIENS = (\{.*?\});\s*$', s, re.M).group(1))
# Cuerpo aproximado (en la rejilla 0-10 de cada uno) y su color de sombra: para las sombritas que los accesorios dejan encima
BODY = {"green": (5, 5.0, 5.0, 4.9, "#14684C"), "orange": (5, 4.95, 5.0, 4.9, "#B0401A"), "purple": (5, 4.95, 5.0, 4.9, "#3E248F"), "yellow": (5.1, 5.15, 4.9, 4.75, "#A87406")}

class Ch:
    def __init__(self, k, tag, AA=None):
        v = AA or A[k]; self.k = k; self.vb = v['vb']; self.bx, self.by, self.bw, self.bh = v['body']
        inner = re.sub(r'^<svg[^>]*>', '', v['svg']); inner = re.sub(r'</svg>\s*$', '', inner)
        inner = re.sub(r'(class="|\.)(st\d+)', lambda m: m.group(1) + tag + m.group(2), inner)
        self.inner = re.sub(r'(id="|#)(radial-gradient|linear-gradient)', lambda m: m.group(1) + tag + '-' + m.group(2), inner)
        self.tag = tag; self.back = []; self.front = []; self.defs = []; self.n = 0; self.S = self.bw / 10
        if k in BODY:
            cu, cv, ru, rv, col = BODY[k]; x, y = self.P(cu, cv)
            self.shcol = col
            self.defs.append(f'<clipPath id="{tag}-body"><ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{self.bw*ru/10:.1f}" ry="{self.bh*rv/10:.1f}"/></clipPath>'
                             f'<filter id="{tag}-blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{self.S*0.28:.1f}"/></filter>'
                             f'<filter id="{tag}-soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{self.S*0.12:.1f}"/></filter>')
    def strip(self, keys):
        for key in keys:
            n0 = len(self.inner)
            self.inner = re.sub(r'<(path|ellipse)\b[^>]*' + re.escape(key) + r'[^>]*?(?:/>|>\s*</\1>)', '', self.inner, count=1)
            assert len(self.inner) < n0, key
    def P(self, u, v): return (self.bx + self.bw * u / 10, self.by + self.bh * v / 10)
    def p(self, u, v): x, y = self.P(u, v); return f"{x:.1f},{y:.1f}"
    def gid(self): self.n += 1; return f"{self.tag}-g{self.n}"
    def lin(self, stops, x1=0, y1=0, x2=0, y2=1):
        i = self.gid(); st = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
        self.defs.append(f'<linearGradient id="{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{st}</linearGradient>'); return f"url(#{i})"
    def rad(self, stops, cx=.38, cy=.32, r=.75):
        i = self.gid(); st = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
        self.defs.append(f'<radialGradient id="{i}" cx="{cx}" cy="{cy}" r="{r}">{st}</radialGradient>'); return f"url(#{i})"
    # Sombra suave que el accesorio deja sobre el cuerpo (solo dentro del cuerpo)
    def shadow(self, d, dx=0.15, dy=0.45, a=0.42):
        S = self.S
        self.front.append(f'<g clip-path="url(#{self.tag}-body)"><path d="{d}" transform="translate({dx*S:.1f} {dy*S:.1f})" fill="{self.shcol}" opacity="{a}" filter="url(#{self.tag}-blur)"/></g>')
    def shadow_stroke(self, d, w, dx=0.1, dy=0.4, a=0.4):
        S = self.S
        self.front.append(f'<g clip-path="url(#{self.tag}-body)"><path d="{d}" transform="translate({dx*S:.1f} {dy*S:.1f})" stroke="{self.shcol}" stroke-width="{w:.1f}" fill="none" stroke-linecap="round" opacity="{a}" filter="url(#{self.tag}-blur)"/></g>')
    def svg(self, h=300):
        vx, vy, vw, vh = self.vb; pad = vw * 0.34; px = vw * getattr(self, 'padk', 0.34); pb = vw * getattr(self, 'padb', 0)
        X0, Y0, W0, H0 = vx - px, vy - pad * 0.95, vw + px * 2, vh + pad * 1.25 + pb
        return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{X0:.1f} {Y0:.1f} {W0:.1f} {H0:.1f}" height="{h}">'
                f'<defs>{"".join(self.defs)}</defs>{"".join(map(txt, self.back))}{self.inner}{"".join(map(txt, self.front))}</svg>')

def F(c, *a): c.front.append(''.join(a))
def B(c, *a): c.back.append(''.join(a))
def FA(c, kind, piv, *a, ph=0): c.front.append(('A', kind, c.P(*piv), ''.join(a), ph))
def BA(c, kind, piv, *a, ph=0): c.back.append(('A', kind, c.P(*piv), ''.join(a), ph))
txt = lambda x: x if isinstance(x, str) else x[3]
def ell(c, u, v, rx, ry, fill, rot=0, extra=''):
    x, y = c.P(u, v); return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx*c.S:.1f}" ry="{ry*c.S:.1f}" transform="rotate({rot} {x:.1f} {y:.1f})" fill="{fill}" {extra}/>'
def circ(c, u, v, r, fill, extra=''):
    x, y = c.P(u, v); return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*c.S:.1f}" fill="{fill}" {extra}/>'
def path(d, fill="none", stroke=None, w=0, extra=''):
    st = f' stroke="{stroke}" stroke-width="{w:.1f}" stroke-linecap="round" stroke-linejoin="round"' if stroke else ''
    return f'<path d="{d}" fill="{fill}"{st} {extra}/>'
def fluff(c, u, v, r, tag_light, tag_dark, n=9):
    S = c.S; x, y = c.P(u, v); out = []
    g = c.rad([(0, "#FFFFFF"), (0.6, tag_light), (1, tag_dark)], .4, .35, .75)
    for i in range(n):
        a = i * 2 * math.pi / n
        out.append(f'<circle cx="{x+math.cos(a)*r*S*0.78:.1f}" cy="{y+math.sin(a)*r*S*0.78:.1f}" r="{r*S*0.42:.1f}" fill="{g}"/>')
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*S*0.82:.1f}" fill="{g}"/>')
    out.append(f'<ellipse cx="{x-r*S*0.3:.1f}" cy="{y-r*S*0.35:.1f}" rx="{r*S*0.3:.1f}" ry="{r*S*0.18:.1f}" fill="#fff" opacity=".8"/>')
    return ''.join(out)

ch = {}
for k in ['green', 'orange', 'purple', 'yellow']: ch[('void', k)] = Ch(k, 'v' + k)

# ===================== THE BEACH =====================
# Verde: visor de snorkel (marco con faldón de hule, vidrio con reflejo) y su tubo de rayas
c = Ch('green', 'bg'); S = c.S
strap = f'M{c.p(0.05,4.5)} Q{c.p(2.6,3.9)} {c.p(5.4,4.4)}'
c.shadow_stroke(strap, S * 0.5)
F(c, path(strap, stroke="#1C6A82", w=S * 0.5), path(f'M{c.p(0.1,4.35)} Q{c.p(2.6,3.75)} {c.p(5.4,4.25)}', stroke="#4FB3CF", w=S * 0.14, extra='opacity=".8"'))
mx, my = c.P(5.25, 3.25); mw, mh = c.bw * 0.5, c.bh * 0.34
mask = f'M{mx+mh*0.5:.1f},{my:.1f} H{mx+mw-mh*0.5:.1f} A{mh*0.5:.1f},{mh*0.5:.1f} 0 0 1 {mx+mw:.1f},{my+mh*0.5:.1f} V{my+mh*0.6:.1f} Q{mx+mw:.1f},{my+mh:.1f} {mx+mw-mh*0.5:.1f},{my+mh:.1f} H{mx+mw*0.62:.1f} Q{mx+mw*0.5:.1f},{my+mh*0.82:.1f} {mx+mw*0.38:.1f},{my+mh:.1f} H{mx+mh*0.5:.1f} Q{mx:.1f},{my+mh:.1f} {mx:.1f},{my+mh*0.6:.1f} V{my+mh*0.5:.1f} A{mh*0.5:.1f},{mh*0.5:.1f} 0 0 1 {mx+mh*0.5:.1f},{my:.1f} Z'
c.shadow(mask)
F(c, path(mask, fill=c.lin([(0, "#5CC8E2"), (0.55, "#2FA3C4"), (1, "#1D7C9E")])))
gx, gy, gw, gh = mx + S * 0.38, my + S * 0.36, mw - S * 0.76, mh - S * 0.95
glass = f'M{gx+gh*0.4:.1f},{gy:.1f} H{gx+gw-gh*0.4:.1f} Q{gx+gw:.1f},{gy:.1f} {gx+gw:.1f},{gy+gh*0.45:.1f} Q{gx+gw:.1f},{gy+gh:.1f} {gx+gw-gh*0.45:.1f},{gy+gh:.1f} H{gx+gh*0.45:.1f} Q{gx:.1f},{gy+gh:.1f} {gx:.1f},{gy+gh*0.45:.1f} Q{gx:.1f},{gy:.1f} {gx+gh*0.4:.1f},{gy:.1f} Z'
c.defs.append(f'<clipPath id="bg-glass"><path d="{glass}"/></clipPath>')
F(c, path(glass, fill="#E2F7FF", extra='opacity=".16"'), path(glass, stroke="#E9FAFF", w=S * 0.14, extra='opacity=".75"'),
  f'<g clip-path="url(#bg-glass)" opacity=".55"><path d="M{gx+gw*0.1:.1f},{gy+gh*1.2:.1f} L{gx+gw*0.42:.1f},{gy-gh*0.2:.1f}" stroke="#fff" stroke-width="{S*0.55:.1f}"/><path d="M{gx+gw*0.48:.1f},{gy+gh*1.2:.1f} L{gx+gw*0.62:.1f},{gy-gh*0.2:.1f}" stroke="#fff" stroke-width="{S*0.2:.1f}"/></g>',
  path(f'M{mx+mh*0.45:.1f},{my+S*0.16:.1f} H{mx+mw-mh*0.5:.1f}', stroke="#9BE3F2", w=S * 0.12, extra='opacity=".9"'))
tube = f'M{c.p(5.9,6.4)} Q{c.p(4.4,7.3)} {c.p(4.15,5.6)} L{c.p(4.0,0.0)} Q{c.p(3.95,-1.7)} {c.p(5.3,-1.75)}'
c.shadow_stroke(tube, S * 0.6, 0.2, 0.3, 0.35)
F(c, path(tube, stroke="#E9673F", w=S * 0.68), path(tube, stroke="#FF8A65", w=S * 0.52),
  path(tube, stroke="#FFFFFF", w=S * 0.54, extra=f'stroke-dasharray="{S*0.55:.1f} {S*1.35:.1f}" opacity=".95"'),
  path(f'M{c.p(3.86,5.4)} L{c.p(3.75,0.2)}', stroke="#FFC2AE", w=S * 0.12, extra='opacity=".8"'),
  f'<rect x="{c.P(5.2,-2.15)[0]:.1f}" y="{c.P(5.2,-2.15)[1]:.1f}" width="{S*0.9:.1f}" height="{S*0.95:.1f}" rx="{S*0.3:.1f}" fill="{c.lin([(0,"#FFE08A"),(1,"#E9B23A")])}"/>')
ch[('beach', 'green')] = c

# Naranja: cangrejito (tenazas con brazo de dos partes, nudillo, dientitos y brillo)
c = Ch('orange', 'bo'); S = c.S
def claw(c, u, v, flip, ang, sc):
    x, y = c.P(u, v); S = c.S * sc
    g = c.rad([(0, "#FFC39C"), (0.55, "#FF7A45"), (1, "#C9461F")], .35, .3, .85)
    arm = c.lin([(0, "#FF9A66"), (1, "#E2582C")], 0, 0, 1, 0)
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang}) scale({flip} 1)">'
            f'<path d="M{S*0.2:.1f},{S*2.2:.1f} Q{-S*0.2:.1f},{S*1.6:.1f} {-S*0.05:.1f},{S*1.1:.1f}" stroke="{arm}" stroke-width="{S*0.62:.1f}" fill="none" stroke-linecap="round"/>'
            f'<circle cx="{-S*0.05:.1f}" cy="{S*1.0:.1f}" r="{S*0.4:.1f}" fill="#F06A3A"/>'
            f'<path d="M{-S*0.05:.1f},{S*1.0:.1f} L0,{S*0.25:.1f}" stroke="{arm}" stroke-width="{S*0.55:.1f}" stroke-linecap="round"/>'
            f'<path d="M0,{S*0.3:.1f} C{-S*1.7:.1f},{S*0.1:.1f} {-S*1.75:.1f},{-S*2.3:.1f} {-S*0.1:.1f},{-S*2.55:.1f} Q{S*0.3:.1f},{-S*2.0:.1f} {-S*0.25:.1f},{-S*1.45:.1f} L{S*1.05:.1f},{-S*1.8:.1f} C{S*1.45:.1f},{-S*0.6:.1f} {S*0.9:.1f},{S*0.35:.1f} 0,{S*0.3:.1f} Z" fill="{g}"/>'
            f'<path d="M{-S*0.25:.1f},{-S*1.45:.1f} l{S*0.25:.1f},{S*0.05:.1f} m{S*0.25:.1f},{-S*0.12:.1f} l{S*0.18:.1f},{S*0.12:.1f} m{S*0.25:.1f},{-S*0.15:.1f} l{S*0.15:.1f},{S*0.15:.1f}" stroke="#B83E19" stroke-width="{S*0.1:.1f}" stroke-linecap="round" opacity=".7"/>'
            f'<ellipse cx="{-S*0.75:.1f}" cy="{-S*1.35:.1f}" rx="{S*0.42:.1f}" ry="{S*0.2:.1f}" fill="#fff" opacity=".6" transform="rotate(-40 {-S*0.75:.1f} {-S*1.35:.1f})"/>'
            f'<circle cx="{S*0.55:.1f}" cy="{-S*1.25:.1f}" r="{S*0.12:.1f}" fill="#fff" opacity=".7"/></g>')
c.strip(['M-359.1-281.8', 'M-276.6-256.8', 'cx="-164.6"'])
# Patitas de cangrejo: tres por lado, gorditas y curvas, con punta (las de atrás más oscuras, detrás del cuerpo)
def crableg(u, v, dx, back):
    x, y = c.P(u, v); ex, ey = x + dx * S, y + S * 2.0; kx, ky = x + dx * S * 0.75, y + S * 0.35
    lg = c.lin([(0, "#E8602F" if back else "#FF9466"), (1, "#B9431C" if back else "#E2582C")], 0, 0, 0, 1)
    return (f'<path d="M{x:.1f},{y:.1f} Q{kx:.1f},{ky - S*0.5:.1f} {ex:.1f},{ey:.1f}" stroke="{lg}" stroke-width="{S*0.62:.1f}" fill="none" stroke-linecap="round"/>'
            f'<path d="M{x + dx*S*0.25:.1f},{y - S*0.05:.1f} Q{kx:.1f},{ky - S*0.62:.1f} {ex - dx*S*0.1:.1f},{ey - S*0.45:.1f}" stroke="#FFC39C" stroke-width="{S*0.12:.1f}" fill="none" stroke-linecap="round" opacity=".55"/>')
BA(c, 'legsA', (3.4, 8.2), *[crableg(u, 8.3, dx, True) for (u, dx) in [(2.4, -1.7), (3.4, -1.2), (4.4, -0.7)]])
BA(c, 'legsB', (6.9, 8.2), *[crableg(u, 8.3, dx, False) for (u, dx) in [(5.8, 0.7), (6.9, 1.2), (8.0, 1.7)]])
def claw2(c, u, v, ang, sc, flip):
    x, y = c.P(u, v); k = c.S * sc
    body = c.rad([(0, "#FFC9A6"), (0.5, "#FF8550"), (1, "#D24E22")], .35, .3, .9)
    fing = c.lin([(0, "#FF9A66"), (1, "#D9502A")], 0, 1, 0, 0)
    q = lambda px, py: f"{px*k:.1f},{py*k:.1f}"
    arm = (f'<path d="M{q(0,0.7)} Q{q(-0.1,1.7)} {q(-0.7,2.2)} L{q(-1.6,2.7)}" stroke="#D9542A" stroke-width="{k*0.62:.1f}" fill="none" stroke-linecap="round"/>'
           f'<path d="M{q(0,0.7)} Q{q(-0.1,1.7)} {q(-0.7,2.2)} L{q(-1.6,2.7)}" stroke="#FF8F5C" stroke-width="{k*0.42:.1f}" fill="none" stroke-linecap="round"/>'
           f'<circle cx="{-0.7*k:.1f}" cy="{2.2*k:.1f}" r="{k*0.36:.1f}" fill="#F06A3A"/>')
    fixed = f'M{q(-0.95,-0.3)} C{q(-1.2,-1.5)} {q(-0.85,-2.5)} {q(-0.2,-2.8)} C{q(-0.2,-2.25)} {q(-0.1,-1.6)} {q(0.15,-1.05)} Z'
    mov = f'M{q(0.2,-0.95)} C{q(0.6,-1.3)} {q(0.95,-1.75)} {q(0.9,-2.3)} C{q(1.4,-1.85)} {q(1.35,-1.0)} {q(0.95,-0.4)} Z'
    teeth = ''.join(f'<circle cx="{px*k:.1f}" cy="{py*k:.1f}" r="{k*0.09:.1f}" fill="#FFD8C2"/>' for px, py in [(-0.17, -2.05), (-0.08, -1.6), (0.45, -1.35), (0.68, -1.75)])
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang}) scale({flip} 1)">{arm}'
            f'<path d="{mov}" fill="{fing}"/><path d="{fixed}" fill="{body}"/>{teeth}'
            f'<ellipse cx="0" cy="{-0.25*k:.1f}" rx="{k*1.02:.1f}" ry="{k*1.08:.1f}" fill="{body}"/>'
            f'<path d="M{q(-0.55,-0.75)} Q{q(-0.5,-1.6)} {q(-0.25,-2.3)}" stroke="#fff" stroke-width="{k*0.16:.1f}" fill="none" stroke-linecap="round" opacity=".55"/>'
            f'<ellipse cx="{-0.4*k:.1f}" cy="{-0.65*k:.1f}" rx="{k*0.35:.1f}" ry="{k*0.2:.1f}" transform="rotate(-35 {-0.4*k:.1f} {-0.65*k:.1f})" fill="#fff" opacity=".6"/>'
            f'<path d="M{q(0.55,0.35)} Q{q(0.9,-0.2)} {q(0.85,-0.75)}" stroke="#B9431C" stroke-width="{k*0.08:.1f}" fill="none" opacity=".4"/></g>')
# Pinza tipo mitón: palma gordita y dos dedos (uno grande y curvo, otro corto) con una muesca en V, todo en una sola pieza;
# brazo corto y grueso con codo, que sale del costado del cuerpo
def claw3(c, base, palm, ang, sc, flip):
    (bu, bv), (pu, pv) = base, palm
    bx, by = c.P(bu, bv); x, y = c.P(pu, pv); k = c.S * sc
    mx, my = (bx + x) / 2 + flip * k * 0.15, (by + y) / 2 + k * 0.55
    arm = (f'<path d="M{bx:.1f},{by:.1f} Q{mx:.1f},{my:.1f} {x:.1f},{y + k*0.7:.1f}" stroke="#C9461F" stroke-width="{k*0.78:.1f}" fill="none" stroke-linecap="round"/>'
           f'<path d="M{bx:.1f},{by:.1f} Q{mx:.1f},{my:.1f} {x:.1f},{y + k*0.7:.1f}" stroke="{c.lin([(0,"#FF9A66"),(1,"#E9602F")],0,0,1,1)}" stroke-width="{k*0.56:.1f}" fill="none" stroke-linecap="round"/>'
           f'<circle cx="{mx - flip*k*0.05:.1f}" cy="{my - k*0.25:.1f}" r="{k*0.4:.1f}" fill="#F06A3A"/>')
    q = lambda px, py: f"{px*k:.1f},{py*k:.1f}"
    shape = (f'M{q(0,1.0)} C{q(-1.1,1.0)} {q(-1.3,-0.2)} {q(-1.05,-0.95)} C{q(-0.95,-1.85)} {q(-0.5,-2.5)} {q(0.05,-2.6)} '
             f'Q{q(0.38,-2.6)} {q(0.3,-2.3)} C{q(-0.05,-2.0)} {q(-0.12,-1.4)} {q(0.12,-1.0)} '
             f'C{q(0.45,-1.25)} {q(0.75,-1.6)} {q(0.85,-1.98)} Q{q(1.08,-2.15)} {q(1.17,-1.85)} '
             f'C{q(1.28,-1.3)} {q(1.28,-0.6)} {q(1.02,-0.1)} C{q(0.8,0.6)} {q(0.5,1.0)} {q(0,1.0)} Z')
    g = c.rad([(0, "#FFCBA8"), (0.45, "#FF8A55"), (1, "#D24E22")], .35, .35, .85)
    claw = (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang}) scale({flip} 1)">'
            f'<path d="{shape}" fill="{g}"/>'
            f'<path d="M{q(0.12,-1.0)} C{q(0.3,-1.2)} {q(0.55,-1.45)} {q(0.7,-1.75)}" stroke="#B9431C" stroke-width="{k*0.09:.1f}" fill="none" stroke-linecap="round" opacity=".45"/>'
            f'<path d="M{q(0.12,-1.0)} C{q(-0.08,-1.4)} {q(-0.02,-1.9)} {q(0.2,-2.3)}" stroke="#B9431C" stroke-width="{k*0.09:.1f}" fill="none" stroke-linecap="round" opacity=".45"/>'
            f'<path d="M{q(-0.75,-0.7)} C{q(-0.75,-1.5)} {q(-0.45,-2.05)} {q(-0.1,-2.3)}" stroke="#fff" stroke-width="{k*0.2:.1f}" fill="none" stroke-linecap="round" opacity=".6"/>'
            f'<ellipse cx="{-0.45*k:.1f}" cy="{0.15*k:.1f}" rx="{k*0.32:.1f}" ry="{k*0.2:.1f}" transform="rotate(-30 {-0.45*k:.1f} {0.15*k:.1f})" fill="#fff" opacity=".45"/>'
            f'<path d="M{q(0.95,0.0)} C{q(0.8,0.55)} {q(0.45,0.85)} {q(0,0.9)}" stroke="#B9431C" stroke-width="{k*0.1:.1f}" fill="none" stroke-linecap="round" opacity=".3"/></g>')
    return arm + claw
# La de atrás: del lado de la espalda, detrás del cuerpo; la de enfrente: sale del costado (lado de los ojos) y se levanta afuera
BA(c, 'clawB', (1.0, 7.6), claw3(c, (1.0, 7.6), (-1.3, 4.6), -18, 1.15, -1))
FA(c, 'clawF', (9.4, 8.0), claw3(c, (9.4, 8.0), (11.3, 5.1), 16, 1.2, 1))
c.shadow(f'M{c.p(8.9,7.4)} q{S*1.0:.1f},{S*0.2:.1f} {S*0.8:.1f},{S*1.3:.1f} q{-S*0.8:.1f},{S*0.1:.1f} {-S*0.8:.1f},{-S*1.3:.1f} Z', -0.3, 0.1, 0.3)
c.padk = 0.42
ch[('beach', 'orange')] = c

# Morado: pulpo (5 tentáculos con su lado claro, rulito en la punta y ventosas)
c = Ch('purple', 'bp'); S = c.S
c.strip(['M63.6-278.8', 'M366.5-227.6', 'M165.4-257.2'])
c.padb = 0.12; c.padk = 0.42
def tentacle(c, pts, curl, w0, dark):
    P = [c.P(u, v) for u, v in pts]; S = c.S
    sm = []
    for i in range(len(P) - 1):
        p0, p1, p2, p3 = P[max(i - 1, 0)], P[i], P[i + 1], P[min(i + 2, len(P) - 1)]
        for kk in range(14):
            t = kk / 14; t2 = t * t; t3 = t2 * t
            sm.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    sm.append(P[-1])
    ang = math.atan2(sm[-1][1] - sm[-2][1], sm[-1][0] - sm[-2][0]); x, y = sm[-1]; st = S * 0.34
    for kk in range(20):
        ang += curl * 0.34; st *= 0.92; x += math.cos(ang) * st; y += math.sin(ang) * st; sm.append((x, y))
    L = [0]
    for i in range(1, len(sm)): L.append(L[-1] + math.hypot(sm[i][0] - sm[i - 1][0], sm[i][1] - sm[i - 1][1]))
    tot = L[-1]; left = []; right = []; W = []
    for i, (px, py) in enumerate(sm):
        a = sm[min(i + 1, len(sm) - 1)]; b2 = sm[max(i - 1, 0)]; dx, dy = a[0] - b2[0], a[1] - b2[1]; n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n, dx / n; w = w0 * max(0.1, (1 - L[i] / tot) ** 0.85); W.append((nx, ny, w))
        left.append((px + nx * w, py + ny * w)); right.append((px - nx * w, py - ny * w))
    d = 'M' + ' L'.join(f'{px:.1f},{py:.1f}' for px, py in left + right[::-1]) + ' Z'
    fill = c.lin([(0, "#6B48D0" if dark else "#7A57DA"), (0.5, "#9273E6" if dark else "#A487F0"), (1, "#6346C4")], 0, 0, 0, 1)
    out = f'<path d="{d}" fill="{fill}"/>'
    # Brillo a lo largo (del lado de afuera)
    hl = [(px + nx * w * 0.45 * -curl, py + ny * w * 0.45 * -curl) for (px, py), (nx, ny, w) in zip(sm[3:int(len(sm) * 0.75)], W[3:int(len(sm) * 0.75)])]
    if len(hl) > 2: out += '<path d="M' + ' L'.join(f'{px:.1f},{py:.1f}' for px, py in hl) + f'" stroke="#D7C8FF" stroke-width="{w0*0.16:.1f}" fill="none" stroke-linecap="round" opacity=".55"/>'
    # Ventosas del lado de adentro de la curva
    for i in range(int(len(sm) * 0.4), len(sm) - 5, 5):
        (px, py), (nx, ny, w) = sm[i], W[i]
        cx, cy = px + nx * w * 0.45 * curl, py + ny * w * 0.45 * curl; r = max(w * 0.34, S * 0.07)
        out += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#EDE5FF" stroke="#7656D8" stroke-width="{r*0.35:.1f}"/>'
    return out
for pts, curl, dark in [
    ([(1.4, 7.0), (0.2, 9.0), (-1.2, 10.3), (-2.4, 10.1)], 1, True),
    ([(8.6, 7.0), (9.8, 9.0), (11.2, 10.3), (12.4, 10.1)], -1, True),
    ([(2.8, 7.6), (2.0, 9.8), (0.9, 11.2)], 1, False),
    ([(7.2, 7.6), (8.0, 9.8), (9.1, 11.2)], -1, False),
    ([(4.3, 7.8), (4.1, 10.2), (3.3, 11.8)], -1, False),
    ([(5.8, 7.8), (6.0, 10.2), (6.8, 11.8)], 1, False)]:
    BA(c, 'tent', pts[0], tentacle(c, pts, curl, S * 1.05, dark), ph=len(c.back))
ch[('beach', 'purple')] = c

# Amarillo: salvavidas inflable (con volumen) y lentes de sol en la cabeza
c = Ch('yellow', 'by'); S = c.S
cx, cy = c.P(5.1, 7.7); R1x, R1y = c.bw * 0.66, c.bh * 0.24; R0x, R0y = c.bw * 0.43, c.bh * 0.12
def seg(a0, a1):
    n = 10
    o = [(cx + math.cos(a0 + (a1 - a0) * i / n) * R1x, cy + math.sin(a0 + (a1 - a0) * i / n) * R1y) for i in range(n + 1)]
    inn = [(cx + math.cos(a1 - (a1 - a0) * i / n) * R0x, cy + math.sin(a1 - (a1 - a0) * i / n) * R0y) for i in range(n + 1)]
    return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in o + inn) + ' Z'
tube = c.lin([(0, "#FFFFFF"), (1, "#E7E1D8")], 0, 0, 0, 1); coral = c.lin([(0, "#FFA27F"), (1, "#E9633F")], 0, 0, 0, 1)
N = 8
for i in range(N):
    a0, a1 = math.pi + i * math.pi / (N / 2) / 2 * 1, 0
for i in range(N):
    a0 = i * 2 * math.pi / N - 0.2; a1 = a0 + 2 * math.pi / N
    d = seg(a0, a1); col = coral if i % 2 else tube
    mid = (a0 + a1) / 2
    (F if math.sin(mid) > 0 else B)(c, f'<path d="{d}" fill="{col}"/>')
c.shadow(seg(math.pi * 0.05, math.pi * 0.95), 0, -0.55, 0.35)
# volumen: sombra abajo y brillo arriba en la parte de enfrente
F(c, f'<path d="M{cx-R1x*0.97:.1f},{cy+S*0.3:.1f} A{R1x*0.97:.1f},{R1y*0.97:.1f} 0 0 0 {cx+R1x*0.97:.1f},{cy+S*0.3:.1f}" stroke="#7A3A1E" stroke-width="{S*0.35:.1f}" fill="none" opacity=".15"/>',
  f'<path d="M{cx-R1x*0.72:.1f},{cy+R1y*0.45:.1f} A{(R1x+R0x)/2:.1f},{(R1y+R0y)/2:.1f} 0 0 0 {cx+R1x*0.2:.1f},{cy+(R1y+R0y)/2*0.98:.1f}" stroke="#fff" stroke-width="{S*0.28:.1f}" fill="none" opacity=".7" stroke-linecap="round"/>')
F(c, path(f'M{c.p(1.6,2.6)} Q{c.p(3.5,1.6)} {c.p(5.3,1.75)}', stroke="#1C1631", w=S * 0.24))
for (u, rot) in [(6.35, -4), (9.0, 6)]:
    x, y = c.P(u, 1.55)
    lens = c.lin([(0, "#4B3C7A"), (0.6, "#2A2148"), (1, "#3E8FA8")], 0, 0, 0.3, 1)
    F(c, f'<g transform="rotate({rot} {x:.1f} {y:.1f})"><path d="M{x-S*1.25:.1f},{y-S*0.7:.1f} H{x+S*1.25:.1f} Q{x+S*1.35:.1f},{y+S*0.9:.1f} {x:.1f},{y+S*0.85:.1f} Q{x-S*1.35:.1f},{y+S*0.9:.1f} {x-S*1.25:.1f},{y-S*0.7:.1f} Z" fill="{lens}" stroke="#1C1631" stroke-width="{S*0.14:.1f}"/>'
      f'<path d="M{x-S*0.8:.1f},{y+S*0.35:.1f} L{x-S*0.15:.1f},{y-S*0.45:.1f}" stroke="#fff" stroke-width="{S*0.18:.1f}" stroke-linecap="round" opacity=".55"/></g>')
F(c, path(f'M{c.p(7.55,1.2)} Q{c.p(7.7,0.9)} {c.p(7.85,1.2)}', stroke="#1C1631", w=S * 0.22))
c.shadow(f'M{c.p(4.0,1.0)} H{c.p(9.2,1.0)[0:0]}{c.P(9.2,1.0)[0]:.1f} V{c.P(9.2,2.3)[1]:.1f} H{c.P(4.0,2.3)[0]:.1f} Z', 0.1, 0.35, 0.3)
ch[('beach', 'yellow')] = c

# ===================== THE SLOPES =====================
# Verde: gorro tejido (puntos en V, franjas, doblez acanalado y pompón esponjoso) y bufanda con flecos
c = Ch('green', 'sg'); S = c.S
dome = f'M{c.p(-0.25,3.5)} C{c.p(-0.6,-1.4)} {c.p(3.2,-2.6)} {c.p(5.2,-2.3)} C{c.p(8.4,-1.9)} {c.p(10.7,0.4)} {c.p(10.25,3.4)} Z'
c.shadow(dome, 0.1, 0.5, 0.4)
F(c, path(dome, fill=c.rad([(0, "#FFB9A3"), (0.6, "#F57A5A"), (1, "#D35A3E")], .4, .25, .85)))
c.defs.append(f'<clipPath id="sg-dome"><path d="{dome}"/></clipPath>')
st = []
for v in (0.9,):
    st.append(f'<path d="M{c.p(-1,v+0.4)} Q{c.p(5,v-0.8)} {c.p(11,v+0.4)} L{c.p(11,v+1.15)} Q{c.p(5,v-0.05)} {c.p(-1,v+1.15)} Z" fill="#FFF3EA"/>')
for row in range(8):
    v = -1.5 + row * 0.55
    for i in range(22):
        u = -0.4 + i * 0.52 + (row % 2) * 0.26
        x, y = c.P(u, v + 0.75 * ((u - 5) / 4.2) ** 2 * 0.9)
        st.append(f'<path d="M{x-S*0.16:.1f},{y-S*0.12:.1f} L{x:.1f},{y+S*0.12:.1f} L{x+S*0.16:.1f},{y-S*0.12:.1f}" stroke="#B9452C" stroke-width="{S*0.07:.1f}" fill="none" opacity=".35"/>')
F(c, f'<g clip-path="url(#sg-dome)">{"".join(st)}</g>')
F(c, f'<ellipse cx="{c.P(2.6,-0.6)[0]:.1f}" cy="{c.P(2.6,-0.6)[1]:.1f}" rx="{S*1.3:.1f}" ry="{S*0.4:.1f}" transform="rotate(-28 {c.P(2.6,-0.6)[0]:.1f} {c.P(2.6,-0.6)[1]:.1f})" fill="#fff" opacity=".35"/>')
cuff = f'M{c.p(-0.45,2.55)} Q{c.p(5,1.6)} {c.p(10.45,2.45)} L{c.p(10.4,3.95)} Q{c.p(5,3.05)} {c.p(-0.4,4.05)} Z'
c.shadow(cuff, 0.1, 0.45, 0.45)
F(c, path(cuff, fill=c.lin([(0, "#FFFBF6"), (1, "#E7DCCD")])))
for i in range(21):
    u = -0.1 + i * 0.5; t = (u - 5) / 5.5
    F(c, path(f'M{c.p(u,2.6 - (1 - t*t) * 0.95 + 0.12)} L{c.p(u,3.95 - (1 - t*t) * 0.95)}', stroke="#D6C8B4", w=S * 0.1))
F(c, fluff(c, 4.4, -2.45, 1.2, "#FFF6EE", "#E2D3C2", 10))
sc = f'M{c.p(0.4,7.5)} Q{c.p(5,9.3)} {c.p(9.6,7.5)} L{c.p(9.45,8.9)} Q{c.p(5,10.7)} {c.p(0.55,8.9)} Z'
c.shadow(sc, 0, -0.45, 0.35)
F(c, path(sc, fill=c.lin([(0, "#5CC8E2"), (1, "#238FB2")])))
for i in range(9):
    u = 1.0 + i * 1.0; t = (u - 5) / 4.6; vv = 7.6 + (1 - t * t) * 1.75
    F(c, path(f'M{c.p(u,vv)} l{S*0.25:.1f},{S*0.55:.1f} l{S*0.25:.1f},{-S*0.55:.1f}', stroke="#1C7898", w=S * 0.09, extra='opacity=".5"'))
F(c, path(f'M{c.p(0.6,7.8)} Q{c.p(5,9.5)} {c.p(9.4,7.8)}', stroke="#A9E6F3", w=S * 0.14, extra='opacity=".75"'))
tail = f'M{c.p(6.6,9.0)} Q{c.p(6.9,10.1)} {c.p(7.0,11.2)} L{c.p(8.5,11.0)} Q{c.p(8.2,9.9)} {c.p(8.1,8.8)} Z'
FA(c, 'swing', (7.35, 8.9), path(tail, fill=c.lin([(0, "#2FA3C4"), (1, "#1C7898")])),
   *[path(f'M{c.p(6.85,v)} L{c.p(8.3,v-0.05)}', stroke="#F57A5A", w=S * 0.22) for v in (9.8, 10.5)],
   *[path(f'M{c.p(7.1+i*0.33,11.15)} l{S*0.05:.1f},{S*0.55:.1f}', stroke="#2FA3C4", w=S * 0.12) for i in range(5)])
ch[('snow', 'green')] = c

# Naranja: casco de esquí con goggles espejo encima
c = Ch('orange', 'so'); S = c.S
hel = f'M{c.p(0.9,2.3)} C{c.p(0.6,-2.2)} {c.p(9.4,-2.2)} {c.p(9.3,2.4)} Q{c.p(5,1.2)} {c.p(0.9,2.3)} Z'
c.shadow(hel, 0.1, 0.45, 0.45)
F(c, path(hel, fill=c.rad([(0, "#6E7BA8"), (0.55, "#3A4468"), (1, "#232A44")], .38, .25, .85)))
F(c, path(f'M{c.p(0.95,2.25)} Q{c.p(5,1.15)} {c.p(9.25,2.35)}', stroke="#151A2C", w=S * 0.3))
for u in (3.6, 5.0, 6.4): F(c, path(f'M{c.p(u,-0.75)} L{c.p(u+0.15,0.15)}', stroke="#151A2C", w=S * 0.3, extra='opacity=".7"'))
F(c, f'<ellipse cx="{c.P(3.1,-0.2)[0]:.1f}" cy="{c.P(3.1,-0.2)[1]:.1f}" rx="{S*1.2:.1f}" ry="{S*0.32:.1f}" transform="rotate(-30 {c.P(3.1,-0.2)[0]:.1f} {c.P(3.1,-0.2)[1]:.1f})" fill="#fff" opacity=".35"/>')
F(c, path(f'M{c.p(1.1,1.3)} Q{c.p(5,-0.1)} {c.p(9.2,1.4)}', stroke="#F1C84D", w=S * 0.42))
gx, gy = c.P(4.4, 0.25); gw, gh = c.bw * 0.52, c.bh * 0.27
F(c, f'<rect x="{gx:.1f}" y="{gy:.1f}" width="{gw:.1f}" height="{gh:.1f}" rx="{gh*0.48:.1f}" fill="#1E2336"/>',
  f'<rect x="{gx+S*0.28:.1f}" y="{gy+S*0.26:.1f}" width="{gw-S*0.56:.1f}" height="{gh-S*0.52:.1f}" rx="{gh*0.36:.1f}" fill="{c.lin([(0,"#FFD27A"),(0.35,"#FF8A65"),(0.7,"#A584E8"),(1,"#5BC6E0")],0,0,1,1)}"/>',
  f'<path d="M{gx+S*0.8:.1f},{gy+gh-S*0.45:.1f} L{gx+S*1.6:.1f},{gy+S*0.45:.1f}" stroke="#fff" stroke-width="{S*0.3:.1f}" stroke-linecap="round" opacity=".7"/>',
  f'<path d="M{gx+S*2.1:.1f},{gy+gh-S*0.45:.1f} L{gx+S*2.5:.1f},{gy+S*0.45:.1f}" stroke="#fff" stroke-width="{S*0.14:.1f}" stroke-linecap="round" opacity=".6"/>')
ch[('snow', 'orange')] = c
ch[('snow', 'purple')] = Ch('purpleYeti', 'sp')

# Amarillo: orejeras esponjosas con su diadema
c = Ch('yellow', 'sy'); S = c.S
band = f'M{c.p(3.0,3.6)} C{c.p(2.2,-1.6)} {c.p(9.2,-2.3)} {c.p(9.8,2.6)}'
c.shadow_stroke(band, S * 0.55, 0.1, 0.45)
F(c, path(band, stroke="#C24E7D", w=S * 0.62), path(band, stroke=c.lin([(0, "#FFB6D2"), (1, "#E0679B")], 0, 0, 1, 0), w=S * 0.46),
  path(f'M{c.p(3.2,1.2)} C{c.p(3.8,-0.6)} {c.p(5.6,-1.0)} {c.p(6.8,-0.9)}', stroke="#fff", w=S * 0.14, extra='opacity=".6"'))
B(c, fluff(c, 9.9, 2.9, 1.05, "#FFD9E8", "#E896B8", 10))
c.shadow(f'M{c.p(1.6,2.6)} h{S*2.8:.1f} v{S*2.6:.1f} h{-S*2.8:.1f} Z', 0.25, 0.4, 0.35)
F(c, fluff(c, 3.0, 3.9, 1.45, "#FFE6F0", "#F2A9C7", 11))
ch[('snow', 'yellow')] = c

# ===================== THE CITY =====================
# Verde: gorra de seis gajos con visera y estrellita, y mochila con bolsa y cierre
c = Ch('green', 'cg'); S = c.S
x, y = c.P(-1.2, 2.9)
B(c, f'<rect x="{x:.1f}" y="{y:.1f}" width="{S*3.6:.1f}" height="{S*4.9:.1f}" rx="{S*1.2:.1f}" fill="{c.lin([(0,"#FFB08A"),(1,"#E9663E")],0,0,1,1)}"/>',
  f'<path d="M{x:.1f},{y+S*1.5:.1f} Q{x+S*1.8:.1f},{y+S*2.3:.1f} {x+S*3.6:.1f},{y+S*1.5:.1f} V{y+S*1.0:.1f} Q{x+S*3.6:.1f},{y:.1f} {x+S*2.4:.1f},{y:.1f} H{x+S*1.2:.1f} Q{x:.1f},{y:.1f} {x:.1f},{y+S*1.0:.1f} Z" fill="#D9552F"/>',
  f'<rect x="{x+S*0.45:.1f}" y="{y+S*2.8:.1f}" width="{S*2.7:.1f}" height="{S*1.7:.1f}" rx="{S*0.55:.1f}" fill="#F27A50"/>',
  f'<path d="M{x+S*0.8:.1f},{y+S*3.2:.1f} H{x+S*2.8:.1f}" stroke="#FFD27A" stroke-width="{S*0.16:.1f}" stroke-linecap="round"/>',
  f'<path d="M{x+S*0.5:.1f},{y+S*0.6:.1f} Q{x+S*0.9:.1f},{y+S*0.2:.1f} {x+S*1.4:.1f},{y+S*0.25:.1f}" stroke="#fff" stroke-width="{S*0.18:.1f}" stroke-linecap="round" opacity=".55" fill="none"/>')
stp = f'M{c.p(1.5,1.4)} Q{c.p(3.3,4.6)} {c.p(2.1,8.4)}'
c.shadow_stroke(stp, S * 0.5)
F(c, path(stp, stroke="#C9512C", w=S * 0.55), path(stp, stroke="#F07A50", w=S * 0.36))
F(c, f'<rect x="{c.P(2.45,4.4)[0]:.1f}" y="{c.P(2.45,4.4)[1]:.1f}" width="{S*0.7:.1f}" height="{S*0.55:.1f}" rx="{S*0.12:.1f}" fill="#2E3448"/>')
crown = f'M{c.p(2.8,1.7)} C{c.p(2.7,-1.2)} {c.p(8.4,-1.3)} {c.p(8.3,1.5)} Q{c.p(5.5,0.9)} {c.p(2.8,1.7)} Z'
c.shadow(crown, 0.1, 0.45, 0.45)
F(c, path(crown, fill=c.rad([(0, "#7FD5EC"), (0.6, "#2FA3C4"), (1, "#1A6E90")], .35, .25, .85)))
for u in (4.3, 5.6, 6.9): F(c, path(f'M{c.p(u,1.3)} Q{c.p(u+0.15,0.1)} {c.p(5.6,-0.75)}', stroke="#17607F", w=S * 0.07, extra='opacity=".55"'))
F(c, f'<ellipse cx="{c.P(4.3,-0.1)[0]:.1f}" cy="{c.P(4.3,-0.1)[1]:.1f}" rx="{S*0.85:.1f}" ry="{S*0.28:.1f}" transform="rotate(-25 {c.P(4.3,-0.1)[0]:.1f} {c.P(4.3,-0.1)[1]:.1f})" fill="#fff" opacity=".45"/>')
brim = f'M{c.p(7.4,1.05)} Q{c.p(10.3,0.25)} {c.p(11.6,1.45)} Q{c.p(10.0,2.15)} {c.p(7.7,1.95)} Z'
c.shadow(brim, -0.1, 0.55, 0.45)
F(c, path(brim, fill=c.lin([(0, "#2386A8"), (1, "#145A78")])), path(f'M{c.p(7.6,1.15)} Q{c.p(10.2,0.4)} {c.p(11.5,1.42)}', stroke="#7FD5EC", w=S * 0.1, extra='opacity=".8"'))
F(c, circ(c, 5.6, -0.8, 0.3, "#1A6E90"), circ(c, 5.55, -0.86, 0.13, "#7FD5EC"))
sx, sy = c.P(6.4, 0.4); pts = ' '.join(f'{sx+math.cos(-math.pi/2+i*math.pi/5)*S*(0.5 if i%2==0 else 0.22):.1f},{sy+math.sin(-math.pi/2+i*math.pi/5)*S*(0.5 if i%2==0 else 0.22):.1f}' for i in range(10))
F(c, f'<polygon points="{pts}" fill="#F1C84D"/>')
ch[('city', 'green')] = c

# Naranja: mensajero (casco aerodinámico con ventilas y bolsa cruzada con hebilla)
c = Ch('orange', 'co'); S = c.S
stp = f'M{c.p(1.7,7.2)} L{c.p(7.9,0.9)}'
c.shadow_stroke(stp, S * 0.5)
F(c, path(stp, stroke="#1E2336", w=S * 0.5), path(f'M{c.p(1.75,7.0)} L{c.p(7.85,0.75)}', stroke="#4A5372", w=S * 0.12))
x, y = c.P(-0.6, 6.2)
F(c, f'<rect x="{x:.1f}" y="{y:.1f}" width="{S*3.2:.1f}" height="{S*2.5:.1f}" rx="{S*0.55:.1f}" fill="{c.lin([(0,"#79D6A9"),(1,"#2F9E73")])}"/>',
  f'<path d="M{x:.1f},{y+S*0.55:.1f} Q{x:.1f},{y:.1f} {x+S*0.55:.1f},{y:.1f} H{x+S*2.65:.1f} Q{x+S*3.2:.1f},{y:.1f} {x+S*3.2:.1f},{y+S*0.55:.1f} V{y+S*1.2:.1f} Q{x+S*1.6:.1f},{y+S*1.55:.1f} {x:.1f},{y+S*1.2:.1f} Z" fill="#268A63"/>',
  f'<rect x="{x+S*1.3:.1f}" y="{y+S*0.95:.1f}" width="{S*0.6:.1f}" height="{S*0.55:.1f}" rx="{S*0.12:.1f}" fill="#F1C84D" stroke="#B88A1A" stroke-width="{S*0.06:.1f}"/>',
  f'<path d="M{x+S*0.35:.1f},{y+S*0.35:.1f} H{x+S*1.1:.1f}" stroke="#fff" stroke-width="{S*0.14:.1f}" stroke-linecap="round" opacity=".6"/>')
hel = f'M{c.p(1.2,2.0)} C{c.p(0.9,-1.9)} {c.p(8.6,-2.4)} {c.p(10.0,1.2)} Q{c.p(10.6,2.1)} {c.p(9.6,2.5)} Q{c.p(5.4,1.3)} {c.p(1.2,2.0)} Z'
c.shadow(hel, 0.1, 0.45, 0.45)
F(c, path(hel, fill=c.rad([(0, "#FFFFFF"), (0.55, "#E6F4F8"), (1, "#A8D4E3")], .38, .25, .85)))
c.defs.append(f'<clipPath id="co-hel"><path d="{hel}"/></clipPath>')
F(c, f'<g clip-path="url(#co-hel)">', path(f'M{c.p(0,1.9)} Q{c.p(5.4,0.9)} {c.p(11,2.4)} L{c.p(11,3)} L{c.p(0,3)} Z', fill="#2FA3C4"), '</g>')
for (u, v) in [(3.1, -0.15), (4.8, -0.55), (6.5, -0.4), (8.0, 0.2)]:
    x, y = c.P(u, v)
    F(c, f'<rect x="{x-S*0.65:.1f}" y="{y-S*0.16:.1f}" width="{S*1.3:.1f}" height="{S*0.32:.1f}" rx="{S*0.16:.1f}" transform="rotate({(u-5.6)*9:.0f} {x:.1f} {y:.1f})" fill="#2E3448" opacity=".8"/>')
F(c, f'<ellipse cx="{c.P(3.2,-0.9)[0]:.1f}" cy="{c.P(3.2,-0.9)[1]:.1f}" rx="{S*1.0:.1f}" ry="{S*0.25:.1f}" transform="rotate(-22 {c.P(3.2,-0.9)[0]:.1f} {c.P(3.2,-0.9)[1]:.1f})" fill="#fff" opacity=".9"/>')
ch[('city', 'orange')] = c

# Morado: obrero (casco con cresta, visera y calcomanía; chaleco con tirantes y franjas reflejantes)
c = Ch('purple', 'cp'); S = c.S
ex, ey = c.P(5.0, 4.95)
c.defs.append(f'<clipPath id="cp-clip"><ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{c.bw*0.5:.1f}" ry="{c.bh*0.49:.1f}"/></clipPath>')
vest = c.lin([(0, "#FFB070"), (1, "#EE6F22")])
c.shadow(f'M{c.p(-1,6.4)} Q{c.p(5,7.7)} {c.p(11,6.1)} L{c.p(11,12)} L{c.p(-1,12)} Z', 0, -0.4, 0.35)
F(c, f'<g clip-path="url(#cp-clip)">',
  path(f'M{c.p(-1,6.5)} Q{c.p(5,7.8)} {c.p(11,6.2)} L{c.p(11,12)} L{c.p(-1,12)} Z', fill=vest),
  
  path(f'M{c.p(-1,8.0)} Q{c.p(5,9.3)} {c.p(11,7.7)}', stroke="#E8ECF2", w=S * 0.5), path(f'M{c.p(-1,7.88)} Q{c.p(5,9.18)} {c.p(11,7.58)}', stroke="#fff", w=S * 0.14),
  path(f'M{c.p(-1,9.1)} Q{c.p(5,10.4)} {c.p(11,8.8)}', stroke="#E8ECF2", w=S * 0.5), path(f'M{c.p(-1,8.98)} Q{c.p(5,10.28)} {c.p(11,8.68)}', stroke="#fff", w=S * 0.14),
  f'<rect x="{c.P(2.0,9.6)[0]:.1f}" y="{c.P(2.0,9.6)[1]:.1f}" width="{S*1.3:.1f}" height="{S*0.9:.1f}" rx="{S*0.2:.1f}" fill="#E2661C"/>',
  '</g>')
hh = f'M{c.p(1.5,1.6)} C{c.p(1.5,-2.3)} {c.p(8.7,-2.3)} {c.p(8.7,1.6)} Z'
c.shadow(hh, 0.1, 0.5, 0.45)
F(c, path(hh, fill=c.rad([(0, "#FFF0A8"), (0.55, "#F6C945"), (1, "#D49A16")], .38, .28, .85)),
  path(f'M{c.p(4.4,-1.35)} Q{c.p(5.1,-1.65)} {c.p(5.8,-1.35)} L{c.p(5.8,1.4)} L{c.p(4.4,1.4)} Z', fill="#E7B12C"),
  path(f'M{c.p(4.5,-1.3)} L{c.p(4.5,1.3)}', stroke="#FFF3C4", w=S * 0.1, extra='opacity=".8"'))
brim = f'M{c.p(0.9,1.6)} Q{c.p(5.4,0.75)} {c.p(10.9,1.25)} Q{c.p(11.3,2.05)} {c.p(10.4,2.35)} Q{c.p(5.4,1.65)} {c.p(1.1,2.3)} Q{c.p(0.6,2.2)} {c.p(0.9,1.6)} Z'
c.shadow(brim, 0, 0.5, 0.45)
F(c, path(brim, fill=c.lin([(0, "#F6C945"), (1, "#C98C12")])), path(f'M{c.p(1.1,1.65)} Q{c.p(5.4,0.85)} {c.p(10.7,1.35)}', stroke="#FFF0A8", w=S * 0.1))
F(c, circ(c, 7.4, 0.35, 0.48, "#FFFFFF"), circ(c, 7.4, 0.35, 0.3, "#FF8A65"))
F(c, f'<ellipse cx="{c.P(3.0,-0.5)[0]:.1f}" cy="{c.P(3.0,-0.5)[1]:.1f}" rx="{S*0.85:.1f}" ry="{S*0.26:.1f}" transform="rotate(-35 {c.P(3.0,-0.5)[0]:.1f} {c.P(3.0,-0.5)[1]:.1f})" fill="#fff" opacity=".6"/>')
ch[('city', 'purple')] = c

# Amarillo: letrero de taxi iluminado (con su brillo, cuadritos y base)
c = Ch('yellow', 'cy'); S = c.S
x, y = c.P(2.2, -2.2); w, h = S * 5.6, S * 2.3
F(c, f'<ellipse cx="{x+w/2:.1f}" cy="{y+h/2:.1f}" rx="{w*0.8:.1f}" ry="{h*1.0:.1f}" fill="{c.rad([(0,"rgba(255,230,140,0.55)"),(1,"rgba(255,230,140,0)")],.5,.5,.5)}"/>')
c.shadow(f'M{x:.1f},{y+h:.1f} h{w:.1f} v{S*0.9:.1f} h{-w:.1f} Z', 0, 0.3, 0.4)
F(c, f'<path d="M{x+S*0.25:.1f},{y+h+S*0.5:.1f} H{x+w-S*0.25:.1f} L{x+w-S*0.6:.1f},{y+h+S*0.95:.1f} H{x+S*0.6:.1f} Z" fill="#1E2336"/>',
  f'<path d="M{x+S*0.45:.1f},{y:.1f} H{x+w-S*0.45:.1f} Q{x+w:.1f},{y:.1f} {x+w:.1f},{y+S*0.5:.1f} L{x+w:.1f},{y+h:.1f} H{x:.1f} L{x:.1f},{y+S*0.5:.1f} Q{x:.1f},{y:.1f} {x+S*0.45:.1f},{y:.1f} Z" fill="{c.lin([(0,"#FFFBE6"),(1,"#FFE79A")])}" stroke="#2E3448" stroke-width="{S*0.16:.1f}"/>',
  f'<text x="{x+w/2:.1f}" y="{y+h*0.74:.1f}" text-anchor="middle" font-family="Outfit,Arial Black,sans-serif" font-weight="900" font-size="{S*1.45:.1f}" fill="#2E3448" letter-spacing="{S*0.08:.1f}">TAXI</text>',
  f'<rect x="{x+S*0.35:.1f}" y="{y+S*0.22:.1f}" width="{w*0.42:.1f}" height="{S*0.26:.1f}" rx="{S*0.13:.1f}" fill="#fff" opacity=".85"/>')
cw = (w - S * 0.5) / 8
for i in range(8):
    for r in range(2):
        F(c, f'<rect x="{x+S*0.25+i*cw:.1f}" y="{y+h+r*S*0.25:.1f}" width="{cw:.1f}" height="{S*0.25:.1f}" fill="{"#2E3448" if (i+r)%2 else "#FFFFFF"}"/>')
ch[('city', 'yellow')] = c

# ===================== THE JUNGLE =====================
# Verde: hoja de costilla de Adán (con sus cortes y nervios) como sombrilla
c = Ch('green', 'jg'); S = c.S
stem = f'M{c.p(9.7,6.6)} Q{c.p(11.0,2.4)} {c.p(6.2,-1.3)}'
BA(c, 'leaf', (9.7, 6.6), path(stem, stroke="#3E7A44", w=S * 0.42), path(stem, stroke="#6DB868", w=S * 0.16, extra='opacity=".7"'))
x, y = c.P(5.3, -2.3)
lf = f'M{x - S*6.2:.1f},{y + S*1.9:.1f} C{x - S*5.6:.1f},{y - S*2.9:.1f} {x + S*5.2:.1f},{y - S*3.3:.1f} {x + S*6.4:.1f},{y + S*1.7:.1f} C{x + S*3.0:.1f},{y + S*0.55:.1f} {x - S*3.0:.1f},{y + S*0.7:.1f} {x - S*6.2:.1f},{y + S*1.9:.1f} Z'
m = ''.join(f'<path d="M{x + S*t:.1f},{y + S*1.2:.1f} L{x + S*(t*1.08):.1f},{y - S*0.9 + abs(t)*S*0.12:.1f}" stroke="black" stroke-width="{S*0.32:.1f}" stroke-linecap="round"/>' for t in (-4.4, -2.4, 2.3, 4.3))
m += ''.join(f'<ellipse cx="{x + S*t:.1f}" cy="{y - S*0.6:.1f}" rx="{S*0.32:.1f}" ry="{S*0.55:.1f}" fill="black"/>' for t in (-1.2, 1.2))
c.defs.append(f'<mask id="jg-cuts"><rect x="-99999" y="-99999" width="199999" height="199999" fill="white"/>{m}</mask>')
c.shadow(f'M{x - S*5:.1f},{y + S*1.6:.1f} Q{x:.1f},{y + S*0.3:.1f} {x + S*5:.1f},{y + S*1.6:.1f} L{x + S*5:.1f},{y + S*2.6:.1f} L{x - S*5:.1f},{y + S*2.6:.1f} Z', 0, 0.9, 0.35)
FA(c, 'leaf', (9.7, 6.6), f'<g mask="url(#jg-cuts)">', path(lf, fill=c.lin([(0, "#8FD08A"), (0.5, "#4E9E58"), (1, "#2C6E41")], 0, 0, 0.4, 1)),
  path(f'M{x - S*5.6:.1f},{y + S*1.5:.1f} Q{x:.1f},{y - S*1.9:.1f} {x + S*5.8:.1f},{y + S*1.3:.1f}', stroke="#C9EDC0", w=S * 0.16, extra='opacity=".9"'),
  ''.join(path(f'M{x + S*t*0.35:.1f},{y - S*0.95 + abs(t)*S*0.05:.1f} Q{x + S*t*0.8:.1f},{y - S*0.4:.1f} {x + S*t:.1f},{y + S*1.05 - abs(t)*S*0.04:.1f}', stroke="#A9DCA0", w=S * 0.08, extra='opacity=".7"') for t in (-5.2, -3.4, -1.6, 1.6, 3.4, 5.2)),
  f'<ellipse cx="{x - S*2.6:.1f}" cy="{y - S*0.9:.1f}" rx="{S*1.4:.1f}" ry="{S*0.32:.1f}" transform="rotate(-12 {x - S*2.6:.1f} {y - S*0.9:.1f})" fill="#fff" opacity=".35"/>', '</g>')
ch[('jungle', 'green')] = c

# Naranja: casco de explorador (ala con sombra, cinta, botón y una hojita en la cinta)
c = Ch('orange', 'jo'); S = c.S
brim = f'M{c.p(-0.6,1.9)} Q{c.p(5.4,0.2)} {c.p(11.8,1.6)} Q{c.p(11.8,2.8)} {c.p(5.4,3.2)} Q{c.p(-0.5,3.0)} {c.p(-0.6,1.9)} Z'
c.shadow(brim, 0, 0.55, 0.45)
F(c, path(brim, fill=c.lin([(0, "#F3E4C2"), (1, "#C6A970")])), path(f'M{c.p(-0.8,1.85)} Q{c.p(5,0.35)} {c.p(10.8,1.85)}', stroke="#FFF6DF", w=S * 0.12))
dome = f'M{c.p(1.4,1.9)} C{c.p(1.2,-2.8)} {c.p(8.8,-2.8)} {c.p(8.6,1.9)} Q{c.p(5,1.2)} {c.p(1.4,1.9)} Z'
F(c, path(dome, fill=c.rad([(0, "#FFF8E6"), (0.6, "#E9D7AE"), (1, "#BFA06A")], .38, .25, .85)))
for u in (3.6, 6.4): F(c, path(f'M{c.p(u,1.2)} Q{c.p(u+(5-u)*0.35,-0.8)} {c.p(5,-1.85)}', stroke="#C9AE78", w=S * 0.08, extra='opacity=".7"'))
F(c, path(f'M{c.p(1.42,1.15)} Q{c.p(5,0.0)} {c.p(8.58,1.15)} L{c.p(8.6,1.9)} Q{c.p(5,0.85)} {c.p(1.4,1.9)} Z', fill=c.lin([(0, "#8A684C"), (1, "#5E4433")])))
lx, ly = c.P(2.6, 1.1)
F(c, f'<g transform="translate({lx:.1f} {ly:.1f}) rotate(-60)"><path d="M0,0 C{-S*0.7:.1f},{-S*0.8:.1f} {-S*0.3:.1f},{-S*2.0:.1f} 0,{-S*2.3:.1f} C{S*0.3:.1f},{-S*2.0:.1f} {S*0.7:.1f},{-S*0.8:.1f} 0,0 Z" fill="{c.lin([(0,"#8FD08A"),(1,"#2F7A48")])}"/><path d="M0,0 L0,{-S*2.1:.1f}" stroke="#D7F2CF" stroke-width="{S*0.08:.1f}"/></g>')
F(c, circ(c, 5.0, -1.95, 0.32, "#C9AE78"), circ(c, 4.95, -2.02, 0.14, "#FFF6DF"))
F(c, f'<ellipse cx="{c.P(3.4,-0.6)[0]:.1f}" cy="{c.P(3.4,-0.6)[1]:.1f}" rx="{S*1.0:.1f}" ry="{S*0.3:.1f}" transform="rotate(-30 {c.P(3.4,-0.6)[0]:.1f} {c.P(3.4,-0.6)[1]:.1f})" fill="#fff" opacity=".6"/>')
ch[('jungle', 'orange')] = c

# Morado: corona de hojas (con nervio) y tres flores de hibisco
c = Ch('purple', 'jp'); S = c.S
CROWN = []
cols = [("#A9DCA0", "#2F7A48"), ("#8FD08A", "#2E6B45"), ("#B9E6B0", "#3F8457")]
c.shadow(f'M{c.p(1.2,1.0)} Q{c.p(5.2,-0.2)} {c.p(9.0,1.2)} L{c.p(9.0,2.2)} Q{c.p(5.2,1.0)} {c.p(1.2,2.0)} Z', 0, 0.3, 0.4)
for i, (u, ang, L) in enumerate([(1.6, -50, 2.6), (2.7, -30, 3.3), (4.1, -12, 3.7), (5.6, 6, 3.9), (7.0, 24, 3.5), (8.3, 44, 2.8)]):
    x, y = c.P(u, 0.85 + abs(u - 5.2) * 0.13); a, b = cols[i % 3]
    veins = ''.join(f'<path d="M0,{-S*L*t:.1f} l{sd*S*L*0.16:.1f},{-S*L*0.12:.1f}" stroke="#D7F2CF" stroke-width="{S*0.06:.1f}" opacity=".7"/>' for t in (0.3, 0.5, 0.7) for sd in (-1, 1))
    CROWN.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang})"><path d="M0,0 C{-S*L*0.34:.1f},{-S*L*0.45:.1f} {-S*L*0.16:.1f},{-S*L*0.88:.1f} 0,{-S*L:.1f} C{S*L*0.16:.1f},{-S*L*0.88:.1f} {S*L*0.34:.1f},{-S*L*0.45:.1f} 0,0 Z" fill="{c.lin([(0,a),(1,b)],0,1,0,0)}"/><path d="M0,0 L0,{-S*L*0.92:.1f}" stroke="#E6F7DF" stroke-width="{S*0.09:.1f}" opacity=".85"/>{veins}</g>')
for (u, c1, c2) in [(2.7, "#FFB59B", "#E9573A"), (5.2, "#FFE38A", "#E9A923"), (7.7, "#FFC2DA", "#E0679B")]:
    x, y = c.P(u, 1.1 + abs(u - 5.2) * 0.13)
    pg = c.rad([(0, "#FFFFFF"), (0.35, c1), (1, c2)], .5, .5, .6)
    for a in range(5):
        ang = -90 + a * 72
        CROWN.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang})"><path d="M0,0 C{S*0.2:.1f},{-S*0.45:.1f} {S*0.95:.1f},{-S*0.55:.1f} {S*0.95:.1f},0 C{S*0.95:.1f},{S*0.55:.1f} {S*0.2:.1f},{S*0.45:.1f} 0,0 Z" fill="{pg}"/></g>')
    CROWN.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{S*0.2:.1f}" fill="#FFF3C4"/>' + path(f'M{x:.1f},{y:.1f} l{S*0.35:.1f},{-S*0.45:.1f}', stroke="#FFF3C4", w=S * 0.08))
FA(c, 'crown', (5.2, 1.3), *CROWN)
ch[('jungle', 'purple')] = c

# Amarillo: alas de mariposa (dos pares, con nervaduras, orilla oscura y puntitos)
c = Ch('yellow', 'jy'); S = c.S
def wing(c, u, v, ang, sc, col1, col2, edge, flip=1):
    x, y = c.P(u, v); S = c.S
    wg = c.rad([(0, "#FFFFFF"), (0.25, col1), (1, col2)], .75, .8, .95)
    wl = c.rad([(0, "#FFFFFF"), (0.3, col1), (1, col2)], .75, .2, .95)
    up = f'M0,0 C{-S*0.9:.1f},{-S*5.4:.1f} {-S*6.2:.1f},{-S*5.6:.1f} {-S*5.2:.1f},{-S*1.5:.1f} C{-S*4.6:.1f},{S*0.1:.1f} {-S*2.2:.1f},{S*0.5:.1f} 0,0 Z'
    lo = f'M0,{S*0.2:.1f} C{-S*3.3:.1f},{S*0.3:.1f} {-S*3.8:.1f},{S*3.4:.1f} {-S*1.6:.1f},{S*3.2:.1f} C{-S*0.5:.1f},{S*2.9:.1f} {-S*0.2:.1f},{S*1.3:.1f} 0,{S*0.2:.1f} Z'
    veins = ''.join(f'<path d="M0,0 Q{-S*a*0.6:.1f},{-S*b*0.4:.1f} {-S*a:.1f},{-S*b:.1f}" stroke="{edge}" stroke-width="{S*0.07:.1f}" fill="none" opacity=".45"/>' for a, b in [(4.6, 3.6), (3.4, 4.3), (5.0, 1.8), (2.0, 4.0)])
    veins += ''.join(f'<path d="M0,{S*0.3:.1f} Q{-S*a*0.6:.1f},{S*b*0.5:.1f} {-S*a:.1f},{S*b:.1f}" stroke="{edge}" stroke-width="{S*0.07:.1f}" fill="none" opacity=".45"/>' for a, b in [(2.6, 2.6), (1.4, 2.9)])
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang}) scale({flip*sc:.2f} {sc:.2f})" opacity=".97">'
            f'<path d="{up}" fill="{wg}" stroke="{edge}" stroke-width="{S*0.22:.1f}"/><path d="{lo}" fill="{wl}" stroke="{edge}" stroke-width="{S*0.22:.1f}"/>{veins}'
            f'<circle cx="{-S*4.2:.1f}" cy="{-S*2.6:.1f}" r="{S*0.42:.1f}" fill="#fff" opacity=".9"/><circle cx="{-S*3.3:.1f}" cy="{-S*3.6:.1f}" r="{S*0.25:.1f}" fill="#fff" opacity=".85"/>'
            f'<circle cx="{-S*1.9:.1f}" cy="{S*2.3:.1f}" r="{S*0.3:.1f}" fill="#fff" opacity=".85"/></g>')
c.padk = 0.62
BA(c, 'wing', (3.6, 1.6), wing(c, 3.6, 1.6, 12, 0.85, "#9BEDE4", "#2FA39A", "#1D6F69"), ph=1)
BA(c, 'wing', (2.4, 2.8), wing(c, 2.4, 2.8, -16, 1.05, "#FFB3D3", "#E0679B", "#A33A6A"), ph=0)
ch[('jungle', 'yellow')] = c

LEVELS = [
 ("void", "The Void", "Los originales (se quedan como están)", ["Verde", "Naranja", "Morado", "Amarillo"]),
 ("beach", "The Beach", "De vacaciones en la playa", ["Snorkel", "Cangrejito", "Pulpo", "Salvavidas y lentes"]),
 ("snow", "The Slopes", "Bien abrigados en la nieve", ["Gorro tejido y bufanda", "Casco y goggles", "Yeti (el que ya está)", "Orejeras"]),
 ("city", "The City", "Un día en la ciudad", ["Gorra y mochila", "Mensajero en bici", "Obrero", "Taxi"]),
 ("jungle", "The Jungle", "Exploradores de la selva", ["Hoja de sombrilla", "Casco de explorador", "Corona de hojas y flores", "Alas de mariposa"]),
]
html = ['''<!doctype html><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;700;800;900&display=swap" rel="stylesheet">
<style>body{margin:0;background:#F6F3FC;font-family:Outfit,system-ui,sans-serif;color:#242521;width:1400px}
h1{font-size:44px;margin:40px 50px 4px;font-weight:900}p.sub{margin:0 50px 26px;font-size:20px;color:#77737f;font-weight:500}
.lv{margin:0 40px 22px;background:#fff;border-radius:28px;padding:22px 30px 18px;box-shadow:0 2px 10px rgba(60,40,120,.06)}
.lv h2{margin:0;font-size:28px;font-weight:800}.lv h2 small{font-size:18px;color:#8a8494;font-weight:600;margin-left:10px}
.row{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:6px;align-items:end}.c{text-align:center;min-width:0}.c svg{display:block;margin:0 auto;max-width:100%;height:auto}
.c b{display:block;font-size:17px;font-weight:700;margin-top:-6px}.c i{font-style:normal;font-size:14px;color:#8a8494;font-weight:500}</style>
<h1>SMUSH! · Personajes por nivel <span style="color:#A584E8">v5</span></h1><p class="sub">Todos miran hacia sus ojos: la ropa se acomoda hacia ese lado. El pulpo y el cangrejo ya no tienen patas (tentáculos y patitas de cangrejo).</p>''']
roles = ["común · 1 golpe", "rápido", "grande · 3 golpes", "raro · vale más"]
for lid, name, sub, labels in LEVELS:
    html.append(f'<div class="lv"><h2>{name}<small>{sub}</small></h2><div class="row">')
    for i, k in enumerate(['green', 'orange', 'purple', 'yellow']):
        html.append(f'<div class="c">{ch[(lid, k)].svg(240)}<b>{labels[i]}</b><i>{roles[i]}</i></div>')
    html.append('</div></div>')
open(D + '/board5.html', 'w').write(''.join(html))
# Uno grande por personaje (para ver el detalle)
big = ['<!doctype html><style>svg{display:block;margin:0 auto;max-width:100%;height:auto}</style><body style="margin:0;background:#fff;display:grid;grid-template-columns:repeat(4,1fr);width:1600px;align-items:end">']
for lid, *_ in LEVELS[1:]:
    for k in ['green', 'orange', 'purple', 'yellow']: big.append(f'<div>{ch[(lid, k)].svg(400)}</div>')
open(D + '/big5.html', 'w').write(''.join(big))
print("ok")

# ===================== Exportar para el juego: capas por personaje =====================
BASE_PARTS = {
    "green": {"ant": [("antL", (-720.6, -551.6), ['M-720.6-551.6', 'cx="-769.6"']), ("antR", (-611.6, -548.6), ['M-611.6-548.6', 'cx="-567.6"'])],
              "feetB": [((-715, -285), 0.5, 'M-698.5-268.2')], "feetF": [((-790, -335), 0, 'M-779.6-288.8'), ((-595, -288), 1, 'M-544.2-214.5')]},
    "orange": {"ant": [("antR", (-260.6, -513.9), ['M-260.6-513.9', 'cx="-210.3"'])],
               "feetB": [((-372, -305), 0, 'M-359.1-281.8'), ((-300, -268), 0.5, 'M-276.6-256.8'), ((-205, -300), 1, 'cx="-164.6"')], "feetF": []},
    "purple": {"ant": [("antL", (89.4, -582.6), ['M89.4-582.6', 'cx="38.4"']), ("antR", (266.7, -577), ['M315.4-642.6', 'M266.7-578.7', 'cx="322.4"'])],
               "feetB": [((45, -350), 0, 'M63.6-278.8'), ((305, -335), 1, 'M366.5-227.6'), ((140, -270), 0.5, 'M165.4-257.2')], "feetF": []},
    "yellow": {"ant": [("antR", (577.5, -507.7), ['M577.5-507.7', 'M619.5-672.6'])],
               "feetB": [((505, -400), 0, 'M518-372.2'), ((655, -405), 1, 'M694-342.6'), ((575, -368), 0.5, 'M586.2-368')], "feetF": []},
}
BASE_PARTS.update({
    "f_green": {"ant": [("antL", (298.3, 255.1), ['M298.3,255.1', 'cx="244.8"']), ("antR", (418.1, 255.5), ['M418.1,255.5c10.8', 'M418.1,255.5c-.3', 'cx="465.3"'])],
                "feetB": [((460, 515), 1, 'M521.3,593.9'), ((245, 505), 0, 'M260.7,555.8'), ((363, 540), 0.5, 'M398.3,530.4')], "feetF": []},
    "f_orange": {"ant": [("antR", (360.3, 367.5), ['M360.3,367.5', 'cx="352.2"'])],
                 "feetB": [((410, 505), 1, 'M439.7,547.9'), ((295, 505), 0, 'M306.9,523.7'), ((363, 530), 0.5, 'M390.2,523.2')], "feetF": []},
    "f_purple": {"ant": [("antL", (331.4, 233.3), ['M331.4,233.3', 'cx="256.2"']), ("antR", (466, 200), ['M530.7,115.2', 'M539.8,227.3', 'cx="541.1"'])],
                 "feetB": [((255, 560), 0, 'M282.7,669.5'), ((580, 580), 1, 'M669.2,745'), ((424, 690), 0.5, 'M485.3,679.4')], "feetF": []},
    "f_yellow": {"ant": [("antR", (385, 282), ['M447,200.2l-4.6', 'M447,200.2c-2.4'])],
                 "feetB": [((505, 530), 1, 'M599.6,602.3'), ((300, 560), 0, 'M317.6,599.9'), ((425, 612), 0.5, 'M463.6,603.5c-2.8')], "feetF": []},
    "yeti": {"ant": [("antL", (433.7, 372.1), ['M433.7,372.1', 'cx="323.1"']), ("antR", (668, 343), ['M731.5,262.4', 'cx="741.9"'])],
             "feetB": [((330, 700), 0, 'M357.4,803.9'), ((720, 705), 1, 'M806.8,874.4'), ((470, 810), 0.5, 'M510.4,830.6')], "feetF": []},
    "f_yeti": {"ant": [("antL", (485.3, 372.4), ['M485.3,372.4', 'cx="418.9"']), ("antR", (615, 330), ['M677.5,247.2', 'cx="722.4"'])],
               "feetB": [((395, 725), 0, 'M418.9,823.6'), ((650, 720), 1, 'M744.1,890.9'), ((525, 815), 0.5, 'M584.4,805.5')], "feetF": []},
})
DEF_RE = re.compile(r'<(linearGradient|radialGradient|clipPath|filter|mask)\b[^>]*?\bid="([^"]+)"[^>]*?(?:/>|>.*?</\1>)', re.S)
def take(content, key):
    m = re.search(r'<(path|ellipse|circle|polygon)\b[^>]*' + re.escape(key) + r'[^>]*?(?:/>|>\s*</\1>)', content)
    if not m: return content, None
    return content[:m.start()] + content[m.end():], m.group(0)
def prune(defs, content):
    need, todo = {}, set(re.findall(r'#([A-Za-z0-9_\-]+)', content))
    while todo:
        i = todo.pop()
        if i in need or i not in defs: continue
        need[i] = defs[i]; todo |= set(re.findall(r'#([A-Za-z0-9_\-]+)', defs[i]))
    return ''.join(need.values())
def export(c, base, expand):
    vx, vy, vw, vh = c.vb
    if expand:
        pad = vw * 0.34; px = vw * getattr(c, 'padk', 0.34); pb = vw * getattr(c, 'padb', 0)
        X0, Y0, W0, H0 = vx - px, vy - pad * 0.95, vw + px * 2, vh + pad * 1.25 + pb
    else:
        X0, Y0, W0, H0 = vx - vw * 0.12, vy - vh * 0.1, vw * 1.24, vh * 1.14
    inner = c.inner
    defs = {}
    for blk in re.findall(r'<defs>(.*?)</defs>', inner, re.S) + ["".join(c.defs)]:
        for m in DEF_RE.finditer(blk): defs[m.group(2)] = m.group(0)
    styles = ''.join(re.findall(r'<style>.*?</style>', inner, re.S))
    content = re.sub(r'<defs>.*?</defs>', '', inner, flags=re.S)
    layers = []
    rules = re.findall(r'([^{}]+)\{([^{}]*)\}', re.sub(r'</?style>', '', styles))
    def css(body):
        used = set(re.findall(r'class="([^"]+)"', body)); used = {c for u in used for c in u.split()}
        out = []
        for sel, decl in rules:
            names = [x.strip().lstrip('.') for x in sel.split(',')]
            keep = [n for n in names if n in used]
            if keep: out.append(','.join('.' + n for n in keep) + '{' + re.sub(r'\s+', ' ', decl.strip()) + '}')
        return '<style>' + ''.join(out) + '</style>' if out else ''
    def svg(body):
        st = css(body)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{X0:.1f} {Y0:.1f} {W0:.1f} {H0:.1f}" width="{W0:.0f}" height="{H0:.0f}">'
                f'<defs>{st}{prune(defs, body + st)}</defs>{body}</svg>')
    buf = []
    def flush():
        if buf: layers.append({"s": svg(''.join(buf)), "a": None}); buf.clear()
    def anim(kind, piv, body, ph=0):
        flush(); layers.append({"s": svg(body), "a": kind, "x": round(piv[0], 1), "y": round(piv[1], 1), "p": ph})
    def items(lst):
        for it in lst:
            if isinstance(it, str): buf.append(it)
            else: anim(it[1], it[2], it[3], it[4])
    parts = BASE_PARTS.get(base)
    ants, fb, ff = [], [], []
    if parts:
        for kind, piv, keys in parts["ant"]:
            got = []
            for k2 in keys:
                content, el = take(content, k2)
                if el: got.append(el)
            if got: ants.append((kind, piv, ''.join(got)))
        for lst, out in ((parts["feetB"], fb), (parts["feetF"], ff)):
            for piv, ph, k2 in lst:
                content, el = take(content, k2)
                if el: out.append((piv, ph, el))
    items(c.back)
    for kind, piv, el in ants: anim(kind, piv, el)
    for piv, ph, el in fb: anim('foot', piv, el, ph)
    buf.append(content)
    for piv, ph, el in ff: anim('foot', piv, el, ph)
    items(c.front)
    flush()
    return {"base": base, "vb": [round(X0, 1), round(Y0, 1), round(W0, 1), round(H0, 1)], "layers": layers}

RIG = {}
NAMES = {"beach": "beach", "snow": "snow", "city": "city", "jungle": "jungle"}
for k in ['green', 'orange', 'purple', 'yellow']:
    RIG[k] = export(ch[('void', k)], k, False)
for lid in ["beach", "snow", "city", "jungle"]:
    for k in ['green', 'orange', 'purple', 'yellow']:
        if lid == "snow" and k == "purple": continue
        RIG[lid + k.capitalize()] = export(ch[(lid, k)], k, True)
json.dump(RIG, open(D + '/rig.json', 'w'), separators=(',', ':'))
print("rig", len(RIG), sum(len(v['layers']) for v in RIG.values()), "layers", len(json.dumps(RIG, separators=(',', ':'))) // 1024, "KB")

# ===================== De frente: el instante en que voltean (un solo dibujo, sin piezas que se muevan) =====================
FRONT_DIR = __import__('os').path.join(__import__('os').path.dirname(__file__), 'front')
FB = json.load(open(FRONT_DIR + '/bbox.json'))
FBODY = {"green": 11, "orange": 5, "purple": 8, "yellow": 2}  # cuál elemento es el cuerpo
def load_front(k):
    raw = open(FRONT_DIR + '/' + k + '.svg').read()
    raw = re.sub(r'<\?xml.*?\?>', '', raw, flags=re.S); raw = re.sub(r'<metadata>.*?</metadata>', '', raw, flags=re.S); raw = re.sub(r'<!--.*?-->', '', raw, flags=re.S)
    x0, y0, x1, y1 = FB[k]['all']; m = 12
    vb = [x0 - m, y0 - m, (x1 - x0) + 2 * m, (y1 - y0) + 2 * m]
    raw = re.sub(r'<svg[^>]*>', f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{vb[0]} {vb[1]} {vb[2]} {vb[3]}">', raw.strip(), count=1)
    b = FB[k]['list'][FBODY[k]][2]
    return {"svg": raw, "vb": vb, "body": [b[0], b[1], b[2] - b[0], b[3] - b[1]], "pad": m}
FA_ = {k: load_front(k) for k in ['green', 'orange', 'purple', 'yellow']}
fch = {}
def FC(k, tag): c = Ch(k, tag, FA_[k]); return c
for k in ['green', 'orange', 'purple', 'yellow']: fch[('void', k)] = FC(k, 'fv' + k)

# --- Playa
c = FC('green', 'fbg'); S = c.S
for sd in (-1, 1):
    st = f'M{c.p(5 + sd*2.3, 5.9)} Q{c.p(5 + sd*3.8, 5.6)} {c.p(5 + sd*5.0, 5.4)}'
    c.shadow_stroke(st, S * 0.45); F(c, path(st, stroke="#1C6A82", w=S * 0.45))
mx, my = c.P(2.6, 4.8); mw, mh = c.bw * 0.48, c.bh * 0.28
mask = f'M{mx+mh*0.45:.1f},{my:.1f} H{mx+mw-mh*0.45:.1f} Q{mx+mw:.1f},{my:.1f} {mx+mw:.1f},{my+mh*0.45:.1f} V{my+mh*0.6:.1f} Q{mx+mw:.1f},{my+mh:.1f} {mx+mw-mh*0.45:.1f},{my+mh:.1f} H{mx+mw*0.6:.1f} Q{mx+mw*0.5:.1f},{my+mh*0.8:.1f} {mx+mw*0.4:.1f},{my+mh:.1f} H{mx+mh*0.45:.1f} Q{mx:.1f},{my+mh:.1f} {mx:.1f},{my+mh*0.6:.1f} V{my+mh*0.45:.1f} Q{mx:.1f},{my:.1f} {mx+mh*0.45:.1f},{my:.1f} Z'
c.shadow(mask); F(c, path(mask, fill=c.lin([(0, "#5CC8E2"), (0.55, "#2FA3C4"), (1, "#1D7C9E")])))
gx, gy, gw, gh = mx + S * 0.35, my + S * 0.32, mw - S * 0.7, mh - S * 0.9
F(c, f'<rect x="{gx:.1f}" y="{gy:.1f}" width="{gw:.1f}" height="{gh:.1f}" rx="{gh*0.4:.1f}" fill="#E2F7FF" opacity=".16" stroke="#E9FAFF" stroke-width="{S*0.13:.1f}"/>',
  f'<path d="M{gx+gw*0.15:.1f},{gy+gh:.1f} L{gx+gw*0.32:.1f},{gy:.1f}" stroke="#fff" stroke-width="{S*0.4:.1f}" opacity=".5"/>')
tube = f'M{c.p(2.9,7.4)} Q{c.p(1.4,7.8)} {c.p(1.3,5.6)} L{c.p(1.2,0.6)} Q{c.p(1.2,-0.8)} {c.p(2.3,-0.9)}'
F(c, path(tube, stroke="#E9673F", w=S * 0.66), path(tube, stroke="#FF8A65", w=S * 0.5), path(tube, stroke="#FFFFFF", w=S * 0.52, extra=f'stroke-dasharray="{S*0.55:.1f} {S*1.35:.1f}" opacity=".95"'))
fch[('beach', 'green')] = c

c = FC('orange', 'fbo'); S = c.S
c.strip(['M439.7,547.9', 'M306.9,523.7', 'M390.2,523.2'])
B(c, *[crableg(u, 8.3, dx, dx < 0) for (u, dx) in [(2.2, -1.9), (3.2, -1.3), (4.2, -0.6), (5.8, 0.6), (6.8, 1.3), (7.8, 1.9)]])
F(c, claw3(c, (0.9, 6.6), (-1.5, 3.4), -14, 1.15, -1), claw3(c, (9.1, 6.6), (11.5, 3.4), 14, 1.15, 1))
fch[('beach', 'orange')] = c

c = FC('purple', 'fbp'); S = c.S; c.padb = 0.12; c.padk = 0.42
c.strip(['M282.7,669.5', 'M669.2,745', 'M485.3,679.4'])
for pts, curl, dark in [([(1.4, 7.0), (0.2, 9.0), (-1.2, 10.3), (-2.4, 10.1)], 1, True), ([(8.6, 7.0), (9.8, 9.0), (11.2, 10.3), (12.4, 10.1)], -1, True),
                        ([(2.8, 7.6), (2.0, 9.8), (0.9, 11.2)], 1, False), ([(7.2, 7.6), (8.0, 9.8), (9.1, 11.2)], -1, False),
                        ([(4.3, 7.8), (4.1, 10.2), (3.3, 11.8)], -1, False), ([(5.7, 7.8), (5.9, 10.2), (6.7, 11.8)], 1, False)]:
    B(c, tentacle(c, pts, curl, S * 1.05, dark))
fch[('beach', 'purple')] = c

c = FC('yellow', 'fby'); S = c.S
cx, cy = c.P(5.0, 8.3); R1x, R1y = c.bw * 0.6, c.bh * 0.22; R0x, R0y = c.bw * 0.42, c.bh * 0.11
tube = c.lin([(0, "#FFFFFF"), (1, "#E7E1D8")], 0, 0, 0, 1); coral = c.lin([(0, "#FFA27F"), (1, "#E9633F")], 0, 0, 0, 1)
for i in range(8):
    a0 = i * 2 * math.pi / 8 + 0.2; a1 = a0 + 2 * math.pi / 8; mid = (a0 + a1) / 2
    (F if math.sin(mid) > 0 else B)(c, f'<path d="{seg(a0, a1)}" fill="{coral if i % 2 else tube}"/>')
c.shadow(seg(math.pi * 0.05, math.pi * 0.95), 0, -0.55, 0.35)
F(c, f'<path d="M{cx-R1x*0.72:.1f},{cy+R1y*0.45:.1f} A{(R1x+R0x)/2:.1f},{(R1y+R0y)/2:.1f} 0 0 0 {cx+R1x*0.2:.1f},{cy+(R1y+R0y)/2*0.98:.1f}" stroke="#fff" stroke-width="{S*0.28:.1f}" fill="none" opacity=".7" stroke-linecap="round"/>')
for u in (3.6, 6.6):
    x, y = c.P(u, 3.4); lens = c.lin([(0, "#4B3C7A"), (0.6, "#2A2148"), (1, "#3E8FA8")], 0, 0, 0.3, 1)
    F(c, f'<path d="M{x-S*1.25:.1f},{y-S*0.65:.1f} H{x+S*1.25:.1f} Q{x+S*1.35:.1f},{y+S*0.9:.1f} {x:.1f},{y+S*0.85:.1f} Q{x-S*1.35:.1f},{y+S*0.9:.1f} {x-S*1.25:.1f},{y-S*0.65:.1f} Z" fill="{lens}" stroke="#1C1631" stroke-width="{S*0.14:.1f}"/>',
      f'<path d="M{x-S*0.8:.1f},{y+S*0.35:.1f} L{x-S*0.15:.1f},{y-S*0.4:.1f}" stroke="#fff" stroke-width="{S*0.18:.1f}" stroke-linecap="round" opacity=".55"/>')
F(c, path(f'M{c.p(4.85,3.05)} Q{c.p(5.1,2.75)} {c.p(5.35,3.05)}', stroke="#1C1631", w=S * 0.22))
fch[('beach', 'yellow')] = c

# --- Nieve
c = FC('green', 'fsg'); S = c.S
dome = f'M{c.p(-0.2,3.9)} C{c.p(-0.5,-1.3)} {c.p(2.6,-2.4)} {c.p(5,-2.4)} C{c.p(7.4,-2.4)} {c.p(10.5,-1.3)} {c.p(10.2,3.9)} Z'
c.shadow(dome, 0, 0.5, 0.4); F(c, path(dome, fill=c.rad([(0, "#FFB9A3"), (0.6, "#F57A5A"), (1, "#D35A3E")], .45, .25, .85)))
c.defs.append(f'<clipPath id="fsg-dome"><path d="{dome}"/></clipPath>')
st = [f'<path d="M{c.p(-1,0.8)} Q{c.p(5,-0.4)} {c.p(11,0.8)} L{c.p(11,1.55)} Q{c.p(5,0.35)} {c.p(-1,1.55)} Z" fill="#FFF3EA"/>']
for row in range(8):
    for i in range(22):
        u = -0.4 + i * 0.52 + (row % 2) * 0.26; v = -1.6 + row * 0.6; x, y = c.P(u, v + 0.75 * ((u - 5) / 5) ** 2 * 0.9)
        st.append(f'<path d="M{x-S*0.16:.1f},{y-S*0.12:.1f} L{x:.1f},{y+S*0.12:.1f} L{x+S*0.16:.1f},{y-S*0.12:.1f}" stroke="#B9452C" stroke-width="{S*0.07:.1f}" fill="none" opacity=".35"/>')
F(c, f'<g clip-path="url(#fsg-dome)">{"".join(st)}</g>')
cuff = f'M{c.p(-0.45,2.9)} Q{c.p(5,2.0)} {c.p(10.45,2.9)} L{c.p(10.4,4.4)} Q{c.p(5,3.5)} {c.p(-0.4,4.4)} Z'
c.shadow(cuff, 0, 0.45, 0.45); F(c, path(cuff, fill=c.lin([(0, "#FFFBF6"), (1, "#E7DCCD")])))
for i in range(21):
    u = -0.1 + i * 0.5; t = (u - 5) / 5.5; F(c, path(f'M{c.p(u,3.0 - (1 - t*t) * 0.9 + 0.12)} L{c.p(u,4.35 - (1 - t*t) * 0.9)}', stroke="#D6C8B4", w=S * 0.1))
F(c, fluff(c, 5.0, -2.5, 1.2, "#FFF6EE", "#E2D3C2", 10))
sc = f'M{c.p(0.4,7.7)} Q{c.p(5,9.5)} {c.p(9.6,7.7)} L{c.p(9.45,9.1)} Q{c.p(5,10.9)} {c.p(0.55,9.1)} Z'
c.shadow(sc, 0, -0.45, 0.35); F(c, path(sc, fill=c.lin([(0, "#5CC8E2"), (1, "#238FB2")])))
tail = f'M{c.p(5.8,9.6)} Q{c.p(6.0,10.6)} {c.p(5.9,11.6)} L{c.p(7.3,11.5)} Q{c.p(7.2,10.5)} {c.p(7.1,9.5)} Z'
F(c, path(tail, fill=c.lin([(0, "#2FA3C4"), (1, "#1C7898")])), path(f'M{c.p(5.95,10.6)} L{c.p(7.2,10.55)}', stroke="#F57A5A", w=S * 0.22))
fch[('snow', 'green')] = c

c = FC('orange', 'fso'); S = c.S
hel = f'M{c.p(0.4,3.4)} C{c.p(0.2,-1.6)} {c.p(9.8,-1.6)} {c.p(9.6,3.4)} Q{c.p(5,2.2)} {c.p(0.4,3.4)} Z'
c.shadow(hel, 0, 0.45, 0.45); F(c, path(hel, fill=c.rad([(0, "#6E7BA8"), (0.55, "#3A4468"), (1, "#232A44")], .4, .25, .85)))
F(c, path(f'M{c.p(0.6,2.5)} Q{c.p(5,1.2)} {c.p(9.4,2.5)}', stroke="#F1C84D", w=S * 0.42))
gx, gy = c.P(1.8, 1.1); gw, gh = c.bw * 0.64, c.bh * 0.27
F(c, f'<rect x="{gx:.1f}" y="{gy:.1f}" width="{gw:.1f}" height="{gh:.1f}" rx="{gh*0.48:.1f}" fill="#1E2336"/>',
  f'<rect x="{gx+S*0.28:.1f}" y="{gy+S*0.26:.1f}" width="{gw-S*0.56:.1f}" height="{gh-S*0.52:.1f}" rx="{gh*0.36:.1f}" fill="{c.lin([(0,"#FFD27A"),(0.35,"#FF8A65"),(0.7,"#A584E8"),(1,"#5BC6E0")],0,0,1,1)}"/>',
  f'<path d="M{gx+S*1.0:.1f},{gy+gh-S*0.45:.1f} L{gx+S*1.8:.1f},{gy+S*0.45:.1f}" stroke="#fff" stroke-width="{S*0.3:.1f}" stroke-linecap="round" opacity=".7"/>')
fch[('snow', 'orange')] = c

c = FC('yellow', 'fsy'); S = c.S
band = f'M{c.p(0.3,4.6)} C{c.p(0.0,-2.2)} {c.p(10.0,-2.2)} {c.p(9.7,4.6)}'
c.shadow_stroke(band, S * 0.55, 0, 0.45)
F(c, path(band, stroke="#C24E7D", w=S * 0.62), path(band, stroke=c.lin([(0, "#FFB6D2"), (1, "#E0679B")], 0, 0, 1, 0), w=S * 0.46))
F(c, fluff(c, 0.2, 4.9, 1.4, "#FFE6F0", "#F2A9C7", 11), fluff(c, 9.8, 4.9, 1.4, "#FFE6F0", "#F2A9C7", 11))
fch[('snow', 'yellow')] = c

# --- Ciudad
c = FC('green', 'fcg'); S = c.S
for sd in (-1, 1):
    stp = f'M{c.p(5 + sd*3.4, 1.4)} Q{c.p(5 + sd*3.9, 4.5)} {c.p(5 + sd*3.6, 8.2)}'
    c.shadow_stroke(stp, S * 0.5); F(c, path(stp, stroke="#C9512C", w=S * 0.55), path(stp, stroke="#F07A50", w=S * 0.36))
crown = f'M{c.p(1.5,2.6)} C{c.p(1.3,-1.4)} {c.p(8.7,-1.4)} {c.p(8.5,2.6)} Q{c.p(5,1.9)} {c.p(1.5,2.6)} Z'
c.shadow(crown, 0, 0.45, 0.45); F(c, path(crown, fill=c.rad([(0, "#7FD5EC"), (0.6, "#2FA3C4"), (1, "#1A6E90")], .4, .25, .85)))
for u in (3.3, 5.0, 6.7): F(c, path(f'M{c.p(u,2.3)} Q{c.p(u+(5-u)*0.4,0.5)} {c.p(5,-0.6)}', stroke="#17607F", w=S * 0.07, extra='opacity=".55"'))
brim = f'M{c.p(1.8,2.3)} Q{c.p(5,1.7)} {c.p(8.2,2.3)} Q{c.p(8.6,3.3)} {c.p(5,3.5)} Q{c.p(1.4,3.3)} {c.p(1.8,2.3)} Z'
c.shadow(brim, 0, 0.5, 0.45); F(c, path(brim, fill=c.lin([(0, "#2386A8"), (1, "#145A78")])))
F(c, circ(c, 5.0, -0.65, 0.3, "#1A6E90"))
sx_, sy_ = c.P(5.0, 0.9); F(c, f'<polygon points="' + ' '.join(f'{sx_+math.cos(-math.pi/2+i*math.pi/5)*S*(0.5 if i%2==0 else 0.22):.1f},{sy_+math.sin(-math.pi/2+i*math.pi/5)*S*(0.5 if i%2==0 else 0.22):.1f}' for i in range(10)) + '" fill="#F1C84D"/>')
fch[('city', 'green')] = c

c = FC('orange', 'fco'); S = c.S
stp = f'M{c.p(1.6,2.2)} L{c.p(8.6,8.0)}'
c.shadow_stroke(stp, S * 0.5); F(c, path(stp, stroke="#1E2336", w=S * 0.5))
x, y = c.P(8.2, 7.4)
F(c, f'<rect x="{x:.1f}" y="{y:.1f}" width="{S*2.8:.1f}" height="{S*2.3:.1f}" rx="{S*0.5:.1f}" fill="{c.lin([(0,"#79D6A9"),(1,"#2F9E73")])}"/><rect x="{x:.1f}" y="{y:.1f}" width="{S*2.8:.1f}" height="{S*0.95:.1f}" rx="{S*0.45:.1f}" fill="#268A63"/><rect x="{x+S*1.1:.1f}" y="{y+S*0.7:.1f}" width="{S*0.6:.1f}" height="{S*0.5:.1f}" rx="{S*0.12:.1f}" fill="#F1C84D"/>')
hel = f'M{c.p(0.6,3.0)} C{c.p(0.3,-1.9)} {c.p(9.7,-1.9)} {c.p(9.4,3.0)} Q{c.p(5,2.0)} {c.p(0.6,3.0)} Z'
c.shadow(hel, 0, 0.45, 0.45); F(c, path(hel, fill=c.rad([(0, "#FFFFFF"), (0.55, "#E6F4F8"), (1, "#A8D4E3")], .4, .25, .85)))
F(c, path(f'M{c.p(0.7,2.85)} Q{c.p(5,1.9)} {c.p(9.3,2.85)}', stroke="#2FA3C4", w=S * 0.32))
for (u, v) in [(3.0, 0.2), (5.0, -0.4), (7.0, 0.2)]:
    x, y = c.P(u, v); F(c, f'<rect x="{x-S*0.18:.1f}" y="{y-S*0.6:.1f}" width="{S*0.36:.1f}" height="{S*1.2:.1f}" rx="{S*0.18:.1f}" transform="rotate({(u-5)*12:.0f} {x:.1f} {y:.1f})" fill="#2E3448" opacity=".8"/>')
fch[('city', 'orange')] = c

c = FC('purple', 'fcp'); S = c.S
ex, ey = c.P(5.0, 4.95)
c.defs.append(f'<clipPath id="fcp-clip"><ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{c.bw*0.5:.1f}" ry="{c.bh*0.49:.1f}"/></clipPath>')
vest = c.lin([(0, "#FFB070"), (1, "#EE6F22")])
F(c, f'<g clip-path="url(#fcp-clip)">', path(f'M{c.p(-1,7.4)} Q{c.p(5,8.6)} {c.p(11,7.4)} L{c.p(11,12)} L{c.p(-1,12)} Z', fill=vest),
  path(f'M{c.p(-1,8.6)} Q{c.p(5,9.8)} {c.p(11,8.6)}', stroke="#E8ECF2", w=S * 0.5), path(f'M{c.p(-1,9.5)} Q{c.p(5,10.7)} {c.p(11,9.5)}', stroke="#E8ECF2", w=S * 0.5), '</g>')
hh = f'M{c.p(1.4,2.3)} C{c.p(1.4,-1.8)} {c.p(8.6,-1.8)} {c.p(8.6,2.3)} Z'
c.shadow(hh, 0, 0.5, 0.45)
F(c, path(hh, fill=c.rad([(0, "#FFF0A8"), (0.55, "#F6C945"), (1, "#D49A16")], .4, .28, .85)), path(f'M{c.p(4.3,-0.9)} Q{c.p(5,-1.2)} {c.p(5.7,-0.9)} L{c.p(5.7,2.1)} L{c.p(4.3,2.1)} Z', fill="#E7B12C"))
brim = f'M{c.p(0.0,2.2)} Q{c.p(5,1.4)} {c.p(10,2.2)} Q{c.p(10.3,3.0)} {c.p(9.6,3.1)} Q{c.p(5,2.3)} {c.p(0.4,3.1)} Q{c.p(-0.3,3.0)} {c.p(0.0,2.2)} Z'
c.shadow(brim, 0, 0.5, 0.45); F(c, path(brim, fill=c.lin([(0, "#F6C945"), (1, "#C98C12")])))
F(c, circ(c, 5.0, 0.6, 0.45, "#FFFFFF"), circ(c, 5.0, 0.6, 0.28, "#FF8A65"))
fch[('city', 'purple')] = c

c = FC('yellow', 'fcy'); S = c.S
x, y = c.P(2.2, -2.0); w, h = S * 5.6, S * 2.3
F(c, f'<path d="M{x+S*0.25:.1f},{y+h+S*0.5:.1f} H{x+w-S*0.25:.1f} L{x+w-S*0.6:.1f},{y+h+S*0.95:.1f} H{x+S*0.6:.1f} Z" fill="#1E2336"/>',
  f'<path d="M{x+S*0.45:.1f},{y:.1f} H{x+w-S*0.45:.1f} Q{x+w:.1f},{y:.1f} {x+w:.1f},{y+S*0.5:.1f} L{x+w:.1f},{y+h:.1f} H{x:.1f} L{x:.1f},{y+S*0.5:.1f} Q{x:.1f},{y:.1f} {x+S*0.45:.1f},{y:.1f} Z" fill="{c.lin([(0,"#FFFBE6"),(1,"#FFE79A")])}" stroke="#2E3448" stroke-width="{S*0.16:.1f}"/>',
  f'<text x="{x+w/2:.1f}" y="{y+h*0.74:.1f}" text-anchor="middle" font-family="Outfit,Arial Black,sans-serif" font-weight="900" font-size="{S*1.45:.1f}" fill="#2E3448">TAXI</text>')
cw = (w - S * 0.5) / 8
for i in range(8):
    for r in range(2): F(c, f'<rect x="{x+S*0.25+i*cw:.1f}" y="{y+h+r*S*0.25:.1f}" width="{cw:.1f}" height="{S*0.25:.1f}" fill="{"#2E3448" if (i+r)%2 else "#FFFFFF"}"/>')
fch[('city', 'yellow')] = c

# --- Selva
c = FC('green', 'fjg'); S = c.S
stem = f'M{c.p(9.6,6.8)} Q{c.p(10.6,2.6)} {c.p(5.4,-1.2)}'
B(c, path(stem, stroke="#3E7A44", w=S * 0.42))
x, y = c.P(5.0, -2.3)
lf = f'M{x - S*6.2:.1f},{y + S*1.9:.1f} C{x - S*5.6:.1f},{y - S*2.9:.1f} {x + S*5.6:.1f},{y - S*2.9:.1f} {x + S*6.2:.1f},{y + S*1.9:.1f} C{x + S*3.0:.1f},{y + S*0.7:.1f} {x - S*3.0:.1f},{y + S*0.7:.1f} {x - S*6.2:.1f},{y + S*1.9:.1f} Z'
F(c, path(lf, fill=c.lin([(0, "#8FD08A"), (0.5, "#4E9E58"), (1, "#2C6E41")], 0, 0, 0.4, 1)),
  path(f'M{x - S*5.6:.1f},{y + S*1.5:.1f} Q{x:.1f},{y - S*1.9:.1f} {x + S*5.6:.1f},{y + S*1.5:.1f}', stroke="#C9EDC0", w=S * 0.16),
  ''.join(path(f'M{x + S*t*0.35:.1f},{y - S*0.95:.1f} Q{x + S*t*0.8:.1f},{y - S*0.4:.1f} {x + S*t:.1f},{y + S*1.05:.1f}', stroke="#A9DCA0", w=S * 0.08) for t in (-5, -3.2, -1.4, 1.4, 3.2, 5)))
fch[('jungle', 'green')] = c

c = FC('orange', 'fjo'); S = c.S
brim = f'M{c.p(-1.4,2.4)} Q{c.p(5,0.8)} {c.p(11.4,2.4)} Q{c.p(11.3,3.6)} {c.p(5,3.9)} Q{c.p(-1.3,3.6)} {c.p(-1.4,2.4)} Z'
c.shadow(brim, 0, 0.55, 0.45); F(c, path(brim, fill=c.lin([(0, "#F3E4C2"), (1, "#C6A970")])))
dome = f'M{c.p(1.2,2.6)} C{c.p(1.0,-2.4)} {c.p(9.0,-2.4)} {c.p(8.8,2.6)} Q{c.p(5,1.9)} {c.p(1.2,2.6)} Z'
F(c, path(dome, fill=c.rad([(0, "#FFF8E6"), (0.6, "#E9D7AE"), (1, "#BFA06A")], .4, .25, .85)),
  path(f'M{c.p(1.22,1.8)} Q{c.p(5,0.7)} {c.p(8.78,1.8)} L{c.p(8.8,2.6)} Q{c.p(5,1.55)} {c.p(1.2,2.6)} Z', fill=c.lin([(0, "#8A684C"), (1, "#5E4433")])),
  circ(c, 5.0, -1.4, 0.32, "#C9AE78"))
fch[('jungle', 'orange')] = c

c = FC('purple', 'fjp'); S = c.S
CROWN = []
for i, (u, ang, L) in enumerate([(1.6, -50, 2.6), (2.7, -30, 3.3), (4.1, -12, 3.7), (5.9, 12, 3.7), (7.3, 30, 3.3), (8.4, 50, 2.6)]):
    x, y = c.P(u, 0.85 + abs(u - 5) * 0.13); a, b = cols[i % 3]
    CROWN.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang})"><path d="M0,0 C{-S*L*0.34:.1f},{-S*L*0.45:.1f} {-S*L*0.16:.1f},{-S*L*0.88:.1f} 0,{-S*L:.1f} C{S*L*0.16:.1f},{-S*L*0.88:.1f} {S*L*0.34:.1f},{-S*L*0.45:.1f} 0,0 Z" fill="{c.lin([(0,a),(1,b)],0,1,0,0)}"/><path d="M0,0 L0,{-S*L*0.92:.1f}" stroke="#E6F7DF" stroke-width="{S*0.09:.1f}" opacity=".85"/></g>')
for (u, c1, c2) in [(2.6, "#FFB59B", "#E9573A"), (5.0, "#FFE38A", "#E9A923"), (7.4, "#FFC2DA", "#E0679B")]:
    x, y = c.P(u, 1.1 + abs(u - 5) * 0.13); pg = c.rad([(0, "#FFFFFF"), (0.35, c1), (1, c2)], .5, .5, .6)
    for a in range(5): CROWN.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({-90 + a*72})"><path d="M0,0 C{S*0.2:.1f},{-S*0.45:.1f} {S*0.95:.1f},{-S*0.55:.1f} {S*0.95:.1f},0 C{S*0.95:.1f},{S*0.55:.1f} {S*0.2:.1f},{S*0.45:.1f} 0,0 Z" fill="{pg}"/></g>')
    CROWN.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{S*0.2:.1f}" fill="#FFF3C4"/>')
F(c, *CROWN)
fch[('jungle', 'purple')] = c

c = FC('yellow', 'fjy'); S = c.S; c.padk = 0.62
B(c, wing(c, 1.6, 3.2, -8, 1.0, "#FFB3D3", "#E0679B", "#A33A6A"), wing(c, 8.4, 3.2, 8, 1.0, "#9BEDE4", "#2FA39A", "#1D6F69", -1))
fch[('jungle', 'yellow')] = c

def export_front(c, base, fa):
    out = export(c, 'f_' + base, True)
    out['base'] = base
    out['body'] = fa['body']; out['gy'] = fa['vb'][1] + fa['vb'][3] - fa['pad']
    return out
for k in ['green', 'orange', 'purple', 'yellow']: RIG[k + '_f'] = export_front(fch[('void', k)], k, FA_[k])
for lid in ["beach", "snow", "city", "jungle"]:
    for k in ['green', 'orange', 'purple', 'yellow']:
        if (lid, k) in fch: RIG[lid + k.capitalize() + '_f'] = export_front(fch[(lid, k)], k, FA_[k])
def load_any(path, bounds, keep=None):
    raw = open(path).read()
    raw = re.sub(r'<\?xml.*?\?>', '', raw, flags=re.S); raw = re.sub(r'<metadata>.*?</metadata>', '', raw, flags=re.S); raw = re.sub(r'<!--.*?-->', '', raw, flags=re.S)
    if keep is not None:
        defs = re.search(r'<defs>.*?</defs>', raw, re.S).group(0); body = raw.replace(defs, '')
        i = [-1]
        def f(m):
            i[0] += 1
            return m.group(0) if i[0] in keep else ''
        body = re.sub(r'<(path|circle|ellipse|polygon|rect|line|polyline)\b[^>]*?(?:/>|>\s*</\1>)', f, body)
        raw = body.replace('<svg', '<svg', 1).replace('>', '>' + defs, 1) if False else re.sub(r'(<svg[^>]*>)', lambda m: m.group(1) + defs, body, count=1)
    x0, y0, x1, y1 = bounds; m = 12
    vb = [x0 - m, y0 - m, (x1 - x0) + 2 * m, (y1 - y0) + 2 * m]
    raw = re.sub(r'<svg[^>]*>', f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{vb[0]} {vb[1]} {vb[2]} {vb[3]}">', raw.strip(), count=1)
    return {"svg": raw, "vb": vb, "body": [230, 330, 615, 530], "pad": m}
YB = json.load(open(FRONT_DIR + '/yeti_bb.json')) if __import__('os').path.exists(FRONT_DIR + '/yeti_bb.json') else None
keepF = [e[0] for e in YB if e[4][2] > 0 and e[4][0] < 1058 and e[4][3] > 0 and e[4][1] < 1058]
ys = Ch('yeti', 'ys', load_any(FRONT_DIR + '/yeti_side.svg', (201, 150, 857, 908)))
yf = Ch('yeti', 'yf', load_any(FRONT_DIR + '/yeti.svg', (215, 108, 841, 913), keepF))
for key, c, parts, gy in (('purpleYeti', ys, 'yeti', 908), ('purpleYeti_f', yf, 'f_yeti', 913)):
    out = export(c, parts, False); out['base'] = 'purpleYeti'; out['body'] = [230, 330, 615, 530]; out['gy'] = gy
    RIG[key] = out
json.dump(RIG, open(D + '/rig.json', 'w'), separators=(',', ':'))
print("rig+front", len(RIG), len(json.dumps(RIG, separators=(',', ':'))) // 1024, "KB")
# Hoja de revisión de los de frente
hh = ['<!doctype html><body style="margin:0;background:#F4F1FD;display:flex;flex-wrap:wrap;width:1500px">']
for key, c in fch.items(): hh.append(f'<div style="width:180px;text-align:center;font:11px sans-serif">{c.svg(170)}<br>{key[0]} {key[1]}</div>')
open(D + '/front_board.html', 'w').write(''.join(hh))
