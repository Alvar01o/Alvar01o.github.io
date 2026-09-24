#!/usr/bin/env python3
"""Genera los PDF del CV (ES/EN) a partir del contenido de la web.

Uso (desde la raíz del repo):
    node scripts/cv/export-content.mjs > /tmp/content.json
    python3 scripts/cv/build_cv.py /tmp/content.json

Requisitos: pip install weasyprint fonttools brotli   (y `npm install` para las fuentes).
Salida: public/cv/Alvaro-Mercado-CV-es.pdf y public/cv/Alvaro-Mercado-Resume-en.pdf
"""
import html
import json
import pathlib
import sys
import tempfile

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from weasyprint import CSS as WCSS, HTML
from weasyprint.text.fonts import FontConfiguration

ROOT = pathlib.Path(__file__).resolve().parents[2]
NM = ROOT / "node_modules"
OUT = ROOT / "public" / "cv"

SITE_URL = "online-resume-inky.vercel.app"  # cámbialo si usas un dominio propio
LINKEDIN = "linkedin.com/in/alvaro-mercado-6b387a10b"
GITHUB = "github.com/Alvar01o"

# Textos propios del CV (más detallados que los de la web)
CV = {
    "es": {
        "file": "Alvaro-Mercado-CV-es.pdf",
        "title": "Alvaro Mercado — CV 2026",
        "subtitle": "Ingeniero de Software Senior · Arquitectura · Cloud & Infraestructura",
        "sections": {"summary": "Resumen", "experience": "Experiencia", "skills": "Habilidades", "education": "Educación", "languages": "Idiomas"},
        "summary": (
            "Ingeniero de software senior con <b>14 años</b> diseñando, construyendo y optimizando sistemas de producción — "
            "buena parte de ellos como <b>contratista independiente para clientes internacionales vía Upwork</b> "
            "(calificación <b>5.0★</b>, +10.000 horas facturadas en 10 proyectos), y actualmente en <b>ITTI</b>, una de las "
            "principales fintech de Paraguay. Especializado en <b>diseño de sistemas</b> y <b>optimización de recursos</b>, "
            "con foco creciente en Cloud/DevOps sobre GCP, AWS y Kubernetes. Experiencia con facturación electrónica (SIFEN) "
            "y pasarelas de pago, y con automatización de flujos de trabajo y <b>orquestación de agentes de IA</b> (MCP). "
            "Español nativo, inglés avanzado."
        ),
        "itti": (
            "Desarrollo y mantenimiento de <b>BIMS</b>, sistema que da servicio a <b>+1.000 clientes en todo el país</b>, "
            "incluyendo la integración con <b>SIFEN</b> (sistema nacional de facturación electrónica), dentro de una de las "
            "principales fintech/regtech de Paraguay (certificada ISO 27001/9001). Trabajo con sistemas legacy: bugfixing y "
            "optimización de código e infraestructura (Redis para caché, colas SQS), deployments en <b>AWS y GCP</b>, y "
            "rediseño de procesos de delivery para acelerar la entrega a clientes. <b>Automatización de flujos de gestión y "
            "orquestación de agentes de IA con integraciones MCP.</b> Refuerzo de seguridad y monitoreo de rendimiento, en "
            "equipos multifuncionales de +20 ingenieros."
        ),
    },
    "en": {
        "file": "Alvaro-Mercado-Resume-en.pdf",
        "title": "Alvaro Mercado — Resume 2026",
        "subtitle": "Senior Software Engineer · Architecture · Cloud & Infrastructure",
        "sections": {"summary": "Summary", "experience": "Experience", "skills": "Skills", "education": "Education", "languages": "Languages"},
        "summary": (
            "Senior software engineer with <b>14 years</b> designing, building and optimizing production systems — much of it "
            "as an <b>independent contractor for international clients via Upwork</b> (<b>5.0★</b> rating, 10,000+ billed hours "
            "across 10 projects), and currently at <b>ITTI</b>, one of Paraguay's leading fintech companies. Specialized in "
            "<b>system design</b> and <b>resource optimization</b>, with a growing focus on Cloud/DevOps across GCP, AWS and "
            "Kubernetes. Experienced with electronic invoicing (SIFEN) and payment gateways, and with workflow automation and "
            "<b>AI agent orchestration</b> (MCP). Native Spanish, advanced English."
        ),
        "itti": (
            "Development and maintenance of <b>BIMS</b>, a system serving <b>1,000+ clients nationwide</b>, including integration "
            "with <b>SIFEN</b> (Paraguay's national e-invoicing system), within one of the country's leading fintech/regtech "
            "companies (ISO 27001/9001 certified). Working on legacy systems: bugfixing and code/infrastructure optimization "
            "(Redis caching, SQS queues), deployments on <b>AWS and GCP</b>, and redesign of delivery processes to speed up "
            "client delivery. <b>Automation of management workflows and orchestration of AI agents with MCP integrations.</b> "
            "Security hardening and performance monitoring, in cross-functional teams of 20+ engineers."
        ),
    },
}

CSS = """
@font-face { font-family: 'Inter'; font-weight: 400; src: url('file://{fonts}/Inter-400.ttf'); }
@font-face { font-family: 'Inter'; font-weight: 500; src: url('file://{fonts}/Inter-500.ttf'); }
@font-face { font-family: 'Inter'; font-weight: 600; src: url('file://{fonts}/Inter-600.ttf'); }
@font-face { font-family: 'Inter'; font-weight: 700; src: url('file://{fonts}/Inter-700.ttf'); }
@font-face { font-family: 'JB'; font-weight: 400; src: url('file://{fonts}/JB-400.ttf'); }
@font-face { font-family: 'JB'; font-weight: 500; src: url('file://{fonts}/JB-500.ttf'); }
@page { size: A4; margin: 13mm 15mm 12mm; }
* { box-sizing: border-box; }
body { font-family: 'Inter', 'DejaVu Sans', sans-serif; font-size: 9.4pt; line-height: 1.5; color: #1b1c1f; margin: 0; }
b { font-weight: 700; color: #0e0f11; }
.mono { font-family: 'JB', 'DejaVu Sans Mono', monospace; }
header.top { display: flex; justify-content: space-between; align-items: flex-start; padding-bottom: 11pt; border-bottom: 0.9pt solid #111; }
h1 { font-size: 27pt; line-height: 1.05; letter-spacing: -0.03em; font-weight: 700; margin: 0 0 7pt; color: #0e0f11; }
.sub { font-family: 'JB'; font-size: 6.9pt; letter-spacing: 0.14em; text-transform: uppercase; color: #4a4d55; max-width: 250pt; line-height: 1.6; }
.contact { font-family: 'JB'; font-size: 7.4pt; text-align: right; line-height: 1.65; color: #35373d; padding-top: 2pt; }
.lab { font-family: 'JB'; font-size: 6.8pt; letter-spacing: 0.22em; text-transform: uppercase; color: #8a8d95; margin: 15pt 0 7pt; }
.summary { font-size: 9.6pt; line-height: 1.55; margin: 0; }
.job { margin-bottom: 12pt; break-inside: avoid; }
.job .head { overflow: hidden; }
.job h2 { font-size: 11.5pt; font-weight: 700; letter-spacing: -0.015em; margin: 0; color: #0e0f11; }
.job h2 small { font-size: 7.6pt; font-weight: 400; color: #7b7e86; letter-spacing: 0; margin-left: 4pt; }
.job .when { float: right; font-family: 'JB'; font-size: 7.2pt; color: #7b7e86; white-space: nowrap; padding-top: 3pt; }
.job .role { font-family: 'JB'; font-size: 6.9pt; letter-spacing: 0.15em; text-transform: uppercase; color: #3d4048; margin: 1.5pt 0 3.5pt; }
.job p { margin: 0 0 5pt; }
.tags { display: flex; flex-wrap: wrap; gap: 3pt; }
.tag { font-family: 'JB'; font-size: 6.5pt; line-height: 1; padding: 3pt 5pt; border: 0.5pt solid #d2d2d2; background: #f2f2f2; border-radius: 2.2pt; color: #33353b; }
.rule { border: 0; border-top: 0.6pt solid #cfcfcf; margin: 13pt 0 0; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 9pt 24pt; }
.grid2 h3 { font-family: 'JB'; font-size: 6.7pt; font-weight: 400; letter-spacing: 0.17em; text-transform: uppercase; color: #8a8d95; margin: 0 0 2pt; }
.grid2 p { margin: 0; font-size: 9pt; line-height: 1.45; }
.edu-item { margin-bottom: 6pt; break-inside: avoid; }
.edu-item .r { display: flex; justify-content: space-between; align-items: baseline; }
.edu-item b { font-size: 9.6pt; }
.edu-item .p { font-family: 'JB'; font-size: 7pt; color: #7b7e86; }
.edu-item .pl { color: #5a5d65; font-size: 8.8pt; }
.langs { display: flex; gap: 16pt; }
.langs span { color: #5a5d65; }
"""


def prepare_fonts(dest: pathlib.Path) -> None:
    """Convierte las fuentes de npm (woff2) a TTF estático para incrustarlas en el PDF."""
    inter = NM / "@fontsource-variable/inter/files/inter-latin-wght-normal.woff2"
    for w in (400, 500, 600, 700):
        f = TTFont(inter)
        inst = instancer.instantiateVariableFont(f, {"wght": w})
        inst.flavor = None
        inst.save(dest / f"Inter-{w}.ttf")
    for w in (400, 500):
        f = TTFont(NM / f"@fontsource/jetbrains-mono/files/jetbrains-mono-latin-{w}-normal.woff2")
        f.flavor = None
        f.save(dest / f"JB-{w}.ttf")


def e(s: str) -> str:
    return html.escape(s, quote=False)


def render(lang: str, data: dict, fonts: pathlib.Path) -> None:
    c = data["content"][lang]
    cv = CV[lang]
    sec = cv["sections"]
    contact = [data["site"]["email"], "Paraguay, Encarnación", SITE_URL, LINKEDIN, GITHUB]

    jobs = []
    for i, j in enumerate(c["experience"]["items"]):
        text = cv["itti"] if i == 0 else e(j["text"])
        note = f'<small>— {e(j["note"])}</small>' if j.get("note") else ""
        tags = "".join(f'<span class="tag">{e(t)}</span>' for t in j["tags"])
        jobs.append(
            f'<div class="job"><div class="head"><div class="when">{e(j["period"])} · {e(j["duration"])}</div>'
            f'<h2>{e(j["company"])}{note}</h2></div>'
            f'<div class="role">{e(j["role"])}</div><p>{text}</p><div class="tags">{tags}</div></div>'
        )

    skills = "".join(f'<div><h3>{e(n)}</h3><p>{e(" · ".join(items))}</p></div>' for n, items in c["skills"]["groups"])
    edu = "".join(
        f'<div class="edu-item"><div class="r"><b>{e(x["title"])}</b><span class="p">{e(x["period"])}</span></div>'
        f'<div class="pl">{e(x["place"])}</div></div>'
        for x in c["education"]["items"]
    )
    langs = "".join(f"<span><b>{e(n)}</b> — {e(l)}</span>" for n, l in c["about"]["langList"])

    doc = f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<title>{e(cv["title"])}</title><meta name="author" content="Alvaro Mercado">
<meta name="description" content="{e(c["meta"]["description"])}"></head><body>
<header class="top"><div><h1>Alvaro Mercado</h1><div class="sub">{e(cv["subtitle"])}</div></div>
<div class="contact">{"<br>".join(e(x) for x in contact)}</div></header>
<div class="lab">{sec["summary"]}</div><p class="summary">{cv["summary"]}</p>
<div class="lab">{sec["experience"]}</div>{"".join(jobs)}
<hr class="rule"><div class="lab">{sec["skills"]}</div><div class="grid2">{skills}</div>
<hr class="rule"><div class="grid2"><div><div class="lab" style="margin-top:12pt">{sec["education"]}</div>{edu}</div>
<div><div class="lab" style="margin-top:12pt">{sec["languages"]}</div><div class="langs">{langs}</div></div></div>
</body></html>"""

    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / cv["file"]
    fc = FontConfiguration()  # necesario para que las @font-face locales se carguen
    sheet = WCSS(string=CSS.replace("{fonts}", str(fonts)), font_config=fc)
    HTML(string=doc, base_url=str(ROOT)).write_pdf(target, stylesheets=[sheet], font_config=fc)
    print("OK", target)


def main() -> None:
    data = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "/dev/stdin"))
    with tempfile.TemporaryDirectory() as tmp:
        fonts = pathlib.Path(tmp)
        prepare_fonts(fonts)
        for lang in ("es", "en"):
            render(lang, data, fonts)


if __name__ == "__main__":
    main()
