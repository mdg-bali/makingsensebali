// Making Sense Bali · Cloudflare Worker proxy
// ---------------------------------------------
// Solves the CORS issue for APIs that don't allow browser origins to call
// them directly with custom headers (e.g. OpenAQ v3, PurpleAir).
//
// The worker:
//   1. Accepts requests from the browser at /openaq/*
//   2. Adds the X-API-Key header server-side
//   3. Forwards to api.openaq.org/v3/*
//   4. Returns the response with proper CORS headers
//   5. Caches responses for 60 seconds to reduce upstream API hits
//
// Deploy steps (in this file's accompanying README):
//   1. Cloudflare dashboard → Workers & Pages → Create Worker
//   2. Paste this entire file as the worker code
//   3. Settings → Variables and Secrets → add encrypted secrets:
//        OPENAQ_API_KEY = <your OpenAQ key>
//        (later: PURPLEAIR_API_KEY = <key>)
//   4. Deploy and note the URL (e.g. scb-bali.tomasdiez.workers.dev)
//   5. Set OPENAQ_PROXY_BASE in data.js to that URL + '/openaq'

const ALLOWED_ORIGINS = [
  'https://mdg-bali.github.io',
  'http://localhost',     // any localhost port for dev
  'http://127.0.0.1',
];

function isAllowedOrigin(origin) {
  if (!origin) return true; // no Origin header (curl, server-to-server)
  return ALLOWED_ORIGINS.some(o => origin === o || origin.startsWith(o));
}

function corsHeaders(origin) {
  // Reflect the requesting origin if it's in our allowlist; otherwise '*'.
  // The worker only proxies public read-only environmental data, so '*' is
  // acceptable as a fallback — there's nothing private to protect.
  return {
    'Access-Control-Allow-Origin': isAllowedOrigin(origin) ? (origin || '*') : '*',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Accept',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = request.headers.get('origin');
    const baseHeaders = corsHeaders(origin);

    // Handle preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: baseHeaders });
    }
    if (request.method !== 'GET') {
      return jsonResponse({error: 'Only GET supported'}, 405, baseHeaders);
    }

    // Route: /openaq/*  →  api.openaq.org/v3/*
    if (url.pathname.startsWith('/openaq/')) {
      return proxyOpenAQ(url, env, baseHeaders);
    }

    // Route: /sck/*  →  api.smartcitizen.me/v0/*
    if (url.pathname.startsWith('/sck/')) {
      return proxySCK(url, env, baseHeaders);
    }

    // Health check
    if (url.pathname === '/' || url.pathname === '/health') {
      return jsonResponse({
        ok: true,
        service: 'smartcitizenbali-proxy',
        routes: [
          'GET /openaq/locations?bbox=...',
          'GET /openaq/locations/{id}/latest',
          'GET /sck/devices/{id}',
          'GET /sck/devices/world_map?per_page=...&page=...',
        ],
      }, 200, baseHeaders);
    }

    return jsonResponse({error: 'Not found', path: url.pathname}, 404, baseHeaders);
  }
};

async function proxyOpenAQ(url, env, baseHeaders) {
  const apiKey = env.OPENAQ_API_KEY;
  if (!apiKey) {
    return jsonResponse(
      {error: 'OPENAQ_API_KEY not configured. Add it as an encrypted secret in worker settings.'},
      500, baseHeaders
    );
  }

  // Strip /openaq prefix and forward
  const upstreamPath = url.pathname.replace(/^\/openaq/, '/v3');
  const upstreamUrl = `https://api.openaq.org${upstreamPath}${url.search}`;

  let upstream;
  try {
    upstream = await fetch(upstreamUrl, {
      method: 'GET',
      headers: {
        'X-API-Key': apiKey,
        'Accept': 'application/json',
        'User-Agent': 'smartcitizenbali-proxy/1.0',
      },
      cf: {
        // Cloudflare edge cache, ~60 seconds — cuts repeat API hits dramatically
        cacheTtl: 60,
        cacheEverything: true,
      },
    });
  } catch (e) {
    return jsonResponse({error: 'Upstream fetch failed', message: String(e)}, 502, baseHeaders);
  }

  const bodyText = await upstream.text();
  return new Response(bodyText, {
    status: upstream.status,
    headers: {
      ...baseHeaders,
      'Content-Type': upstream.headers.get('content-type') || 'application/json',
      'Cache-Control': 'public, max-age=60',
    },
  });
}

async function proxySCK(url, env, baseHeaders) {
  // Smart Citizen Platform public endpoints don't require auth, but optional
  // Bearer token can be set as SCK_API_KEY for owner-only data.
  const apiKey = env.SCK_API_KEY;

  const upstreamPath = url.pathname.replace(/^\/sck/, '/v0');
  const upstreamUrl = `https://api.smartcitizen.me${upstreamPath}${url.search}`;

  const upstreamHeaders = {
    'Accept': 'application/json',
    'User-Agent': 'smartcitizenbali-proxy/1.0',
  };
  if (apiKey) upstreamHeaders['Authorization'] = `Bearer ${apiKey}`;

  let upstream;
  try {
    upstream = await fetch(upstreamUrl, {
      method: 'GET',
      headers: upstreamHeaders,
      cf: { cacheTtl: 60, cacheEverything: true },
    });
  } catch (e) {
    return jsonResponse({error: 'Upstream fetch failed', message: String(e)}, 502, baseHeaders);
  }

  const bodyText = await upstream.text();
  return new Response(bodyText, {
    status: upstream.status,
    headers: {
      ...baseHeaders,
      'Content-Type': upstream.headers.get('content-type') || 'application/json',
      'Cache-Control': 'public, max-age=60',
    },
  });
}

function jsonResponse(obj, status, baseHeaders) {
  return new Response(JSON.stringify(obj, null, 2), {
    status,
    headers: { ...baseHeaders, 'Content-Type': 'application/json' },
  });
}
