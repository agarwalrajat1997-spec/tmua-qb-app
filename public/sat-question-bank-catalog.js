/* Navigation taxonomy only. Original question IDs, content and progress are unchanged. */
(function (root) {
  'use strict';
  const domains = [
    { id: 'algebra', paper: 'Math', code: '01', title: 'Algebra', description: 'Build confidence with linear equations, systems, inequalities and straight-line graphs.', groups: { linear: 'Linear equations & word problems', systems: 'Systems of linear equations', inequalities: 'Inequalities & regions', functions: 'Linear functions & graphs' } },
    { id: 'advanced-math', paper: 'Math', code: '02', title: 'Advanced Math', description: 'Explore expressions, quadratics, nonlinear equations and functions.', groups: { expressions: 'Expressions, exponents & radicals', quadratics: 'Quadratics & polynomial equations', rational: 'Rational & radical equations', nonlinear: 'Nonlinear systems', functions: 'Functions, graphs & transformations', exponential: 'Exponential growth & decay' } },
    { id: 'data-analysis', paper: 'Math', code: '03', title: 'Problem-Solving & Data Analysis', description: 'Connect ratios and percentages with data, probability and statistical reasoning.', groups: { ratios: 'Ratios, rates, fractions & units', percentages: 'Percentages & proportional change', statistics: 'Data, averages & distributions', models: 'Scatterplots & statistical models', probability: 'Probability', inference: 'Statistical claims & inference' } },
    { id: 'geometry', paper: 'Math', code: '04', title: 'Geometry & Trigonometry', description: 'Work with angles, triangles, circles, area, volume and trigonometry.', groups: { angles: 'Lines & angles', triangles: 'Triangles & similarity', trig: 'Right triangles & trigonometry', circles: 'Circles, arcs & sectors', measures: 'Area, volume & spatial reasoning' } },
    { id: 'strategies', paper: 'Math', code: '+', title: 'Math Problem-Solving Strategies', description: 'Practise choosing values, testing cases and working backwards.', supplementary: true, groups: { plug: 'Plugging in values', testing: 'Testing cases', backwards: 'Working backwards' } },
    { id: 'information', paper: 'Reading and Writing', code: '01', title: 'Information & Ideas', description: 'Find central ideas, draw inferences and use evidence from texts and graphics.', groups: { ideas: 'Central ideas & details', inference: 'Inferences & logical completion', evidence: 'Textual evidence', quantitative: 'Quantitative evidence & graphics', reading: 'Reading comprehension' } },
    { id: 'craft', paper: 'Reading and Writing', code: '02', title: 'Craft & Structure', description: 'Explore vocabulary in context, an author’s purpose and connections between texts.', groups: { words: 'Words in context', purpose: 'Text structure & purpose', connections: 'Cross-text connections & paired passages' } },
    { id: 'expression', paper: 'Reading and Writing', code: '03', title: 'Expression of Ideas', description: 'Connect ideas with transitions and shape notes into effective writing.', groups: { transitions: 'Transitions', synthesis: 'Rhetorical synthesis' } },
    { id: 'conventions', paper: 'Reading and Writing', code: '04', title: 'Standard English Conventions', description: 'Strengthen sentence structure, punctuation, grammar and usage.', groups: { boundaries: 'Sentence boundaries & punctuation', verbs: 'Verbs, tense & agreement', pronouns: 'Pronouns & possessives', modifiers: 'Modifiers & supplements', structure: 'Form, structure & sense' } },
  ];
  const normalize = value => String(value || '').toLowerCase().replace(/[–—-]/g, ' ').replace(/\s+/g, ' ').trim();
  function classify(q) {
    const t = normalize(q.topic), s = normalize(q.subtopic);
    const pair = (domain, category) => ({ domain, category });
    // These legacy labels cover nonlinear questions; checked against their published stems.
    if (['sat-xlsx-000239', 'sat-xlsx-000244', 'sat-xlsx-000255'].includes(q.qid)) return pair('advanced-math', 'nonlinear');
    if (q.paper === 'Reading and Writing') {
      if (/transition/.test(s)) return pair('expression', 'transitions');
      if (/rhetorical|synthesis/.test(s)) return pair('expression', 'synthesis');
      if (/words in context/.test(s)) return pair('craft', 'words');
      if (/cross text|paired passage/.test(s)) return pair('craft', 'connections');
      if (/text structure|purpose|main function/.test(s)) return pair('craft', 'purpose');
      if (/quantitative|infographic/.test(s)) return pair('information', 'quantitative');
      if (/evidence/.test(s)) return pair('information', 'evidence');
      if (/inference|logical completion/.test(s)) return pair('information', 'inference');
      if (/main idea|central idea/.test(s)) return pair('information', 'ideas');
      if (/pronoun|possessive|plurals/.test(s)) return pair('conventions', 'pronouns');
      if (/verb/.test(s)) return pair('conventions', 'verbs');
      if (/modifier|appositive|supplement/.test(s)) return pair('conventions', 'modifiers');
      if (/boundar|punctuation|complex series/.test(s)) return pair('conventions', 'boundaries');
      if (/sentence structure|form, structure/.test(s)) return pair('conventions', 'structure');
      if (s === 'general reading') return pair('information', 'reading');
    } else if (q.paper === 'Math') {
      if (t === 'overall strategy') return pair('strategies', /plug/.test(s) ? 'plug' : /backward/.test(s) ? 'backwards' : 'testing');
      if (/geometry/.test(t)) {
        if (/circle|\barcs?\b|\bsectors?\b|tangent/.test(s)) return pair('geometry', 'circles');
        if (/trig|right triangle|special triangle/.test(s)) return pair('geometry', 'trig');
        if (/area|volume|cube|cylinder|three dimensional/.test(s)) return pair('geometry', 'measures');
        if (/triangle|similar|congruen/.test(s)) return pair('geometry', 'triangles');
        return pair('geometry', 'angles');
      }
      if (/percent/.test(s)) return pair('data-analysis', 'percentages');
      if (/\bratios?\b|proportion|\brates?\b|unit|fraction/.test(s)) return pair('data-analysis', 'ratios');
      if (/probability/.test(s)) return pair('data-analysis', 'probability');
      if (/statistical claim|sample statistic|margin of error/.test(s)) return pair('data-analysis', 'inference');
      if (/scatterplot|correlation|best fit|residual|two variable data|interpreting linear models/.test(s)) return pair('data-analysis', 'models');
      if (/average|chart|table/.test(s) && !/function/.test(s) || /one variable data/.test(s)) return pair('data-analysis', 'statistics');
      if (/inequalit|linear programming/.test(s)) return pair('algebra', 'inequalities');
      if (/nonlinear.*two variables|squared variables|difference of squares and systems|intersections? of graphs/.test(s)) return pair('advanced-math', 'nonlinear');
      if (/system/.test(s)) return pair('algebra', 'systems');
      if (/quadratic|vertex form/.test(s)) return pair('advanced-math', 'quadratics');
      if (/rational equation|radical equation/.test(s)) return pair('advanced-math', 'rational');
      if (/exponential growth|exponential decay/.test(s)) return pair('advanced-math', 'exponential');
      if (/exponent|radical|polynomial|identit|expression|difference of squares|factoring/.test(s)) return pair('advanced-math', 'expressions');
      if (/nonlinear equations/.test(s)) return pair('advanced-math', 'quadratics');
      if (/\blinear function|parallel lines|perpendicular lines/.test(s)) return pair('algebra', 'functions');
      if (/function|graph|domain|range/.test(s)) return pair('advanced-math', 'functions');
      if (/equation|translating words/.test(s)) return pair('algebra', 'linear');
    }
    // New or unrecognised labels stay accessible without silently guessing a topic.
    return pair('other', 'other');
  }
  function catalogFor(paper, questions) {
    const result = domains.filter(d => !paper || d.paper === paper);
    if (questions.some(q => (!paper || q.paper === paper) && q.domain === 'other')) result.push({ id: 'other', paper: paper || '', code: '+', title: 'More practice', description: 'Additional questions available in this section.', groups: { other: 'Additional practice' } });
    return result;
  }
  const api = { domains, classify, catalogFor };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.SATCatalog = api;
})(typeof window === 'undefined' ? globalThis : window);

