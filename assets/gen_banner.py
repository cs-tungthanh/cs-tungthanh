"""Generate light/dark profile banner SVGs from one template."""
import sys

THEMES = {
    "dark": dict(bg="#0d1117", border="#30363d", dot="#21262d", fg="#e6edf3",
                 muted="#8b949e", accent="#2dd4bf", accent2="#58a6ff",
                 node="#161b22", nodeStroke="#30363d"),
    "light": dict(bg="#ffffff", border="#d0d7de", dot="#eaeef2", fg="#1f2328",
                  muted="#59636e", accent="#0f766e", accent2="#0969da",
                  node="#f6f8fa", nodeStroke="#d0d7de"),
}

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"

# Architecture diagram nodes: (id, label, x, y)
W, H = 120, 44
NODES = [
    ("client", "client", 596, 138),
    ("gw", "api-gateway", 752, 138),
    ("go", "go-service", 912, 70),
    ("node", "node-service", 912, 206),
]
# Data stores, in one column right of the services: (id, label, y of the pill's middle)
SW, SH = 76, 26
STORE_X = 1104
STORES = [
    ("postgres", "postgres", 92),
    ("dynamodb", "dynamodb", 160),
    ("redis", "redis", 228),
]
# Which service talks to which store, as on the website's diagram
STORE_EDGES = [
    ("go", "postgres"),
    ("go", "dynamodb"),
    ("node", "dynamodb"),
    ("node", "postgres"),
    ("node", "redis"),
]


def node(label, x, y, c):
    return (
        f'<rect x="{x}" y="{y}" width="{W}" height="{H}" rx="8" fill="{c["node"]}" stroke="{c["nodeStroke"]}"/>'
        f'<text x="{x + W / 2}" y="{y + 27}" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{c["fg"]}">{label}</text>'
    )


def mid_r(n):
    _, _, x, y = n
    return x + W, y + H / 2


def mid_l(n):
    _, _, x, y = n
    return x, y + H / 2


def svg(c):
    client, gw, go, nd = NODES
    ax, ay = mid_r(client)
    bx, by = mid_l(gw)
    gx, gy = mid_r(gw)
    p_ab = f"M{ax},{ay} L{bx},{by}"
    p_go = f"M{gx},{gy} C{gx + 40},{gy} {go[2] - 40},{go[3] + H / 2} {go[2]},{go[3] + H / 2}"
    p_nd = f"M{gx},{gy} C{gx + 40},{gy} {nd[2] - 40},{nd[3] + H / 2} {nd[2]},{nd[3] + H / 2}"
    edge = f'fill="none" stroke="{c["muted"]}" stroke-opacity="0.55" stroke-width="1.5"'

    def packet(path, color, begin):
        return (
            f'<circle r="4" fill="{color}" opacity="0">'
            f'<animateMotion dur="2.6s" begin="{begin}" repeatCount="indefinite" path="{path}"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.85;1" dur="2.6s" begin="{begin}" repeatCount="indefinite"/>'
            f'</circle>'
        )

    full_go = p_ab + " " + p_go.replace("M", "L", 1)
    full_nd = p_ab + " " + p_nd.replace("M", "L", 1)

    services = {"go": go, "node": nd}
    store_y = {sid: y for sid, _, y in STORES}

    def store_path(service, store):
        x1, y1 = mid_r(services[service])
        x2, y2 = STORE_X, store_y[store]
        if y1 == y2:
            return f"M{x1},{y1} L{x2},{y2}"
        mx = (x1 + x2) / 2
        return f"M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}"

    store_edges = "".join(
        f'<path d="{store_path(svc, st)}" {edge} stroke-dasharray="3 4"/>' for svc, st in STORE_EDGES
    )
    stores = "".join(
        f'<rect x="{STORE_X}" y="{y - SH / 2}" width="{SW}" height="{SH}" rx="13" fill="{c["bg"]}" stroke="{c["nodeStroke"]}"/>'
        f'<text x="{STORE_X + SW / 2}" y="{y + 4}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{c["muted"]}">{lbl}</text>'
        for _, lbl, y in STORES
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="320" viewBox="0 0 1200 320" role="img" aria-label="Tung Thanh — Software Engineer and Solution Architect">
  <defs>
    <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.2" fill="{c["dot"]}"/>
    </pattern>
    <linearGradient id="fade" x1="0" x2="1">
      <stop offset="0" stop-color="{c["bg"]}" stop-opacity="1"/>
      <stop offset="0.45" stop-color="{c["bg"]}" stop-opacity="0.85"/>
      <stop offset="1" stop-color="{c["bg"]}" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <rect x="0.5" y="0.5" width="1199" height="319" rx="16" fill="{c["bg"]}" stroke="{c["border"]}"/>
  <rect x="1" y="1" width="1198" height="318" rx="16" fill="url(#grid)"/>
  <rect x="1" y="1" width="700" height="318" rx="16" fill="url(#fade)"/>

  <!-- window chrome -->
  <circle cx="32" cy="30" r="6" fill="#ff5f57"/>
  <circle cx="52" cy="30" r="6" fill="#febc2e"/>
  <circle cx="72" cy="30" r="6" fill="#28c840"/>

  <!-- intro -->
  <text x="64" y="104" font-family="{MONO}" font-size="18" fill="{c["muted"]}"><tspan fill="{c["accent"]}">$</tspan> whoami<tspan fill="{c["accent"]}">
    <animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/>▍</tspan></text>
  <text x="62" y="170" font-family="{SANS}" font-size="58" font-weight="700" fill="{c["fg"]}" letter-spacing="-1">Tung Thanh</text>
  <text x="64" y="212" font-family="{SANS}" font-size="22" fill="{c["muted"]}">Software Engineer · Solution Architect</text>
  <text x="64" y="262" font-family="{MONO}" font-size="18" fill="{c["accent"]}">solve() <tspan fill="{c["muted"]}">→</tspan> build() <tspan fill="{c["muted"]}">→</tspan> ship()</text>

  <!-- architecture sketch -->
  <path d="{p_ab}" {edge}/>
  <path d="{p_go}" {edge}/>
  <path d="{p_nd}" {edge}/>
  {store_edges}
  {packet(full_go, c["accent"], "0s")}
  {packet(full_nd, c["accent2"], "1.3s")}
  {"".join(node(l, x, y, c) for _, l, x, y in NODES)}
  {stores}
</svg>
'''


out = sys.argv[1]
for name, colors in THEMES.items():
    with open(f"{out}/banner-{name}.svg", "w") as f:
        f.write(svg(colors))
