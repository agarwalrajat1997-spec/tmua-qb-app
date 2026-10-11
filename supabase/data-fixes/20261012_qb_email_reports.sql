-- Email reports received after the 6 October 2026 audit.
-- Transactional content corrections with private rollback snapshots.
-- Run the complete file in one transaction; use ROLLBACK for a rehearsal.
-- No auth/access changes. Preserve historical attempts, flags and time spent.
DO $fix$
DECLARE
  repair_key constant text := 'email_bug_audit_20261006_20261012_v1';
  fixes jsonb := $payload$[{"table": "esat_qb_questions", "qid": "ESAT-BIO-0115", "expected": {"prompt_html": "<p>A mammalian cell is \\(10\\,\\mu\\text{m}\\) wide. One plasma membrane has a thickness equal to \\(0.2\\%\\) of this width. Molecule X is transported out of the cell from a region of concentration \\(2\\) arbitrary units to a region of concentration \\(8\\) arbitrary units.</p><p>Which row gives the membrane thickness and the transport process?</p>", "options": [{"html": "0.01; diffusion", "label": "A", "assets": null}, {"html": "0.01; active transport", "label": "B", "assets": null}, {"html": "0.02; diffusion", "label": "C", "assets": null}, {"html": "0.02; active transport", "label": "D", "assets": null}, {"html": "10; diffusion", "label": "E", "assets": null}, {"html": "10; active transport", "label": "F", "assets": null}, {"html": "20; diffusion", "label": "G", "assets": null}, {"html": "20; active transport", "label": "H", "assets": null}], "answer": "H"}, "patch": {"prompt_html": "<p>A mammalian cell is \\(10\\,\\mu\\text{m}\\) wide. One plasma membrane has a thickness equal to \\(0.2\\%\\) of this width. Molecule X is transported out of the cell from a region of concentration \\(2\\) arbitrary units to a region of concentration \\(8\\) arbitrary units.</p><p>Which row gives the membrane thickness in nanometres (nm) and the transport process?</p>", "options": [{"html": "0.01 nm; diffusion", "label": "A", "assets": null}, {"html": "0.01 nm; active transport", "label": "B", "assets": null}, {"html": "0.02 nm; diffusion", "label": "C", "assets": null}, {"html": "0.02 nm; active transport", "label": "D", "assets": null}, {"html": "10 nm; diffusion", "label": "E", "assets": null}, {"html": "10 nm; active transport", "label": "F", "assets": null}, {"html": "20 nm; diffusion", "label": "G", "assets": null}, {"html": "20 nm; active transport", "label": "H", "assets": null}]}}, {"table": "esat_qb_questions", "qid": "ESAT-P1-0804-28048806", "expected": {"prompt_html": "Simplify<br>\\[(x^{2} + 5)(2x) x^{3/4}, \\quad x &gt; 0.\\]", "options": [{"html": "\\(2x^{9/4} + 10x^{1/4}\\)", "label": "A"}, {"html": "\\(2x^{5/4} + 10x^{-1/4}\\)", "label": "B"}, {"html": "\\(2x^{7/4} + 10x^{1/4}\\)", "label": "C"}, {"html": "\\(x^{9/4} + 5x^{1/4}\\)", "label": "D"}, {"html": "\\(2x^{3/4} + 10x^{-3/4}\\)", "label": "E"}], "answer": "A", "solution_html": "Since \\(x^{3/4} = x^{3/4}\\), \\(2x(x^{2} + 5) x^{3/4} = 2x^{3} + 10x x^{3/4} = 2x^{9/4} + 10x^{1/4}.\\)"}, "patch": {"prompt_html": "<p>Simplify</p><p>\\[(x^2+5)(2x)x^{-3/4},\\qquad x&gt;0.\\]</p>", "solution_html": "<p>Expand the brackets, then add the exponents when multiplying powers of \\(x\\):</p><p>\\[(x^2+5)(2x)x^{-3/4}=(2x^3+10x)x^{-3/4}=2x^{3-3/4}+10x^{1-3/4}=2x^{9/4}+10x^{1/4}.\\]</p><p>The answer is <strong>A</strong>.</p>"}}, {"table": "esat_qb_questions", "qid": "ESAT-P1-0805-7CA782B5", "expected": {"prompt_html": "For<br>\\[f(x) = 2x^{9/4} + 10x^{1/4},\\]<br>find \\(f'(x)\\).", "options": [{"html": "\\(\\frac{9}{2} x^{5/4} + 5 x^{-3/4}\\)", "label": "A"}, {"html": "\\(\\frac{9}{4} x^{5/4} + \\frac{5}{4} x^{-3/4}\\)", "label": "B"}, {"html": "\\(\\frac{9}{2} x^{9/4} + 5 x^{1/4}\\)", "label": "C"}, {"html": "\\(8 x^{9/4} + 30 x^{1/4}\\)", "label": "D"}, {"html": "\\(\\frac{9}{2} x^{5/4} - 5 x^{-3/4}\\)", "label": "E"}], "answer": "A", "solution_html": "Differentiate: \\(f'(x) = 2 \\cdot \\frac{9}{4} x^{5/4} + 10 \\cdot \\frac{1}{4} x^{-3/4} = \\frac{9}{2} x^{5/4} + 5 x^{-3/4}.\\)"}, "patch": {"prompt_html": "<p>For \\(x&gt;0\\), let</p><p>\\[f(x)=2x^{9/4}+10x^{1/4}.\\]</p><p>Find \\(f'(x)\\).</p>", "options": [{"html": "\\(\\frac{9}{2}x^{5/4}+\\frac{5}{2}x^{-3/4}\\)", "label": "A"}, {"html": "\\(\\frac{9}{4} x^{5/4} + \\frac{5}{4} x^{-3/4}\\)", "label": "B"}, {"html": "\\(\\frac{9}{2} x^{9/4} + 5 x^{1/4}\\)", "label": "C"}, {"html": "\\(8 x^{9/4} + 30 x^{1/4}\\)", "label": "D"}, {"html": "\\(\\frac{9}{2} x^{5/4} - 5 x^{-3/4}\\)", "label": "E"}], "solution_html": "<p>Apply the power rule to each term:</p><p>\\[\\frac{d}{dx}(2x^{9/4})=2\\cdot\\frac94x^{5/4}=\\frac92x^{5/4},\\]</p><p>\\[\\frac{d}{dx}(10x^{1/4})=10\\cdot\\frac14x^{-3/4}=\\frac52x^{-3/4}.\\]</p><p>Therefore \\[f'(x)=\\frac92x^{5/4}+\\frac52x^{-3/4}.\\]</p><p>In particular, \\(10\\times\\frac14=\\frac52\\), not \\(5\\). The answer is <strong>A</strong>.</p>"}}, {"table": "esat_qb_questions", "qid": "ESAT-P1-0685-0490625F", "expected": {"prompt_html": "<p>Set u_0 = \\frac{1}{4}, and for k \\ge 0 let u_{k+1} be determined by the recurrence \\[u_{k+1} = 2u_k - 2u_k^2.\\]\n</p>\n<p>This sequence tends to a limit; call it L. What is the least value of k such that \\[|u_k-L| \\le \\frac{1}{2^{1000}}?\\]\n</p>", "options": [{"html": "10", "label": "A"}, {"html": "87", "label": "B"}, {"html": "123", "label": "C"}, {"html": "329", "label": "D"}, {"html": "401", "label": "E"}], "answer": "A", "solution_html": "<p>Note that terms of the sequence (u_k) lie in the interval \\left(0,\\frac12\\right) and are strictly increasing.\n</p>\n<p>Since the sequence (u_k) tends to the limit L, we set u_{k+1}=u_k=L&gt;0.\n</p>\n<p>The given equation becomes \\[L=2L-2L^2,\\] from which L=\\frac12.\n</p>\n<p>The given inequality becomes \\[\\frac12-\\frac{1}{2^{1000}} \\leq u_k \\leq \\frac12+\\frac{1}{2^{1000}},\\] and we only need to consider \\frac12-\\frac{1}{\\(2^{1000}\\)} \\(\\leq\\) u_k.\n</p>\n<p>We have\n\\begin{alignat*}{8} u_0 &amp;= \\phantom{1}\\frac14 &amp;&amp;= \\frac{\\(2^1\\)-1}{\\(2^2\\)}, \\\\ u_1 &amp;= \\phantom{1}\\frac38 &amp;&amp;= \\frac{\\(2^2\\)-1}{\\(2^3\\)}, \\\\ u_2 &amp;= \\ \\frac{15}{32} &amp;&amp;= \\frac{\\(2^4\\)-1}{\\(2^5\\)}, \\\\ u_3 &amp;= \\frac{255}{512} &amp;&amp;= \\frac{\\(2^8\\)-1}{\\(2^9\\)}, \\\\ &amp; \\phantom{1111} \\vdots \\end{alignat*}\nBy induction, it can be proven that \\[u_k=\\frac{2^{2^k}-1}{2^{2^k+1}}=\\frac12-\\frac{1}{2^{2^k+1}}.\\]\nWe substitute this into the inequality, then solve for k:\n\\begin{align*} \\frac12-\\frac{1}{\\(2^{1000}\\)} &amp;\\(\\leq\\) \\frac12-\\frac{1}{2^{\\(2^k\\)+1}} \\\\ -\\frac{1}{\\(2^{1000}\\)} &amp;\\(\\leq\\) -\\frac{1}{2^{\\(2^k\\)+1}} \\\\ \\(2^{1000}\\) &amp;\\(\\leq\\) 2^{\\(2^k\\)+1} \\\\ 1000 &amp;\\(\\leq\\) \\(2^k\\)+1. \\end{align*}\nSince \\(2^9\\)+1 \\(\\leq\\) 1000 \\(\\leq\\) \\(2^{10}\\)+1, the least such value of k is \\(\\boxed{\\textbf{(A)}\\: 10}\\).\n</p>", "nice_tip_html": "Try to find a closed form for the recurrence by testing the first few terms and spotting a pattern, then use inequalities on the closed form to solve for k.", "paper": "ESAT Mathematics 1"}, "patch": {"prompt_html": "<p>Set \\(u_0=\\frac14\\). For integers \\(k\\geq0\\), define the sequence by</p><p>\\[u_{k+1}=2u_k-2u_k^2.\\]</p><p>The sequence tends to a limit \\(L\\). What is the least value of \\(k\\) such that</p><p>\\[|u_k-L|\\leq\\frac{1}{2^{1000}}?\\]</p>", "solution_html": "<p>The useful substitution is \\(v_k=1-2u_k\\). Then</p><p>\\[v_{k+1}=1-2(2u_k-2u_k^2)=(1-2u_k)^2=v_k^2,\\qquad v_0=\\frac12.\\]</p><p>Each step squares the previous value: \\(\\frac12,\\frac14,\\frac1{16},\\frac1{256},\\ldots\\). Hence</p><p>\\[v_k=2^{-2^k},\\qquad u_k=\\frac12-\\frac{1}{2^{2^k+1}}.\\]</p><p>Thus \\(L=\\frac12\\), and the required inequality is equivalent to</p><p>\\[\\frac{1}{2^{2^k+1}}\\leq\\frac{1}{2^{1000}}\\quad\\Longleftrightarrow\\quad2^k+1\\geq1000.\\]</p><p>At \\(k=9\\), \\(2^9+1=513&lt;1000\\). At \\(k=10\\), \\(2^{10}+1=1025\\geq1000\\). Therefore the least value is <strong>10, option A</strong>.</p>", "nice_tip_html": "<p>Try \\(v_k=1-2u_k\\). The quadratic recurrence becomes \\(v_{k+1}=v_k^2\\), so its powers double at each step.</p>", "paper": "ESAT Mathematics 2"}}, {"table": "tmua_qb_questions", "qid": "TMUA-P1-0685-0490625F", "expected": {"prompt_html": "<p>Set u_0 = \\frac{1}{4}, and for k \\ge 0 let u_{k+1} be determined by the recurrence \\[u_{k+1} = 2u_k - 2u_k^2.\\]\n</p>\n<p>This sequence tends to a limit; call it L. What is the least value of k such that \\[|u_k-L| \\le \\frac{1}{2^{1000}}?\\]\n</p>", "options": [{"html": "10", "label": "A"}, {"html": "87", "label": "B"}, {"html": "123", "label": "C"}, {"html": "329", "label": "D"}, {"html": "401", "label": "E"}], "answer": "A", "solution_html": "<p>Note that terms of the sequence (u_k) lie in the interval \\left(0,\\frac12\\right) and are strictly increasing.\n</p>\n<p>Since the sequence (u_k) tends to the limit L, we set u_{k+1}=u_k=L&gt;0.\n</p>\n<p>The given equation becomes \\[L=2L-2L^2,\\] from which L=\\frac12.\n</p>\n<p>The given inequality becomes \\[\\frac12-\\frac{1}{2^{1000}} \\leq u_k \\leq \\frac12+\\frac{1}{2^{1000}},\\] and we only need to consider \\frac12-\\frac{1}{\\(2^{1000}\\)} \\(\\leq\\) u_k.\n</p>\n<p>We have\n\\begin{alignat*}{8} u_0 &amp;= \\phantom{1}\\frac14 &amp;&amp;= \\frac{\\(2^1\\)-1}{\\(2^2\\)}, \\\\ u_1 &amp;= \\phantom{1}\\frac38 &amp;&amp;= \\frac{\\(2^2\\)-1}{\\(2^3\\)}, \\\\ u_2 &amp;= \\ \\frac{15}{32} &amp;&amp;= \\frac{\\(2^4\\)-1}{\\(2^5\\)}, \\\\ u_3 &amp;= \\frac{255}{512} &amp;&amp;= \\frac{\\(2^8\\)-1}{\\(2^9\\)}, \\\\ &amp; \\phantom{1111} \\vdots \\end{alignat*}\nBy induction, it can be proven that \\[u_k=\\frac{2^{2^k}-1}{2^{2^k+1}}=\\frac12-\\frac{1}{2^{2^k+1}}.\\]\nWe substitute this into the inequality, then solve for k:\n\\begin{align*} \\frac12-\\frac{1}{\\(2^{1000}\\)} &amp;\\(\\leq\\) \\frac12-\\frac{1}{2^{\\(2^k\\)+1}} \\\\ -\\frac{1}{\\(2^{1000}\\)} &amp;\\(\\leq\\) -\\frac{1}{2^{\\(2^k\\)+1}} \\\\ \\(2^{1000}\\) &amp;\\(\\leq\\) 2^{\\(2^k\\)+1} \\\\ 1000 &amp;\\(\\leq\\) \\(2^k\\)+1. \\end{align*}\nSince \\(2^9\\)+1 \\(\\leq\\) 1000 \\(\\leq\\) \\(2^{10}\\)+1, the least such value of k is \\(\\boxed{\\textbf{(A)}\\: 10}\\).\n</p>", "nice_tip_html": "Try to find a closed form for the recurrence by testing the first few terms and spotting a pattern, then use inequalities on the closed form to solve for k."}, "patch": {"prompt_html": "<p>Set \\(u_0=\\frac14\\). For integers \\(k\\geq0\\), define the sequence by</p><p>\\[u_{k+1}=2u_k-2u_k^2.\\]</p><p>The sequence tends to a limit \\(L\\). What is the least value of \\(k\\) such that</p><p>\\[|u_k-L|\\leq\\frac{1}{2^{1000}}?\\]</p>", "solution_html": "<p>The useful substitution is \\(v_k=1-2u_k\\). Then</p><p>\\[v_{k+1}=1-2(2u_k-2u_k^2)=(1-2u_k)^2=v_k^2,\\qquad v_0=\\frac12.\\]</p><p>Each step squares the previous value: \\(\\frac12,\\frac14,\\frac1{16},\\frac1{256},\\ldots\\). Hence</p><p>\\[v_k=2^{-2^k},\\qquad u_k=\\frac12-\\frac{1}{2^{2^k+1}}.\\]</p><p>Thus \\(L=\\frac12\\), and the required inequality is equivalent to</p><p>\\[\\frac{1}{2^{2^k+1}}\\leq\\frac{1}{2^{1000}}\\quad\\Longleftrightarrow\\quad2^k+1\\geq1000.\\]</p><p>At \\(k=9\\), \\(2^9+1=513&lt;1000\\). At \\(k=10\\), \\(2^{10}+1=1025\\geq1000\\). Therefore the least value is <strong>10, option A</strong>.</p>", "nice_tip_html": "<p>Try \\(v_k=1-2u_k\\). The quadratic recurrence becomes \\(v_{k+1}=v_k^2\\), so its powers double at each step.</p>"}}, {"table": "tmua_qb_questions", "qid": "TMUA-P1-0804-28048806", "expected": {"prompt_html": "Simplify<br>\\[(x^{2} + 5)(2x) x^{3/4}, \\quad x &gt; 0.\\]", "options": [{"html": "\\(2x^{9/4} + 10x^{1/4}\\)", "label": "A"}, {"html": "\\(2x^{5/4} + 10x^{-1/4}\\)", "label": "B"}, {"html": "\\(2x^{7/4} + 10x^{1/4}\\)", "label": "C"}, {"html": "\\(x^{9/4} + 5x^{1/4}\\)", "label": "D"}, {"html": "\\(2x^{3/4} + 10x^{-3/4}\\)", "label": "E"}], "answer": "A", "solution_html": "Since \\(x^{3/4} = x^{3/4}\\), \\(2x(x^{2} + 5) x^{3/4} = 2x^{3} + 10x x^{3/4} = 2x^{9/4} + 10x^{1/4}.\\)"}, "patch": {"prompt_html": "<p>Simplify</p><p>\\[(x^2+5)(2x)x^{-3/4},\\qquad x&gt;0.\\]</p>", "solution_html": "<p>Expand the brackets, then add the exponents when multiplying powers of \\(x\\):</p><p>\\[(x^2+5)(2x)x^{-3/4}=(2x^3+10x)x^{-3/4}=2x^{3-3/4}+10x^{1-3/4}=2x^{9/4}+10x^{1/4}.\\]</p><p>The answer is <strong>A</strong>.</p>"}}, {"table": "tmua_qb_questions", "qid": "TMUA-P1-0805-7CA782B5", "expected": {"prompt_html": "For<br>\\[f(x) = 2x^{9/4} + 10x^{1/4},\\]<br>find \\(f'(x)\\).", "options": [{"html": "\\(\\frac{9}{2} x^{5/4} + 5 x^{-3/4}\\)", "label": "A"}, {"html": "\\(\\frac{9}{4} x^{5/4} + \\frac{5}{4} x^{-3/4}\\)", "label": "B"}, {"html": "\\(\\frac{9}{2} x^{9/4} + 5 x^{1/4}\\)", "label": "C"}, {"html": "\\(8 x^{9/4} + 30 x^{1/4}\\)", "label": "D"}, {"html": "\\(\\frac{9}{2} x^{5/4} - 5 x^{-3/4}\\)", "label": "E"}], "answer": "A", "solution_html": "Differentiate: \\(f'(x) = 2 \\cdot \\frac{9}{4} x^{5/4} + 10 \\cdot \\frac{1}{4} x^{-3/4} = \\frac{9}{2} x^{5/4} + 5 x^{-3/4}.\\)"}, "patch": {"prompt_html": "<p>For \\(x&gt;0\\), let</p><p>\\[f(x)=2x^{9/4}+10x^{1/4}.\\]</p><p>Find \\(f'(x)\\).</p>", "options": [{"html": "\\(\\frac{9}{2}x^{5/4}+\\frac{5}{2}x^{-3/4}\\)", "label": "A"}, {"html": "\\(\\frac{9}{4} x^{5/4} + \\frac{5}{4} x^{-3/4}\\)", "label": "B"}, {"html": "\\(\\frac{9}{2} x^{9/4} + 5 x^{1/4}\\)", "label": "C"}, {"html": "\\(8 x^{9/4} + 30 x^{1/4}\\)", "label": "D"}, {"html": "\\(\\frac{9}{2} x^{5/4} - 5 x^{-3/4}\\)", "label": "E"}], "solution_html": "<p>Apply the power rule to each term:</p><p>\\[\\frac{d}{dx}(2x^{9/4})=2\\cdot\\frac94x^{5/4}=\\frac92x^{5/4},\\]</p><p>\\[\\frac{d}{dx}(10x^{1/4})=10\\cdot\\frac14x^{-3/4}=\\frac52x^{-3/4}.\\]</p><p>Therefore \\[f'(x)=\\frac92x^{5/4}+\\frac52x^{-3/4}.\\]</p><p>In particular, \\(10\\times\\frac14=\\frac52\\), not \\(5\\). The answer is <strong>A</strong>.</p>"}}]$payload$::jsonb;
  item jsonb;
  actual jsonb;
  patch jsonb;
  row_record record;
  answer_record record;
  corrected_state jsonb;
  answers jsonb;
  replacement jsonb;
  changed boolean;
  changed_count integer;
  content_count integer := 0;
  progress_count integer := 0;
  state_count integer := 0;
  event_count integer := 0;
  esat_ids text[] := ARRAY['ESAT-P1-0804-28048806','ESAT-P1-0805-7CA782B5','ESAT-BIO-0115','d46204de-e559-496e-9dca-e027f12b191e','ec89dc41-c644-47ca-83a7-c67d6d331bb9','7d5968aa-95a8-4ac0-9138-234743509be3'];
  tmua_ids text[] := ARRAY['TMUA-P1-0804-28048806','TMUA-P1-0805-7CA782B5','1364','1365','SB-1364','SB-1365'];
BEGIN
  IF EXISTS (SELECT 1 FROM public._question_fix_backups b WHERE b.fix_key = repair_key) THEN
    RAISE EXCEPTION 'This repair has already been applied; inspect its snapshots before rerunning';
  END IF;
  FOR item IN SELECT value FROM jsonb_array_elements(fixes) LOOP
    IF item->>'table' NOT IN ('esat_qb_questions','tmua_qb_questions') THEN
      RAISE EXCEPTION 'Unexpected table';
    END IF;
    EXECUTE format('SELECT to_jsonb(q) FROM public.%I q WHERE qid=$1 FOR UPDATE', item->>'table')
      INTO actual USING item->>'qid';
    IF actual IS NULL OR NOT actual @> (item->'expected') THEN
      RAISE EXCEPTION 'Question changed since review: %', item->>'qid';
    END IF;
    INSERT INTO public._question_fix_backups(fix_key,table_name,qid,row_data)
      VALUES(repair_key,item->>'table',item->>'qid',actual);
    patch := item->'patch';
    EXECUTE format('UPDATE public.%I SET
      prompt_html = COALESCE($1->>''prompt_html'',prompt_html),
      options = COALESCE($1->''options'',options),
      solution_html = COALESCE($1->>''solution_html'',solution_html),
      nice_tip_html = COALESCE($1->>''nice_tip_html'',nice_tip_html),
      paper = COALESCE($1->>''paper'',paper),
      source_json = COALESCE(source_json,''{}''::jsonb) || $1,
      updated_at = now()
      WHERE qid=$2', item->>'table') USING patch,item->>'qid';
    GET DIAGNOSTICS changed_count = ROW_COUNT;
    IF changed_count <> 1 THEN RAISE EXCEPTION 'Expected exactly one row for %',item->>'qid'; END IF;
    IF item->>'table' = 'esat_qb_questions' THEN
      -- Keep both flattened and nested import snapshots aligned so a restore or
      -- later import cannot silently reintroduce the old wording/options.
      UPDATE public.esat_qb_questions q
      SET raw_json = CASE WHEN jsonb_typeof(q.raw_json)='object'
        THEN q.raw_json || patch || jsonb_build_object('source_json',q.source_json)
        ELSE q.raw_json END
      WHERE q.qid=item->>'qid';
    END IF;
    EXECUTE format('SELECT to_jsonb(q) FROM public.%I q WHERE qid=$1',item->>'table')
      INTO actual USING item->>'qid';
    IF NOT actual @> patch OR NOT actual->'source_json' @> patch THEN
      RAISE EXCEPTION 'Content verification failed for %',item->>'qid';
    END IF;
    content_count := content_count+1;
  END LOOP;

  -- These three question versions had no unique valid answer. Offer a clean
  -- reattempt, preserving flags and time spent instead of assigning a new score
  -- to an answer selected against different wording/options.
  FOR row_record IN SELECT p.* FROM public.qb_progress p WHERE
    (p.product='esat-question-bank' AND p.question_id=ANY(esat_ids)) OR
    (p.product='tmua-question-bank' AND p.question_id=ANY(tmua_ids))
    FOR UPDATE
  LOOP
    INSERT INTO public._question_fix_backups(fix_key,table_name,qid,row_data)
      VALUES(repair_key,'qb_progress',row_record.id::text,to_jsonb(row_record));
    UPDATE public.qb_progress SET status='seen',selected_answer=NULL,
      answer_submitted_at=NULL,answer_elapsed_seconds=NULL,submission_id=NULL,updated_at=now()
      WHERE id=row_record.id;
    progress_count := progress_count+1;
  END LOOP;

  FOR row_record IN SELECT p.* FROM public.user_progress p
    WHERE p.key='app_state' AND p.product IN ('esat-question-bank','tmua-question-bank')
      AND jsonb_typeof(p.data->'parsed'->'answers')='object'
      AND ((p.product='esat-question-bank' AND (p.data->'parsed'->'answers') ?| esat_ids)
        OR (p.product='tmua-question-bank' AND (p.data->'parsed'->'answers') ?| tmua_ids)
        OR (p.product='esat-question-bank' AND EXISTS(
          SELECT 1 FROM jsonb_each(p.data->'parsed'->'answers') old_answer
          JOIN public._question_fix_backups b
            ON b.fix_key=repair_key AND b.table_name='esat_qb_questions'
            AND b.qid=ANY(esat_ids)
            AND b.row_data->>'solution_html'=old_answer.value->>'solution_html'
          WHERE old_answer.key ~ '^[0-9]+$')))
      FOR UPDATE
  LOOP
    corrected_state := row_record.data->'parsed';
    answers := corrected_state->'answers';
    changed := false;
    FOR answer_record IN SELECT key,value FROM jsonb_each(answers) LOOP
      IF (row_record.product='esat-question-bank' AND answer_record.key=ANY(esat_ids)) OR
         (row_record.product='tmua-question-bank' AND answer_record.key=ANY(tmua_ids)) OR
         -- Legacy ESAT numeric keys are not current display labels. Only reset
         -- one when its cached solution exactly identifies a reviewed question.
         (row_record.product='esat-question-bank' AND answer_record.key ~ '^[0-9]+$' AND
          EXISTS(SELECT 1 FROM public._question_fix_backups b WHERE b.fix_key=repair_key
            AND b.table_name='esat_qb_questions' AND b.qid=ANY(esat_ids)
            AND b.row_data->>'solution_html'=answer_record.value->>'solution_html'))
      THEN
        replacement := (answer_record.value - ARRAY['answer','solution_html']) ||
          jsonb_build_object('selected','','checked',false,'isCorrect',false,'locked',false);
        answers := jsonb_set(answers,ARRAY[answer_record.key],replacement);
        changed := true;
      END IF;
    END LOOP;
    IF changed THEN
      INSERT INTO public._question_fix_backups(fix_key,table_name,qid,row_data)
        VALUES(repair_key,'user_progress',row_record.user_id::text||':'||row_record.product||':'||row_record.key,to_jsonb(row_record));
      corrected_state := jsonb_set(corrected_state,'{answers}',answers);
      UPDATE public.user_progress SET data=data || jsonb_build_object(
        'parsed',corrected_state,'raw',corrected_state::text,'saved_at',now()),updated_at=now()
        WHERE user_id=row_record.user_id AND product=row_record.product AND key=row_record.key;
      state_count := state_count+1;
    END IF;
  END LOOP;

  FOR row_record IN SELECT e.* FROM public.tmua_qb_attempt_events e WHERE
    (e.product='esat-question-bank' AND e.question_id=ANY(esat_ids)) OR
    (e.product='tmua-question-bank' AND e.question_id=ANY(tmua_ids)) FOR UPDATE
  LOOP
    INSERT INTO public._question_fix_backups(fix_key,table_name,qid,row_data)
      VALUES(repair_key,'tmua_qb_attempt_events',row_record.id::text,to_jsonb(row_record));
    UPDATE public.tmua_qb_attempt_events SET predictor_eligible=false,
      exclusion_reason='invalid_question_before_20261012_correction',
      metadata=COALESCE(metadata,'{}'::jsonb)||jsonb_build_object('content_fix',repair_key)
      WHERE id=row_record.id;
    event_count := event_count+1;
  END LOOP;
  IF content_count<>7 THEN RAISE EXCEPTION 'Expected seven content repairs'; END IF;
  RAISE NOTICE 'Verified: % content, % canonical progress, % saved states, % excluded historical attempts',
    content_count,progress_count,state_count,event_count;
END;
$fix$;

SELECT table_name,count(*) AS backed_up_rows FROM public._question_fix_backups
WHERE fix_key='email_bug_audit_20261006_20261012_v1' GROUP BY table_name ORDER BY table_name;
