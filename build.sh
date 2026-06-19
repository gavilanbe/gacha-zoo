#!/bin/zsh
# build del deploy público de Gacha Zoo
set -e
cd ~/gacha-zoo
rm -rf dist && mkdir dist
python3 - <<'PY'
s=open('index.html').read()
a='<meta name="theme-color" content="#FFF3E2">'
s=s.replace(a, a+'\n<meta name="robots" content="noindex">',1)
open('dist/index.html','w').write(s)
PY
cp music.m4a music-s1.m4a music-s2.m4a music-s3.m4a music-s4.m4a music-s5.m4a music-s6.m4a music-s7.m4a music-s8.m4a music-s9.m4a music-s10.m4a music-s11.m4a music-s12.m4a music-s13.m4a music-s14.m4a manifest.json sw.js icon-180.png icon-192.png icon-512.png dist/
cp worker-src.js dist/_worker.js
echo "build OK"
