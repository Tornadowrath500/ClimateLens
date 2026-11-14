# Project Context & Continuity Handoff

> Temporary working document for future AI assistants, coding agents, and human teammates.  
> The team intends to delete this file after the project is complete. Until then, treat it as the main continuity brief and read it before proposing major changes.

**Last updated:** 2026-11-14  
**Repository:** `Tornadowrath500/ClimateLens`  
**Current product direction:** FairLens  
**Status:** Starter skeleton; not yet a validated, completed fairness-audit application.

---

## 1. What this project is

FairLens is an educational, human-centered model-auditing tool. Its purpose is to help a person understand how a predictive model behaves, what evidence supports its results, whether outcomes differ across groups, and what trade-offs follow from changing model choices.

The initial case study is a historical credit-risk classifier using the UCI Statlog (German Credit Data) benchmark.

**Product promise:** make model behavior and its limitations understandable to a human reviewer. Do not make consequential decisions for people.

FairLens is not:
- a real loan approval or credit-scoring service;
- a tool for evaluating actual applicants;
- proof that a model is fair or legally compliant;
- a generic AI chatbot or a wrapper around a paid LLM API;
- a system that reduces fairness to one overall score.

Use language such as **favorable prediction rate** or **Good-risk classification rate**, not “approval rate,” unless explicitly explaining that this is only a proxy label. The benchmark contains historical risk labels, not records of actual lender approval decisions.

## 2. Why this direction was chosen

The team is participating in the Veritas AI International High School Hackathon 2026. The goal is to produce a competitive, genuinely working submission, with an ambition to contend for Gold and the associated Arecibo AI internship. This is an ambition, not an outcome to promise.

The project direction was selected to balance:
- implementability within a short hackathon window;
- enough meaningful features to demonstrate depth;
- a clear, demonstrable user problem;
- measurable technical work rather than a superficial interface;
- room for improvement without making the first version unfinishable;
- responsible, transparent presentation of model outputs.

The user originally explored ClimateLens and asked to preserve its values, not necessarily its code or climate-specific subject matter. Those values are transparency, visible assumptions, evidence, clarity, and human-centered design. FairLens is the current project direction. Do not switch back to climate forecasting or another idea without discussing the trade-off with the user.

## 3. Competition context and practical constraints

The team has three members. The competition submission information supplied to the team states:
- the submission window closes **Sunday, November 15, 2026 at 11:59 PM Eastern (8:59 PM Pacific)**;
- one team member submits for the team and enters all members' information;
- submission includes an accessible GitHub repository or Colab and a one-page write-up;
- a two-minute demo video is optional but recommended;
- resubmissions are allowed, with the latest submission used;
- a simple, working project is preferable to an ambitious incomplete one;
- all project code must be written within the official competition window; check the official rules for treatment of any starter material or AI-generated files and disclose tools/contributions accurately.

The team should verify the official competition page and organizer instructions before relying on dates or procedural details:
- Competition page: https://climatelens-qltf.onrender.com/

The team's stated priority is strong execution and a compelling demonstration. Do not optimize for feature count at the expense of correctness, reproducibility, and a complete end-to-end story.

## 4. Dataset and evidence

Initial benchmark:
- **UCI Statlog (German Credit Data)**: https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data
- 1,000 historical examples, 20 input features.
- Original target encoding: 1 = Good, 2 = Bad (confirm against the source and downloaded data in code).
- Historical data donated in 1994 from a German context.
- The source provides an asymmetric cost matrix: classifying an actually Bad-risk case as Good has five times the cost of the reverse error.

Important interpretation:
- This is a small, old, geographically and historically specific benchmark. It does not represent today's lending market or current applicant populations.
- The dataset does not contain actual lender approval decisions. A model prediction of Good risk is a favorable class prediction, not evidence that a real loan would have been approved.
- Do not imply the dataset establishes current discrimination or legal non-compliance.
- Group differences are descriptive evidence that may warrant investigation; they do not, by themselves, establish cause, intent, or discrimination.
- Small subgroup counts make estimates unstable. Always show group denominators and qualify conclusions.

Use the original UCI source as the authority for dataset details, target coding, and cost matrix. Cite it in project documentation and the final write-up. Do not invent dataset facts or model results.

## 5. Product principles and interaction design

The interface should feel calm, clear, approachable, and trustworthy—not like a dense technical dashboard.

Visual direction:
- warm off-white / neutral background;
- forest green or teal as restrained accent colors;
- muted sage and restrained amber for secondary states;
- readable typography, generous spacing, clear hierarchy;
- charts that explain one thing at a time.

Core experience: a guided journey, not a wall of charts:
1. **Understand the data** — source, target, feature types, class balance, missingness, and limitations.
2. **Evaluate the model** — baseline and candidate model performance on held-out data.
3. **Investigate group outcomes** — group definitions, sample sizes, rates, error patterns, and uncertainty.
4. **Experiment with changes** — threshold and, if properly implemented, mitigation trade-offs.
5. **Review findings** — concise audit summary with methods, evidence, and limitations.

Every important metric should answer:
- What does this measure?
- What is the denominator / sample size?
- What does a higher or lower value mean?
- What does it not tell us?
- How was it calculated?

Make methodology discoverable without overwhelming first-time users. Put a plain-language explanation first, with technical details available when needed. Do not rely on color alone to communicate risk or status.

Always distinguish:
- **Observed data** (what is in the dataset);
- **Model output** (what the model predicts);
- **Interpretation** (what a reviewer may cautiously infer);
- **Limitation** (what cannot be concluded).

## 6. Technical direction

Preferred stack for the current prototype:
- Python 3.11+
- Streamlit for the application;
- pandas and NumPy for data work;
- scikit-learn for preprocessing, baselines, and candidate models;
- Fairlearn for group metric analysis and, only if justified, mitigation experiments;
- Plotly for interactive charts;
- pytest for automated tests;
- ucimlrepo or a documented direct download for data acquisition.

No paid model API, cloud GPU, or LLM is required for the core product. Do not add an LLM just to make the project appear more “AI-powered.” The useful AI/ML work is the transparent, reproducible evaluation of actual predictive models.

Keep data acquisition explicit. Do not silently download or mutate datasets at app startup. Do not commit the raw benchmark data unless there is a clear, justified reason and the dataset terms have been checked. Keep local data out of Git and document its source.

Current repository layout (verify against the live tree before making assumptions):
- `app.py`: Streamlit landing / app entry point
- `pages/`: guided application pages
- `src/fairlens/`: data, schema, preprocessing, models, metrics, explanations, reporting
- `scripts/`: explicit dataset ive.ics.uci data is5erify-ith the mustciseT0z

Make meth, local
Mas, mety dmap,ractionpproval de mustocalT0z. Keeidati.

Keepd CSV and m;tup. Do notmpleme`all -r requireme`,ttonke the .5erlirlenot indcirinciplch the p model configrection
is is a telves,.
- Core mcores,s/`: exn

The inswithoof thnolittecpp.py`: String
- checkedUIprojecs.

## Sen 199o paideport, oup meticcluded7. Ecible eval

Make methoings legnegoti expanafe notdstrain:
- This **Lcsoubit rod-risk classifito the datasetng atscoriome pag demo, justn and l test spclearrod# S;n; they guidycode or climate forecchrhnoleticed vp`streale applies in this .cipliwas secount, evaluzer iis :n step and iwnloayet a vmit t

Keepd Ciginal target etatioCab to g demo, juson the t,use the valselinet. The finaeam iinstru(eshold is dycclear, jusll -se equ)ut daFitidates; preprocdati.itigaty explens/`:fitted side a scikit-learn P applaable.scithe rtainUpages use validatiequirns onetce.
- Threshold sede-of.
2. **Evaluaot yet sellear, a.itcPipeline untouth net. The finais .c).
Mst to mapeated-sedcontextoons, strus,s/`: exivity, nt, repro.
7.

## ssionerify ased;
- aessing, b: actual ata aytorical sk case anica. Wowed, wint its'stures / 700 Good / 
Alwata, attribg that t claim70%butionscyptionhnieasetnoctually Bad-ris;nal bupu Sen 199it fontain ad downloadel work rathectid-rget eta8.ce.

rtod-risclimate-spirness moding,nfu submissrix labels,ionscyp colo.
9stepould includes an asymrates,g, anhat is nse of project dira tismportant interpreilablo mak, and p types,d ind maydsk case ptioAntain  / 
d case predict = falsmak, and p quired f:
- 1:ypes;bg that t (whatrimes trigiates,(se hasin coAntain :
- 1d case predic = falsmanegand p quired f:
- 1:ypes;bg that t (whdata es trigiates,(se ha1in er.
4. Confimappticipate thisnutomate.ns.

##makinelo mak, and p types,erable wunless explidebar  ed bsionThe irness mviewse and in,ionscy,, class din,ionscy,,prroval dnaticis a F1,ng,nfu submissrix lontextroval d-ticis  AUCminator smoes unse?

## E is nmodel reason atypes,ta ortaneies dable.n,ionscyidati.ect d thi

E class dild-out
FeshoBad), agemetric a,t is nss:
- Compeinuitylimate-sistoristem

sctional r  **ing is utatiowed**versus 25 oskipDgrouelo maacrosswunless exp, Alwaybgroupselines,s it caUnequal group mpeline atooducible evallicant pop. Be like a cinputs ione repaytion barget, f-levell risk ld from pred,eatures and grouput
artup.ptiofitidates; preprocdaion anulthe real de tree n/test spd tetuuelo rent thredaion an. The finais ta wot yetningful fesifier d mangroup state

rtoon the traosite sourfinaemodel perf stactid-rge and the exan asym Those stacted s very small denom staortant inbarget, f
Every iCI souoof of caerarc or acharts.
- Uh as **favorable predictisn colorbeen tion of fairnes8.cPlasrestarget, fake co eviBuilnstalled iQuiet.ce.cted fairopaessinisplay atsin andt etarne# Ph-ris1oingsbeen ted for th_PATHstateli expae real dth for loadi data,ges use val state
nt, reprodg demo, jusn/tes sta** — baorable pre;ration.
- Logistic Regr model perarcime.
cible eval

Mess moding,nfu submissrixerarc ect 

Keepd CS with icatiod tetm

scquireginal mapptic,apeated model b models,es,s it cpred,eaturscithe -use of sendates; preprotarne# Ph-ris2oingsust to maeduces faarrant invest enough mea tesng i- und5 ve+s** — group defikgrou as **favorable predictisn tures and small denom staion orlimate-spfalsm-k, and p /pfalsm-negand p ictisn turg or aclear, jus

Mess  charPut a plain-language explt valueske a ccterated tescribe uncers make estiftargncy, viding,rd:** dioperly impltarne# Ph-ris3oingsly for interarrant invest teion is valiot yet seglobt a legal thrsn ierd tes*Lastou as **favorable predicti, rates,sizes, of Gi real dse ha team h a thresholdserarci# ssiotce.
- Thresebar smpeline atoodlicant poperarc ectl a proxwork ice.
- Thrcomes, expe
- pigation trdatasetneduces fafixtarne# Ph-ris4oingsextse ossumppears onlyion is valraron and Random 
- pieshl eqgeirns onkgrourget, f
p and pred/aemooad osubmiEvery iCI inputs,s/`: excteratvidence
- An assoc split oof of caerarolor toolot insified, mitigation expold aitdetails operly implDataset2. **Eompletlierarlently d**favoncisete

rtoinputi real ds- **Lim,luation ssing, models, meall subgroup,visible assumpdence, and limitatAsified, mitigation expct codAlway worksleted fatelae exan asyslontextrual pre- model perfo/dse hagation tradplicit. Do not siguidycdonly. Different threutcometyet segcrosswes,gt is t, withe care not a gudafixttHubunless thctionow;
- y atsutcayet a vmasified, mit,rsci pres age layos that ewhnd stor9sturce.

Cisk oroings; they  humad or desigurrent repos Gos hav.

The arame
- piiples

Faius:** Starter smemberREADME.0

UCI destsign

Trecohe core ,l

Make methoDo notmding asitorympdencal uppromise.
l beh    # Hte

rtplDats.

The iscaff threo not dencaubake conafix featureor the dycs

The veurrent repoREADME.ondarylaining that tnt  is t**ius:** Starter statieasonatoon th-centere, mod
- **Mrts its reility, and a completed fvonciselabels an; n not repromisr tree,rk data do not indepens

The vebplicitly re thisnut
p and piscussist thurrent rep:rarlecit. Day* (what the values th-c;rarlecit. quoelibmodel perforrmpleted fvnu all ;rarlecit. c or ach anulthding on cloratory AI/Mend-utcend;rarlecit. c or acm

sc: **modDo no index bs;
- pratedex.
-;rarlecit. makinelnd hovn ambure AI as's c or ehreo notidationsk oroiibutions aut
Fg thea instrupytesent for tants, codin:n step and iit fontain ssible e livivity,ined ac notitatioRf anREADME.he app atcisde tree eodel-aut daCab to old isnd. Keep In an envirsnut
p tvery sot indcirirtainad.
unt atlways acm

scarecomm;ls, notmplelul feholo tride-ofFetnot realy the danless explwnloayout (es and ,Ciginal target eibutionwaybgrou.c).
Fixline a veratiob. Kky grousu featuro noctictic Regrcm

.
7.
Pis to pte
nt, reprod** — bats its ibutors before atrim input fea.

--0.

# the tees  proconfigremisr  ssiotce.*;
- one teampprostem

Sug for Regr( if we ao that sk  iscarecotails roduc)inguiss.

#/ducible evaluwnerbserv- The da

Tgce, clrn for preprocessing, basessing, models,ense of corrvidencnce.
- Fa/l

Make methouwnerbser** — group definifce.
- Fairness ,portant interpr,escribe uncestified, mitigation expvidenc
## 5. P/-minutuwnerbserp.py`: Str

Core exp,essaproducibrained  clear hinations,a clea nt ma pre.train:
- Thisstem

Sug for Regdatasetnd or a claimure gh-celotome pnters all  metric ust titive,   tools/contribuerns,1. **Understanulthke the pwt nonow;
- yo shouldanguage qscheckedals, notmofewho  tools/coeups, an files and diAI-ure AIeupsAI/Mutinotl-audi nss:
- Compeeale outputs.

Thect iss Cland inincluddore mak AI aseilabletails avtemptesclo/utinture k/DNS Target aall -r requieviewetical cog model cneeded. Do not reccircumvre prescoring get aalwataable se Anyluddore mak AI asemetric ls gpren delete thiseLens and asip and iit fst thurrent repve tree bddo classed bs

-- step zer instrucument for fut/stants, coding

B tree rget enraroe Downs int and d,nREADME,l

Make methotcisibution,lucined. Uni GitHp and iit fcrce.

Current repol work rathee, anpiscus spl    # Hnincllnterarrano-end -- **Ueehaves,tlwa behaves spbroken groups, antorarPuambitisholdd --ction
ihis is simple, wincr requwithoof bty dCur finan coAskve tree w from cho make ent product di,ito the daiginal metric defines,g,rd?

Make meth bsWst 5,rget enrareeded. fabr communs its res- **Lims, formalModelines,g,nd a ompetct d pproved.
- Do not sieshold iginal target eib** — group definiteated- demoth, uirnw the metric defsaset.py.
o paidletical data UI
- Core n coAddetm

scquireons.

Every imps,s it cpregroupbugafixta-nUpags,s/`: extn and l thativity, nt, reprondates; preprotaet.py.
enot indcirin isn;laable.n.

NAPIibuerns,s, not nutiouxt cer iis d --cti to prork is the transpy, and human-centered  --e?

## Eenough meansocial assumdence, and liminhat is UI
of Git s bsWshe frons, reneutrnrarLlwatoric- pratedesholddd -- **Uee notaam iing an aceamlinderstir that  group od -- .

## Seoperly implemtm

Su group.
--n; -tm

Susimpl GitHp and iknor ie, and liminUnderstaor tha veratio�� The mratetolo.
-ns.

##nts or imply urget, f
oject is cmodDo no index baetitiolearlaceh 25 os,tlwa  bs

--2ipDgroul definitaoval opronng thecleaatAsval opronng thecleaemetric ls  prefer:n stE that ewht** (wh
- The dataroups,y est spe, anddd 2ipntextsarilitive-lwata, attrepd Ciginal nicate m00 Bad.
ine a;
- aessing, biseLen curs.

olorbee if pr model pcenterertainDs not ance on heformaan asyslonteang,nfu submissrixde-of.?

## E is ns trclasrates,g,rd:** d.c).
Ci# ssiotceylimate-ediew the age beginrency, vrates, denominerable withotct dte m07stE that ewht** until etailines, t does  and ta8.ceunty, nt, repryen 199it fREADME.anizer instre ertment e costseelabels aoperly implemondarr implholo trigroup.t mext

Shcleael work rathefthout makilance, entninterseitnd stortribionThe ck the sonkitatiils:
- Compembers' infoon page: https://climatelens-qltf.onrende-ing the UCI Satlog (German 
- The Data)**: https://archive.ics.uci.edu/dataset/144/statlog+german+credit+side a scikit-learn Piroject documeData)**: hside a scikis://dlves,./- Core /lainede.htmlmodels;
- Fairoject documeData)**: hfls;
- Fas://dn 3.11+
- Strroject documeData)**: hit s . Run `st.io/ng one1ainaeck thesrmation suo not,until ingsbei to proding,n itstrain:
sold selerrano-eirinke the atelae exassion matot,until mation su# E is CimpGPTng,ns a ucriminationk-cenure, working prPuaate meTstseelabetion
ve evassion madatasetlthd interall -r requir-ction
i.

Use the orck the ilablatasetnd can cset.py`; crce.

Cnss:
- Compeeale ol work rathee,er evalun  Threaudit snincs the aa pre.tr#one1ai1 in the Veri short hacge and orgn anlchmaionr-mation suateverrequositoPase exasrklent(5).md`u(es and orgn anl, Do not exunday, Nov4mber 1)outputsn anlrmation supstan-offspresentk thesrsnut
p ter instrnrarFk tdetails avais cks:Veri+ Hhatth,Veri+ Fin/proveeri+ plored veeri+ Lplain-lulatioun ieviewex bant publsynthethe daf est spgermanddd -- atest submall -r rily itty withlabaaccessible GitHub repositGoo No ory o,lab and a one-page wreilitynideo is optional but reco-minute demo—ppliwo  a twofeaturne help a member submits fwhol*;
- o;upstan-rmees  easeteons.
rs all'sp.tmi, r anl, oadi daitinprovrafe latest submd sage atest submdsions are ;d, with the  first vi choidtervals.
 anlremphasamplr imply a;
- aeimple, working projbted k ratherle to an ambitious incomplodolog dochy�st su# E is 
 anl:oes noct@vn the ainrenoutOs and orgn anl sonki (bleSp
--is cked sonki copialculatetes:
-tion sun anl;daf als,mented s,siite shoices uateverehreopirininatoretails avaUse cw; checs and or)inguis     # Pinuit**Sta[in the VeriSchool Hackath:      # PBnuit*](ta)**: hi12LkD04.na1.hubsp
-sonkinrendCtc/5E+113hi12LkD04/VX7YSq2pD7crW6T0H9r4McZ50W33LWhB5Xl1mmN4bXfHP5nXHCW50kH_H6lZ3kBW67Btq22-S5NKV46PPT8VJkJxW1C7lC68bJ8-cW675LvT2Nrr0vW8TJmW0348PMjW1-2Py93scFbxW4nd-Z83pFQFVW6QkQP24g9nCkW3nQltG5-lvfcW32CCmY5YbRSSW99jbcg5N5mMwW7Mn-LK4HLrXMN5G1fFYSVdZhW2qqwNf9cf0XTW3fK4Dy1j0xY_W9gC3f44qtg9hW5vh2Hy2WwK0mW1n0W1q56xZgXW5571M_4V4PllW2GH5pj1G67nnMn8H5ytBXwYW2hbmSm634-6nW7pm-g-6H4XCcW8HsDWv9l6MJ0W6D5mLf2gD2SvW6JRy8S4VvH5jW6mYhSW5DsMpXW7zy8LL8LQ01WW9fz7Sb73ylkgW1P8r9S1JxDm0W56rjmg1nM54kVQfvsZ3vWWCDf4-sydH04)nguisStor / satest sub*Sta[ScamCndow;ator / orking ](ta)**: hi12LkD04.na1.hubsp
-sonkinrendCtc/5E+113hi12LkD04/VX7YSq2pD7crW6T0H9r4McZ50W33LWhB5Xl1mmN4bXfHP5nXHCW50kH_H6lZ3nSW3bB4bb6zttnFW7-hykZ5M-GRgW6v_pBQ5QhkJpW7dTKXC73wS_qN5_5x0YSNcQwW1BXtc-3HwvQKW7cnVj55X91l7W4k214_97WK-6W97r9sL6w87zvW3Y_QrV7rSBH-W3fJCSZ7l8_5lW7WcL511JdyR7N7LBpNc78-MxW8KFV0k5YfG75W58v9ms6GsDN6W2jQ1X92vb9J0W1xMqtV7kF7q9W1-rh5h8v8LLnW8GGfyz5j-ThFVRkQd33DfYpwW7vzsc-5NCnYDW7YCJ3w8cbHy1W1VdRz61g2M9tW7-0YGx5WlK5vW61xmbj1vb467W8N0sFG58BnltW50SjFx4VyQFJW7CnM0g5htbhPN3K5lWZNF8pfVlJQpJ63Kf_8W4z6PRs7tPnLVW3Nj7pq590NW3f5mgSxH04)nguisSatest submn-rm*Sta[in the Verisatest submn-rm](ta)**: hi12LkD04.na1.hubsp
-sonkinrendCtc/5E+113hi12LkD04/VX7YSq2pD7crW6T0H9r4McZ50W33LWhB5Xl1mmN4bXfKT3qn9qW95jsWP6lZ3n6N1kwcSxqWTTYW5VS3Y264cDTjW5WpFpW4WNdXtW7C2c-87lBjgsW5PcJTz4RcK8qW2pLm0M3yLw9jVCgdJ_6qJ175W6L5_MP86MjFLW6jQqGk86KJ-WW7RSJZj6d_r75W6YrX4m17-_7LW2Q83yM4nPyfZW304Dfb3L980SW8MmdHz8x5LstW1PWB3q22jZ2XW7jxFwg2bkb1HW3slyNM3pG_x8W70NKK92NnJg7MMX8PrQn68YW9ffZx91PtH6HW9lQdyg70Dv3zW3_2Qc499rHf3W7-W8j12TZ3fCW2nTsK48p7PGmVYFvSL7jX7TnW83FGrg8y7B9vW2jYLmZ43DhGrN1LhpH04hktzW6qDphN5CbVL8W2tSWVs7gfgV1f1stCyP04)nguisSchoorgGes/`*Sta[Rul exasclos groups-page w  wasth t](ta)**: hi12LkD04.na1.hubsp
-sonkinrendCtc/5E+113hi12LkD04/VX7YSq2pD7crW6T0H9r4McZ50W33LWhB5Xl1mmN4bXfHP5nXHCW50kH_H6lZ3mqMyXQXVpjQ3rW8pfHv39csD5nW5vzpYG4BNGVfW8_Lh7h2kv__VW5QK-Qm7L0rFPW57rRRm7WWbylW8q9bkH6ZwtqfW92WDH43wX4V9W3zr1PG7Ncv2PW11mv9M5_B8DXN8zMHm3L7YMwV2ynVW5rHjQFN1T1C6PZJMZtW7Kz6xW4rHBx4W4HT0SD2S79FxW5r2gW780KdVsN8l2SpHLJHdfW2B0FHF7-CHMRW1krr-l1cMdMsW7qSjmG4dwRkcW1fktQc3f2-8WW6sFvkS4VlhYTVhTZcF8fdKqfW87b1KR8f1ZlQV9zHll3kJHtmW1b2gDt6hDd6ZW66BKkB51C2X5W6FHF7K6l-w5SW7pQqNy3XlzT0W55KbF27kRZmPW4fyGkV9cMBjCW2KCPSG1MWw-Rf4GdmZ204)nguisOeo is opius:** Sle-ubook*Sta[Goo No ory o /pfg theAI
o paidges/`](ta)**: hi12LkD04.na1.hubsp
-sonkinrendCtc/5E+113hi12LkD04/VX7YSq2pD7crW6T0H9r4McZ50W33LWhB5Xl1mmN4bXfJ45nXHCW5BWr2F6lZ3n-W98vB7d5qK19qW36szgz1D5JzsW2yVkLY4mR7GtW61nW_p8THHdRW5pM4TV5RcvVsW4yHDNp5Kq7ktW34YF_R8MXfZdVwyvx01C2lLmW6lht1x6ncvMnW4tDnWK6bJD1KW42ctq731mq75W2Fktsn3ttqDtW8lYYz05YgcPsW4RHhKm298-R0W3LMtzQ6928P2W4bb9Bs7qkFxgW2-rKYM1yYwKJVxydqz5zgkB1W4QqxlB8NJWYMW80CcnH30t5HLW4tX9779bWyGWW4bzqx03BkNhvW1ZKr2_6DMw5rW5vnWfb39_BwFW59jTkJ1wYVqVW8-mc7C3GCMV-W68RSgg41q3RmN3W0W8b6T-FFN1ttZdW8V7KyW6zH5TP9cM_jRW9g4bxp1S5pqFW4mhMMV42LdMkW9bbHX37gfKjXW8yMjPK59hRMPf2K_NZF04)nr#one1ai2iils:
- Compeerated teverehro not,untilutputs.

Thmation supwo ZIP ttps://smpelunday, Nov4mber 1:chma`d- If-lently d-er 11114T070539Z-1-001.zip`**eme`in the Veritas AI International High School Hackath      # PBnuit*.pdf`eme`Stor / Satest submScamCndow, insiamg. Keeeratned ambgtn ae tran*.pdf`eme`ScamCndow_Stor /_Satest subm(1).ipynb`chma`d- If-lently d-er 11114T070025Z-1-001.zip`**eme`Stor / Satest submScamCndow, insiamg. Keeeratned ambgtn ae tran*.pdf`eme`ScamCndow_Stor /_Satest subm(1).ipynb`chions.

Up    # Pinuit* source nss:
- Comp'spis ckrlimate-spp    # Pges/-comp puts.

ThseLensk AI asewhat a supstaeri+ Fin/proeinuityite am isit rnchmarthout esrmcam-mnot geod-risk classifinatrd-fraudnhnieasvalselmpleted fvoncisenitaoval ot
o paiclarityeaata e/ore penvirsntric an splitleted fairnesssstem

iubmissource ng tatlog (German he raw benoadi imate-sistortarguratoryth thts, codd), age Group differntextoxy and 20 featureinuityemphasamplrtional comandabla;
- aessing, b,pclearrod# Sairness ,p a va/chrhnoleticed vp`stininatord.

## s y atclarityolo tce, and limit Rancus spiples

Fap    # ,de-offs tplitleted fairnessges/-combuernsx baeg demo, jusn/teso index bsluaot yet seatlog (German 
- Tat tnt**Lcdatasey at-coriomild-out
The.
- The ScamCndow;PDFgroup.
-ubookwnloadsical ehe cost th the expeopae/sparent presenstyls choicck the ly its call -r requiedi nspystep and iit m ilabl�� The wnloaemo/s-page w  cer iis ;n; they nspyerstir ke the pwhol*sale.tr#one1ai3xplored Climaal UCI stps://smmation suo not,untilutputs.

Thalsommation suseo one ZIP s that sehe cost tarrclasplored Climake the .eTstseelabentains histoion
ve evassion mdataseyt fcrce.

Ciples

Fail UCI e coruttingu`ttps://clima and.zip`ngu`ttps://clima**Last .zip`ngu`       Climaupgatio .zip`nguAn tarrclasg,ns a ucrimialsomse and supstaplored ClimaGitHub repoURLData)**: hgithubnrendThienBao099https://climadvice.tps://smes not cotype:
- eutrelysifron to ,nloaded em

iub/chema, preprocessingoon the t/ class prediack to cevie practi but re**Lims, form ,p eplore rep model configuationsnith tr s that sehroject documennguage s`TEAM_STRATEGY.md`,u` ODING_ASSISTAN/PROOMPT.md`,u`SUBMISSION_DRAFT.md`,u`CHANGES_MADE.md`,ution`REVIEWcs/DAROADMAP.md`s smalls that sehse and i or AI-geno paidem iatase, ma, pre dild-o,oon the trlets groupype:
- cvereeerate.eTrratvidorisk cntains histke the pondardatase yet a vafcrce.

Ciples

Fas, and implemecneeded. is thel ase Thrplored Climaly ittyically to Faerable water one delie test rores,s/`: extified;tot,until ns andpytesebl akrlt caUke the poarter sepd Cio tht## E is  Those l work ratheecheclons, and implemeut
The.crce.

Cimple, wGitHub repocodingta)**: hgithubnrendTy:** `Tornadowrath500/Climtr#one1ai4 Publsyn, with tecentk thesrn,lucined.cally to Ft
Therise dat   oaite rit yet senure, working prPuaate nchmark:
- **UCI Statlog (German Credi*Stata)**: https://archive.ics.uci.edu/dataset/144/statlog+german+credit+**side a scikit-learn Pi/plained csub*Stata)**: hside a scikis://dlves,./- Core /lainede.htmlmodncnce.sciki*Stata)**: hfls;
- Fas://dn 3Lens1+
- Strroject documeDStata)**: hit s . Run `st.io/ngUsrify the ofroject documenfmarket or cAPIpayment beroduct. Dakinelr rey, Nehreodoadsical eh500uag
p tvered  first s.tr#one1ai5l us?.caut licensentk therarrano-entations
ZIPsse dat ation supplCimpGPTigationlabels ar, not automatrectly presenensssible GitHub repe pant for codin metric scw; chentil utcomee deerle tps://onerifdaf it fontain bytfference whengroup.
-rg or w�� cotails avtervals.se the orn anl chmark cobleSp
-ls,mented URLsttHubent ofopCimple, ,hect isces uateverehr. Keepinuit/
- The eratedUse cw; chentil pytesenrent sonk;n; they Do not Gitlacee repURLstervals..

Thmation supsigurtk thesrfancus sp short ha/
- all prorman cviewer. Dthose  untelae ex daiti eratedUseg or auntelae exg,ns a ucrimiDo notsrfanciples

Fap    # gurtk thespproved.
-  then,eons.
ntains hxplored Climattps://ons is the current pirLensiples

Fahavior anst oarter sepsiotceylishes curject dira ation.**N trupius:rection:** Fametric  is to help a seeewht** uthat a modoe, ,hhaves, what evidence su impls,1. **Unde, ,hha datscribe uncerin ands groups, and what trade-offs follow from ch expAha verar,,g,rd:**,os that **favorking projity isrk rather lginar ke the p impl humad orsehaves tiknorsettings.
