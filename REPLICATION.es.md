[English](REPLICATION.md) · [Bahasa Indonesia](REPLICATION.id.md) · **Español**

# Replicar Making Sense [tu lugar]

Una guía para **capítulos Fab City con un Fab Lab anfitrión** que quieren levantar su propia instancia biorregional de Making Sense — combinando sensores de hardware abierto, redes de datos públicos, reportes ciudadanos y una encuesta participativa bajo una sola campaña.

El despliegue de referencia es [Making Sense Bali](README.md), alojado por Fab Lab Bali dentro del capítulo Fab City Bali. Este documento es la misma campaña empaquetada como un kit. Si diriges un capítulo Fab City y cuentas con un Fab Lab anfitrión dispuesto a anclar el trabajo, puedes hacer fork de este repositorio, personalizarlo para tu biorregión y desplegar una instancia funcional en aproximadamente **3–6 meses desde la decisión hasta el lanzamiento público**.

Si no tienes la combinación Fab City + Fab Lab — o no la quieres — la mayoría de las herramientas subyacentes son útiles por sí solas: el [Smart Citizen Kit](https://smartcitizen.me/) para sensores, OpenAQ / Sensor.Community para datos abiertos, el [toolkit de reportes Sense Making](reports/) para la infraestructura del bot. Puedes usar cualquiera de ellas sin operar una campaña "Making Sense [lugar]". El nombre de la campaña y la red federada a la que se une están reservados para las instancias de capítulos Fab City, por razones de rendición de cuentas y gobernanza que se exponen abajo.

---

## 1. ¿Es esto para ti?

Making Sense [tu lugar] requiere cuatro compromisos. Si alguno de ellos está flojo, resuélvelo antes de empezar el trabajo técnico — el trabajo técnico es la mitad fácil.

### Anclas institucionales requeridas

- **Un capítulo Fab City** para tu biorregión. El capítulo es el hogar político y de red de la campaña. Si tu ciudad aún no es un capítulo Fab City, esa es una conversación aparte que debes tener primero con [Fab City](https://fab.city/).
- **Un Fab Lab anfitrión** dispuesto a ser el ancla institucional. El Fab Lab está nombrado, rinde cuentas y es visible en la campaña — es el hogar legal, ético y operativo. No un grupo comunitario informal ni un proyecto personal.
- **Un líder de campaña nombrado.** Una persona que es dueña del trabajo, toma decisiones y es contactable públicamente. No un comité, no un rol rotativo. El líder nombrado es lo que hace la campaña legible para medios, gobierno y socios.

### Capacidad operativa requerida

- **Un pequeño equipo técnico o un operador** — no a tiempo completo, pero alguien con la soltura para operar un Synology NAS (o una máquina Linux equivalente con Docker), personalizar un sitio web estático, desplegar unos cuantos Smart Citizen Kits, gestionar un Airtable. No se requiere desarrollo de software para la puesta en marcha; sí se requiere comodidad para seguir documentación técnica.
- **Capacidad de involucramiento comunitario** — alguien (a menudo la misma persona, a veces una organización socia) que pueda llevar la encuesta de la Fase 1, hablar con los residentes, gestionar el flujo de reportes y decidir qué se aprueba y publica. Este es el trabajo humano que da sentido a los datos.
- **Unos cuantos meses de atención.** Esto no es un proyecto de fin de semana. La Fase 1 toma ~6 semanas de diseño y difusión para hacerse bien. Levantar la infraestructura técnica toma una o dos semanas. Operar la campaña es continuo.

### Lo que no es

- Un producto llave en mano. Tomarás decisiones locales a lo largo del camino — qué barrios priorizar, en qué idioma operar, qué preguntas de encuesta importan para tu biorregión, qué categorías de contaminación dominan tu contexto.
- Un proyecto de investigación. Los datos son para uso comunitario primero, investigación después. Si tu objetivo principal es la publicación académica, este kit está sobredimensionado para tus necesidades.
- Una campaña de incidencia. Making Sense [tu lugar] es participativa y construye evidencia. Puede alimentar la incidencia, pero la campaña en sí es descriptiva — saca a la luz lo que los residentes notan, no predecide cuál es la respuesta.
- Un piloto corto. La red de federación solo funciona si las instancias se mantienen vivas a lo largo de los años. Un Fab Lab que se suma debería esperar alojar la campaña a largo plazo.

---

## 2. Las fases

Making Sense [tu lugar] corre en tres fases superpuestas. No son estrictamente secuenciales — la Fase 2 empieza mientras la Fase 1 aún recoge respuestas; la Fase 3 comienza en cuanto tienes suficientes datos sobre los que actuar — pero el orden en que se inician importa.

### Fase 1 — Asuntos de interés (semanas 1–8)

La campaña empieza preguntando a los residentes qué problemas ambientales afectan su vida diaria. No lo que creemos que deberían importarles — lo que realmente notan. Esta es la base participativa. Sáltatela y habrás construido una campaña de instrumentos, no una campaña comunitaria.

**Lo que produces en la Fase 1:**

- Una encuesta alojada en Airtable (o equivalente) que captura asuntos de interés, ubicaciones, frecuencia, severidad
- 50–500 respuestas de tu biorregión, según el tamaño de la ciudad y la difusión
- Un resumen público en tu sitio de campaña: "Esto es lo que los residentes nos dijeron que les preocupa"
- Una lista corta de prioridades que da forma a la colocación de sensores de la Fase 2 y a los textos del bot de reportes

**Decisiones en la Fase 1:**

- Idioma(s) de la encuesta — idioma local siempre; inglés opcional según la audiencia
- Canales de difusión — escuelas, organizaciones vecinales (banjars, juntas vecinales, AC), redes sociales, carteles, organizaciones socias
- Duración de la encuesta — 3–8 semanas de recolección activa es lo típico
- Cómo se ve "terminado" — un umbral de respuestas, una ventana de tiempo, o ambos

Puedes hacer fork de las preguntas de la encuesta de Making Sense Bali como punto de partida (mira [docs/phase-1-survey.md](docs/phase-1-survey.md), y el **[formulario de la encuesta en vivo de Bali](https://airtable.com/appwQPP3ywSp4uu25/pag1mi3F086XPIlBy/form)** como referencia). La encuesta de Bali es ella misma un trabajo en curso, que itera a medida que aprendemos qué preguntas dan respuestas útiles. Haz fork de las preguntas que te resulten útiles, adapta o reemplaza el resto — los asuntos de interés de tu biorregión no son los de Bali.

### Fase 2 — Sensado y reporte (semanas 4–en adelante)

Mientras llegan las respuestas de la Fase 1, empiezas la capa de sensado y reporte. Dos canales:

**Cuantitativo — Smart Citizen Kits.** Despliega los nodos SCK operados por tu campaña en ubicaciones estratégicas. Empieza con dos o tres (un nodo casa operado por la campaña, un nodo oficina, un nodo alojado por un socio), y expande según las prioridades de la Fase 1. Cada unidad cuesta ~$150, funciona por WiFi y publica de forma abierta en [smartcitizen.me](https://smartcitizen.me/). El panel del sitio de la campaña autodescubre y renderiza tus kits.

**Cualitativo — reportes ciudadanos.** Levanta el [componente de reportes](reports/) — un bot de WhatsApp al que los residentes pueden escribir sobre lo que están viendo. Vertederos de basura, fugas de agua, humo, escombros de construcción, gases de vehículos. Cada reporte es revisado por tu operador antes de su publicación. Los reportes aprobados aparecen en tu sitio de campaña junto a los datos de los sensores.

Los dos canales alimentan el mismo mapa. Un evento de quema aparece como una lectura de sensor (un pico de PM2.5) Y como un reporte de residente ("humo en el extremo sur de la playa desde esta mañana"). Juntos son más fuertes que cualquiera por separado.

**Decisiones en la Fase 2:**

- Dónde colocar los SCK (las prioridades de la Fase 1 deberían guiar esto)
- Con cuántos sensores empezar (3–5 es razonable; puede crecer a 20+ con el tiempo)
- Si integrar datos de OpenAQ / Sensor.Community / PurpleAir — el sitio ya lo hace para tu bbox
- Calendario del operador del bot — quién revisa los reportes a diario, quién responde a los mensajes rotos
- Lista de testers del piloto — empieza con 5–10 residentes de confianza antes de abrirlo

### Fase 3 — Respuesta y aprendizaje (continua, empieza a medida que se acumulan datos)

Es la fase hacia la que se está construyendo la red y donde Making Sense [tu lugar] se gana su sustento. Los datos por sí solos no cambian nada; los datos interpretados por una comunidad, con un ancla nombrada, a veces sí.

Cómo se ve la "respuesta" depende de tu contexto local. Patrones comunes:

- **Bucles de conciencia** — reportes recurrentes de vuelta a los residentes que participaron, para que sepan que su aporte se está usando
- **Afloramiento de patrones** — resúmenes mensuales que identifican eventos recurrentes ("quema de basura cada miércoles en la playa sur") que apuntan a las fuentes
- **Organización comunitaria** — acción local desencadenada por la evidencia agregada (hablar con los negocios que hacen la quema, organizar limpiezas colectivas)
- **Incidencia política** — llevar los datos agregados al gobierno local, los banjars / consejos vecinales, las agencias ambientales
- **Aprendizaje federado** — cuando existan otras instancias de Making Sense [lugar], compartir patrones entre biorregiones (dinámicas de corredores de humo, problemas de agua ligados al monzón, etc.)

La Fase 3 es la más dependiente del contexto local. No prescribimos cómo llevarla. Sí exigimos que te comprometas a llevarla — de lo contrario la campaña se vuelve recolección de datos sin consecuencia, lo cual corroe la confianza de la comunidad.

---

## 3. Componentes — qué hacer fork, qué desplegar, qué configurar

Making Sense [tu lugar] se ensambla a partir de estas piezas:

| Componente | Qué haces | Esfuerzo |
|---|---|---|
| **Sitio de la campaña** (`index.html`, CSS, textos) | Fork, personaliza texto + localidad + acentos visuales para tu ciudad | 1–2 días de edición cuidadosa |
| **Capa de datos de sensores** (`data.js`) | Actualiza el bounding box de tu biorregión, registra tus propios IDs de dispositivo SCK | 1–2 horas |
| **Smart Citizen Kits** | Compra, registra en smartcitizen.me, despliega en tu biorregión | Adquisición ~2 semanas + 1 hora por despliegue |
| **Nodos DIY de taller** (opcional) | Construye nodos de bajo costo XIAO ESP32-S3 + HM3301 + BME680 para mayor densidad de sensores | Taller de medio día por cohorte + pedido de piezas — mira [`hardware/diy-node/`](hardware/diy-node/) |
| **Proxies Cloudflare Worker** (`worker/`) | Opcional — solo si te golpean los límites de tasa de OpenAQ | 1–2 horas si hace falta |
| **Encuesta de la Fase 1** | Diseña las preguntas para tu contexto, aloja en Airtable (o alternativa) | 1 semana de diseño cuidadoso de preguntas + recolección de datos continua |
| **Componente de reportes** (`reports/`) | Fork, configura locale + idioma + allowlist, despliega en el NAS | 1 día de configuración + varias horas de despliegue en el NAS |
| **Identidad Murmurations** (`murmurations.json`) | Edita nombre de la org, socios, geolocalización, etiquetas; publica en tu dominio | 1 hora |

El esfuerzo realista total para ir de "queremos hacer esto" a "estamos públicamente en vivo con sensores + reportes + una encuesta": **6–10 semanas** con un operador trabajando a tiempo parcial, o 3–4 semanas si tienes un equipo dedicado para un sprint.

---

## 4. Haz fork de la campaña — paso a paso

Estos son los pasos de alto nivel. Cada paso enlaza a documentos detallados donde existen.

### Paso 1 — Establece las anclas institucionales

Antes de cualquier código o hardware:

- Confirma el estado de tu capítulo Fab City. Si aún no eres capítulo, habla primero con [Fab City](https://fab.city/).
- Identifica y confirma tu Fab Lab anfitrión. Consigue un compromiso institucional explícito, no solo entusiasmo.
- Nombra a tu líder de campaña. Déjalo por escrito en algún lugar interno.
- Decide el nombre de tu campaña. Convención: **Making Sense [Lugar]** — *Making Sense Barcelona*, *Making Sense Yucatán*, *Making Sense Bangalore*. Mantén el prefijo "Making Sense" para que la red sea reconocible. Una advertencia: esta es la **red** de campañas contemporánea, distinta del proyecto de investigación **Making Sense** de la UE de 2015–2017 del que desciende. Acredita siempre ese proyecto *con sus fechas* en tu linaje para que ambos no se confundan — sobre todo en Barcelona, donde Fab Lab Barcelona llevó el piloto original de la UE.

### Paso 2 — Haz fork de este repositorio

```bash
git clone https://github.com/mdg-bali/makingsensebali your-org/makingsense-yourplace
cd makingsense-yourplace

# Update the remote to your own GitHub org
git remote set-url origin git@github.com:your-org/makingsense-yourplace.git
git push -u origin main
```

GitHub Pages: actívalo en tu fork. El sitio queda en vivo en `your-org.github.io/makingsense-yourplace/`.

### Paso 3 — Personaliza el sitio de la campaña

Edita `index.html` y `dashboard/index.html`:

- Reemplaza "Bali" / "Bukit" por tu ciudad / biorregión en todo el texto
- Actualiza el texto del hero, el encuadre de la metodología, la atribución de "alojado por"
- Actualiza la paleta de colores si quieres — el saffron + teal actual está teñido de Bali; Barcelona quizá prefiera otra
- Actualiza el bounding box y el centro del mapa en `data.js` (`BALI_BOUNDS`, `BALI_CENTER`)
- Actualiza `murmurations.json` con el nombre de tu org, ubicación, socios y etiquetas

Guía de personalización detallada: [docs/web-presence.md](docs/web-presence.md).

### Paso 4 — Despliega los Smart Citizen Kits

- Compra 2–5 unidades SCK en [smartcitizen.me](https://smartcitizen.me/store) (~$150 cada una)
- Regístralas en smartcitizen.me, obtén tus IDs de dispositivo
- Despliégalas — oficina de la campaña, Fab Lab anfitrión, ubicación de un socio, tu casa
- Actualiza en `data.js` `KNOWN_BALI_SCK_IDS` → `KNOWN_[YOURCITY]_SCK_IDS` con tus IDs de dispositivo

Guía detallada: [docs/sensors.md](docs/sensors.md).

**Alternativa más barata — nodos DIY de taller.** Para 5× de densidad espacial por dólar respecto al SCK, la carpeta [`hardware/diy-node/`](hardware/diy-node/) documenta dos niveles: un Basic de ~$15–25 (XIAO ESP32-S3 + BME680, calidad del aire interior + clima + VOC, sin PM) y un Plus de ~$35–60 (Basic + Grove HM3301, añade PM1/2.5/10). Menor fidelidad que el SCK, montaje de medio día en tu Fab Lab anfitrión, accesible para participantes sin perfil técnico. Los nodos DIY no son un reemplazo del SCK — son nodos de densidad espacial referenciados contra la calibración del SCK. Mira `hardware/diy-node/README.md` para la estrategia de niveles completa.

### Paso 5 — Diseña y lanza la encuesta de la Fase 1

- Haz fork de las preguntas de la encuesta de Bali en [docs/phase-1-survey.md](docs/phase-1-survey.md)
- Adáptalas a tu contexto — reemplaza los ejemplos específicos de Bali por los problemas relevantes de tu biorregión
- Tradúcelas al/los idioma(s) local(es)
- Crea una base de Airtable para las respuestas (el plan gratuito cubre ~1000 respuestas)
- Inserta la encuesta en tu sitio de campaña o enlázala
- Inicia la difusión: escuelas, consejos vecinales, redes sociales, organizaciones socias

### Paso 6 — Levanta el componente de reportes

Este es el trabajo técnico más pesado. Lee [`reports/README.md`](reports/README.md) y [`reports/DEPLOY.md`](reports/DEPLOY.md) de principio a fin antes de empezar.

Vas a necesitar:

- Un host siempre encendido con Docker — el Synology DS725+ (~$300 + discos) es la referencia; cualquier máquina Linux con Docker sirve
- Una Mac con Apple Silicon de repuesto para la inferencia de visión (o sustituye por Claude Haiku por ~$5/mes)
- Un número de WhatsApp — se recomienda un SIM dedicado / número de empresa para producción (uno personal sirve para la fase piloto)

Cambios de configuración respecto a los valores por defecto de Bali:

- `reports/config.json` — `node_id`, `bioregion`, `primary_url`, allowlist para tus testers
- `reports/messages.py` — traduce todas las cadenas de cara al usuario a tu(s) idioma(s) local(es)
- `reports/murmurations_adapter.py` — actualiza `BUKIT_BBOX` / `BALI_LOCALITIES` con el bounding box y los nombres de barrio de tu biorregión

### Paso 7 — Publica tu perfil de Murmurations

Edita `murmurations.json` para tu campaña:

- `name`, `nickname`, `primary_url` — tu campaña
- `tags` — tu contexto local
- `description`, `mission` — tu encuadre local
- `urls` — las URLs de tu campaña
- `locality`, `region`, `country_iso_3166`, `geolocation` — tu biorregión
- `contact_details` — tu Fab Lab
- `relationships` — mantén las relaciones schema-org hacia fab.city, fablabs.io, making-sense.eu, smartcitizen.me; añade los socios locales que tengas

Luego envía la URL del perfil al [Murmurations Index](https://murmurations.network/) para que tu campaña sea descubrible.

### Paso 8 — Lanza la Fase 1 públicamente

Cuéntale a la gente que la campaña existe. Difusión a través de:

- Los canales que ya tiene el Fab Lab anfitrión
- La red del capítulo Fab City
- Escuelas locales y organizaciones comunitarias
- Redes sociales (las plataformas que tus residentes realmente usan)
- Prensa, si tienes un contacto de medios

La Fase 1 es la fase de involucramiento con más carga al inicio. Planifícala.

### Paso 9 — Empieza la Fase 2 en paralelo

Una vez que los SCK estén desplegados y el bot de reportes esté en vivo con una allowlist pequeña, empieza a recoger datos en paralelo con la encuesta de la Fase 1. El mapa combinado (sensores + reportes aprobados) en tu sitio de campaña se convierte en el artefacto público.

---

## 5. Localización — qué cambia para tu biorregión

La base de código es configurable a propósito, pero varias decisiones son textuales y requieren juicio humano, no solo ediciones de código.

### Idioma

El texto de cara al usuario del bot de reportes está en [`reports/messages.py`](reports/messages.py). Todas las cadenas son bilingües (idioma local primero, inglés en cursiva debajo). Para tu despliegue:

- Elige tu idioma local principal (catalán + español para Barcelona, maya yucateco + español para Yucatán, kannada + inglés para Bangalore)
- Elige un idioma secundario (el inglés es la convención; podría ser otro si tu contexto lo justifica)
- Que un **hablante nativo revise cada cadena** antes de salir al público. La confianza se construye en la primera respuesta.

El sitio de la campaña (`index.html`) tiene su propio texto, mayormente en inglés en el despliegue de referencia de Bali. Para audiencias cuyo primer idioma no es el inglés, tradúcelo.

### Bounding box de la localidad y barrios

En `reports/murmurations_adapter.py`:

- `BUKIT_BBOX` → el bounding box de tu ciudad/biorregión (lat/lon min/max)
- `BALI_LOCALITIES` → lista de nombres de barrio que deberían reconocerse en las descripciones de los reportes

El bot los usa para autocategorizar dónde se ubica un reporte. Las localidades de Barcelona son Eixample, Gràcia, Raval, Sant Antoni, Poblenou, Sants, Sarrià, Horta — y muchas más.

### Designación de biorregión

En `reports/config.json` define `bioregion` como uno de los valores del enum de biorregión de Murmurations (el esquema en `reports/schemas/environmental_observation-v1.0.0.json` los lista). La biorregión de Barcelona es `mediterranean_basin`. Si tu biorregión no está en el enum, propón una ampliación a través del esquema.

### Identidad visual

La paleta actual del sitio (saffron + teal + papel crema) evoca Bali — sol, agua, papel tropical. Para tu despliegue puedes mantenerla (señala la pertenencia a la red) o virar hacia acentos locales. Las variables CSS están definidas al principio de `index.html` para cambiar la paleta con facilidad.

### Categorías

El enum `pollution_category` del esquema cubre la mayoría de las preocupaciones ambientales: quema, basura, vehículos, construcción, polvo, industrial, química, agua, ruido, deforestación. Si tu biorregión tiene una categoría que no encaja (p. ej., específica de tu industria, clima o geografía), propón añadirla al esquema en vez de sobrecargar las categorías existentes.

### Gobernanza y atribución

Tres referencias que tu fork debería actualizar de forma consistente:

- "Hosted by Fab Lab Bali" → alojado por tu Fab Lab
- "Part of Fab City Bali" → parte de tu capítulo Fab City
- Tomas Diez como líder nombrado → tu líder nombrado

Mantén las referencias a Making Sense, Smart Citizen Kit, Fab Lab Barcelona / IAAC en el linaje — esos son el origen compartido que todas las instancias de Making Sense [lugar] comparten.

---

## 6. Federación — unirse a la red

Cada instancia de Making Sense [lugar] es independiente pero descubrible. La federación ocurre hoy mediante dos mecanismos y uno a futuro:

### Hoy — Murmurations

Una vez que publicas tu `murmurations.json` y lo envías al [Murmurations Index](https://murmurations.network/), tu campaña es descubrible en el ecosistema más amplio de Murmurations. Cualquier red de datos comunitarios puede consultar `tags=citizen sensing` o `tags=fab lab` y encontrar tu instancia junto a Making Sense Bali, Making Sense Barcelona y otras.

Esta es la forma más ligera de federación: tu campaña es *encontrable* pero cada instancia opera de forma independiente. Sin compartir datos entre nodos, sin infraestructura compartida.

### Hoy — enlaces bidireccionales

Cada sitio de Making Sense [lugar] enlaza con los demás a través de las redes Fab City y Fab Lab. La sección de linaje en el README de cada campaña reconoce la metodología y la plataforma compartidas. La red se vuelve visible mediante la cita, no mediante la integración técnica.

### A futuro — federación PLANETAI

PLANETAI es el horizonte de más largo plazo: una capa de federación que agrega los reportes aprobados a través de las instancias de Making Sense [lugar], te permite consultar patrones entre biorregiones y provee infraestructura compartida (alojamiento de perfiles, descubrimiento entre instancias, servicios de IA opcionales). La infraestructura de PLANETAI aún no está construida — cuando lo esté, unirse a la federación será opcional (opt-in) y se configurará en `reports/config.json`.

Por ahora, diseña y opera tu instancia como si fuera a federarse. El esquema de Murmurations es compartido, la forma del reporte es compartida, la metodología es compartida. Cuando exista PLANETAI, el trabajo técnico para federar será un cambio de configuración, no una refactorización.

---

## 7. Dónde conseguir ayuda

- **Repositorio**: [github.com/mdg-bali/makingsensebali](https://github.com/mdg-bali/makingsensebali) — abre issues, propón pull requests
- **Conversaciones de replicación**: [fablabbali@gmail.com](mailto:fablabbali@gmail.com) — la bandeja de Fab Lab Bali. Escríbenos antes de empezar; una llamada corta al inicio ahorra semanas de adivinanzas.
- **Red Fab City**: [fab.city](https://fab.city/) — para el estado del capítulo, presentaciones de socios
- **Plataforma Smart Citizen**: [smartcitizen.me](https://smartcitizen.me/) — hardware, configuración de cuenta, preguntas sobre sensores

Si estás considerando seriamente la replicación, escríbenos antes de empezar. Una llamada corta al inicio ahorra semanas de adivinanzas — y nos permite coordinar los tiempos de lanzamiento, compartir materiales y conectarte con capítulos cercanos.

---

## 8. Licencia y atribución

Todo el código de este repositorio: **MIT**.
Documentación, esquemas, encuestas y metodología: **CC-BY-SA 4.0**.

Si haces fork y operas un Making Sense [lugar], te pedimos tres cosas:

1. **Acredita el linaje.** Making Sense (Fab Lab Barcelona / IAAC, 2015–2017), Smart Citizen (cofundada por Tomas Diez y Alex Posada, 2012), Making Sense Bali (Fab Lab Bali, 2026) en tu README y en tu sitio de campaña.
2. **Mantén la red legible.** Usa la convención de nombres "Making Sense [lugar]". Publica tu perfil de Murmurations. Enlaza con otras instancias.
3. **Comparte de vuelta.** Mejoras al código, a la metodología, a los documentos — los pull requests son bienvenidos. El kit mejora cuando cada nueva instancia aporta de vuelta lo que aprendió.

---

Construido por [Fab Lab Bali](https://fablabbali.com), para la red [Fab City](https://fab.city/).
Para Barcelona, Yucatán, Montreal, Goa, Santiago, y las demás instancias biorregionales que están por venir.
