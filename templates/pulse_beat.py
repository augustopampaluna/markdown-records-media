import numpy as np, subprocess
from PIL import Image, ImageFilter
im=Image.open('assets/backgrounds/bg_glass_corridor_9x16_v01.png').convert('RGB').resize((720,1280),Image.LANCZOS)
a=np.asarray(im,dtype=np.float32)/255
L=a.mean(axis=2)
# edge/highlight mask: bright areas, soft
mask=np.clip((L-0.45)/0.35,0,1)
mimg=Image.fromarray((mask*255).astype(np.uint8))
bloom=np.asarray(mimg.filter(ImageFilter.GaussianBlur(14)),dtype=np.float32)/255
mask3=mask[...,None]; bloom3=bloom[...,None]
FPS=24; BEAT=10  # 144 BPM exactly
N=120
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','720x1280','-r',str(FPS),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','16','out_pulse.mp4'],stdin=subprocess.PIPE)
env_log=[]
for n in range(N):
    ph=(n%BEAT)/BEAT
    env=np.exp(-5.0*ph)          # sharp attack on the beat, decay
    env_log.append(env)
    dim=0.55                      # base level between beats
    out=a*(dim+0.0*mask3)         # whole scene dims slightly
    out=a*(1-mask3*(1-dim)*(1-env)) # highlights drop between beats, full on beat
    out=out+bloom3*0.35*env*mask3.mean()*0+bloom3*0.30*env
    out=np.clip(out,0,1)
    p.stdin.write((out*255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
