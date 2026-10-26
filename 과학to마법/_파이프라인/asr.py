import sherpa_onnx, soundfile as sf, numpy as np, json, glob
m=glob.glob('models/*')[0]
r=sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f'{m}/encoder-epoch-99-avg-1.int8.onnx',decoder=f'{m}/decoder-epoch-99-avg-1.int8.onnx',joiner=f'{m}/joiner-epoch-99-avg-1.int8.onnx',tokens=f'{m}/tokens.txt',num_threads=2,decoding_method='greedy_search')
a,sr=sf.read('rec16.wav',dtype='float32')
sil=[(1.30,None)]
# silence list from -40dB pass
S=[(3.51,4.84),(7.38,9.14),(10.65,11.79),(12.02,13.11),(14.11,16.81),(20.07,20.67),(24.64,26.22),(28.40,29.08),(30.94,33.09),(46.25,47.29),(50.32,51.43),(53.11,53.94),(55.53,56.14),(60.56,63.13),(63.53,64.14),(67.97,68.58),(69.79,71.57),(76.25,77.79),(84.24,85.75),(85.99,86.67),(88.51,89.23),(91.73,92.97),(96.27,97.59),(101.43,103.57)]
segs=[];st=1.30
for s,e in S: segs.append((st,s)); st=e
out=[]
for s,e in segs:
    x=a[int(max(0,s-0.15)*sr):int((e+0.15)*sr)]
    st_=r.create_stream(); st_.accept_waveform(sr,x); r.decode_stream(st_)
    out.append({'s':round(s,2),'e':round(e,2),'t':st_.result.text})
    print(f"{s:6.2f}-{e:6.2f} {st_.result.text}")
json.dump(out,open('asr.json','w'),ensure_ascii=False,indent=1)
