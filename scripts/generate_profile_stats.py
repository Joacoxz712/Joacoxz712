import json, os, urllib.request
from datetime import datetime, timedelta, timezone
from collections import Counter
from pathlib import Path
USER=os.getenv("GITHUB_USERNAME","Joacoxz712")
TOKEN=os.getenv("GH_TOKEN","")
OUT=Path("assets")
OUT.mkdir(exist_ok=True)
PINK="#e8b6d2"
 VIOLET="#c7a6e8"
 TEXT="#f2edf2"
 MUTED="#b9afc1"
PANEL="#15131d"
FONT="Comfortaa, sans-serif"
FONT_TITLE="Josefin Sans, sans-serif"

def api(url):
 h={"Accept":"application/vnd.github+json","User-Agent":"coco-profile-stats"}
 if TOKEN:
     h["Authorization"]="Bearer "+TOKEN
 with urllib.request.urlopen(urllib.request.Request(url,headers=h),timeout=25) as r:
     return json.load(r)

def gql(query):
 if not TOKEN:
     raise RuntimeError("No GitHub token")
 body=json.dumps({"query":query}).encode()
 req=urllib.request.Request("https://api.github.com/graphql",data=body,headers={"Authorization":"Bearer "+TOKEN,"Content-Type":"application/json","User-Agent":"coco-profile-stats"})
 with urllib.request.urlopen(req,timeout=25) as r:
     d=json.load(r)
 if d.get("errors"):
     raise RuntimeError(str(d["errors"]))
 return d["data"]["user"]["contributionsCollection"]

def esc(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def write(n,s):
    (OUT/n).write_text(s,encoding="utf-8")
profile=api(f"https://api.github.com/users/{USER}")
repos=[]
for page in range(1,4):
 batch=api(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=updated&page={page}")
 repos+=batch
 if len(batch)<100:
     break
repos=[r for r in repos if not r.get("fork")]
stars=sum(r.get("stargazers_count",0) for r in repos)
forks=sum(r.get("forks_count",0) for r in repos)
langs=Counter(r.get("language") for r in repos if r.get("language"))
 total=sum(langs.values()) or 1
top=langs.most_common(6)
now=datetime.now(timezone.utc)
 start=(now-timedelta(days=365)).strftime("%Y-%m-%dT00:00:00Z")
end=now.strftime("%Y-%m-%dT23:59:59Z")
calendar=None
try:
 q=f'''query {{ user(login: "{USER}") {{ contributionsCollection(from: "{start}", to: "{end}") {{ contributionCalendar {{ totalContributions weeks {{ contributionDays {{ contributionCount date contributionLevel }} }} }} }} }} }}'''
 calendar=gql(q)
except Exception as e:
    print("Contribution data unavailable; truthful fallback:",e)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="252" viewBox="0 0 1120 252"><defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#100f18"/><stop offset="1" stop-color="#211522"/></linearGradient><linearGradient id="line"><stop stop-color="{PINK}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient></defs><rect width="1120" height="252" rx="22" fill="url(#bg)"/><text x="38" y="48" fill="{PINK}" font-family="{FONT}" font-size="22" font-weight="700">COCO’S GITHUB SNAPSHOT</text><text x="1080" y="47" text-anchor="end" fill="{MUTED}" font-family="{FONT}" font-size="15">LIVE DATA ✦ {now.strftime("%d %b %Y").upper()}</text>']
for i,(label,value) in enumerate([("PUBLIC REPOSITORIES",profile.get("public_repos",0)),("FOLLOWERS",profile.get("followers",0)),("STARS EARNED",stars),("FORKS",forks)]):
 x=38+i*270
 svg.append(f'<g><rect x="{x}" y="78" width="248" height="132" rx="16" fill="{PANEL}" stroke="#68465e" stroke-opacity=".65"/><text x="{x+20}" y="119" fill="{MUTED}" font-family="{FONT}" font-size="16">{label}</text><text x="{x+20}" y="178" fill="{TEXT}" font-family="{FONT}" font-size="48" font-weight="700">{value}</text></g>')
svg.append(f'<path d="M38 222H1082" stroke="url(#line)" stroke-width="2"/></svg>')
write("profile-stats.svg","".join(svg))
palette=["#e8b6d2","#c7a6e8","#92c8d8","#d58b98","#b7a3d6","#8ba7bb"]
lang_h=160+24*max(0,len(top)-1)
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="{lang_h}" viewBox="0 0 1120 {lang_h}"><defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#100f18"/><stop offset="1" stop-color="#211522"/></linearGradient></defs><rect width="1120" height="{lang_h}" rx="22" fill="url(#bg)"/><text x="38" y="48" fill="{PINK}" font-family="{FONT_TITLE}" font-size="22" font-weight="700">LANGUAGES ACROSS MY REPOSITORIES</text><text x="38" y="78" fill="{MUTED}" font-family="{FONT}" font-size="15">Count of repositories by primary language</text>']
for i,(name,count) in enumerate(top):
 y=120+i*24
 s.append(f'<text x="40" y="{y+13}" fill="{TEXT}" font-family="{FONT}" font-size="17">{esc(name)}</text><rect x="245" y="{y-2}" width="700" height="14" rx="7" fill="#302a38"/><rect x="245" y="{y-2}" width="{700*count/total:.1f}" height="14" rx="7" fill="{palette[i%len(palette)]}"/><text x="970" y="{y+13}" fill="{TEXT}" font-family="{FONT}" font-size="17">{count} repos</text>')
if not top:
    s.append(f'<text x="40" y="145" fill="{MUTED}" font-family="{FONT}" font-size="18">No public language data yet.</text>')
s.append("</svg>")
write("profile-languages.svg","".join(s))
if calendar:
 weeks=calendar["contributionCalendar"]["weeks"]
  totalc=calendar["contributionCalendar"]["totalContributions"]
  cells=[]
 months=[]
 sx,sy,cell,gap=44,94,12,5
 for wi,week in enumerate(weeks[-53:]):
  first=week["contributionDays"][0]["date"]
  dt0=datetime.fromisoformat(first)
  if dt0.day<=7:
      months.append(f'<text x="{sx+wi*(cell+gap)}" y="82" fill="{MUTED}" font-family="{FONT}" font-size="13">{dt0.strftime("%b")}</text>')
  for day in week["contributionDays"]:
   dt=datetime.fromisoformat(day["date"])
    y=sy+dt.weekday()*(cell+gap)
   x=sx+wi*(cell+gap)
   col={"NONE":"#282431","FIRST_QUARTILE":"#66415c","SECOND_QUARTILE":"#985c83","THIRD_QUARTILE":"#c17ba6","FOURTH_QUARTILE":PINK}.get(day.get("contributionLevel"),"#282431")
   cells.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{col}"><title>{day["date"]}: {day["contributionCount"]} contributions</title></rect>')
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="220" viewBox="0 0 1120 220"><defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#100f18"/><stop offset="1" stop-color="#211522"/></linearGradient></defs><rect width="1120" height="220" rx="22" fill="url(#bg)"/><text x="38" y="42" fill="{PINK}" font-family="{FONT}" font-size="22" font-weight="700">CONTRIBUTIONS THROUGH THE LAST YEAR</text><text x="1080" y="42" text-anchor="end" fill="{TEXT}" font-family="{FONT}" font-size="20">{totalc} total</text>{"".join(months)}{"".join(cells)}<text x="44" y="207" fill="{MUTED}" font-family="{FONT}" font-size="13">LESS</text><rect x="95" y="195" width="12" height="12" rx="3" fill="#282431"/><rect x="114" y="195" width="12" height="12" rx="3" fill="#66415c"/><rect x="133" y="195" width="12" height="12" rx="3" fill="#985c83"/><rect x="152" y="195" width="12" height="12" rx="3" fill="#c17ba6"/><rect x="171" y="195" width="12" height="12" rx="3" fill="{PINK}"/><text x="195" y="207" fill="{MUTED}" font-family="{FONT}" font-size="13">MORE ✦ GITHUB CONTRIBUTION CALENDAR</text></svg>'
 write("contribution-calendar.svg",svg)
else:
 write("contribution-calendar.svg",f'<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="170" viewBox="0 0 1120 170"><rect width="1120" height="170" rx="22" fill="{PANEL}"/><text x="38" y="54" fill="{PINK}" font-family="{FONT}" font-size="22">CONTRIBUTION CALENDAR</text><text x="38" y="98" fill="{MUTED}" font-family="{FONT}" font-size="18">GitHub did not return contribution data for this update. No numbers have been fabricated.</text></svg>')
print(f"Generated graphics from {len(repos)} non-fork repositories and {len(top)} primary languages; contribution calendar: {bool(calendar)}")
