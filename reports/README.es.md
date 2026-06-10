[English](README.md) · [Bahasa Indonesia](README.id.md) · **Español**

# Sense Making

**El componente de reportes de [Making Sense Bali](../README.md) — un kit de reportes ciudadanos basado en WhatsApp para nodos Fab City y campañas biorregionales.**

> Esta carpeta es uno de los componentes de la campaña Making Sense Bali. Para
> el contexto completo de la campaña — metodología, sensores, presencia web, encuesta —
> consulta el [README del repo padre](../README.md). Lo que sigue es la
> referencia técnica específica del componente de reportes.

Sense Making es el componente de reportes de una campaña de sensado ciudadano.
Los residentes describen problemas ambientales y urbanos locales — basura, fugas de agua,
escombros de construcción, contaminación vehicular, quema de residuos, ruido — a través de
una interfaz familiar (WhatsApp), en su propio idioma. Un operador local
revisa cada reporte antes de su publicación. Los reportes aprobados se vuelven públicos en
el sitio de la campaña y, cuando existen nodos federados, se vuelven descubribles a través de
las biorregiones mediante el protocolo Murmurations.

El kit es deliberadamente pequeño, soberano y replicable. Funciona sobre
infraestructura de tipo doméstico (un NAS y una laptop), no usa SaaS en la ruta
crítica, no tiene costos de API por mensaje, y otro Fab Lab puede bifurcarlo en
una tarde. La interfaz de reportes es bilingüe por defecto y se configura
por localidad.

Este trabajo desciende del proyecto [Making Sense](https://making-sense.eu/)
(EU Horizon 2020, Fab Lab Barcelona / IAAC y socios, 2015–2017) — el marco
canónico participativo para el sensado ambiental ciudadano. Sense
Making toma la metodología de Making Sense y la empaqueta como un kit distribuido,
desplegable en casa, para el panorama Fab City de 2026.

---

## Estado

| | |
|---|---|
| **Despliegue de referencia** | Making Sense Bali · Bali, Indonesia · fase piloto, Q2 2026 |
| **Operado por** | [Fab Lab Bali](https://fablabbali.com) como la capa de reportes de [Making Sense Bali](https://mdg-bali.github.io/makingsensebali/) |
| **Kit de replicación** | Disponible — consulta [REPLICATION.md](REPLICATION.md) |
| **Próximo planificado** | Pelapor Barcelona · Fab Lab Barcelona · 2026 H2 |
| **Capa de federación** | PLANETAI · planificada, infraestructura aún no construida |

---

## Lo que experimentan los residentes

Una conversación de WhatsApp. El bot empieza con un compromiso de privacidad, y luego
explica el flujo de tres pasos:

```
Resident → halo

Bot     ← 🌴 Making Sense Bali
          🔒 Privacy is our top priority.
          Your phone number is NEVER STORED on our servers.

          This bot is run by Fab Lab Bali so residents can report
          environmental and community issues in your area — trash on
          streets, water leaks, smoke from burning, construction
          dust, vehicle pollution.

          How to report (3 steps):
          1️⃣ Write a description of the issue
          2️⃣ Share your location 📍
          3️⃣ Send a photo (optional)

          Reply AGREE to continue.
          Reply /optout anytime to leave.

Resident → SETUJU
Bot     ← ✅ Thanks! You can now report issues.

Resident → sampah berserakan di pantai bingin
Bot     ← 📝 Description received.
          Step 2/3: Share your location 📍

Resident → [shares location pin]
Bot     ← ✅ Location saved — your report is complete.
          Step 3/3 (optional): Send a photo 📸
```

Todo el texto del bot es bilingüe (idioma local + inglés en cursiva debajo). El idioma
por nodo se configura editando un solo archivo (`messages.py`); la localidad
por nodo (vecindarios, bounding box) se configura en `config.json` y la
tabla de localidades del adaptador.

---

## Lo que ven los operadores

Un panel web en la red local con siete pestañas:

- **Status** — salud del sistema (bot, emparejamiento de WhatsApp, cola de vision), conteo de reportes de hoy
- **Pending review** — reportes entrantes a la espera de aprobación, con aprobar/rechazar de un clic
- **Allowlist** — gestiona quién puede interactuar con el bot (números de teléfono en E.164)
- **WhatsApp** — flujo de emparejamiento, escaneo de QR, estado de conexión, sin necesidad de SSH
- **Reports** — lista completa de reportes con categoría, severidad, localidad, timestamp
- **Map** — vista geográfica de los reportes aprobados (Leaflet, se autocentra en la biorregión)
- **Consent** — libro de consentimiento anonimizado, revoca a cualquier remitente

El panel es un único archivo Flask con plantillas inline, Pico.css para
el estilizado, Leaflet para el mapa, basic auth desde una variable env. Sin paso de build.
Cualquiera que sepa leer Python puede personalizar la apariencia o el comportamiento.

---

## Cómo funciona

```
                      WhatsApp
                          │
                          ▼
┌─────────────────────────────────────────────┐    M1 / inference host
│ Always-on host (Synology NAS / VPS)         │    ┌──────────────────────┐
│ ┌─────────────────────────────────────────┐ │    │ MLX vision server    │
│ │ Evolution API · WhatsApp transport      │ │    │  Phi-3.5-Vision      │
│ ├─────────────────────────────────────────┤ │    │                      │
│ │ Sense Making bot · webhook → save       │─┼───▶│ Worker · pulls queue │
│ │   allowlist · consent · vision queue    │ │    │   updates report     │
│ ├─────────────────────────────────────────┤ │    └──────────────────────┘
│ │ Operator dashboard · approval UI        │ │
│ ├─────────────────────────────────────────┤ │    public:
│ │ Postgres + Redis (Evolution backing)    │ │    ┌──────────────────────┐
│ └─────────────────────────────────────────┘ │    │ campaign GitHub Pages│
│   reports/    canonical (with PII)          │    │  (approved only,     │
│   profiles/   approved + sanitized          │───▶│   sanitized)         │
└─────────────────────────────────────────────┘    └──────────────────────┘
                                                   future: PLANETAI federation
```

Cinco contenedores Docker corren en el always-on host. La inferencia de vision vive en
una máquina Apple Silicon separada para que el always-on host nunca necesite una GPU —
el bot encola un trabajo de vision, el worker en la Mac lo recoge cuando está en línea.
Si la Mac está dormida, las fotos se acumulan en la cola y se procesan cuando despierta.
El bot nunca se bloquea por la inferencia.

Por qué esta forma: la soberanía importa. Todo el stack corre sobre infraestructura
que un hogar posee. Sin APIs propietarias en la ruta, sin facturas mensuales de SaaS, sin
ningún proveedor que pueda desplataformar la campaña. Para un nodo Fab City eso no es
algo incidental — es el punto.

Para el detalle de la arquitectura, consulta [ARCHITECTURE.md](ARCHITECTURE.md).
Para el despliegue, consulta [DEPLOY.md](DEPLOY.md).

---

## Privacidad

Tres compromisos, aplicados por el código:

1. **Los números de teléfono nunca se almacenan** en reportes ni en perfiles públicos.
   El bot almacena solo un hash SHA-256 unidireccional para el seguimiento del consentimiento.
2. **Los reportes se sanitizan antes de la federación.** El adaptador de Murmurations
   elimina toda la PII (hashes de remitentes, rutas locales de imágenes, claves de medios) de los
   perfiles publicados en sitios públicos.
3. **Nada sale de la infraestructura local sin la aprobación explícita del
   operador.** La compuerta de aprobación en el panel es el límite de
   publicación. Los reportes sin revisar se quedan en el NAS y nunca se federan.

El flujo de consentimiento es opt-in por respuesta (`SETUJU` / `AGREE`), el opt-out es un solo
comando (`/optout`), y el operador puede revocar el consentimiento de cualquier remitente
individual a través del panel.

---

## Replícalo

Si operas un nodo Fab City, un Fab Lab, o una campaña comunitaria de sensado y
quieres tu propio despliegue, lee **[REPLICATION.md](REPLICATION.md)**.

Vas a necesitar:

- Un always-on host con Docker (recomendado: Synology DS725+ NAS, ~$300, pero
  cualquier máquina Linux con Docker sirve)
- Una Mac Apple Silicon de repuesto para la inferencia de vision (o sustituye con la
  vision API de Claude Haiku por ~$5/mes)
- Un número de WhatsApp dedicado al bot (un número personal sirve para
  la fase piloto, se recomienda un número de empresa dedicado para producción)
- 4–6 horas del tiempo de un operador para ponerlo en marcha de principio a fin
- Comodidad con una terminal para la configuración inicial; la operación diaria está en el
  panel

Costo recurrente sobre infraestructura doméstica: **~$10–20/mes** (electricidad,
renovación del dominio, fallback opcional de vision-API).

---

## Linaje

| | |
|---|---|
| 2015–2017 | [Making Sense](https://making-sense.eu/) — marco de sensado ciudadano de EU Horizon 2020, liderado por Fab Lab Barcelona / IAAC y socios |
| 2013–presente | [Smart Citizen Kit](https://smartcitizen.me/) — plataforma de sensores ambientales open-hardware de Fab Lab Barcelona |
| 2025–presente | Making Sense Bali — campaña de Fab Lab Bali, la campaña anfitriona del primer despliegue de Sense Making |
| 2026–presente | Sense Making — kit de reportes factorizado para la replicación biorregional |

---

## Estructura del repositorio

```
.
├── bot_murmurations.py       Flask bot — WhatsApp webhook, allowlist, consent
├── dashboard.py              Flask dashboard — approval UI, ops controls
├── murmurations_adapter.py   Federated profile generator (PII-sanitized)
├── vision_analyzer.py        Vision client (MLX / Ollama / Haiku / mock)
├── mlx_vision_server.py      MLX FastAPI server (runs on the Mac)
├── m1_vision_worker.py       Vision queue consumer
├── messages.py               All bilingual bot copy — translate for replication
├── docker-compose.yml        Five-container stack for the always-on host
├── Dockerfile                Shared image for bot + dashboard
├── schemas/
│   └── environmental_observation-v1.0.0.json   Murmurations schema
├── sync_profiles.sh          Push approved profiles to public sites
├── DEPLOY.md                 Detailed deployment steps
├── REPLICATION.md            Forking guide for new bioregions
├── ARCHITECTURE.md           Design decisions
└── OPERATIONS.md             Day-to-day operator playbook
```

---

## Licencia

Código: MIT.
Documentación, esquemas, mensajes: CC-BY-SA 4.0.

Ambas reflejan el enfoque de Making Sense y Smart Citizen — lo bastante abiertas para bifurcar
libremente, share-alike sobre lo que se distribuye públicamente.

---

Construido por [Fab Lab Bali](https://fablabbali.com), para la red
[Fab City](https://fab.city/).
