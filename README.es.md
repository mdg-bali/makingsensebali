[English](README.md) · [Bahasa Indonesia](README.id.md) · **Español**

# Making Sense Bali

**Una campaña de sensado ambiental liderada por la comunidad para Bali, anclada en Fab Lab Bali, dentro del capítulo Fab City Bali.**

Making Sense Bali combina sensores ambientales de hardware abierto, datos públicos de redes regionales y globales, y reportes de residentes sobre problemas ambientales observados localmente — quema de basura, eventos de calidad del aire, fugas de agua, escombros de construcción, ruido, los asuntos que preocupan a quienes realmente viven aquí. El trabajo se hace en Indonesia, por gente de Indonesia, sobre preocupaciones identificadas por gente de Indonesia.

La campaña está alojada y rinde cuentas a **[Fab Lab Bali](https://fablabbali.com)**, el laboratorio de fabricación local en Denpasar, como parte del capítulo **Fab City Bali** de la red global [Fab City](https://fab.city/). Metodológicamente, el trabajo desciende del proyecto **[Making Sense](https://making-sense.eu/)** (EU Horizon 2020, Fab Lab Barcelona / IAAC y socios, 2015–2017) y usa la plataforma **[Smart Citizen Kit](https://smartcitizen.me/)**, cofundada por Tomas Diez y Alex Posada en Fab Lab Barcelona / IAAC en 2012. Making Sense Bali está liderada por Tomas Diez — cofundador de Smart Citizen, ahora residente en Bali — y funciona como una instancia biorregional independiente, en estrecha relación con los proyectos originales.

En vivo: **[mdg-bali.github.io/makingsensebali](https://mdg-bali.github.io/makingsensebali/)**

---

## Cómo se ve Making Sense Bali

Tres superficies, una campaña:

1. **El sitio público** en `mdg-bali.github.io/makingsensebali/` — el hogar de la campaña: metodología, estado, el panel en vivo, la encuesta de asuntos de interés, los reportes de los residentes, la atribución a la red más amplia.

2. **El panel en vivo** en `/dashboard/` — lecturas de sensores ambientales en tiempo real, agregadas desde múltiples redes abiertas: despliegues de Smart Citizen Kit operados por la campaña, estaciones OpenAQ en Bali, dispositivos Sensor.Community, PurpleAir (cuando está configurado). PM2.5, PM10, temperatura, humedad, ruido. Cada chincheta muestra la fuente, la última lectura y enlaces a la plataforma original.

3. **La capa de reportes** — los residentes envían observaciones ambientales a un bot de WhatsApp ("Making Sense Bali" en el despliegue de Bali). Cada reporte es revisado por el operador local antes de su publicación. Los reportes aprobados aparecen en el sitio público como datos de origen comunitario junto a las lecturas de los sensores. Los números de teléfono nunca se almacenan.

---

## La metodología

Making Sense Bali sigue un enfoque por fases derivado de Making Sense, adaptado para Bali:

**Fase 1 — Asuntos de interés.** Una encuesta, alojada actualmente en Airtable, pregunta a los residentes qué problemas ambientales afectan su vida diaria. El resultado no es una lista jerarquizada de "problemas a resolver" — es un mapa de atención. ¿Dónde nota la gente la quema de basura? ¿Dónde es insoportable el ruido? ¿Dónde sabe mal el agua? La encuesta establece que la campaña responde a preocupaciones definidas por la comunidad, no impone una agenda externa.

**Fase 2 — Sensado y reporte.** Dos canales corren en paralelo. Los sensores de hardware abierto (Smart Citizen Kits) se despliegan en ubicaciones estratégicas — actualmente un nodo casa y un nodo oficina operados por la campaña, con capacidad para expandirse a escuelas y sitios comunitarios. En paralelo, el bot de reportes recoge observaciones cualitativas de los residentes: fotos, ubicaciones, descripciones de problemas que los sensores no pueden ver. El conjunto de datos combinado se publica de forma abierta.

**Fase 3 — Respuesta y aprendizaje.** Es la fase hacia la que se está construyendo la red. Los datos agregados y los patrones de reportes informan la acción local — desde la conciencia individual (tu casa está en un corredor de humo) hasta la organización comunitaria (esta quema de basura es un evento recurrente con una fuente conocida) y la incidencia política (el gobierno regional tiene datos sobre los que puede actuar). El aprendizaje federado entre biorregiones es el horizonte de más largo plazo.

---

## Componentes

Making Sense Bali se ensambla a partir de estas piezas. Cada una tiene su propio alcance y su propia historia de despliegue:

| Componente | Qué hace | Dónde reside |
|---|---|---|
| **Sitio de la campaña** | Página de inicio pública, metodología, panel de sensores, reportes, atribución | Este repo · GitHub Pages |
| **Capa de datos de sensores** | Agrega Smart Citizen Kit + OpenAQ + Sensor.Community vía Cloudflare Workers | Este repo · [`data.js`](data.js), [`worker/`](worker/) |
| **Smart Citizen Kits** | Sensores de hardware abierto de calidad del aire + ruido + clima desplegados en Bali | [smartcitizen.me](https://smartcitizen.me/) — nodo casa 19236, nodo oficina 19600 |
| **Nodos DIY de taller** | Sensores construidos en taller en dos niveles — Basic (XIAO + BME680, ~USD 15–25, calidad del aire interior + clima + VOC) y Plus (Basic + HM3301, ~USD 35–60, añade PM exterior). La capa asequible de densidad espacial para banjars, escuelas, warungs. | [`hardware/diy-node/`](hardware/diy-node/) |
| **Encuesta de asuntos de interés** | Aporte comunitario de la Fase 1 sobre preocupaciones ambientales | Airtable (backend propietario, formulario de cara al público) |
| **Componente de reportes** | Bot de WhatsApp + panel del operador para reportes ciudadanos | [`reports/`](reports/) — toolkit Sense Making |
| **Identidad Murmurations** | Perfil de organización federado, descubrible en las redes de datos comunitarios | [`murmurations.json`](murmurations.json) en este repo |

---

## Hardware — con qué sensamos

La campaña no está atada a un único modelo de sensor. Es una red de varios niveles con instrumentos de referencia, Smart Citizen Kits listos para usar y nodos DIY construidos en taller que alimentan el mismo panel con los indicadores de fidelidad apropiados. Cada nivel inferior se calibra contra el de arriba; las correcciones viven en la capa de procesamiento del panel, no en el firmware.

| Nivel | Hardware | Costo | Rol |
|---|---|---|---|
| **0 — Referencia** | BAM-1020, Aeroqual AQM 65, o estación alojada de BMKG / Udayana | USD 5.000–25.000+ | Verdad de terreno (ground truth). Grado regulatorio. Ancla de calibración para todo lo de abajo. Se persigue mediante una alianza con **BMKG Stasiun Klimatologi Bali** (Sanglah) o la **Universidad Udayana**. |
| **1 — Smart Citizen Kit 2.3** | SCK oficial de [smartcitizen.me](https://smartcitizen.me/store) | ~USD 150 | Columna vertebral multiparamétrica confiable — PM, eCO₂, ruido, clima, luz. Firmware probado a fondo. Los nodos actualmente desplegados por la campaña (casa 19236, oficina 19600). |
| **2 — DIY Plus** | XIAO ESP32-S3 + BME680 + HM3301 | ~USD 35–60 | Densidad espacial en exteriores. PM + clima + gas/VOC. Construible en taller en Fab Lab Bali. |
| **3 — DIY Basic** | XIAO ESP32-S3 + BME680 | ~USD 15–25 | Máximo alcance — calidad del aire interior, moho/dengue/calor/VOC. El kit más accesible. |

Por el mismo dinero que 10 SCK oficiales, la campaña puede desplegar ~75–100 nodos mezclando niveles — aportando tanto la credibilidad de referencia (Nivel 0/1) como la resolución espacial que permite a un panel decir *qué barrio* quema basura los miércoles por la noche, y no solo "el sur de Bali tuvo PM elevado".

La documentación completa del hardware — BOMs, esquemas, firmware, la cadena de calibración y los casos de uso específicos de Bali (hábitat del mosquito del dengue, moho y salud respiratoria, estrés térmico, exposición a VOC en interiores, contaminación del aire exterior, triangulación de eventos de combustión) — está en [`hardware/diy-node/README.md`](hardware/diy-node/).

---

## Linaje y gobernanza

Making Sense Bali se inscribe en un linaje específico. Importa porque define quién rinde cuentas, qué supuestos carga la campaña y con qué red se federa.

- **2012–presente** — Smart Citizen, cofundada por **Tomas Diez** y **Alex Posada** en Fab Lab Barcelona / IAAC. La plataforma de sensores de hardware abierto que usa esta campaña.
- **2015–2017** — Making Sense (EU Horizon 2020), Fab Lab Barcelona / IAAC y socios (Waag, JKU Linz, University of Dundee). El marco participativo que aplicamos.
- **2026–presente** — Making Sense Bali. Liderada por Tomas Diez (cofundador de Smart Citizen, ahora residente en Bali), con Fab Lab Bali como anfitrión institucional y Fab City Bali como contexto de capítulo.

La plataforma original Smart Citizen y Fab Lab Barcelona son administradas hoy por otros equipos; Making Sense Bali es independiente pero coordinada, no un satélite ni una franquicia. Ambos proyectos continúan, en distintas biorregiones, bajo distintos equipos, con una metodología que se solapa y una estética compartida de hardware abierto, datos abiertos y rendición de cuentas a la comunidad.

Una nota sobre los nombres, ya que las palabras se solapan: la **red** de campañas replicable usa la convención **Making Sense [lugar]** — Making Sense Bali, Making Sense Barcelona, y así sucesivamente. Estas campañas contemporáneas llevan la metodología de EU Making Sense a nuevas biorregiones; *no son* el proyecto europeo de 2015–2017 en sí, que sigue siendo el origen reconocido (siempre citado con sus fechas). Los sensores, a su vez, son **Smart Citizen Kits** — el hardware abierto — que es una cosa aparte de nuevo.

La estructura de rendición de cuentas de Making Sense Bali:

- **Institución anfitriona**: Fab Lab Bali
- **Contexto de capítulo**: Fab City Bali
- **Membresía de red**: red global [Fab City](https://fab.city/) · [Fab Lab Network](https://fablabs.io/)
- **Contacto**: (mailto:fablabbali@gmail.com)

---

## Estado

La campaña se encuentra actualmente en la transición temprana de la Fase 1 → Fase 2 (Q2 2026):

- La encuesta de la Fase 1 está en vivo y recogiendo respuestas
- El panel de sensores está operativo con los dos nodos SCK de la campaña y agregación en vivo de OpenAQ, Sensor.Community
- La ruta de hardware del nodo DIY está documentada y publicada — las variantes Basic (XIAO + BME680) y Plus (añade HM3301) listas para el primer taller en Fab Lab Bali, pendiente la ruta de referencia del Nivel 0
- El componente de reportes (Sense Making) está en piloto — el bot corre en la infraestructura de Fab Lab Bali, restringido por allowlist a los primeros testers, con la barrera de aprobación en marcha
- Los reportes públicos fluyen al sitio de la campaña tras la revisión del operador

---

## Replícala — Making Sense [tu lugar]

Making Sense Bali es replicable de forma intencional. Otros capítulos Fab City con un Fab Lab anfitrión pueden hacer fork de esta plantilla de campaña para su biorregión.

**Vas a necesitar:**

- Un **capítulo Fab City** para tu ciudad o biorregión ([fab.city/network](https://fab.city/))
- Un **Fab Lab anfitrión** dispuesto a ser el ancla institucional y la parte responsable
- **Cierta presencia de sensores** — como mínimo un Smart Citizen Kit (o un puñado de nodos DIY de taller — mira [`hardware/diy-node/`](hardware/diy-node/) para la vía económica), más la opción de mostrar datos de OpenAQ / Sensor.Community / PurpleAir que ya existan en tu región
- **Capacidad técnica modesta** — alguien que pueda operar un NAS, un Cloudflare Worker y desplegar el bot de reportes (no se requiere desarrollo de software, pero sí soltura operativa)
- **Adaptación al idioma local** — traducir el sitio de la campaña y los textos del bot de reportes

La guía de replicación completa está en **[REPLICATION.md](REPLICATION.md)**.

Actualmente en conversación: **Making Sense Barcelona** (Fab Lab Barcelona, segunda mitad de 2026). Otros capítulos Fab City a los que se está contactando incluyen Yucatán, Montreal, Goa y Santiago. Cada Making Sense [lugar] es su propia campaña, alojada por su propio Fab Lab, anclada en su propia biorregión, compartiendo metodología y federando datos descubribles — esa es la red que el proyecto está construyendo, un capítulo a la vez.

---

## Estructura del repositorio

Todo vive en un único repo para que un Fab Lab que haga fork de Making Sense [su lugar]
obtenga la pila completa con un solo `git clone`.

```
.
├── README.md              this file — campaign overview
├── REPLICATION.md         how to stand up Making Sense [your place]
├── docs/
│   ├── methodology.md     Making Sense, adapted for bioregional deployment
│   ├── phase-1-survey.md  running the matters-of-concern survey
│   ├── sensors.md         deploying SCK + integrating OpenAQ / Sensor.Community
│   ├── reports.md         operating the reports component
│   ├── web-presence.md    customizing the campaign site
│   └── federation.md      Murmurations identity, future PLANETAI
│
├── index.html             campaign home page
├── data.js                sensor data aggregator (SCK + OpenAQ + Sensor.Community)
├── dashboard/             live sensor dashboard
│   └── index.html
├── worker/                Cloudflare Worker proxies (OpenAQ, SCK)
│   └── openaq-proxy.js
├── murmurations.json      federated organization profile
│
└── reports/               Sense Making · the reports component
    ├── README.md          toolkit overview
    ├── bot_murmurations.py
    ├── dashboard.py
    ├── docker-compose.yml
    └── ...                see reports/README.md for the full layout
```

---

## Licencia

Código: MIT.
Documentación, metodología, esquemas, encuestas: CC-BY-SA 4.0.

El mismo patrón de licencia que Making Sense y Smart Citizen Kit. Haz fork,
adáptalo para tu biorregión, comparte de vuelta lo que construyas — de eso se trata.

---

Alojado por [Fab Lab Bali](https://fablabbali.com) · Parte de [Fab City Bali](https://fab.city/) · Miembro de la red [Fab City](https://fab.city/) y de la [Fab Lab Network](https://fablabs.io/).
