-- ===========================
-- Thriving Scholars TMUA seed (13 tests)
-- Run AFTER schema
-- ===========================

insert into public.tests
(slug,title,kind,paper,duration_minutes,topics,cover_image_url,solution_pdf_url,test_url,sort_order,is_free,is_public)
values
('topic-test-1-algebra-functions','Topic Test 1 (Algebra & Functions)','topic','paper1',45, array['Algebra','Functions'], '/tmua/assets/picture1.png', null, '/tmua/practice-tests/topic-test-1-algebra-functions.html', 1, true, true),

('tmua-mock-test-1','TMUA Mock Test 1 (Paper 1)','mock','paper1',75, array['Algebra','Sequences','Functions','Geometry'], '/tmua/assets/picture1.png', null, '/tmua/practice-tests/tmua-mock-test-1.html', 2, false, true),
('tmua-mock-test-2','TMUA Mock Test 2 (Paper 1)','mock','paper1',75, array['Graphs','Trigonometry','Logarithms'], '/tmua/assets/picture1.png', null, '/tmua/practice-tests/tmua-mock-test-2.html', 3, false, true),
('tmua-mock-test-3','TMUA Mock Test 3 (Paper 1)','mock','paper1',75, array['Calculus'], '/tmua/assets/picture1.png', null, '/tmua/practice-tests/tmua-mock-test-3.html', 4, false, true),

('tmua-mock-test-4','TMUA Mock Test 4 (Paper 2)','mock','paper2',75, array['Logic','Proofs'], '/tmua/assets/picture1.png', null, '/tmua/practice-tests/tmua-mock-test-4.html', 5, false, true),
('tmua-mock-test-5','TMUA Mock Test 5 (Paper 1)','mock','paper1',75, array['All Topics'], '/tmua/assets/picture1.png', null, '/tmua/practice-tests/tmua-mock-test-5.html', 6, false, true),
('tmua-mock-test-6','TMUA Mock Test 6 (Paper 2)','mock','paper2',75, array['All Topics'], '/tmua/assets/picture1.png', null, '/tmua/practice-tests/tmua-mock-test-6.html', 7, false, true),

('tmua-official-sample-1','TMUA Official Sample 1 (Paper 1)','official_sample','paper1',75, array['All Topics'], '/tmua/assets/picture2.png', null, '/tmua/practice-tests/tmua-official-sample-1.html', 8, true, true),
('tmua-official-sample-2','TMUA Official Sample 2 (Paper 1)','official_sample','paper1',75, array['All Topics'], '/tmua/assets/picture2.png', null, '/tmua/practice-tests/tmua-official-sample-2.html', 9, true, true),

('tmua-mock-full-test-1','TMUA Mock Full Test 1 (P1+P2)','full_mock','paper1+paper2',150, array['All Topics'], '/tmua/assets/picture2.png', null, '/tmua/practice-tests/tmua-mock-full-test-1.html', 10, false, true),
('tmua-mock-full-test-2','TMUA Mock Full Test 2 (P1+P2)','full_mock','paper1+paper2',150, array['All Topics'], '/tmua/assets/picture2.png', null, '/tmua/practice-tests/tmua-mock-full-test-2.html', 11, false, true),

('tmua-official-2022','TMUA Official 2022 (P1+P2)','official_past_paper','paper1+paper2',150, array['All Topics'], '/tmua/assets/picture2.png', null, '/tmua/practice-tests/tmua-official-2022.html', 12, true, true),
('tmua-official-2023','TMUA Official 2023 (P1+P2)','official_past_paper','paper1+paper2',150, array['All Topics'], '/tmua/assets/picture2.png', null, '/tmua/practice-tests/tmua-official-2023.html', 13, true, true)
on conflict (slug) do nothing;