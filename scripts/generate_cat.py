import json, os, urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from PIL import Image, ImageDraw

USER = os.getenv('GITHUB_USERNAME', 'Joacoxz712')
TOKEN = os.getenv('GH_TOKEN', '')
headers = {'Accept':'application/vnd.github+json','User-Agent':'nerv-git-cat'}
if TOKEN: headers['Authorization'] = 'Bearer ' + TOKEN
req = urllib.request.Request(f'https://api.github.com/users/{USER}/events/public?per_page=100', headers=headers)
with urllib.request.urlopen(req, timeout=25) as response: events = json.load(response)
counts = {}
for event in events:
    stamp = event.get('created_at')
    if stamp:
        day = datetime.fromisoformat(stamp.replace('Z','+00:00')).date().isoformat()
        counts[day] = counts.get(day, 0) + 1

W,H = 1000,300
frames=[]
today = datetime.now(timezone.utc).date()
for frame in range(16):
    im=Image.new('RGB',(W,H),(8,9,14)); d=ImageDraw.Draw(im)
    d.text((30,22),'GIT-CAT // PUBLIC ACTIVITY TERRAIN',fill=(211,74,94))
    d.text((30,275),'NERV DEVELOPMENT LOG  /  RECENT PUBLIC EVENTS',fill=(170,165,166))
    # Isometric tiles: recent 98 days, heights represent public event counts.
    for i in range(98):
        col,row=i%14,i//14
        x=100+col*55+row*22; y=72+row*23+col*5
        day=(today-timedelta(days=97-i)).isoformat(); n=counts.get(day,0)
        h=min(n,5)*5
        color=(37,37,43) if n==0 else [(84,32,43),(121,35,51),(165,43,64),(211,74,94),(240,120,131)][min(n,5)-1]
        pts=[(x,y-h),(x+24,y+12-h),(x,y+24-h),(x-24,y+12-h)]
        d.polygon(pts,fill=color,outline=(75,52,58))
        if h: d.polygon([(x,y-h-7),(x+24,y+12-h-7),(x,y+24-h-7),(x-24,y+12-h-7)],fill=(min(255,color[0]+35),min(255,color[1]+25),min(255,color[2]+25)))
    # Tiny white pixel cat; moves along the activity path.
    idx=min(97, int(frame/15*97)); col,row=idx%14,idx//14
    cx=100+col*55+row*22; cy=72+row*23+col*5-22
    white=(244,243,240); red=(165,31,53)
    d.rectangle((cx-10,cy-5,cx+10,cy+9),fill=white)
    d.polygon([(cx-10,cy-5),(cx-9,cy-14),(cx-3,cy-7),(cx+3,cy-7),(cx+9,cy-14),(cx+10,cy-5)],fill=white)
    d.point((cx-4,cy),fill=red); d.point((cx+4,cy),fill=red)
    tail_y=cy+5+(frame%2)*2; d.line((cx+10,cy+4,cx+16,tail_y,cx+19,tail_y-4),fill=white,width=3)
    frames.append(im)
Path('assets').mkdir(exist_ok=True)
frames[0].save('assets/git-cat.gif',save_all=True,append_images=frames[1:],duration=120,loop=0,optimize=True)
# Switch README to the generated GIF once it exists.
p=Path('README.md'); s=p.read_text(encoding='utf-8')
s=s.replace('assets/git-cat-preview.svg','assets/git-cat.gif')
p.write_text(s,encoding='utf-8')
print(f'Generated animated cat from {len(events)} recent public events.')