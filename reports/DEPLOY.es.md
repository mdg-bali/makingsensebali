[English](DEPLOY.md) · [Bahasa Indonesia](DEPLOY.id.md) · **Español**

# Guía de despliegue — Making Sense Bali Reporter

Pon en marcha el primer nodo PLANETAI Community-tier sobre infraestructura doméstica.

## Qué corre dónde

```
┌──────────────────────────────────────────────────────────┐
│ Synology DS725+ NAS — always on (UPS-backed)             │
│                                                          │
│   Container Manager:                                     │
│     • aq-evolution   (WhatsApp transport, Baileys)       │
│     • aq-bot         (Flask webhook + Murmurations)      │
│                                                          │
│   /volume1/docker/aq-reporter/                           │
│     ├── data/reports/   (canonical, NAS-only, has PII)   │
│     ├── data/profiles/  (sanitized, rsync source)        │
│     ├── data/images/    (raw photos, NAS-only)           │
│     └── data/vision_queue/   (jobs for the M1)           │
│                                                          │
│   Cron:                                                  │
│     */5 * * * *  sync_profiles.sh   → planetai.fab.city  │
│                                                          │
├──────────────────────────────────────────────────────────┤
│ M1 MacBook Pro — when home                               │
│                                                          │
│   mlx_vision_server.py    (FastAPI, port 8000)           │
│     ← loads Phi-3.5-Vision-4bit (~2.5GB) at startup      │
│                                                          │
│   m1_vision_worker.py     (polls vision_queue)           │
│     ← mounts NAS folder via SMB                          │
│     ← calls localhost:8000/analyze for each photo        │
│     ← writes analysis back into report                   │
│     ← regenerates Murmurations profile                   │
│     ← optionally sends WhatsApp follow-up                │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

El bot nunca se bloquea por la inferencia. Si el M1 está dormido, las fotos se acumulan
en la cola y se procesan cuando despierta. Si el M1 está muerto durante una
semana, el bot sigue recolectando reportes — simplemente quedan sin clasificar
hasta que alguien (o un worker de fallback) los procesa.

## Prerrequisitos

- Synology DSM 7.2+ con Container Manager instalado
- Un M1 MacBook (o cualquier Mac Apple Silicon) con al menos 16GB de RAM
- Un número de WhatsApp que puedas dedicar al bot (tu número personal
  sirve para el piloto, pero querrás uno separado antes de escalar)
- Un UPS para el NAS — los apagones en Bukit son reales, ~$80 una sola vez
- Hosting web de `planetai.fab.city` listo para recibir `/bali/profiles/*.json`

## 1. Lleva el código al NAS

Desde tu laptop:

```bash
# Option A: rsync (recommended)
rsync -av --exclude='data' --exclude='.env' \
  ~/fablab-bali/aq-reporter/ \
  tomas@nas.local:/volume1/docker/aq-reporter/

# Option B: SSH + git clone if you've pushed this to a repo
ssh tomas@nas.local
cd /volume1/docker
git clone <your-repo> aq-reporter
```

## 2. Configura los secrets

Conéctate por SSH al NAS:

```bash
cd /volume1/docker/aq-reporter
cp .env.example .env

# Generate a strong API key — Evolution and the bot share it
openssl rand -hex 32  # paste into .env as EVOLUTION_API_KEY

# Edit config.json if you want to override defaults (node_id, etc.)
```

Crea `consent.json` con un objeto vacío para que el bot pueda escribir en él:

```bash
echo '{}' > consent.json
```

## 3. Inicia los contenedores

```bash
cd /volume1/docker/aq-reporter
docker compose up -d
docker compose logs -f evolution-api
```

En los logs de Evolution verás un código QR. **Abre WhatsApp en el
teléfono que estás usando para el bot → Settings → Linked Devices → Link a
Device → escanea el QR.**

Una vez vinculado:

```bash
docker compose logs -f aq-bot
```

Deberías ver `AQBot ready — node=bali.fab.city listening on :5055/webhook`.

## 4. Envía un mensaje de prueba

Desde cualquier cuenta de WhatsApp, envía un mensaje al número del bot:

> halo

El bot debería responder con el prompt de consentimiento (Bahasa + inglés). Responde
**SETUJU**. El bot debería confirmar. Luego envía:

> ada asap di pantai bingin

Debería responder pidiéndote tu ubicación. Envía una ubicación (clip →
Location → Send your current location). El bot debería responder que el
reporte está completo.

Revisa el NAS:

```bash
ls /volume1/docker/aq-reporter/data/reports/   # should have AQ_*.json
ls /volume1/docker/aq-reporter/data/profiles/  # should have matching profile
cat /volume1/docker/aq-reporter/data/profiles/AQ_*.json | jq .locality
# → "Bingin"
```

Si ves `Bingin` (o `Bukit` del fallback del bbox), el bot está conectado
de principio a fin en el lado del NAS.

## 5. Configura el M1 vision worker

En el M1 MacBook:

```bash
# Mount the NAS share
open smb://nas.local/aq-reporter
# (or use Finder → Go → Connect to Server → smb://nas.local)
# Mounts at /Volumes/aq-reporter

# Set up Python env
python3 -m venv ~/.venv/aq-vision
source ~/.venv/aq-vision/bin/activate
pip install mlx-vlm fastapi uvicorn pillow requests
```

Inicia el servidor MLX (esto dispara la descarga del modelo en la primera ejecución, ~2.5GB):

```bash
cd ~/fablab-bali/aq-reporter
python mlx_vision_server.py
```

En una segunda terminal, inicia el worker:

```bash
source ~/.venv/aq-vision/bin/activate
AQ_REPO=/Volumes/aq-reporter \
AQ_VISION_BACKEND=mlx \
AQ_VISION_ENDPOINT=http://localhost:8000/analyze \
AQ_NOTIFY_USERS=1 \
AQ_EVOLUTION_BASE=http://nas.local:8080 \
AQ_EVOLUTION_INSTANCE=bali-aq \
AQ_EVOLUTION_KEY=<same-key-as-NAS-env> \
  python m1_vision_worker.py
```

(Para que Evolution sea alcanzable desde el M1, necesitarás exponer el puerto
8080 en la LAN del NAS — consulta la sección comentada en `docker-compose.yml`.)

## 6. Prueba de foto de principio a fin

Envíale al bot una foto de cualquier contaminación (una escena con humo, un montón de basura,
polvo de construcción). Deberías ver:

- Logs del bot (NAS): `msg from +62... type=image` → foto guardada, encolada
- Logs del worker (M1): `analyzing AQ_... → burning / high (conf=0.85) in 6.3s`
- El bot responde en WhatsApp: "🔥 Hasil analisis / Analysis: kategori burning..."
- Un nuevo perfil en `data/profiles/` con `ai_analysis` lleno

## 7. Configura la sincronización de perfiles a planetai.fab.city

Edita `sync_profiles.sh` (o define las env vars en cron) para que apunte a donde
se sirve planetai.fab.city:

- Si planetai está alojado **en el mismo NAS** (Synology Web Station):
  `AQ_SYNC_TARGET=/volume1/web/planetai/bali/profiles/`
- Si planetai está alojado **en un VPS** con acceso SSH:
  `AQ_SYNC_TARGET=user@planetai.fab.city:/var/www/planetai/bali/profiles/`
  (configura primero las SSH keys para que el cron pueda correr sin supervisión)
- Si planetai está alojado en un **static host** (Netlify/Vercel/Cloudflare
  Pages): un flujo basado en git push puede ser más simple — apunta el script a un
  clon local del repo del sitio y haz push desde cron.

Pruébalo una vez:

```bash
DRY_RUN=1 ./sync_profiles.sh   # shows what it would do
./sync_profiles.sh             # actually sync
```

Luego registra el cron. En Synology: **Control Panel → Task Scheduler →
Create → Scheduled Task → User-defined script**:

```bash
/volume1/docker/aq-reporter/sync_profiles.sh >> /var/log/aq-sync.log 2>&1
```

Frecuencia: cada 5 minutos.

## 8. Envía el esquema a Murmurations

Una vez que los perfiles sean accesibles públicamente en
`https://planetai.fab.city/bali/profiles/AQ_*.json`, envía el esquema
primero al test index:

```bash
curl -X POST https://test-index.murmurations.network/v2/nodes \
  -H "Content-Type: application/json" \
  -d '{"profile_url": "https://planetai.fab.city/bali/profiles/<an-id>.json"}'
```

Cuando eso haga round-trip limpiamente, cambia `murmurations_auto_index: true` en
`config.json` y reinicia el bot. Los nuevos reportes se registrarán automáticamente con
el index.

## 9. Incorpora a tus primeros 5 usuarios

Elige a 5 personas de Bukit que conozcas bien — un líder de banjar, un par de
vecinos, alguien de la escuela. Guíalos en persona.
Observa qué preguntas hacen. Brechas comunes a esperar:

- Muchos no sabrán cómo compartir la ubicación → graba un tutorial en video de 30 segundos
- Las notas de voz llegarán de inmediato → programa el sprint de Whisper
- La gente enviará fotos sin contexto ("¡mira esto!") → la plantilla de respuesta
  del bot necesita dejar más claro que la ubicación es obligatoria

## Verificaciones operativas

```bash
# Bot health
curl http://nas.local:5055/health

# Vision server health (from M1)
curl http://localhost:8000/health

# Queue depth
ls /Volumes/aq-reporter/vision_queue/AQ_*.json 2>/dev/null | wc -l

# Today's report count
ls /Volumes/aq-reporter/reports/AQ_$(date +%Y%m%d)*.json | wc -l

# Last sync
tail -5 /var/log/aq-sync.log
```

## Solución de problemas

**Evolution API pierde la sesión de WhatsApp tras un reinicio.**
Los datos de sesión de Baileys viven en `data/evolution/`. Mientras ese volumen
persista entre reinicios de contenedor, la sesión también lo hace. Si
la sesión es invalidada por WhatsApp (p. ej. abriste WhatsApp Web
en otro lugar), tendrás que volver a emparejar — revisa los logs por un nuevo QR.

**Las respuestas del bot no llegan a los usuarios.**
Verifica que `AQ_EVOLUTION_KEY` coincida tanto en `.env` como en el env del bot. Verifica también
que `WEBHOOK_GLOBAL_URL` en Evolution apunte a `http://aq-bot:5055/webhook`
(el nombre de la container-network, no localhost).

**El M1 worker llena la cola con resultados `:error`.**
El backend de vision es inalcanzable. Verifica:
- `curl http://localhost:8000/health` desde el M1 → ¿el servidor MLX está arriba?
- ¿El `AQ_VISION_ENDPOINT` del worker coincide con el puerto real del servidor?
- ¿El worker puede alcanzar el NAS por SMB? `ls /Volumes/aq-reporter`

**La sincronización de perfiles falla con permission denied.**
El usuario que corre el cron necesita acceso de escritura a la ruta destino. En
Synology Web Station, el web root suele ser propiedad de `http:http`.
O bien corre la sincronización como ese usuario, o configura permisos de escritura de grupo.

## Próximos sprints (después del piloto)

- **Voice notes** — Whisper.cpp o MLX-Whisper en el M1, transcribir
  Bahasa, tratar la transcripción como un reporte de texto.
- **Integración con Smart Citizen** — obtener datos de sensores de un Smart Citizen
  Kit desplegado en Bukit, fusionar con reportes comunitarios.
- **Kit de replicación** — extraer las partes configurables a un repo
  plantilla que otros Fab Labs puedan clonar (objetivo: Yucatán, Kerala, Detroit).
- **Panel biorregional** — agregador que extrae de todos los nodos Planet AI
  Community mediante búsqueda en Murmurations.
- **Action loop** — definir e instrumentar la mitad de "action" de la
  hipótesis de latencia observación→acción. Elegir un canal de acción creíble
  (reporte mensual del banjar, amplificación de Fab City, programa de mascarillas).
