from PIL import Image, ImageDraw
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
import json, os

USER = os.getenv('GITHUB_USERNAME', 'Joacoxz712')
TOKEN = os.getenv('GH_TOKEN', '')
headers = {'Accept':'application/vnd.github+json','User-Agent':'nerv-git-cat'}
if TOKEN: headers['Authorization'] = 'Bearer ' + TOKEN
req = Request(f'https://api.github.com/users/{USER}/events/public?per_page=100', headers=headers)
try:
    with urlopen(req, timeout=20) as response: events = json.load(response)
except Exception as exc:
    print(f'Public events unavailable: {exc}; generating the visual with zero activity.')
    events = []
activity = {}
for event in events:
    stamp = event.get('created_at')
    if stamp:
        day = datetime.fromisoformat(stamp.replace('Z','+00:00')).date().isoformat()
        activity[day] = activity.get(day, 0) + 1

W, H, FRAME_COUNT = 720, 260, 16
today = datetime.now(timezone.utc).date()
frames = []
for frame in range(FRAME_COUNT):
    im = Image.new('RGB', (W,H), (8,9,14)); d = ImageDraw.Draw(im)
    # NERV night skyline and muted red moon
    d.ellipse((520,18,612,110), fill=(75,30,48))
    d.ellipse((542,5,630,92), fill=(8,9,14))
    buildings = [(0,90,70,205),(55,68,125,205),(110,105,170,205),(155,52,220,205),(210,85,275,205),(265,110,330,205),(325,72,390,205),(385,96,450,205),(445,55,510,205),(500,100,570,205),(560,78,630,205),(620,110,720,205)]
    for j,(x1,y1,x2,y2) in enumerate(buildings):
        d.rectangle((x1,y1,x2,y2), fill=(13,16,26), outline=(32,35,48))
        for wy in range(y1+12,y2-8,19):
            for wx in range(x1+8,x2-6,16):
                if (wx//8+wy//7+j)%5==0: d.rectangle((wx,wy,wx+4,wy+7), fill=(104,119,137))
        if j in (1,4,8,10): d.rectangle((x1+5,y1+7,x1+12,y1+10), fill=(165,31,53))
    # Rooftop catwalk
    d.rectangle((0,204,W,260), fill=(20,22,31)); d.line((0,204,W,204), fill=(120,48,62), width=2)
    for x in range(0,W,40):
        d.line((x,205,x,230), fill=(49,52,64), width=2)
        d.line((x,230,x+40,230), fill=(49,52,64), width=2)
    # Activity heat marks along the path, based on recent public events.
    for i in range(70):
        day=(today-timedelta(days=69-i)).isoformat(); count=activity.get(day,0)
        x=15+i*9
        if count: d.rectangle((x,240,x+4,240+min(count,4)*3), fill=(165,31,53))
    # Cat walks across the roof and loops; alternating pixel legs and tail.
    cx=40 + int(frame/(FRAME_COUNT-1)*620); cy=176
    white=(244,243,240); red=(190,55,70)
    d.ellipse((cx-15,cy+16,cx+23,cy+27), fill=(5,6,10))
    d.rectangle((cx-12,cy,cx+13,cy+17), fill=white)
    d.rectangle((cx-17,cy-2,cx-4,cy+11), fill=white)
    d.polygon([(cx-17,cy),(cx-16,cy-12),(cx-8,cy-5),(cx-4,cy)], fill=white)
    d.polygon([(cx+3,cy),(cx+11,cy-12),(cx+15,cy-3),(cx+13,cy+2)], fill=white)
    d.rectangle((cx+10,cy+2,cx+24,cy+11), fill=white)
    d.point((cx+17,cy+5), fill=red)
    leg=frame%2*3
    d.line((cx-7,cy+14,cx-10-leg,cy+22), fill=white, width=4)
    d.line((cx+7,cy+14,cx+10+leg,cy+22), fill=white, width=4)
    d.line((cx-16,cy+5,cx-23,cy-2+(frame%3)), fill=white, width=4)
    d.line((cx-23,cy-2+(frame%3),cx-28,cy-8+(frame%3)), fill=white, width=3)
    d.text((22,18), 'NERV // GIT-CAT  |  PUBLIC ACTIVITY SIGNAL', fill=(211,74,94))
    d.text((22,240), 'LEARNING  /  BUILDING  /  REPEATING', fill=(170,165,166))
    frames.append(im)
os.makedirs('assets', exist_ok=True)
frames[0].save('assets/git-cat.gif', save_all=True, append_images=frames[1:], duration=120, loop=0, optimize=True, disposal=2)
p='README.md'
with open(p, encoding='utf-8') as f: readme=f.read()
readme=readme.replace('assets/git-cat-preview.svg','assets/git-cat.gif')
with open(p,'w',encoding='utf-8') as f: f.write(readme)
print(f'Generated {FRAME_COUNT}-frame city cat using {len(events)} recent public events.')