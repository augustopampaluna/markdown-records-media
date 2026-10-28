from PIL import Image, ImageDraw, ImageFont
bg=Image.open('assets/backgrounds/bg_glass_floor_4x5_v01.png').convert('RGB'); W,H=bg.size
d=ImageDraw.Draw(bg)
m=int(W*0.08)
def sg(size,w):
    f=ImageFont.truetype('brand/fonts/SpaceGrotesk[wght].ttf',size); f.set_variation_by_axes([w]); return f
mono=lambda s:ImageFont.truetype('brand/fonts/IBMPlexMono-Medium.ttf',s)
def bez(p0,p1,p2,p3,n=40):
    return [((1-t)**3*p0[0]+3*(1-t)**2*t*p1[0]+3*(1-t)*t*t*p2[0]+t**3*p3[0],(1-t)**3*p0[1]+3*(1-t)**2*t*p1[1]+3*(1-t)*t*t*p2[1]+t**3*p3[1]) for t in [i/n for i in range(n+1)]]
polys=[[(192,678),(312,678),(312,804),(192,804)],[(328,450),(514,630),(514,804),(487,804),(328,641)],[(699,450),(699,804),(691,804),(518,629)],
[(725,450),(875,450)]+bez((875,450),(968.3,450),(1044,529.2),(1044,627))+bez((1044,627),(1044,724.8),(968.3,804),(875,804))+[(725,804)]]
lw=int(W*0.20); lh=int(lw*354/852); SS=4
mk=Image.new('L',(lw*SS,lh*SS),0); md=ImageDraw.Draw(mk); k=lw*SS/852
for p in polys: md.polygon([((x-192)*k,(y-450)*k) for x,y in p],fill=255)
mk=mk.resize((lw,lh),Image.LANCZOS)
def track(x,y,t,f,fill,sp):
    for ch in t:
        d.text((x,y),ch,font=f,fill=fill); x+=d.textlength(ch,font=f)+sp
# statement
f=sg(int(W*0.105),600); fill=(244,245,246)
y=int(H*0.20)
d.text((m,y),"Dark pressure.",font=f,fill=fill)
d.text((m,y+int(W*0.125)),"Precise sound.",font=f,fill=fill)
# meta top
# bottom: logo signature + lockup text
white=Image.new('RGBA',(lw,lh),(255,255,255,0)); white.putalpha(mk)
ly=H-int(H*0.07)-lh
bg.paste(white,(m,ly),white)
tx=m+lw+int(W*0.04)
track(tx,ly+int(lh*0.05),"MARKDOWN RECORDS",mono(int(W*0.024)),(244,245,246),3)
track(tx,ly+int(lh*0.60),"RAW SIGNALS. NO MERCY.",mono(int(W*0.018)),(150,152,156),2)
bg.save('out_statement.png')
