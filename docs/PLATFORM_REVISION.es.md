[English](PLATFORM_REVISION.md) · [Bahasa Indonesia](PLATFORM_REVISION.id.md) · **Español**

# Making Sense Bali · Informe de revisión de la plataforma (v2)

**Estado:** informe — sin empezar.
**Responsable de la ejecución:** Claude Code (o una persona desarrolladora trabajando en el código). Este documento es el traspaso; todo lo que Claude Code necesita para hacer el trabajo debería poder deducirse de aquí más el repo.
**Responsable de la intención:** Tomas Diez (líder de Making Sense Bali). Lee [README.md](../README.md) primero si no conoces la campaña.
**Última actualización:** 2026-05-30.

---

## 1. Por qué esta revisión

El panel actual en `mdg-bali.github.io/makingsensebali/dashboard/` funciona como una vista *instantánea*: un mapa de sensores con sus últimas lecturas, una lista de reportes ciudadanos representados como tarjetas, unos cuantos paneles de referencia. Demuestra que la campaña existe. Todavía no ayuda a nadie a *interpretar* qué está pasando a nivel ambiental en Bali.

El cambio que aporta esta revisión: de "cuál es la lectura actual de PM2.5 en este pin" a "**qué cambió en este barrio durante el último día, y está conectado con lo que la gente está reportando?**" Esa pregunta es la que convierte un panel en una herramienta que un coordinador de banjar, un analista del Dinas Kesehatan o un padre o madre preocupado por el asma de su hijo puede usar de verdad.

Tres capacidades concretas hacen posible ese cambio:

1. **Gráficos de series temporales** por métrica de sensor, en dos ventanas: las últimas 24 horas y los últimos 7 días. Los valores actuales estáticos son insuficientes para cualquier decisión ambiental.
2. **Detección de picos/anomalías** que aflora los momentos que vale la pena investigar, en lugar de pedirle a una persona que mire los gráficos con la vista para encontrarlos.
3. **Correlación bidireccional entre los picos de los sensores y los reportes ciudadanos.** Cuando ocurre un pico de PM al mismo tiempo que alguien reporta quema de basura a dos calles, el panel debería conectar esos dos hechos. Cuando ocurre un pico sin reporte, el panel debería sugerir "esto parece algo — ¿alguien quiere reportar lo que está viendo?"

En conjunto, estas capacidades transforman el panel de una pantalla pasiva en el instrumento participativo que la metodología Making Sense de la campaña realmente requiere.

Junto a ellas, el componente de reportes necesita un rediseño de UI — la cuadrícula de tarjetas actual es demasiado pesada para lo que es, conceptualmente, un feed de observaciones de residentes. Conviértelo en un feed, expandible al hacer clic.

## 2. Estado actual — qué existe hoy

| Superficie | Archivo(s) | Notas |
|---|---|---|
| Página de aterrizaje | [`index.html`](../index.html) (1234 líneas) | Encuadre metodológico, enlace a la encuesta, contexto del proyecto. Mayormente bien; fuera del alcance de esta revisión salvo que las series temporales/picos necesiten un widget de resumen aquí. |
| Panel | [`dashboard/index.html`](../dashboard/index.html) (779 líneas) | Mapa + statusbar + panel de selección + feed de reportes + sensores clasificados + estándares de referencia + implicaciones de salud. El grueso de esta revisión. |
| Capa de datos de sensores | [`data.js`](../data.js) (609 líneas) | Obtiene de Smart Citizen (`fetchSmartCitizenSensors`, `fetchSmartCitizenDetail`), OpenAQ (`fetchOpenAQSensors`), PurpleAir, Sensor.Community. También obtiene reportes ciudadanos desde JSON estático en `data/reports/`. |
| CF Worker (proxy CORS) | [`worker/openaq-proxy.js`](../worker/openaq-proxy.js) (172 líneas) | Proxy de OpenAQ. Patrón a seguir si alguna otra fuente necesita sortear CORS. |
| Componente de reportes | [`reports/`](../reports/) (~36KB de docs + código Python) | Bot de WhatsApp + panel del operador. **Fuera del alcance** de esta revisión — el front-end consume los reportes como JSON estático, no se necesitan cambios de API. |
| Datos estáticos de reportes | `data/reports/*.json` | Reportes ciudadanos aprobados como archivos JSON individuales más un manifiesto `index.json`. Esto es lo que lee `fetchReports()` en data.js. |

Cableado existente que conviene conocer:

- **Chart.js 4.4.0 ya está cargado** en `dashboard/index.html` (línea 16). Actualmente sin usar. No se necesita ninguna dependencia de gráficos nueva.
- **Leaflet + leaflet-heat** está cargado para el mapa. El mapa renderiza tanto los pines de sensores como un mapa de calor de densidad de reportes.
- **`state.reports`** contiene la lista de reportes actual en el JS del panel (poblada por `fetchReports()` en data.js).
- **`state.sensors`** contiene los sensores (las lecturas de BME680/HM3301 llegan vía la API de SC como un dispositivo con múltiples tipos de sensor).
- **El recuadro delimitador de Bali** está configurado en `BALI_BOUNDS` / `BALI_CENTER` en data.js — la paginación del mapa mundial filtra por esto.
- **Los IDs de sensores de Smart Citizen** que usa la campaña hoy están documentados en [`hardware/diy-node/firmware/diy_node/diy_node.ino`](../hardware/diy-node/firmware/diy_node/diy_node.ino) (174 = BMP280 Temp, 56 = SHT31 RH, 175 = BMP280 Pressure, 87/88/89 = PMS5003 PM2.5/10/1). El endpoint `/v0/sensors` de SC es la fuente autoritativa para nuevos IDs a medida que otros kits entren en línea.

El renderizado de reportes existente (`renderReportFeed()` en `dashboard/index.html` línea 501) ya itera `state.reports` hacia un feed HTML — así que el andamiaje está ahí, las tarjetas solo necesitan un rediseño.

## 3. Estado objetivo — qué construir

### 3.1 Gráficos de series temporales (por métrica, por dispositivo)

Para cada sensor mostrado en el panel "Selected" del mapa, el panel debería mostrar:

- Gráfico de las **últimas 24 horas** — alta resolución temporal (cada lectura)
- Gráfico de los **últimos 7 días** — submuestreado (bins por hora o cada 4 horas, según la densidad)

Los gráficos deben ser por métrica (Temperatura, Humedad, Presión, PM1, PM2.5, PM10, resistencia de gas cuando esté disponible). Renderiza con Chart.js (ya cargado).

**Superficie de API para datos históricos:**

El `/v0/devices/{id}/readings` de Smart Citizen acepta:
- `sensor_id` — requerido, el ID global del sensor
- `from` — marca de tiempo ISO 8601 (inicio de la ventana)
- `to` — marca de tiempo ISO 8601 (fin de la ventana)
- `rollup` — agrupamiento opcional (p. ej., `5m`, `1h`)

Un helper de obtención de histórico pertenece a `data.js`:

```js
async function fetchSmartCitizenHistory(deviceId, sensorId, fromIso, toIso, rollup = null) {
  // Returns [{ recorded_at: ISO, value: number }, ...]
}
```

Para las fuentes OpenAQ y Sensor.Community, existen endpoints de histórico pero tienen formas distintas. Trata el histórico de OpenAQ como Fase 2 — para el lanzamiento de v2, las series temporales solo se requieren para los dispositivos SC (que incluyen los nodos DIY). Las demás fuentes pueden mostrar solo valores actuales.

**Cacheo:** usa `localStorage` para cachear las obtenciones históricas con un TTL de 5 minutos. Volver a obtener 7 días de histórico en cada carga de página es un derroche y consume cuota contra la API de SC.

**Aceptación requerida:** abrir el panel "Selected" del mapa para un dispositivo Smart Citizen muestra dos tiras de gráfico (24h, 7d) para cada uno de sus sensores conectados. Estado de carga visible mientras se obtiene. Estado vacío con un mensaje sensato si aún no existe ningún dato histórico (dispositivo nuevo).

### 3.2 Detección de picos / anomalías

Para cada serie temporal mostrada, aflora los puntos que son anómalos estadística o semánticamente.

**Dos métodos de detección complementarios, ambos por métrica:**

1. **Basado en umbrales** (semántico) — usa los valores de referencia publicados que ya están documentados en el panel de estándares de referencia del panel:
   - PM2.5: directriz diaria de la OMS 5 µg/m³, US AQI "moderate" 12, "unhealthy for sensitive groups" 35
   - PM10: directriz diaria de la OMS 45 µg/m³, US AQI moderate 55
   - Temperatura: confort en interiores 24–28°C, preocupación por estrés térmico >32°C
   - Humedad: umbral de riesgo de moho >60% RH sostenido
   - Resistencia de gas: solo relativa — sin umbral absoluto, usa el método del z-score
   
   Documenta estos umbrales en una sola tabla `THRESHOLDS` en data.js (o un nuevo módulo `peaks.js`) para que los valores canónicos vivan en un único lugar.

2. **Estadístico** (relativo a la anomalía) — para cada métrica, calcula una línea base móvil de 7 días (media + desviación estándar) para el dispositivo. Marca cualquier lectura más de 2σ por encima (o por debajo, para cosas como la resistencia de gas donde más bajo = peor) como un pico. Recalcula la línea base una vez por carga de página.

Para v1, **el basado en umbrales gana donde está definido** (PM, T, RH). El estadístico cubre la resistencia de gas y cualquier métrica futura sin umbral absoluto.

**Tratamiento visual en el gráfico:**

- Los puntos pico se marcan con un símbolo distinto (p. ej., un anillo rojo)
- Pasa el cursor/toca el pico para ver: marca de tiempo, valor, qué umbral o límite σ se cruzó
- El recuento agregado de "picos en las últimas 24h" / "picos en los últimos 7d" aflorado en el statusbar de arriba

**Aceptación requerida:** si el PM2.5 se disparó a 80 µg/m³ a las 2 de la tarde de ayer en el nodo DIY de la oficina, ese punto está claramente marcado en rojo en el gráfico de 24h, y el statusbar muestra "Active peaks (24h): 1" con clic de acceso a una vista de lista.

### 3.3 Reportes — rediseño del feed

Estado actual: cada reporte se renderiza como una tarjeta con una miniatura, una insignia de categoría, la localidad, una vista previa de la descripción y una marca de tiempo. Ocupan mucho espacio vertical y el panel se siente pesado.

Objetivo: **feed compacto de entradas de una línea, expandibles al hacer clic.** Inspiración: la línea de tiempo de Twitter / Mastodon. Cada fila muestra:

- Marca de tiempo (relativa — "12m ago", "3h ago", "yesterday")
- Insignia de categoría (chip de color)
- Localidad
- Los primeros ~80 caracteres de la descripción

Hacer clic/tocar expande al detalle completo en línea (foto, descripción completa, análisis de IA, sincronización del pin del mapa). Se contrae con un segundo clic.

**Comportamiento:**

- Carga diferida (lazy-load) de la foto solo cuando la fila está expandida
- Ordenar por `submittedAt` desc (ya es el caso)
- Scroll infinito o "Load more" si hay >50 reportes
- Chips de filtro en la parte superior: categoría, gravedad, últimas 24h / últimos 7d / todo el tiempo

La función `renderReportFeed()` en `dashboard/index.html` (línea 501) es el único sitio de renderizado. Reelabora ahí.

**Aceptación requerida:** el feed cabe 20+ reportes en el mismo espacio vertical que 5 tarjetas hoy. Tocar una fila la expande en línea en ~150ms y desplaza el mapa hacia esa ubicación (comportamiento actual).

### 3.4 Correlación bidireccional entre picos y reportes

La capacidad estratégicamente más valiosa de la revisión.

**Dirección A — pico → reporte:** cuando un gráfico muestra un pico, obtén cualquier reporte dentro de:
- **Ventana de tiempo:** ±2 horas de la marca de tiempo del pico
- **Radio geográfico:** 1km de la ubicación del sensor

Muestra los reportes coincidentes como chips pequeños debajo del gráfico: "2 nearby reports — [burning waste · 230m away · 35 min before peak] [smoke · 480m · 1h after]". Haz clic en un chip para saltar a ese reporte en el feed.

Si no existen reportes coincidentes, aflora un aviso de acción: **"This spike has no citizen report attached. If you're nearby right now, [report what you're seeing →]"** con un enlace a la encuesta o al bot de WhatsApp.

**Dirección B — reporte → sensor:** cuando un reporte se expande en el feed, obtén las lecturas de sensores dentro de:
- **Ventana de tiempo:** ±1 hora de la marca de tiempo de envío del reporte
- **Radio geográfico:** 1km

Muestra los sensores coincidentes como chips pequeños dentro del reporte expandido: "Nearby sensors: [DIY Node Office — PM2.5 16 µg/m³ at submission time] [OpenAQ Denpasar — PM2.5 22 µg/m³]". Haz clic para abrir la vista de histórico del sensor.

Si un sensor muestra un pico en torno a la misma marca de tiempo, aflóralo con fuerza: "**Sensor data corroborates this report** — PM2.5 spiked to 80 µg/m³ at the DIY Node 350m away, 12 minutes before this report was filed."

**Aceptación requerida:** cuando ocurre un evento conocido (p. ej., alguien quema basura cerca del nodo de la oficina), el pico en el gráfico enlaza con el reporte del residente sobre el humo, y viceversa. Prueba esto con un reporte sintético vinculado a un pico real en los datos existentes antes de darlo por hecho.

### 3.5 UX bilingüe

Las cadenas en el panel deberían pasar por una capa de traducción (una función simple `t(key)` respaldada por un diccionario JSON). Conmutador de idioma en el statusbar. Por defecto: inglés. Añade como mínimo traducciones al **bahasa indonesio** para las cadenas de cara al público (títulos de gráficos, alertas de picos, avisos de acción, insignias de categoría, etiquetas del statusbar).

No traduzcas las etiquetas técnicas (nombres de modelo de sensor, "PM2.5", "kPa", "µg/m³" — esas se quedan en inglés sin importar la configuración regional).

Esto es un "estaría bien tenerlo" en v1, no un bloqueante. Si el tiempo aprieta, monta el andamiaje de la infraestructura `t(key)` con cadenas solo en inglés y documenta el archivo de diccionario para que quienes traduzcan lo rellenen más adelante.

## 4. Fases sugeridas

**Fase 1 — Infraestructura de series temporales.** ~1 semana.
- Helper `fetchSmartCitizenHistory` en data.js
- Capa de cacheo con `localStorage`
- Renderizado de gráficos en el panel Selected (24h + 7d por métrica)
- Estados de carga y vacío

**Fase 2 — Detección de picos.** ~3 días.
- Tabla `THRESHOLDS` + cálculo de la línea base estadística
- Marcado visual en los gráficos
- Contador de picos en el statusbar

**Fase 3 — Rediseño del feed de reportes.** ~2 días.
- Diseño de fila compacta
- Interacción de expandir en el lugar
- Chips de filtro

**Fase 4 — Motor de correlación.** ~1 semana.
- Búsqueda de cercanía pico → reporte
- Búsqueda de cercanía reporte → sensor
- Aviso "Report this peak"
- Afloramiento de "Sensor data corroborates"

**Fase 5 — Pulido + bilingüe.** ~3 días.
- Capa de traducción `t()`
- Cadenas en bahasa indonesio
- Pasada de QA móvil

Total: ~3 semanas de trabajo enfocado. Las fases 1 y 2 pueden lanzarse de forma independiente y son los puntos de partida de mayor apalancamiento.

## 5. Criterios de aceptación — la lista de verificación de "hecho"

La revisión está terminada cuando, en el panel en vivo:

- [ ] Hacer clic en cualquier dispositivo Smart Citizen del mapa muestra gráficos de series temporales (24h + 7d) para todos sus sensores conectados
- [ ] Al menos un pico de PM2.5 está visiblemente resaltado en un gráfico con el umbral de la OMS señalado en el estado de hover
- [ ] La sección de reportes es un feed escaneable donde 20+ reportes caben en una pantalla
- [ ] Un reporte expandido muestra los sensores cercanos y sus lecturas en el momento del envío
- [ ] Un gráfico con un pico muestra los reportes cercanos (si los hay) o un aviso de acción para reportar (si no los hay)
- [ ] El statusbar muestra los recuentos de "Active peaks · 24h" y "Active peaks · 7d"
- [ ] En móvil (375px de ancho), el panel sigue siendo usable — gráficos desplazables horizontalmente si hace falta, sin scroll horizontal de página
- [ ] El sitio sigue cargando en <3 segundos en una conexión 3G simulada (actualmente pasa; no introduzcas regresión)
- [ ] Ninguna dependencia nueva más allá de lo ya cargado (Chart.js, Leaflet, leaflet-heat); no añadas nada sin justificación

## 6. No objetivos — qué NO hacer en esta revisión

- **No introduzcas un framework.** Nada de React, Vue, Svelte, Next, Astro. La arquitectura de HTML-estático-con-vanilla-JS es intencional — la campaña es replicable a otros capítulos de Fab City vía un `git clone`, sin paso de build. Conserva esa propiedad.
- **No añadas un backend.** Cloudflare Workers solo para proxy CORS. Sin servidor Node.js, sin servidor de base de datos del lado del servidor. Todo el procesamiento ocurre en el navegador o en la plataforma SC.
- **No modifiques el componente de reportes (Python/Flask).** Esta revisión es solo front-end. El componente de reportes (bot de WhatsApp + panel del operador) es un código aparte que solo produce JSON que el panel consume. Relación de solo lectura.
- **No reescribas código que funciona por razones de estilo.** El código actual es funcional y legible. Refactoriza solo cuando añadir una nueva capacidad lo requiera.
- **No pierdas el encuadre metodológico.** El README y el hero del panel posicionan explícitamente esto como un descendiente de *Making Sense* — un instrumento participativo, no solo un visor de datos. No le quites esa voz.
- **No añadas login, autenticación ni estado por usuario.** El panel es de lectura pública para todos. Las funciones de operador se quedan en el componente de reportes.

## 7. Dependencias e incógnitas

- **Límites de tasa de `/v0/devices/{id}/readings` de Smart Citizen** — sin documentar. Prueba con una carga realista (10 dispositivos × 7 días × 6 sensores = 420 consultas de histórico en la primera carga de página es demasiado). La caché de localStorage debe estar en su lugar antes de salir en vivo para evitar alcanzar los límites y ser bloqueado.
- **Sintaxis del parámetro `rollup` de Smart Citizen** — verifica contra la documentación en https://developer.smartcitizen.me. Si no es lo que asume este informe, ajústalo.
- **Estabilidad de la API de reportes** — el patrón de JSON estático (`data/reports/index.json` + archivos por reporte) es lo que consume `fetchReports()`. Esto lo posee el componente de reportes; coordina con quien lo mantiene antes de depender de campos nuevos.
- **Aún no hay entrada de catálogo para el BME680** — la plataforma SC no tiene una entrada para el Bosch BME680. Actualmente publicamos a los IDs de BMP280/SHT31/PMS5003 (ver [hardware/diy-node/README.md](../hardware/diy-node/README.md)). Oscar (equipo de SC) puede añadir entradas BME680 adecuadas del lado del servidor en algún momento. En cualquier caso el panel lee los IDs de sensor que tenga conectado el dispositivo — no se requiere ningún acoplamiento codificado de forma fija.
- **Aún no hay un conjunto de blueprints de kit para los dispositivos DIY** — afecta la detectabilidad del endpoint del mapa mundial de SC. La lista de seguridad `KNOWN_BALI_SCK_IDS` del panel (línea 42 de data.js) es la solución temporal. Cuando se desplieguen nodos DIY nuevos, añade sus IDs ahí hasta que Oscar adjunte los blueprints.

## 8. Cómo empezar

1. Crea una rama de trabajo: `git checkout -b dashboard-v2`
2. Lee [`dashboard/index.html`](../dashboard/index.html) y [`data.js`](../data.js) de principio a fin. No son grandes; una hora para interiorizar la estructura actual rinde frutos a lo largo de toda la revisión.
3. Echa un vistazo al renderizado de reportes existente (`renderReportFeed()` línea 501 en `dashboard/index.html`) — ese es el código que más se toca en esta revisión.
4. Empieza con la Fase 1 (series temporales). Consigue que un gráfico se renderice para el nodo DIY de la oficina (dispositivo 19651) antes de generalizar.
5. PR a `main`. GitHub Pages recoge los cambios automáticamente.

## 9. Cuando esto esté hecho

Actualiza este informe con un encabezado "Status: complete" y un resumen de un párrafo de lo que se concretó. Si algo en este informe resultó estar mal (una API no se comportó como se esperaba, un no objetivo necesitó replantearse), documéntalo aquí para que quien haga la siguiente revisión aprenda de ello. El `REPLICATION.md` de la campaña hará referencia al panel v2 como la versión que otros capítulos de Fab City bifurcan — la exactitud importa.

## 10. Contacto

- Líder de la campaña: Tomas Diez · `tomas@fab.city`
- Responsable del componente de reportes: equipo de Fab Lab Bali · `fablabbali@gmail.com`
- Contacto de la plataforma Smart Citizen: Oscar (equipo de la plataforma SC)

---

**Apéndice — referencia rápida de los IDs de sensores en uso actualmente (despliegue en Bali)**

| ID de dispositivo | Tipo | Notas |
|---|---|---|
| 19236 | SCK 2.1 | Nodo de casa — primer despliegue de la campaña |
| 19600 | SCK 2.1 | Nodo de oficina — segundo despliegue de la campaña |
| 19618 | SCK 2.1 | Añadido anterior; consulta el README para el contexto |
| **19651** | **DIY Plus (XIAO + BME680 + HM3301)** | **Primer nodo construido en un taller DIY — oficina de Tomas, mayo de 2026** |

Los futuros nodos de talleres DIY aparecerán aquí a medida que se desplieguen. El patrón es el mismo: registrar vía `hardware/diy-node/tools/register_device.py`, añadir el ID a `KNOWN_BALI_SCK_IDS` en data.js, flashear el firmware con los IDs de sensor de `hardware/diy-node/tools/find_sensor_ids.py`.
