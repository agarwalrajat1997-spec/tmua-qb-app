import Link from 'next/link';
import { redirect } from 'next/navigation';
import { createSupabaseServerClient } from '@/lib/supabase/server';
import { isMissingSession } from '@/lib/auth/service-recovery';
import OneToOneSessions from '../OneToOneSessions';

export const dynamic = 'force-dynamic';
export const metadata = { title: '1:1 tutoring | Thriving Scholars' };

export default async function OneToOneStudentPage() {
  const supabase = await createSupabaseServerClient();
  const { data: { user }, error } = await supabase.auth.getUser();
  if (error && !isMissingSession(error)) {
    return <main style={{ maxWidth: 960, margin: '0 auto', padding: '32px 20px' }}>
      <h1>1:1 tutoring</h1>
      <p role="alert">Unable to check your session right now. Please retry.</p>
      <a href="/dashboard/one-to-one">Retry</a>
    </main>;
  }
  if (!user) redirect('/login?next=%2Fdashboard%2Fone-to-one');

  return <main style={{ maxWidth: 960, margin: '0 auto', padding: '32px 20px' }}>
    <nav aria-label="Portal navigation" style={{ display: 'flex', justifyContent: 'space-between', gap: 16 }}>
      <Link href="/dashboard">← Dashboard</Link>
      <a href="/api/logout">Sign out</a>
    </nav>
    <header style={{ marginTop: 28 }}>
      <h1 style={{ fontSize: 32, marginBottom: 8 }}>1:1 tutoring</h1>
      <p style={{ color: '#59616b' }}>Signed in as {user.email}</p>
    </header>
    <OneToOneSessions />
  </main>;
}