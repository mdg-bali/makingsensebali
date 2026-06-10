[English](TEST_PLAN.md) · [Bahasa Indonesia](TEST_PLAN.id.md) · **Español**

# Plan de pruebas pre-beta — MLX + bot de principio a fin

Esta es la checklist para sentarse con un café. Ejecútala en orden una mañana
normal — debería tomar 1–2 horas en total. Al final sabrás si
el sistema está listo para los primeros 3–5 usuarios beta de Bukit.

No necesitas el NAS para los pasos 1–5. El lado MLX es autónomo
y puede probarse por su cuenta primero.

---

## Fase A — Servidor MLX (solo M1, ~30 min)

### A1. Configura el entorno de Python

```bash
cd ~/fablab-bali/aq-reporter

python3 -m venv ~/.venv/aq-vision
source ~/.venv/aq-vision/bin/activate

pip install --upgrade pip
pip install mlx-vlm fastapi uvicorn pillow requests
```

✅ Éxito: `pip list` muestra mlx-vlm, fastapi, uvicorn, pillow, requests.

⚠️ Si mlx-vlm falla al instalarse: no estás en Apple Silicon, o tu
macOS es anterior a 13.5. Arregla el env antes de continuar.

### A2. Verifica que mlx-vlm puede cargar un modelo de forma independiente

No confíes todavía en nuestro wrapper — prueba primero mlx-vlm en sí:

```bash
python3 -c "
from mlx_vlm import load, generate
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config
print('mlx-vlm imports OK')
print('Loading Phi-3.5-Vision-4bit (~2.5GB, first run downloads it)...')
model, processor = load('mlx-community/Phi-3.5-vision-instruct-4bit')
config = load_config('mlx-community/Phi-3.5-vision-instruct-4bit')
print('Model loaded OK')
"
```

✅ Éxito: imprime `Model loaded OK` tras una descarga de 1–5 minutos.

⚠️ Si la importación de `apply_chat_template` falla: mlx-vlm cambió su API.
Verifica `python3 -c "import mlx_vlm; print(mlx_vlm.__version__)"` y
busca en el changelog de mlx-vlm. Arreglo probable: ajusta la línea de importación en
`mlx_vision_server.py` a la nueva ruta que corresponda.

### A3. Ejecuta nuestro servidor y golpea /health

```bash
cd ~/fablab-bali/aq-reporter
python mlx_vision_server.py
```

Espera `model ready in N.Ns` en los logs. En una segunda terminal:

```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```

✅ Éxito:
```json
{
  "ok": true,
  "model": "mlx-community/Phi-3.5-vision-instruct-4bit",
  "mlx_available": true
}
```

### A4. Envía una imagen real a /analyze

Encuentra cualquier foto en tu Mac (una foto real de Bukit es lo mejor). Luego:

```bash
# Encode a test image to base64
IMG="$HOME/Desktop/some_photo.jpg"   # ← change to a real path

python3 -c "
import base64, json, requests, sys
img_b64 = base64.b64encode(open(sys.argv[1], 'rb').read()).decode()
prompt = '''Classify this image. Respond with ONLY a JSON object:
{
  \"detected\": true|false,
  \"category\": one of [burning, trash, vehicle, construction, industrial, dust, other, none],
  \"confidence\": 0.0 to 1.0,
  \"indicators\": [short phrases],
  \"description\": one short sentence,
  \"severity\": one of [low, medium, high, critical]
}'''
r = requests.post('http://localhost:8000/analyze',
                  json={'image_b64': img_b64, 'prompt': prompt},
                  timeout=120)
print(json.dumps(r.json(), indent=2))
" "$IMG"
```

✅ Éxito: la respuesta es un objeto JSON válido con `category`, `severity`,
`confidence`, `indicators`. La latencia en un M1 de 16GB debería ser de 5–15 segundos
para Phi-3.5-Vision-4bit.

⚠️ Si la respuesta es `{"detected": false, "category": "other", ...
"model_version": "...:parse_error"}`: el modelo devolvió prosa en lugar de
JSON. Phi-3.5 hace esto ocasionalmente. Si pasa en más de
~1 de cada 5 fotos, considera cambiar a Qwen2-VL-7B-4bit (define
`AQ_MLX_MODEL=mlx-community/Qwen2-VL-7B-Instruct-4bit`).

### A5. Prueba la calidad de clasificación con 5 ejemplos deliberados

Este es el paso más importante. Encuentra 5 fotos que cubran el espectro:

1. Quema de basura obvia (humo + fuego visible)
2. Polvo de construcción / obra en construcción
3. Escena de tráfico / escape de motocicletas
4. Un paisaje normal de Bukit (sin contaminación) — prueba de falso positivo
5. Una selfie en interiores o foto de comida — prueba de irrelevancia

Pasa cada una por `/analyze` y anota el resultado. No esperes
la perfección. Espera:

- Quema de basura → `category: burning, severity: high or critical`
- Construcción → `category: construction, severity: medium`
- Tráfico → `category: vehicle, severity: medium`
- Paisaje limpio → `category: none, detected: false`
- Selfie → `category: none or other, detected: false`

Si 4/5 caen en el cajón correcto, ship. Si 3/5, el prompt necesita trabajo.
Si 2/5 o peor, cambia de modelo.

---

## Fase B — Integración Worker → MLX (~20 min)

### B1. Detén el servidor MLX brevemente, luego reinícialo en segundo plano

```bash
# Ctrl-C the running server
# Then start it as a background process:
cd ~/fablab-bali/aq-reporter
nohup python mlx_vision_server.py > /tmp/mlx-server.log 2>&1 &
echo $! > /tmp/mlx-server.pid

# Verify it came back up
sleep 5 && curl -s http://localhost:8000/health
```

### B2. Ejecuta el worker contra una cola falsa local (sin necesidad del NAS)

```bash
# Set up a fake repo locally for testing
mkdir -p /tmp/aq-test/{reports,profiles,images,vision_queue}
mkdir -p /tmp/aq-test/vision_queue/{processing,done,failed}

# Copy code into it
cp ~/fablab-bali/aq-reporter/*.py /tmp/aq-test/
cp ~/fablab-bali/aq-reporter/config.json /tmp/aq-test/ 2>/dev/null || \
  echo '{"node_id":"bali.fab.city","bioregion":"indo_pacific_coral_triangle","primary_url":"https://planetai.fab.city/bali"}' \
  > /tmp/aq-test/config.json

# Put a real photo into images/ — use one of your A5 test photos
cp ~/Desktop/some_photo.jpg /tmp/aq-test/images/test1.jpg

# Create a fake report
cat > /tmp/aq-test/reports/AQ_LOCAL_001.json <<EOF
{
  "id": "AQ_LOCAL_001",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "source": "whatsapp",
  "sender_hash": "testsender",
  "type": "photo",
  "description": "test photo from Pecatu",
  "image_path": "/tmp/aq-test/images/test1.jpg",
  "ai_analysis": null,
  "status": "pending",
  "location": {"lat": -8.83, "lon": 115.10}
}
EOF

# Enqueue the vision job
cat > /tmp/aq-test/vision_queue/AQ_LOCAL_001.json <<EOF
{
  "report_id": "AQ_LOCAL_001",
  "image_path": "/tmp/aq-test/images/test1.jpg",
  "queued_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

# Run the worker (it processes the queue and exits when empty if we wrap it)
AQ_REPO=/tmp/aq-test \
AQ_VISION_BACKEND=mlx \
AQ_VISION_ENDPOINT=http://localhost:8000/analyze \
AQ_POLL_INTERVAL=1 \
  timeout 60 python ~/fablab-bali/aq-reporter/m1_vision_worker.py
```

El worker corre indefinidamente — mátalo con Ctrl-C en cuanto lo hayas visto
procesar el trabajo (`timeout 60` lo matará tras 60s de todos modos).

✅ Éxito: ves líneas de log como
```
analyzing AQ_LOCAL_001 (test1.jpg)
  → burning / high (conf=0.82) in 7.4s
```

### B3. Inspecciona lo que escribió el worker

```bash
# Report should now have ai_analysis filled in
cat /tmp/aq-test/reports/AQ_LOCAL_001.json | python3 -m json.tool

# Profile should be in profiles/ (sanitized, no sender info)
cat /tmp/aq-test/profiles/AQ_LOCAL_001.json | python3 -m json.tool

# Job should be in vision_queue/done/ with notify_jid stripped
ls /tmp/aq-test/vision_queue/done/
cat /tmp/aq-test/vision_queue/done/AQ_LOCAL_001.json
```

✅ Éxito: el reporte tiene `ai_analysis` poblado, el perfil está
sanitizado (sin `sender_hash`, sin `image_path`), y el trabajo está archivado
en `done/` sin `notify_jid`.

---

## Fase C — Bot de principio a fin vía curl-como-WhatsApp (~20 min)

Sáltate esto si tu NAS aún no está listo. De lo contrario, esto valida
todo el pipeline antes de que cualquier mensaje real de WhatsApp llegue al sistema.

### C1. Inicia el bot localmente

Más fácil que levantar Docker para pruebas:

```bash
cd ~/fablab-bali/aq-reporter
pip install flask  # if not already
# Override paths so this test uses /tmp/aq-test, not your real data
AQ_VISION_BACKEND=mock python bot_murmurations.py
```

(Usamos `mock` aquí porque el bot no llama a vision — el M1 worker
lo hace. La llamada de vision del bot solo se dispara si `synchronous_vision=true` en
config, lo cual evitaríamos de todos modos en producción.)

### C2. Simula mensajes de WhatsApp con curl

El bot escucha en `:5055/webhook`. Envíale payloads con forma de Evolution:

```bash
# First contact — should get consent prompt
curl -sX POST http://localhost:5055/webhook \
  -H 'Content-Type: application/json' \
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {"id":"t1","remoteJid":"6281555000111@s.whatsapp.net","fromMe":false},
      "pushName":"Test User",
      "messageTimestamp": '$(date +%s)',
      "message":{"conversation":"halo"}
    }
  }'
```

Observa los logs del bot. Deberías ver `msg from +6281555000111 type=text`
y una respuesta de dry-run sobre el prompt de consentimiento.

```bash
# Grant consent
curl -sX POST http://localhost:5055/webhook \
  -H 'Content-Type: application/json' \
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {"id":"t2","remoteJid":"6281555000111@s.whatsapp.net","fromMe":false},
      "messageTimestamp": '$(date +%s)',
      "message":{"conversation":"SETUJU"}
    }
  }'

# Send a text report
curl -sX POST http://localhost:5055/webhook \
  -H 'Content-Type: application/json' \
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {"id":"t3","remoteJid":"6281555000111@s.whatsapp.net","fromMe":false},
      "messageTimestamp": '$(date +%s)',
      "message":{"conversation":"ada asap di pantai bingin"}
    }
  }'

# Share location (Bingin)
curl -sX POST http://localhost:5055/webhook \
  -H 'Content-Type: application/json' \
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {"id":"t4","remoteJid":"6281555000111@s.whatsapp.net","fromMe":false},
      "messageTimestamp": '$(date +%s)',
      "message":{"locationMessage":{"degreesLatitude":-8.806,"degreesLongitude":115.130}}
    }
  }'
```

✅ Éxito: `reports/` tiene un nuevo AQ_*.json, `profiles/` tiene un perfil
coincidente con `locality: "Bingin"`, sin campos de PII.

---

## Fase D — Auditoría de privacidad + seguridad (~15 min)

No te saltes esto. Ejecútalo antes de que cualquier usuario real llegue al sistema.

### D1. Barrido de PII en los perfiles

```bash
cd ~/fablab-bali/aq-reporter
python3 -c "
import json, glob
bad = 0
for p in glob.glob('profiles/AQ_*.json'):
    prof = json.load(open(p))
    leaks = [k for k in prof if k in ('sender','sender_hash','image_path','media_key','phone','number')]
    leaks += [k for k in prof if k.startswith('_')]
    if leaks:
        print(f'LEAK in {p}: {leaks}')
        bad += 1
print(f'{bad} leaks found')
"
```

✅ Éxito: `0 leaks found`.

### D2. Chequeo de cordura de la compuerta de consentimiento

```bash
# A sender who never consented should NEVER have a report in profiles/.
# Pull a sample sender_hash and check.
python3 -c "
import json, glob, hashlib
# Phone number you tested with above
test_phone = '+6281555000111'
expected_hash = hashlib.sha256(test_phone.encode()).hexdigest()[:16]

# Did they grant consent?
consent = json.load(open('consent.json')) if open('consent.json') else {}
print('Consent status:', consent.get(expected_hash, 'unknown'))

# Are their reports in the canonical store?
for r_path in glob.glob('reports/AQ_*.json'):
    r = json.load(open(r_path))
    if r.get('sender_hash') == expected_hash:
        print('  Found report:', r_path)
"
```

Si el remitente tiene consentimiento `granted` y existen reportes, eso es lo esperado.
Si el remitente tiene consentimiento `unknown` pero sus reportes pasaron,
eso es un bug — márcalo antes de llegar a los usuarios.

### D3. Inspección de archivos de imagen

Abre una de las fotos que llegaron y verifica:

- ¿Están los datos EXIF GPS en el archivo? `exiftool images/AQ_*.jpg | grep GPS`
  → si es así, deberías agregar el stripping de EXIF antes de publicar imágenes
- ¿Hay caras identificables visibles? → posterga el auto-blur a un sprint
  posterior, pero asegúrate de que tu documento de consentimiento les diga a los usuarios que sus fotos podrían
  mostrar personas

### D4. Revisión del texto en Bahasa

Abre `bot_murmurations.py`, encuentra:

- `CONSENT_PROMPT`
- `CONSENT_CONFIRMED`
- `OPTOUT_CONFIRMED`
- Las cadenas de respuesta en `_handle_text`, `_handle_image`, `_handle_location`,
  `_handle_audio`, `_handle_command`

**Envíaselas a un hablante nativo de Bahasa antes de que los usuarios las vean.** Esto
no es negociable. La confianza empieza con la primera respuesta.

---

## Fase E — Checklist de preparación de usuarios beta (5 min)

Antes de invitar a tus primeros 3–5 usuarios, verifica:

- [ ] El servidor MLX corre de forma fiable durante al menos 1 hora (sin crashes, sin OOM)
- [ ] El worker procesa 10+ fotos de prueba sin crashear
- [ ] La latencia de inferencia promedio está por debajo de 20 segundos (de lo contrario los usuarios pensarán que está roto)
- [ ] Las respuestas del bot están en buen Bahasa (D4 arriba)
- [ ] La sincronización de perfiles a planetai.fab.city funciona (ejecuta `./sync_profiles.sh` una vez, luego verifica que una URL como `https://planetai.fab.city/bali/profiles/AQ_<id>.json` realmente cargue)
- [ ] Tienes una forma de monitorear lo que está pasando (`tail -f` sobre los logs del bot + worker, o un panel simple)
- [ ] Tienes una forma de eliminar los datos de un usuario si lo piden (busca por sender_hash; elimina report + profile + re-rsync para actualizar el mirror público)
- [ ] Tienes una forma de hacer broadcast a todos los usuarios que dieron consentimiento por si lo necesitas (p. ej. "el bot estará caído por mantenimiento el domingo") — esto probablemente signifique un pequeño script de una sola vez usando el endpoint de envío de Evolution API
- [ ] Energía: el NAS está sobre un UPS, el M1 está enchufado (o has aceptado que vision se pausa cuando el M1 duerme)
- [ ] Tú mismo has sido usuario durante al menos 24 horas y has enviado ~10 reportes reales sin sorpresas

---

## Protocolo de lanzamiento beta

Cuando estés listo, no satures un grupo de banjar con el número del bot.
Incorpora en este orden:

1. **Tú** (ya hecho para cuando leas esto)
2. **Un socio** — Elaine o Tafia, alguien que te dirá la verdad
3. **Tres vecinos amistosos de Bukit** con quienes puedas hablar en persona
4. **Cinco más, por referencia** de los primeros tres
5. **Un grupo pequeño de banjar/escuela** (10–20 personas) — solo después de que lo anterior se sienta estable durante una semana

En cada paso, observa los modos de fallo:
- ¿La gente envía ubicación? Si no, la UX necesita empujar más fuerte
- ¿Las fotos llegan con contexto útil? Si no, el prompt necesita trabajo
- ¿La gente envía notas de voz? Construye Whisper en el próximo sprint
- ¿Qué proporción de reportes se clasifica realmente de forma limpia? Si <60%, cambia de modelo
- ¿Hay alguien confundido por el prompt de consentimiento? Reescríbelo

Cuando tengas 50+ reportes de 10+ usuarios reales y el sistema haya corrido
sin supervisión durante una semana, has superado la barra del piloto y puedes empezar
a hablar con otros Fab Labs sobre un sister node.
