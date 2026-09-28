-- Align ESAT Biology and Chemistry topics with the official UAT-UK headings.
-- This is a topic-only migration: qids, question content, answers, scoring and
-- progress rows are preserved. The backup makes the change reversible by qid.
create schema if not exists private;

create table if not exists private.esat_biology_chemistry_topic_backup_20260915 as
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

insert into private.esat_biology_chemistry_topic_backup_20260915
  (qid, old_topic, subtopic, paper, is_active, source_updated_at, backed_up_at)
select q.qid, q.topic, q.subtopic, q.paper, q.is_active, q.updated_at, now()
from public.esat_qb_questions q
where q.paper in ('ESAT Biology', 'ESAT Chemistry')
  and not exists (
    select 1
    from private.esat_biology_chemistry_topic_backup_20260915 b
    where b.qid = q.qid
  );

update public.esat_qb_questions q
set topic = case
  -- Biology (official B1-B11 headings)
  when q.paper = 'ESAT Biology' and q.topic = '21_Cell Biology and Organisation'
    and q.subtopic ~* '(respiration|gas exchange)' then 'B9. Animal physiology'
  when q.paper = 'ESAT Biology' and q.topic = '21_Cell Biology and Organisation'
    and q.subtopic ~* '(osmosis|active transport|ion gradient)' then 'B2. Movement across membranes'
  when q.paper = 'ESAT Biology' and q.topic = '21_Cell Biology and Organisation'
    and q.subtopic ~* '(mitosis|binary fission)' then 'B3. Cell division and sex determination'
  when q.paper = 'ESAT Biology' and q.topic = '21_Cell Biology and Organisation'
    and q.subtopic ~* 'stem cell' then 'B6. Gene technologies'
  when q.paper = 'ESAT Biology' and q.topic = '21_Cell Biology and Organisation'
    then 'B1. Cells'
  when q.paper = 'ESAT Biology' and q.topic = '22_Biological Molecules and Enzymes'
    and q.subtopic ~* '(enzyme|substrate|protease|lipase|starch|reaction progress|agar diffusion)' then 'B8. Enzymes'
  when q.paper = 'ESAT Biology' and q.topic = '22_Biological Molecules and Enzymes'
    and q.subtopic ~* '(DNA|mutation)' then 'B5. DNA'
  when q.paper = 'ESAT Biology' and q.topic = '22_Biological Molecules and Enzymes'
    then 'B8. Enzymes'
  when q.paper = 'ESAT Biology' and q.topic = '23_Membranes, Exchange and Transport'
    and q.subtopic ~* 'counter-current' then 'B9. Animal physiology'
  when q.paper = 'ESAT Biology' and q.topic = '23_Membranes, Exchange and Transport'
    then 'B2. Movement across membranes'
  when q.paper = 'ESAT Biology' and q.topic = '24_Photosynthesis and Respiration'
    and q.subtopic ~* '(photosynthesis|leaf|light intensity|limiting factors)' then 'B11. Plant physiology'
  when q.paper = 'ESAT Biology' and q.topic = '24_Photosynthesis and Respiration'
    and q.subtopic ~* '(exercise|lactate|oxygen debt|gas exchange)' then 'B9. Animal physiology'
  when q.paper = 'ESAT Biology' and q.topic = '24_Photosynthesis and Respiration'
    and q.subtopic ~* 'enzyme' then 'B8. Enzymes'
  when q.paper = 'ESAT Biology' and q.topic = '24_Photosynthesis and Respiration'
    then 'B11. Plant physiology'
  when q.paper = 'ESAT Biology' and q.topic = '25_Genetics, Inheritance and Cell Division'
    and q.subtopic ~* '(genetic engineering|plasmid|stem cell)' then 'B6. Gene technologies'
  when q.paper = 'ESAT Biology' and q.topic = '25_Genetics, Inheritance and Cell Division'
    and q.subtopic ~* '(DNA|nucleotide|translation|genetic code|mutation|base)' then 'B5. DNA'
  when q.paper = 'ESAT Biology' and q.topic = '25_Genetics, Inheritance and Cell Division'
    and q.subtopic ~* '(mitosis|meiosis|fertilisation|binary fission|chromosome|sex determination)' then 'B3. Cell division and sex determination'
  when q.paper = 'ESAT Biology' and q.topic = '25_Genetics, Inheritance and Cell Division'
    then 'B4. Inheritance'
  when q.paper = 'ESAT Biology' and q.topic = '26_Evolution, Variation and Classification' then 'B7. Variation'
  when q.paper = 'ESAT Biology' and q.topic = '27_Ecology and Ecosystems' then 'B10. Ecosystems'
  when q.paper = 'ESAT Biology' and q.topic = '28_Plant Biology and Physiology' then 'B11. Plant physiology'
  when q.paper = 'ESAT Biology' and q.topic = '29_Animal and Human Physiology' then 'B9. Animal physiology'
  when q.paper = 'ESAT Biology' and q.topic = '30_Biotechnology and Genetic Engineering' then 'B6. Gene technologies'
  when q.paper = 'ESAT Biology' and q.topic = '31_Practical Skills'
    and q.subtopic ~* 'diffusion' then 'B2. Movement across membranes'
  when q.paper = 'ESAT Biology' and q.topic = '31_Practical Skills' then 'B7. Variation'

  -- Chemistry (official C1-C17 headings)
  when q.paper = 'ESAT Chemistry' and q.topic = '32_Atomic Structure and Periodicity'
    and q.subtopic ~* '(group 1|group 17|halogen)' then 'C7. Group chemistry'
  when q.paper = 'ESAT Chemistry' and q.topic = '32_Atomic Structure and Periodicity'
    and q.subtopic ~* '(periodic|periodicity|group|period|comparing properties)' then 'C2. The Periodic Table'
  when q.paper = 'ESAT Chemistry' and q.topic = '32_Atomic Structure and Periodicity' then 'C1. Atomic structure'
  when q.paper = 'ESAT Chemistry' and q.topic = '33_Bonding, Structure and States of Matter'
    and q.subtopic ~* 'dry air' then 'C17. Air and water'
  when q.paper = 'ESAT Chemistry' and q.topic = '33_Bonding, Structure and States of Matter'
    and q.subtopic ~* 'fractional distillation' then 'C8. Separation techniques'
  when q.paper = 'ESAT Chemistry' and q.topic = '33_Bonding, Structure and States of Matter'
    and q.subtopic ~* '(phase change|states of matter)' then 'C15. Kinetic/Particle theory'
  when q.paper = 'ESAT Chemistry' and q.topic = '33_Bonding, Structure and States of Matter' then 'C6. Chemical bonding, structure and properties'
  when q.paper = 'ESAT Chemistry' and q.topic = '34_Stoichiometry and Formulae'
    and q.subtopic ~* '(balanc|ionic equation)' then 'C3. Chemical reactions, formulae and equations'
  when q.paper = 'ESAT Chemistry' and q.topic = '34_Stoichiometry and Formulae'
    and q.subtopic ~* 'ionic compound' then 'C6. Chemical bonding, structure and properties'
  when q.paper = 'ESAT Chemistry' and q.topic = '34_Stoichiometry and Formulae' then 'C4. Quantitative chemistry'
  when q.paper = 'ESAT Chemistry' and q.topic = '35_Energetics and Thermochemistry'
    and q.subtopic ~* 'activation energy' then 'C10. Rates of reaction'
  when q.paper = 'ESAT Chemistry' and q.topic = '35_Energetics and Thermochemistry' then 'C11. Energetics'
  when q.paper = 'ESAT Chemistry' and q.topic = '36_Kinetics and Rates of Reaction' then 'C10. Rates of reaction'
  when q.paper = 'ESAT Chemistry' and q.topic = '37_Equilibria, Acids and Bases'
    and q.subtopic ~* 'equilibrium' then 'C3. Chemical reactions, formulae and equations'
  when q.paper = 'ESAT Chemistry' and q.topic = '37_Equilibria, Acids and Bases'
    and q.subtopic ~* '(titration|concentration)' then 'C4. Quantitative chemistry'
  when q.paper = 'ESAT Chemistry' and q.topic = '37_Equilibria, Acids and Bases' then 'C9. Acids, bases and salts'
  when q.paper = 'ESAT Chemistry' and q.topic = '38_Redox and Electrochemistry'
    and q.subtopic ~* '(electrolysis|electroplating|cathode|anode|electrolyte|molten|aqueous)' then 'C12. Electrolysis'
  when q.paper = 'ESAT Chemistry' and q.topic = '38_Redox and Electrochemistry' then 'C5. Oxidation, reduction and redox'
  when q.paper = 'ESAT Chemistry' and q.topic = '39_Inorganic Chemistry and Metals'
    and q.subtopic ~* '(ion test|qualitative|silver chloride)' then 'C16. Chemical tests'
  when q.paper = 'ESAT Chemistry' and q.topic = '39_Inorganic Chemistry and Metals'
    and q.subtopic ~* '(group 1|halogen)' then 'C7. Group chemistry'
  when q.paper = 'ESAT Chemistry' and q.topic = '39_Inorganic Chemistry and Metals'
    and q.subtopic ~* '(formula|bonding|oxide)' then 'C6. Chemical bonding, structure and properties'
  when q.paper = 'ESAT Chemistry' and q.topic = '39_Inorganic Chemistry and Metals' then 'C14. Metals'
  when q.paper = 'ESAT Chemistry' and q.topic = '40_Organic Chemistry' then 'C13. Carbon/Organic chemistry'
  when q.paper = 'ESAT Chemistry' and q.topic = '41_Analytical Chemistry and Separation'
    and q.subtopic ~* '(test|halide|metal-ion)' then 'C16. Chemical tests'
  when q.paper = 'ESAT Chemistry' and q.topic = '41_Analytical Chemistry and Separation'
    and q.subtopic ~* 'diffusion' then 'C15. Kinetic/Particle theory'
  when q.paper = 'ESAT Chemistry' and q.topic = '41_Analytical Chemistry and Separation'
    and q.subtopic ~* 'ionic solid' then 'C6. Chemical bonding, structure and properties'
  when q.paper = 'ESAT Chemistry' and q.topic = '41_Analytical Chemistry and Separation' then 'C8. Separation techniques'
  else q.topic
end,
updated_at = now()
where q.paper in ('ESAT Biology', 'ESAT Chemistry')
  and q.topic in (
    '21_Cell Biology and Organisation',
    '22_Biological Molecules and Enzymes',
    '23_Membranes, Exchange and Transport',
    '24_Photosynthesis and Respiration',
    '25_Genetics, Inheritance and Cell Division',
    '26_Evolution, Variation and Classification',
    '27_Ecology and Ecosystems',
    '28_Plant Biology and Physiology',
    '29_Animal and Human Physiology',
    '30_Biotechnology and Genetic Engineering',
    '31_Practical Skills',
    '32_Atomic Structure and Periodicity',
    '33_Bonding, Structure and States of Matter',
    '34_Stoichiometry and Formulae',
    '35_Energetics and Thermochemistry',
    '36_Kinetics and Rates of Reaction',
    '37_Equilibria, Acids and Bases',
    '38_Redox and Electrochemistry',
    '39_Inorganic Chemistry and Metals',
    '40_Organic Chemistry',
    '41_Analytical Chemistry and Separation'
  );
