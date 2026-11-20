import { createSupabaseServerClient } from '@/lib/supabase/server';

export const dynamic = 'force-dynamic';
const BRIDGE = 'https://kaxsermvayanmwouvoaz.supabase.co/functions/v1/tmua-one-to-one';
const headers = { 'Content-Type': 'application/json', 'Cache-Control': 'private, no-store', Vary: 'Cookie' };

async function forward(body: { action: 'snapshot' | 'join'; sessionId?: string }) {
  try {
    const supabase = await createSupabaseServerClient();
    const { data: { session } } = await supabase.auth.getSession();
    if (!session?.access_token) return Response.json({ error: 'Please sign in again.' }, { status: 401, headers });
    // This token is only forwarded; the bridge verifies it with TMUA Auth.
    const response = await fetch(BRIDGE, {
      method: 'POST', headers: { Authorization: `Bearer ${session.access_token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(body), cache: 'no-store', signal: AbortSignal.timeout(25000),
    });
    const data = await response.json();
    return Response.json(data, { status: response.status, headers });
  } catch {
    return Response.json({ error: '1:1 sessions are temporarily unavailable. Please retry.' }, { status: 503, headers });
  }
}

export async function GET() { return forward({ action: 'snapshot' }); }

export async function POST(request: Request) {
  if (request.headers.get('origin') !== new URL(request.url).origin) {
    return Response.json({ error: 'Invalid request origin.' }, { status: 403, headers });
  }
  try {
    const raw = await request.text();
    if (raw.length > 4096) return Response.json({ error: 'Request too large.' }, { status: 413, headers });
    const { sessionId } = JSON.parse(raw);
    if (typeof sessionId !== 'string' || !/^[0-9a-f-]{36}$/i.test(sessionId)) throw new Error('Invalid session');
    return forward({ action: 'join', sessionId });
  } catch {
    return Response.json({ error: 'Invalid session.' }, { status: 400, headers });
  }
}

