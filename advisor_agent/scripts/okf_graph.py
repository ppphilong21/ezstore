"""Render the OKF bundle as a self-contained interactive graph (one HTML file, no network needed).

    uv run python scripts/okf_graph.py [bundle_dir] [-o okf-graph.html]
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sales_advisor.okf import Bundle, default_bundle_path  # noqa: E402

PAGE = """<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>EZStore OKF graph</title>
<style>
:root{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#6b6a65;--line:#c9c6bd;--card:#fff}
@media (prefers-color-scheme:dark){:root{--bg:#161614;--fg:#ecebe6;--muted:#a19f97;--line:#4a4842;--card:#22211e}}
body{margin:0;font:14px/1.5 -apple-system,"PingFang TC","Noto Sans TC",sans-serif;background:var(--bg);color:var(--fg)}
header{padding:12px 16px;border-bottom:1px solid var(--line)}h1{font-size:16px;margin:0}
#wrap{display:flex;height:calc(100vh - 50px)}svg{flex:1;min-width:0}
aside{width:340px;max-width:45vw;overflow:auto;border-left:1px solid var(--line);padding:12px 16px;background:var(--card)}
aside pre{white-space:pre-wrap;font:12px/1.5 ui-monospace,Menlo,monospace;color:var(--muted)}
.legend span{display:inline-block;margin-right:10px;font-size:12px}.dot{width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:4px}
text{font-size:11px;fill:var(--fg);pointer-events:none}line{stroke:var(--line)}circle{cursor:pointer;stroke:var(--bg);stroke-width:1.5}
</style></head><body><header><h1>EZStore OKF bundle — __N__ concepts, __E__ links</h1><div class="legend" id="legend"></div></header>
<div id="wrap"><svg id="g"></svg><aside id="side"><p>點一個節點看概念內容（frontmatter + 內文）。拖曳可移動。</p></aside></div>
<script>
const data=__DATA__;
const colors=["#2f6fb0","#c2552d","#3b8a5a","#8a5bb0","#b08a2f","#2f9aa0","#a03f6b"];
const groups=[...new Set(data.nodes.map(n=>n.group))];const color=g=>colors[groups.indexOf(g)%colors.length];
document.getElementById("legend").innerHTML=groups.map(g=>`<span><i class="dot" style="background:${color(g)}"></i>${g}</span>`).join("");
const svg=document.getElementById("g");let W=svg.clientWidth,H=svg.clientHeight;
const N=data.nodes.map((n,i)=>({...n,x:W/2+Math.cos(i)*200*Math.random(),y:H/2+Math.sin(i)*200*Math.random(),vx:0,vy:0}));
const idx=Object.fromEntries(N.map((n,i)=>[n.id,i]));const E=data.links.filter(l=>l.source in idx&&l.target in idx);
const ns="http://www.w3.org/2000/svg";const lines=E.map(()=>svg.appendChild(document.createElementNS(ns,"line")));
const deg={};E.forEach(l=>{deg[l.source]=(deg[l.source]||0)+1;deg[l.target]=(deg[l.target]||0)+1});
const nodes=N.map(n=>{const c=document.createElementNS(ns,"circle");c.setAttribute("r",6+2*Math.sqrt(deg[n.id]||0));c.setAttribute("fill",color(n.group));
 c.onclick=()=>show(n);svg.appendChild(c);const t=document.createElementNS(ns,"text");t.textContent=n.title;svg.appendChild(t);return [c,t]});
function show(n){document.getElementById("side").innerHTML=`<h2 style="font-size:15px">${n.title}</h2><p><b>${n.id}</b> · ${n.type}</p><p>${n.description}</p><pre>${n.text}</pre>`}
let drag=null;svg.onmousedown=e=>{const p=pt(e);drag=N.reduce((b,n)=>((n.x-p.x)**2+(n.y-p.y)**2<(b?.d??400))?{n,d:(n.x-p.x)**2+(n.y-p.y)**2}:b,null)?.n||null};
svg.onmousemove=e=>{if(drag){const p=pt(e);drag.x=p.x;drag.y=p.y;drag.vx=drag.vy=0}};window.onmouseup=()=>drag=null;
function pt(e){const r=svg.getBoundingClientRect();return{x:e.clientX-r.left,y:e.clientY-r.top}}
function tick(){W=svg.clientWidth;H=svg.clientHeight;
 for(let i=0;i<N.length;i++)for(let j=i+1;j<N.length;j++){const a=N[i],b=N[j];let dx=a.x-b.x,dy=a.y-b.y,d2=dx*dx+dy*dy+0.01,f=4200/d2;a.vx+=dx*f/Math.sqrt(d2);a.vy+=dy*f/Math.sqrt(d2);b.vx-=dx*f/Math.sqrt(d2);b.vy-=dy*f/Math.sqrt(d2)}
 E.forEach(l=>{const a=N[idx[l.source]],b=N[idx[l.target]];const dx=b.x-a.x,dy=b.y-a.y,d=Math.sqrt(dx*dx+dy*dy)||1,f=(d-120)*0.02;a.vx+=dx/d*f;a.vy+=dy/d*f;b.vx-=dx/d*f;b.vy-=dy/d*f});
 N.forEach(n=>{if(n===drag)return;n.vx+=(W/2-n.x)*0.004;n.vy+=(H/2-n.y)*0.004;n.vx*=0.82;n.vy*=0.82;n.x=Math.max(20,Math.min(W-20,n.x+n.vx));n.y=Math.max(20,Math.min(H-20,n.y+n.vy))});
 E.forEach((l,i)=>{const a=N[idx[l.source]],b=N[idx[l.target]];lines[i].setAttribute("x1",a.x);lines[i].setAttribute("y1",a.y);lines[i].setAttribute("x2",b.x);lines[i].setAttribute("y2",b.y)});
 N.forEach((n,i)=>{nodes[i][0].setAttribute("cx",n.x);nodes[i][0].setAttribute("cy",n.y);nodes[i][1].setAttribute("x",n.x+9);nodes[i][1].setAttribute("y",n.y+4)});
 requestAnimationFrame(tick)}tick();
</script></body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle", nargs="?", default=str(default_bundle_path()))
    ap.add_argument("-o", "--output", default="okf-graph.html")
    args = ap.parse_args()
    b = Bundle(args.bundle)
    nodes = [
        {"id": c.id, "title": c.title, "type": c.type, "description": html.escape(c.description),
         "group": c.id.split("/", 1)[0] if "/" in c.id else "root",
         "text": html.escape(c.path.read_text(encoding="utf-8"))[:3000]}
        for c in b.concepts.values()
    ]
    links = [{"source": c.id, "target": t} for c in b.concepts.values() for t in c.links]
    out = (PAGE.replace("__DATA__", json.dumps({"nodes": nodes, "links": links}, ensure_ascii=False))
           .replace("__N__", str(len(nodes))).replace("__E__", str(len(links))))
    Path(args.output).write_text(out, encoding="utf-8")
    print(f"wrote {args.output}: {len(nodes)} concepts, {len(links)} links")
    return 0


if __name__ == "__main__":
    sys.exit(main())
