import json, numpy as np, soundfile as sf, subprocess
seg=json.load(open('asr.json'))
line=[1,1,2,2,2,3,3,4,4,5,5,6,6,6,7,7,7,7,8,9,9,9,9,10]
a,sr=sf.read('rec.wav',dtype='float32')
pad=0.12; out=[]; tl=[]; t=0.35
out.append(np.zeros(int(0.35*sr),np.float32))
for i,s in enumerate(seg):
    x=a[int((s['s']-pad)*sr):int((s['e']+pad)*sr)].copy()
    f=int(0.02*sr); x[:f]*=np.linspace(0,1,f); x[-f:]*=np.linspace(1,0,f)
    tl.append({'i':i,'line':line[i],'s':t,'e':t+len(x)/sr}); out.append(x); t+=len(x)/sr
    if i<len(seg)-1:
        g=0.42 if line[i+1]!=line[i] else 0.18
        out.append(np.zeros(int(g*sr),np.float32)); t+=g
out.append(np.zeros(int(0.8*sr),np.float32)); t+=0.8
sf.write('tight.wav',np.concatenate(out),sr)
json.dump({'dur':t,'tl':tl},open('tl_raw.json','w'),indent=1)
print('raw tight dur',round(t,2))
