[English](SETUP.md) · [Bahasa Indonesia](SETUP.id.md) · **Español**

# Making Sense Bali — generador de sincronización de datos (mini)

Pre-cocina los datos del sitio para que los visitantes carguen al instante en vez de machacar
la API de Smart Citizen en vivo, y lleva los reportes ciudadanos aprobados desde el NAS hasta
el mapa público. Se ejecuta en el **mini** (salida real a internet + exo local).

Cada ejecución escribe en el repo y hace push:
- `data/sensors.json` — instantánea de los kits Smart Citizen conocidos (+ OpenAQ si hay una clave configurada)
- `data/reports/` + `index.json` — perfiles Murmurations aprobados extraídos del NAS
- `data/areas.json` — resumen por barrio (conteos, categorías, tags principales, severidad máxima, PM2.5 cercano) + una narrativa exo opcional de 2 frases

Es **a prueba de fallos**: cada etapa está aislada; un fallo nunca bloquea a las demás, y la ejecución nunca tira abajo la programación.

## Configuración inicial (en el mini)

1. **Clona el repo** en algún lugar estable:
   ```
   git clone git@github.com:mdg-bali/makingsensebali.git ~/makingsensebali
   ```

2. **GitHub deploy key (acceso de push)** — para que el mini pueda hacer push:
   ```
   ssh-keygen -t ed25519 -f ~/.ssh/msb_deploy -N ""
   ```
   Añade `~/.ssh/msb_deploy.pub` al repo en GitHub → **Settings → Deploy keys → Add → Allow write access**.
   Apunta git hacia ella (en `~/.ssh/config`):
   ```
   Host github.com
     IdentityFile ~/.ssh/msb_deploy
     IdentitiesOnly yes
   ```

3. **Clave SSH del mini → NAS (para la extracción de reportes)** — para que `rsync` funcione sin contraseña:
   ```
   ssh-copy-id fablabbali@tx-nas-bali     # or append the mini's pubkey to the NAS authorized_keys
   rsync -az --include='AQ_*.json' --exclude='*' \
     fablabbali@tx-nas-bali:/volume1/docker/aq-reporter/data/profiles/ ~/tmp_test/   # verify it pulls
   ```
   (Confirma la ruta de perfiles del NAS; en este despliegue es `/volume1/docker/aq-reporter/data/profiles/`.)

4. **Edita el plist** `com.fabcity.makingsense-sync.plist` — corrige `MSB_REPO_DIR`, `MSB_NAS_RSYNC_SRC`, `MSB_NAS_PHOTOS_SRC` (las fotos públicas sin EXIF, para que el mapa pueda mostrarlas), la ruta de python y las rutas de log para que coincidan con el mini. Pon `MSB_NARRATIVE` en `0` para enviar solo resúmenes estructurados (sin párrafo exo).

   **Redes externas de calidad del aire (así es como superas los cuatro kits).** Cada una es de mejor esfuerzo (best-effort): un fallo se registra y se omite, nunca bloquea a las demás. **Los secretos viven en un `.env` con gitignore junto a `generate.py` (NO en el plist versionado — es un repo público).** Copia las claves allí; `generate.py` lo carga al arrancar y sobrevive a los re-despliegues del plist:

   ```
   # tools/makingsense-sync/.env   (gitignored)
   MSB_AQICN_TOKEN=...
   MSB_AQICN_STATIONS=-519205
   MSB_PURPLEAIR_KEY=...
   MSB_PURPLEAIR_IDS=36601,46949
   ```

   - **AirGradient** — activado por **defecto, sin clave**. Extrae el feed público de datos abiertos de AirGradient y conserva las ubicaciones de Bali — estos son los sensores de la **Nafas Foundation** (Tonja, Pemogan, …). `pm02` es una lectura real en µg/m³. Pon `MSB_AIRGRADIENT=0` para desactivarlo.
   - `MSB_AQICN_TOKEN` — **la referencia de mayor valor.** Token gratuito en <https://aqicn.org/data-platform/token/> (solo correo). Aporta el **monitor gubernamental oficial de KLHK** (las estaciones WAQI de Bali no están listadas, así que el UID conocido también se fija mediante `MSB_AQICN_STATIONS`). WAQI reporta el PM2.5 como un subíndice US-AQI, así que el generador lo convierte de vuelta a µg/m³ (puntos de corte de la EPA anteriores a 2024) y conserva el AQI bruto en `reading.aqi` con una bandera `pm25_from_aqi: true`. Comprueba la coherencia de la primera ejecución contra la página de la estación en aqicn.org.
   - `MSB_PURPLEAIR_KEY` — clave de lectura gratuita en <https://develop.purpleair.com/>. `MSB_PURPLEAIR_IDS` por defecto es `36601,46949` (Jimbaran + Klungkung Lumi Clinic); añade más índices a medida que aparezcan en el mapa de PurpleAir.
   - `MSB_OPENAQ_KEY` — dejada en su sitio pero **no esperes nada**: las dos únicas estaciones de OpenAQ en Bali (Ubud, Balangan) llevan offline desde 2025. Conservada para el día en que reaparezca una en vivo.
   - No añadidas (sin una vía limpia/soberana): los sensores de villas privadas de **IQAir** (cargador de página versionado por build, se rompe en cada despliegue) y las estaciones de **Nafas** que no están en el feed público de AirGradient (el tiempo real está tras la autenticación de la app). Usa AirGradient para Nafas; revisa IQAir solo si exponen una API real.

5. **Dry run** (todo excepto el push):
   ```
   MSB_REPO_DIR=~/makingsensebali python3 ~/makingsensebali/tools/makingsense-sync/generate.py --dry-run
   ```
   Comprueba que `data/sensors.json`, `data/areas.json` y `data/reports/index.json` se ven bien, y que los resúmenes de `areas.json` se leen bien (si no, pon `MSB_NARRATIVE=0`).

6. **Instala la programación** (cada 15 min):
   ```
   cp ~/makingsensebali/tools/makingsense-sync/com.fabcity.makingsense-sync.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.fabcity.makingsense-sync.plist
   ```

7. **Verifica**: `tail -f ~/makingsensebali/tools/makingsense-sync/sync.log` y confirma que un commit aterriza en GitHub.

## Notas
- La deploy key está limitada a este único repo (solo push). No hay secretos en el repo.
- La cadencia es `StartInterval` (900s = 15 min). Los sensores no cambian rápido; los reportes aparecen dentro de un ciclo desde su aprobación.
- Si el mini está dormido, el ciclo se omite y se reanuda al despertar — aceptable para un sitio de campaña, pero es la razón por la que esto vive en el mini, no en el NAS siempre encendido (que está tras firewall respecto a GitHub + la API de SC).
- **Fase 2 (lado del sitio, cambio aparte):** `data.js` debe cargar `data/sensors.json` primero (instantáneo) antes de cualquier refresco en vivo, y el home/dashboard debe renderizar `data/areas.json`. Hasta entonces el generador produce los archivos pero el sitio sigue obteniendo los sensores en vivo.
