# Independent cross-review of Statistics & Probability

Reviewer: Calculus II content author. Review covered every hard question Q134–149; representative medium questions Q83, Q91, Q96, Q102, Q109, Q115, Q120, Q125, Q128; and easy Q57, Q74. No files in the Statistics bank were modified by this reviewer.

## Findings sent to the integrator

1. **Q83(b): exact regression intersection.** The sample means are exactly 13.75 and 15.25. Recommend stating `(13.75, 15.25)` rather than the displayed `(13.8, 15.2)`. The latter y-coordinate is a consequence of half-even numerical formatting; standard three-significant-figure rounding of 15.25 is 15.3. Regression of x on y independently gives slope 1.110183639399 and intercept −3.180300500835, so the estimate at y=12 is 10.141903171953, or 10 marks as published.
2. **Q109(c): clarify the joint-event working.** The first method line computes `P(D1 ∩ D3)=0.541875`, while the next line jumps to the required joint probability 0.308. The final answer is correct. Recommend directly showing `P(D1 ∩ R3)=0.85[0.75·0.25+0.25·0.7]=0.308125`, followed by division by `P(R3)=0.392875`, yielding 0.784282532612.

No substantive algebra or probability errors were found in the reviewed hard questions. The minor findings above concern rounding and clarity of the written scheme.

## Independent numerical evidence

Computed directly with SciPy normal/binomial distribution functions and a bracketed polynomial root, independently of the authoring generator:

| Question | Quantity | Recomputed value |
|---|---|---|
|134(a)|Central normal probability|0.545179081489|
|134(a)|Expected count above 340|40.398806007508|
|134(a)|Binomial tail at least 45|0.225756030068|
|134(b)|Sigma|62.424331685790|
|134(b)|Conditional probability / expected count|0.484849054691 / 116.363773125839|
|141|CDF at n=11,12,13|0.006909937034 / 0.008289084180 / 0.009538478923|
|143(d)|Unique median|1.448983918001|
|143(e)|Binomial tail at least four|0.992805180372|
|146(c)|Binomial CDF at six|0.861015217029|
|146(d)|At-least-one probability at n=6,7|0.960599587942 / 0.977016426299|
|147(c)|Binomial tail above four|0.089765667419|
|148(b,c)|Real-root probability / conditional probability|0.045500263896 / 0.272950738920|
|149(e)|At-least-four probability at N=14,15|0.478660039604 / 0.538713123649|
|115(b,c,d)|Elite / exactly-one / nested tail|0.161281317821 / 0.401621448554 / 0.267863717880|
|115(e,f)|Upper cutoff / new standard deviation|5.804992075240 / 0.333585499164|
|96(b)|Normal interval probability|0.850430491540|
|120(a,d,e)|Drive interval / on-time probability / days|0.040048468338 / 0.930562500667 / 205|
|128(c,d)|Posterior type-A / binomial tail|0.092907432215 / 0.308256755052|

Manually rederived the exact rational/proof results in Q135–140, Q144–147 and Q149: normalization, variance algebra, independence, geometric-series convergence, derangements by inclusion–exclusion, cosine-density quartiles, median events, minimum integer bag counts, and consecutive negative-binomial probability ratios. The Q148 root-conditioning argument correctly maps the smaller absolute root below one to `|A|>5/2`.
