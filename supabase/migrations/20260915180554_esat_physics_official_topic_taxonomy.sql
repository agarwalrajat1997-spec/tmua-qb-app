-- Align ESAT Physics topics with the official UAT-UK P1-P7 headings.
-- The backup makes this data-only taxonomy change reversible by qid.
create schema if not exists private;

create table if not exists private.esat_physics_topic_backup_20260915 as
select
  qid,
  topic as old_topic,
  subtopic,
  paper,
  is_active,
  updated_at as source_updated_at,
  now() as backed_up_at
from public.esat_qb_questions
where false;

insert into private.esat_physics_topic_backup_20260915
  (qid, old_topic, subtopic, paper, is_active, source_updated_at, backed_up_at)
select q.qid, q.topic, q.subtopic, q.paper, q.is_active, q.updated_at, now()
from public.esat_qb_questions q
where q.paper = 'ESAT Physics'
  and not exists (
    select 1
    from private.esat_physics_topic_backup_20260915 b
    where b.qid = q.qid
  );

update public.esat_qb_questions q
set topic = case
  when q.topic in ('12_Mechanics', '13_Energy and Power')
    then 'P3. Mechanics'
  when q.topic = '14_Electricity and Magnetism'
    and q.subtopic ~* '(electromagnetic|magnetic|current-carrying|torque|transformer)'
    then 'P2. Magnetism'
  when q.topic = '14_Electricity and Magnetism'
    then 'P1. Electricity'
  when q.topic = '15_Waves and Optics'
    then 'P6. Waves'
  when q.topic = '16_Materials and Fluids'
    then 'P5. Matter'
  when q.topic = '17_Thermal Physics'
    then 'P4. Thermal physics'
  when q.topic = '18_Atomic and Nuclear Physics'
    then 'P7. Radioactivity'
  when q.topic = '19_Astrophysics' and q.subtopic ilike '%Stefan%'
    then 'P4. Thermal physics'
  when q.topic = '19_Astrophysics'
    then 'P6. Waves'
  when q.topic = '20_Physics Skills & Miscellaneous' and q.subtopic ilike '%Units%'
    then 'P3. Mechanics'
  when q.topic = '20_Physics Skills & Miscellaneous'
    then 'P7. Radioactivity'
  else q.topic
end,
updated_at = now()
where q.paper = 'ESAT Physics'
  and q.topic in (
    '12_Mechanics',
    '13_Energy and Power',
    '14_Electricity and Magnetism',
    '15_Waves and Optics',
    '16_Materials and Fluids',
    '17_Thermal Physics',
    '18_Atomic and Nuclear Physics',
    '19_Astrophysics',
    '20_Physics Skills & Miscellaneous'
  );
