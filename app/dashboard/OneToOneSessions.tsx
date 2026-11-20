'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import styles from './OneToOneSessions.module.css';

type Session = { id: string; started_at: string; status: string; credits_used: number;
  recording_url: string | null; recording_password: string | null };
type Course = { id: string; title: string; credits_remaining: number;
  live_session: { id: string; started_at: string; student_joined_at: string | null } | null; sessions: Session[] };

function recordingLink(value: string | null) {
  try { const url = new URL(value ?? ''); return url.protocol === 'https:' ? url.href : null; } catch { return null; }
}

export default function OneToOneSessions() {
  const [courses, setCourses] = useState<Course[] | null>(null);
  const [error, setError] = useState('');
  const [joining, setJoining] = useState<string | null>(null);
  const [joinError, setJoinError] = useState('');
  const inFlight = useRef(false);
  const controller = useRef<AbortController | null>(null);

  const refresh = useCallback(async () => {
    if (inFlight.current) return;
    inFlight.current = true;
    const abort = new AbortController();
    controller.current = abort;
    const timeout = setTimeout(() => abort.abort(), 28000);
    try {
      const response = await fetch('/api/tmua/one-to-one', { cache: 'no-store', signal: abort.signal });
      const data = await response.json();
      if (!response.ok || !Array.isArray(data.courses)) throw new Error(data.error || 'Unable to load your 1:1 sessions.');
      setCourses(data.courses);
      setError('');
    } catch (failure) {
      setError(failure instanceof Error && failure.name !== 'AbortError' ? failure.message : 'Unable to refresh your 1:1 sessions. Please retry.');
    } finally { clearTimeout(timeout); inFlight.current = false; }
  }, []);

  useEffect(() => {
    void refresh();
    const update = () => { if (!document.hidden) void refresh(); };
    const interval = setInterval(update, 10000);
    window.addEventListener('focus', update);
    document.addEventListener('visibilitychange', update);
    return () => { clearInterval(interval); controller.current?.abort(); window.removeEventListener('focus', update); document.removeEventListener('visibilitychange', update); };
  }, [refresh]);

  async function join(sessionId: string) {
    if (joining) return;
    // Reserve the tab during the click so the browser does not block it after fetch.
    const tab = window.open('about:blank', '_blank');
    if (tab) tab.opener = null;
    setJoining(sessionId); setJoinError('');
    try {
      const response = await fetch('/api/tmua/one-to-one', { method: 'POST',
        headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ sessionId }),
        signal: AbortSignal.timeout(28000) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to join. Please retry.');
      const url = new URL(data.url);
      if (url.protocol !== 'https:' || url.username || url.password || !/(^|\.)zoom\.(us|com)$/.test(url.hostname)) throw new Error('Meeting unavailable.');
      if (tab) tab.location.replace(url.href); else window.location.assign(url.href);
      void refresh();
    } catch (failure) {
      tab?.close();
      setJoinError(failure instanceof Error && failure.name !== 'TimeoutError' ? failure.message : 'Joining timed out. Please retry.');
      void refresh();
    } finally { setJoining(null); }
  }

  return <section className={styles.section} aria-labelledby="one-to-one-title">
    <div className={styles.heading}>
      <div><div className={styles.eyebrow}>Personal tutoring</div><h2 id="one-to-one-title">1:1 sessions</h2></div>
      <button className={styles.secondary} type="button" onClick={() => void refresh()}>Refresh</button>
    </div>
    {error && <p role="alert" className={styles.error}>{error} <button type="button" onClick={() => void refresh()}>Retry</button></p>}
    {joinError && <p role="alert" className={styles.error}>{joinError}</p>}
    {courses === null && !error && <p role="status">Loading your 1:1 sessions…</p>}
    {courses?.length === 0 && !error && <div>
      <p>You have no 1:1 sessions booked.</p>
      <a className={styles.button} href="https://www.thrivingscholars.com/pricing" target="_blank" rel="noopener noreferrer">Book 1:1 tutoring ↗</a>
    </div>}
    {!!courses?.length && <>
      <p className={styles.plan}>You are on the 1:1 tutoring plan.</p>
      {courses.map(course => <article className={styles.course} key={course.id}>
        <div className={styles.heading}><h3>{course.title}</h3><span className={styles.credits}>{course.credits_remaining} credits remaining</span></div>
        {course.live_session ? <div className={styles.live}>
          <div><strong>Your session is live</strong><p>Your tutor has opened the meeting.</p></div>
          <button className={styles.button} type="button" disabled={!!error || !!joining} onClick={() => void join(course.live_session!.id)}>
            {joining === course.live_session.id ? 'Opening…' : course.live_session.student_joined_at ? 'Rejoin session ↗' : 'Join session ↗'}
          </button>
        </div> : <p>Your join button will appear here when your tutor starts the session. This page updates automatically.</p>}
        <details className={styles.recordings}>
          <summary>Session history & recordings ({course.sessions.length})</summary>
          {course.sessions.length === 0 ? <p>Your recordings will appear here after your sessions are processed.</p> :
            <ul>{course.sessions.map(session => {
              const url = recordingLink(session.recording_url);
              return <li key={session.id}><div><time dateTime={session.started_at}>{new Date(session.started_at).toLocaleString()}</time><p>{session.credits_used} credits used</p></div>
                <div>{url ? <><a href={url} target="_blank" rel="noopener noreferrer">Watch recording ↗</a>{session.recording_password && <p>Passcode: <code>{session.recording_password}</code></p>}</> : <span>Recording not available yet</span>}</div>
              </li>;
            })}</ul>}
        </details>
      </article>)}
    </>}
  </section>;
}

