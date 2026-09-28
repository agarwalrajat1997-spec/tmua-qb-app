// Disposable PostgreSQL policy regression. No production connection is used.
// Install outside the app: npm install --prefix /tmp/ts-rls-audit @electric-sql/pglite@0.5.8
// PGLITE_MODULE=/tmp/ts-rls-audit/node_modules/@electric-sql/pglite/dist/index.js node scripts/verify-progress-rls.mjs
// Print the reviewed rollback SQL (does not execute it): node scripts/verify-progress-rls.mjs --print-rollback
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const baseline = JSON.parse(readFileSync(new URL('./progress-rls-baseline.json', import.meta.url), 'utf8'));
const migration = readFileSync(new URL('../supabase/migrations/20260920172919_optimize_progress_ownership_policies.sql', import.meta.url), 'utf8');
const quote = (s) => '"' + s.replaceAll('"', '""') + '"';
const createPolicy = (p) => `create policy ${quote(p.policyname)} on public.${quote(p.tablename)} as ${p.permissive} for ${p.cmd} to ${p.roles.map(quote).join(',')}${p.qual ? ` using (${p.qual})` : ''}${p.with_check ? ` with check (${p.with_check})` : ''};`;
const optimizedNames = ['qb_progress', 'user_progress'].flatMap(table => ['select','insert','update','delete'].map(command => [table, `${table}_${command}_own`])).concat([['student_access','student_access_select_own']]);
const cachedUid = '(( SELECT auth.uid() AS uid) = user_id)';
const optimizedPolicies = optimizedNames.map(([tablename,policyname]) => {
  const cmd = tablename === 'student_access' ? 'SELECT' : policyname.split('_').at(-2).toUpperCase();
  return {schemaname:'public',tablename,policyname,permissive:'PERMISSIVE',roles:tablename==='student_access'?['authenticated']:['public'],cmd,
    qual:tablename==='student_access'?"(lower(email) = ( SELECT lower((auth.jwt() ->> 'email'::text)) AS lower))":cmd==='INSERT'?null:cachedUid,
    with_check:['INSERT','UPDATE'].includes(cmd)?cachedUid:null};
});
const rollback = `-- Restores the audited pre-change policies only; student rows/grants stay unchanged.\nbegin;\nset local lock_timeout='3s';\nset local statement_timeout='15s';\ndo $guard$\ndeclare expected jsonb := '${JSON.stringify(optimizedPolicies).replaceAll("'","''")}'::jsonb; policy jsonb; actual jsonb;\nbegin\n  if (select count(*) from pg_policies where schemaname='public' and tablename in ('qb_progress','user_progress','student_access')) <> 9 then raise exception 'Policy inventory changed; review rollback'; end if;\n  for policy in select value from jsonb_array_elements(expected) loop\n    select to_jsonb(p) into actual from pg_policies p where schemaname='public' and tablename=policy->>'tablename' and policyname=policy->>'policyname';\n    if actual is distinct from policy then raise exception 'Policy changed; review rollback: %.%',policy->>'tablename',policy->>'policyname'; end if;\n  end loop;\nend $guard$;\n${optimizedNames.map(([t,n]) => `drop policy ${quote(n)} on public.${quote(t)};`).join('\n')}\n${baseline.map(createPolicy).join('\n')}\ncommit;\n`;
if (process.argv.includes('--print-rollback')) {
  process.stdout.write(rollback);
  process.exit(0);
}

const { PGlite } = await import(process.env.PGLITE_MODULE || '@electric-sql/pglite');
const db = new PGlite();
const A = '00000000-0000-0000-0000-00000000000a';
const B = '00000000-0000-0000-0000-00000000000b';
const product = 'tmua-question-bank';
const otherProduct = 'esat-question-bank';
await db.exec(`
create role anon; create role authenticated; create role service_role bypassrls;
create schema auth;
grant usage on schema public,auth to anon,authenticated,service_role;
create function auth.jwt() returns jsonb language sql stable as $$ select nullif(current_setting('request.jwt.claims',true),'')::jsonb $$;
create function auth.uid() returns uuid language sql stable as $$ select (auth.jwt()->>'sub')::uuid $$;
create table public.user_progress(user_id uuid,product text,key text,data jsonb,primary key(user_id,product,key));
create table public.qb_progress(user_id uuid,product text,question_id text,status text,primary key(user_id,product,question_id));
create table public.student_access(email text,product text,approved boolean,expires_at timestamptz);
alter table public.user_progress enable row level security;
alter table public.qb_progress enable row level security;
alter table public.student_access enable row level security;
grant all on public.user_progress to anon,authenticated,service_role;
grant all on public.qb_progress to authenticated,service_role;
grant select on public.student_access to authenticated;
grant all on public.student_access to service_role;
${baseline.map(createPolicy).join('\n')}
insert into public.user_progress select u::uuid,p,'app_state','{"marker":"original"}'::jsonb from unnest(array['${A}','${B}']) u cross join unnest(array['${product}','${otherProduct}']) p;
insert into public.qb_progress select u::uuid,p,'q1','seen' from unnest(array['${A}','${B}']) u cross join unnest(array['${product}','${otherProduct}']) p;
insert into public.student_access values
 ('learner-a@example.test','${product}',true,null),
 ('Learner-A@example.test','${otherProduct}',false,'2020-01-01'),
 ('learner-b@example.test','${product}',true,null),
 ('learner-b@example.test','${otherProduct}',true,null);
`);

async function stateSnapshot() {
  return (await db.query(`select jsonb_build_object(
    'policies',(select jsonb_agg(to_jsonb(p) order by tablename,policyname) from pg_policies p where schemaname='public'),
    'grants',(select jsonb_agg(to_jsonb(p) order by table_name,grantee,privilege_type) from information_schema.role_table_grants p where table_schema='public'),
    'user_progress',(select jsonb_agg(to_jsonb(p) order by user_id,product,key) from public.user_progress p),
    'qb_progress',(select jsonb_agg(to_jsonb(p) order by user_id,product,question_id) from public.qb_progress p),
    'student_access',(select jsonb_agg(to_jsonb(p) order by email,product) from public.student_access p),
    'rls',(select jsonb_agg(jsonb_build_object('name',relname,'enabled',relrowsecurity,'forced',relforcerowsecurity) order by relname) from pg_class where oid in ('public.user_progress'::regclass,'public.qb_progress'::regclass,'public.student_access'::regclass))
  ) as snapshot`)).rows[0].snapshot;
}

async function probe(role, claims, sql) {
  await db.exec('begin');
  try {
    await db.exec(`set local role ${quote(role)}`);
    await db.query(`select set_config('request.jwt.claims',$1,true)`, [JSON.stringify(claims)]);
    const result = await db.query(sql);
    return { rows: result.rows, affected: result.affectedRows ?? 0 };
  } catch (error) {
    return { error: error.code };
  } finally {
    await db.exec('rollback');
  }
}

const cases = {
  anon: ['anon', {}],
  missingClaims: ['authenticated', {}],
  own: ['authenticated', {sub:A,email:'learner-a@example.test'}],
  other: ['authenticated', {sub:B,email:'learner-b@example.test'}],
  uppercaseEmail: ['authenticated', {sub:A,email:'LEARNER-A@EXAMPLE.TEST'}],
  metadataCannotOverride: ['authenticated', {sub:A,email:'learner-a@example.test',user_metadata:{sub:B,email:'learner-b@example.test'}}],
  metadataEmailOnly: ['authenticated', {sub:A,user_metadata:{email:'learner-a@example.test'}}],
  rootEmailControlsAccess: ['authenticated', {sub:A,email:'learner-b@example.test'}],
  signedInAnonymousUser: ['authenticated', {sub:A,email:'learner-a@example.test',is_anonymous:true}],
  service: ['service_role', {}],
};

async function matrix() {
  const result = {};
  for (const [name,[role,claims]] of Object.entries(cases)) {
    result[name] = {};
    for (const [table,id] of [['user_progress','key'],['qb_progress','question_id']]) {
      const valueCol = table === 'user_progress' ? 'data' : 'status';
      const value = table === 'user_progress' ? `'{}'::jsonb` : `'seen'`;
      const queries = {
        read: `select user_id,product,${id} from public.${table} order by user_id,product,${id}`,
        ownInsert: `insert into public.${table}(user_id,product,${id},${valueCol}) values('${A}','${product}','probe',${value}) returning user_id`,
        otherInsert: `insert into public.${table}(user_id,product,${id},${valueCol}) values('${B}','${product}','probe',${value}) returning user_id`,
        ownUpdate: `update public.${table} set ${valueCol}=${value} where user_id='${A}' and product='${product}' returning user_id`,
        otherUpdate: `update public.${table} set ${valueCol}=${value} where user_id='${B}' and product='${product}' returning user_id`,
        transferOwnership: `update public.${table} set user_id='00000000-0000-0000-0000-00000000000c' where user_id='${A}' and product='${product}' returning user_id`,
        ownDelete: `delete from public.${table} where user_id='${A}' and product='${product}' returning user_id`,
        otherDelete: `delete from public.${table} where user_id='${B}' and product='${product}' returning user_id`,
        productRead: `select product from public.${table} where product='${otherProduct}' order by user_id`,
      };
      for (const [action,sql] of Object.entries(queries)) result[name][`${table}:${action}`] = await probe(role,claims,sql);
    }
    result[name].access = await probe(role,claims,'select email,product,approved,expires_at from public.student_access order by email,product');
    result[name].accessWrite = await probe(role,claims,`insert into public.student_access values ('learner-a@example.test','probe',true,null) returning email`);
  }
  return result;
}

const before = await stateSnapshot();
const beforeMatrix = await matrix();
// Unknown policies must stop the migration, rather than silently broadening/removing access.
await db.exec('create policy unexpected_probe on public.user_progress for select using (false)');
await assert.rejects(db.exec(migration), /inventory has changed/);
await db.exec('rollback; drop policy unexpected_probe on public.user_progress');
await db.exec(migration);
const after = await stateSnapshot();
const afterMatrix = await matrix();
assert.deepEqual(afterMatrix,beforeMatrix,'Every before/after role and ownership operation must match');
for (const key of ['grants','user_progress','qb_progress','student_access','rls']) assert.deepEqual(after[key],before[key],`${key} changed`);
assert.equal(before.policies.length,15);
assert.equal(after.policies.length,9);
assert.deepEqual(after.policies,[...optimizedPolicies].sort((a,b)=>(a.tablename+a.policyname).localeCompare(b.tablename+b.policyname)));
const ownershipPlan = await probe('authenticated',cases.own[1],'explain (format json) select count(*) from public.qb_progress');
assert.match(JSON.stringify(ownershipPlan),/InitPlan/,'Ownership must be evaluated once through an InitPlan');
for (const table of ['user_progress','qb_progress']) {
  assert.equal(afterMatrix.own[`${table}:read`].rows.length,2);
  assert.ok(afterMatrix.own[`${table}:read`].rows.every(row => row.user_id === A));
  assert.equal(afterMatrix.own[`${table}:otherInsert`].error,'42501');
  assert.equal(afterMatrix.own[`${table}:transferOwnership`].error,'42501');
  assert.equal(afterMatrix.own[`${table}:otherUpdate`].rows.length,0);
  assert.equal(afterMatrix.own[`${table}:otherDelete`].rows.length,0);
  assert.equal(afterMatrix.own[`${table}:productRead`].rows.length,1);
  assert.equal(afterMatrix.missingClaims[`${table}:read`].rows.length,0);
}
assert.equal(afterMatrix.anon['user_progress:read'].rows.length,0);
assert.equal(afterMatrix.anon['qb_progress:read'].error,'42501');
assert.equal(afterMatrix.own.access.rows.length,2,'Visibility includes own expired/unapproved rows exactly as before');
assert.deepEqual(afterMatrix.uppercaseEmail.access,afterMatrix.own.access);
assert.deepEqual(afterMatrix.metadataCannotOverride.access,afterMatrix.own.access);
assert.equal(afterMatrix.metadataEmailOnly.access.rows.length,0,'User metadata must not authorize access');
assert.ok(afterMatrix.rootEmailControlsAccess.access.rows.every(row => row.email==='learner-b@example.test'));
assert.equal(afterMatrix.own.accessWrite.error,'42501');
assert.equal(afterMatrix.anon.access.error,'42501');
assert.equal(afterMatrix.service.access.rows.length,4);
await db.exec('alter policy user_progress_select_own on public.user_progress using (false)');
await assert.rejects(db.exec(rollback),/Policy changed/);
await db.exec('rollback; alter policy user_progress_select_own on public.user_progress using ((select auth.uid())=user_id)');
await db.exec(rollback);
assert.deepEqual(await stateSnapshot(),before,'Rollback must restore exact policies, grants and rows');
await db.close();
console.log('PASS: 200 before/after operations match; ownership, product filters, root email, anon roles, grants, row preservation and rollback verified.');
