# ════════════════════════════════════════════════════════════════
# GACHA ZOO — Makefile
# Uso rápido:  make deploy        (build + verificación + subir a prod)
# Ayuda:       make help
# ════════════════════════════════════════════════════════════════

SHELL := /bin/zsh
CHROME := /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
PORT := 8431
SF2 := $(HOME)/eva-intro/snes.sf2

.PHONY: help check build deploy serve stop shot cap music db-query db-tables whoami

help: ## Lista de comandos
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

check: ## Valida la sintaxis del JS embebido en index.html
	@python3 -c "import io,re; s=io.open('index.html',encoding='utf8').read(); io.open('/tmp/gz-mod.js','w',encoding='utf8').write(re.search(r'<script type=\"module\">(.*?)</script>',s,re.S).group(1))"
	@node --check /tmp/gz-mod.js && echo "✓ sintaxis OK"
	@node --check worker-src.js && echo "✓ worker OK"

build: check ## Genera dist/ (index + noindex + assets + _worker.js)
	./build.sh

deploy: build ## Build + deploy a Cloudflare Pages (prod: gacha-bbi.pages.dev)
	npx wrangler pages deploy
	@curl -s -o /dev/null -w "prod responde: %{http_code}\n" "https://gacha-bbi.pages.dev/"

serve: ## Servidor local en http://127.0.0.1:$(PORT) (fuente, no dist)
	@pkill -f "http.server $(PORT)" 2>/dev/null; true
	@(python3 -m http.server $(PORT) >/tmp/gz-http.log 2>&1 &) && sleep 1
	@echo "→ http://127.0.0.1:$(PORT)/index.html?demo=1"

stop: ## Para el servidor local y mata Chromes headless zombis
	@pkill -f "http.server $(PORT)" 2>/dev/null; pkill -f "Chrome.*--headless" 2>/dev/null; true

# make shot ID=jiggy  → retrato 512px del personaje en /tmp/gz-shot-<ID>.png
shot: serve ## Retrato de estudio de un personaje (ID=<id del animal>)
	@rm -rf /tmp/gz-h-mk; "$(CHROME)" --headless --disable-gpu --user-data-dir=/tmp/gz-h-mk \
	  --enable-unsafe-swiftshader --use-angle=swiftshader --window-size=600,600 \
	  --virtual-time-budget=6000 --screenshot=/tmp/gz-shot-$(ID).png \
	  "http://127.0.0.1:$(PORT)/index.html?demo=1&still=1&shot=$(ID)" 2>/dev/null; \
	pkill -f gz-h-mk; ls -la /tmp/gz-shot-$(ID).png

# make cap Q="s=12&demo=1&dojo=1" OUT=midojo  → captura general
cap: serve ## Captura headless (Q=querystring, OUT=nombre)
	@rm -rf /tmp/gz-h-mk; "$(CHROME)" --headless --disable-gpu --user-data-dir=/tmp/gz-h-mk \
	  --enable-unsafe-swiftshader --use-angle=swiftshader --window-size=900,650 \
	  --virtual-time-budget=9000 --screenshot=/tmp/gz-$(OUT).png \
	  "http://127.0.0.1:$(PORT)/index.html?$(Q)&still=1" 2>/dev/null; \
	pkill -f gz-h-mk; ls -la /tmp/gz-$(OUT).png

# make music SID=s14 PROGS=24,46,33  → genera music-s14.m4a (programas GM por canal 0,1,2)
music: ## Música de una serie nueva (SID=sXX PROGS=lead,acomp,bajo)
	cd src-music && python3 -c "import mido; m=mido.MidiFile('gacha_zoo_loop.mid'); pr=[int(x) for x in '$(PROGS)'.split(',')]; PROG={0:pr[0],1:pr[1],2:pr[2]}; [setattr(msg,'program',PROG[msg.channel]) for tr in m.tracks for msg in tr if msg.type=='program_change' and msg.channel in PROG]; m.save('gacha_zoo_$(SID).mid')"
	cd src-music && fluidsynth -ni -F gacha_zoo_$(SID)_raw.wav -r 44100 $(SF2) gacha_zoo_$(SID).mid >/dev/null 2>&1
	cd src-music && ffmpeg -y -v error -i gacha_zoo_$(SID)_raw.wav -t 76.8 gacha_zoo_$(SID)_trimmed.wav
	cd src-music && ffmpeg -y -v error -i gacha_zoo_$(SID)_trimmed.wav -c:a aac -b:a 112k ../music-$(SID).m4a
	@ffprobe -v quiet -show_entries format=duration -of csv music-$(SID).m4a
	@echo "⚠️  Recuerda añadir music-$(SID).m4a a build.sh"

# make db-query SQL="SELECT name FROM players"
db-query: ## Consulta D1 remota (SQL="...")
	npx wrangler d1 execute gacha-db --remote --command "$(SQL)"

db-tables: ## Lista tablas y recuentos de D1
	npx wrangler d1 execute gacha-db --remote --command "SELECT name FROM sqlite_master WHERE type='table'"

whoami: ## Comprueba la cuenta de Cloudflare activa
	npx wrangler whoami
