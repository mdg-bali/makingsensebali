[English](README.md) · [Bahasa Indonesia](README.id.md) · **Español**

# `data/reports/` — perfiles de reportes ciudadanos aprobados

Este directorio contiene los perfiles de Murmurations saneados de los reportes
ciudadanos que el operador de la campaña ha aprobado. Los archivos de aquí
son artefactos públicos — la página de inicio (`index.html`) y el panel
(`dashboard/index.html`) los obtienen mediante `fetchReports()` de `data.js`
y los renderizan en el mapa junto a los pines de los sensores.

## Archivos

- **`index.json`** — manifiesto que lista todos los nombres de archivo de perfiles aprobados.
  Se actualiza automáticamente con `reports/sync_profiles.sh` tras cada
  ciclo de aprobación.
- **`AQ_<timestamp_id>.json`** — un archivo por reporte aprobado. El formato
  es el esquema Murmurations [`environmental_observation-v1.0.0`](../../reports/schemas/environmental_observation-v1.0.0.json).
  Ya viene sin PII gracias al adaptador de Sense Making.

## Cómo llegan los perfiles aquí

1. Un residente envía un reporte por WhatsApp al bot
2. El bot lo guarda localmente como `pending_review`
3. El operador revisa el reporte en el panel local y hace clic en
   **Approve**
4. El bot escribe un perfil de Murmurations saneado en su directorio
   `profiles/` local
5. `reports/sync_profiles.sh` (ejecutado por cron en el NAS) copia los nuevos
   perfiles a este directorio `data/reports/`, regenera
   `index.json`, hace commit y lo empuja a GitHub
6. GitHub Pages reconstruye; el mapa muestra el nuevo reporte

Nada de lo que hay aquí debería editarse jamás a mano, salvo para una
eliminación de emergencia (p. ej., un reporte aprobado por error). Para eliminar un perfil,
borra su archivo y quita el nombre del archivo de `index.json`, luego
haz commit y empújalo.

## Garantías de privacidad

- Estos perfiles ya están despojados de los números de teléfono del remitente,
  los hashes del remitente, las rutas de imágenes locales y las claves de medios de Evolution API
  gracias a `reports/murmurations_adapter.py` antes de escribirse.
- La identidad de quien reporta nunca es recuperable a partir de nada de este
  directorio.
- Para más detalles, consulta `reports/README.md` y la sección de privacidad de
  `../../REPLICATION.md`.
