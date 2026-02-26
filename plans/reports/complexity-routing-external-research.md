# External Research: Complexity Routing Frameworks

**Research question:** What established frameworks exist for classifying software development work types (production vs exploration/prototyping vs investigation) and routing them to appropriate execution ceremony levels?

---

## 1. Cynefin Framework

**Originator:** Dave Snowden (IBM, 1999; The Cynefin Co)

**Classification dimensions:**
- Cause-effect relationship clarity (knowable vs. unknowable)
- Predictability of outcomes

**Work type vocabulary (5 domains):**
- **Clear (Simple):** Best practices apply; routine, well-understood tasks
- **Complicated:** Expert analysis required; cause-effect knowable but non-obvious; multiple valid solutions
- **Complex:** Cause-effect only retrospectively visible; novel territory; requires experimentation
- **Chaotic:** No cause-effect relationship discernible; crisis requiring immediate action
- **Disorder:** Current domain unknown; break into sub-problems

**Ceremony/process routing:**

| Domain | Approach | Software Development Fit |
|--------|----------|--------------------------|
| Clear | Sense → Categorize → Respond (apply best practices, SOPs, checklists) | Routine maintenance, well-specified features with known implementation |
| Complicated | Sense → Analyze → Respond (expert review, structured methodology, formal planning) | Complex features requiring architectural expertise; systems integration |
| Complex | Probe → Sense → Respond (safe-to-fail experiments, iteration, pattern recognition) | Novel domains, unclear requirements, innovation work |
| Chaotic | Act → Sense → Respond (rapid response, decisive action without predefined roadmap) | Production incidents, crisis response |

**Exploration handling:**
Complex domain maps to exploration work: prototypes, experiments, and spikes are the prescribed approach. The key diagnostic is whether cause-effect is predictable *before* action. If not, probe first. The Cynefin model explicitly routes exploration to iterative probing rather than upfront planning.

**Connection to agile:** Scrum's empiricism (inspect-adapt cycles) was designed for Complex domain work. The implication: applying Scrum ceremony to Clear domain work is over-engineering; applying waterfall to Complex domain work is under-engineering.

**Limitations:**
- Domain classification is itself a judgment call requiring experience
- Framework describes *problem context* not *work type* — a production feature can live in any domain
- Does not distinguish between a prototype of a novel solution vs. production delivery of the same solution once the novel aspects are resolved
- No explicit ceremony graduation model (how to transition from probe to build)

**Sources:**
- [Cynefin framework - Wikipedia](https://en.wikipedia.org/wiki/Cynefin_framework)
- [Agile project management using the Cynefin framework - TechTarget](https://www.techtarget.com/searchsoftwarequality/tip/Agile-project-management-using-the-Cynefin-framework)
- [The Cynefin Framework - Creately](https://creately.com/guides/understanding-the-cynefin-framework/)
- [Decision-making support with the Cynefin framework - LogRocket](https://blog.logrocket.com/product-management/decision-making-support-cynefin-framework/)

---

## 2. Stacey Matrix

**Originator:** Ralph Douglas Stacey

**Classification dimensions:**
- **Requirements axis:** How clear/agreed-upon requirements are (close to certainty ↔ far from certainty)
- **Technology/Approach axis:** How well the implementation approach is understood (close to certainty ↔ far from certainty)

**Work type vocabulary (4 quadrants):**
- **Simple:** Clear requirements, known approach → routine work
- **Complicated:** Clear requirements, uncertain approach (or vice versa) → expertise-driven work
- **Complex:** Unclear requirements AND uncertain approach → exploration work
- **Chaotic:** No clarity on either axis → crisis work

**Ceremony/process routing:**

| Quadrant | Process Prescription |
|----------|---------------------|
| Simple | Best practices, standard procedures, routine decision-making |
| Complicated | Expert analysis, predictive models, structured planning |
| Complex | Open dialogue, experiments, iterative development, stakeholder feedback (Agile) |
| Chaotic | Rapid response teams, improvisation, no predefined roadmap |

**Exploration handling:**
Complex quadrant explicitly calls for experimentation over planning. In software development, the matrix is often plotted on Requirements vs. Implementation axes — coding tasks with known solutions fall in Complicated; user experience design in novel markets falls in Complex.

**Key insight for routing:** Stacey gives a 2D routing mechanism. A task can be complicated on the technology axis but simple on requirements — routing to expert planning, not experimentation. A task unclear on both axes routes to exploration first.

**Limitations:**
- Like Cynefin, classifies the *problem context*, not the *artifact type* — a prototype is still in Complex; its production counterpart may have moved to Complicated
- No explicit model for ceremony graduation once exploration resolves uncertainty
- Does not distinguish between a throwaway prototype and a production-bound exploration

**Sources:**
- [Stacey Matrix - Praxis Framework](https://www.praxisframework.org/en/library/stacey-matrix)
- [On Complexity: Why Your Software Project Needs Scrum - Christiaan Verwijs, LinkedIn](https://www.linkedin.com/pulse/complexity-why-your-software-project-needs-scrum-christiaan-verwijs)
- [Understanding The Stacey Matrix - AgilityPortal](https://agilityportal.io/blog/stacey-matrix)

---

## 3. Boehm Spiral Model

**Originator:** Barry Boehm (1986)

**Classification dimensions:**
- **Risk profile:** What is the dominant risk type driving this iteration?
- **Uncertainty level:** How much is known about requirements and approach?

**Work type vocabulary:**
The spiral model is a *process model generator* — each spiral cycle selects from: waterfall, incremental, evolutionary prototyping, or throwaway prototyping. Work types within each cycle:
- **Objective setting:** Requirements, constraints, design alternatives
- **Risk analysis and resolution:** Prototypes, simulations, feasibility studies
- **Development and testing:** Working software increment
- **Review and planning:** Customer evaluation, next iteration scope

**Ceremony/process routing:**
Risk drives selection. The model explicitly keys process weight to dominant risk type:

| Dominant Risk | Prescribed Approach |
|---------------|---------------------|
| Unclear user interface / unclear requirements | Throwaway prototyping (low ceremony, disposable artifact) |
| Sub-system integration uncertainty | Waterfall (high ceremony, structured specification) |
| Performance requirements uncertainty | Simulation, benchmarking |
| Unclear architecture | Evolutionary prototyping |

**Key routing mechanism:** Risk analysis at the start of each spiral cycle determines *what process to apply for this cycle*, not for the whole project. A project can use throwaway prototyping in early cycles and switch to incremental waterfall once uncertainty is resolved.

**Exploration handling:**
Throwaway prototypes are a first-class artifact type in the spiral model. They are prescribed when user interface or requirements risks dominate — precisely the case where exploration is warranted. The prototype is explicitly expected to be discarded; it produces learning, not production code.

**Limitations:**
- Designed for project-level process selection, not task-level routing within a project
- Risk analysis itself requires expertise to apply correctly
- No vocabulary for "prototype in plans/prototypes/ vs. prototype bound for production" — the model operates at a coarser granularity
- Overhead of explicit risk analysis per cycle can be excessive for small tasks

**Sources:**
- [Spiral model - Wikipedia](https://en.wikipedia.org/wiki/Spiral_model)
- [A Spiral Model of Software Development and Enhancement - Boehm (1988 paper)](https://www.cse.msu.edu/~cse435/Homework/HW3/boehm.pdf)
- [Navigating Complexity: Boehm's Spiral Model - CodingMinutes](https://blog.codingminutes.com/boehms-spiral-model)
- [What is Spiral Model in Software Engineering? - GeeksforGeeks](https://www.geeksforgeeks.org/software-engineering/software-engineering-spiral-model/)

---

## 4. Extreme Programming (XP) Spikes

**Originator:** Kent Beck (XP, late 1990s)

**Classification dimensions:**
- **Deliverable type:** Knowledge vs. capability
- **Uncertainty driver:** Technical uncertainty vs. requirements uncertainty

**Work type vocabulary:**
XP introduced "spike solutions" as a distinct story type alongside user stories:
- **User story:** Delivers working capability; estimable; production-bound
- **Technical spike:** Explores technical approach; produces knowledge; often disposable code
- **Functional spike:** Explores requirements clarity; produces understanding of what to build

**Ceremony/process routing:**

| Work Type | Ceremony |
|-----------|----------|
| User story | Full sprint cycle, acceptance criteria, testing, review |
| Technical spike | Time-boxed (hours to 2-3 days); no acceptance testing; demonstrated to team; deliverable = decision or report |
| Functional spike | Time-boxed; involves customer/PO; deliverable = clarified requirements |

**Key routing criterion:** The question is *what does this produce?* If the output is working software for users → user story. If the output is knowledge for the team → spike. Spikes are estimable (time-boxed) but their output is not acceptance-tested against user criteria.

**Exploration handling:**
Spikes are XP's formalized exploration mechanism. Characteristics:
- Explicit time-box (typically 1-5 days maximum; longer = it has become implementation)
- No definition of done in user terms; done = learning achieved or time expired
- Code produced may be throwaway; the point is the learning
- Placed in backlog but processed differently (no user acceptance criteria)

**Distinction from production:** Spikes are not "smaller stories." They are categorically different: deliverable type is different, done criteria are different, review process is different. The same code written as production vs. spike has different obligations.

**Limitations:**
- Does not distinguish between a one-hour investigation and a multi-week prototype
- No routing guidance for "prototype that evolves into production" — the boundary is handled by social convention, not process rule
- Binary: either a spike or a story; no gradations for longer-running exploration (e.g., month-long R&D)

**Sources:**
- [What is a Spike in Extreme Programming (XP)? - PMAspirant](https://pmaspirant.com/what-is-a-spike-in-extreme-programming)
- [What Are Agile Spikes? - Mountain Goat Software](https://www.mountaingoatsoftware.com/blog/spikes)
- [Spike (software development) - Grokipedia](https://grokipedia.com/page/Spike_(software_development))
- [What is Spike in Scrum? - Visual Paradigm](https://www.visual-paradigm.com/scrum/what-is-scrum-spike/)

---

## 5. SAFe Enabler Taxonomy

**Originator:** Scaled Agile, Inc. (Scaled Agile Framework)

**Classification dimensions:**
- **Value recipient:** Customer-facing vs. system/team-facing
- **Purpose:** Capability delivery vs. capability enablement

**Work type vocabulary:**
SAFe defines two story types and four enabler subtypes:

Story types:
- **User story:** Delivers direct customer value
- **Enabler story:** Delivers system capability that enables future value delivery

Enabler subtypes:
- **Exploration enabler:** Research, prototyping, feasibility assessment, requirements discovery, alternative evaluation
- **Architectural enabler:** Builds architectural runway for future features
- **Infrastructure enabler:** Improves development/test/deployment environments
- **Compliance enabler:** Regulatory, audit, verification/validation work

**Ceremony/process routing:**
SAFe routes enablers through the same backlog management process as user stories (estimated, sized, demonstrated). However, enablers have no customer acceptance criteria — "demonstrated" means showing what was learned or built, not testing user value.

Spikes are a subtype of exploration enablers: time-boxed investigations where the deliverable is explicit knowledge rather than working code.

**Key routing insight:** SAFe formalizes the distinction between "work that delivers value" and "work that enables future value delivery." Exploration enablers are explicitly the category for prototypes, spikes, and research — they route through the same agile ceremonies but with different done criteria and different review expectations.

**Exploration handling:**
Exploration enablers explicitly include: prototyping, research, requirements discovery, evaluating alternatives. The category legitimizes exploration work as first-class backlog items without requiring production-grade output.

**Limitations:**
- Enablers still go through the same sprint/PI ceremony as features — SAFe does not prescribe lighter-weight ceremony for exploration
- The distinction exists in classification and done criteria, not in process weight reduction
- Does not address artifact destination (production codebase vs. throwaway prototype vs. plans/prototypes/)

**Sources:**
- [Spikes - Scaled Agile Framework](https://framework.scaledagile.com/spikes)
- [Enablers - Scaled Agile Framework](https://framework.scaledagile.com/enablers)
- [Difference between Spike and Enablers - Scrum.org](https://www.scrum.org/forum/scrum-forum/32366/difference-between-spike-and-enablers)

---

## 6. Lean Startup: Build-Measure-Learn

**Originator:** Eric Ries (2011, building on Steve Blank's Customer Development)

**Classification dimensions:**
- **Uncertainty level:** Are we building the right thing (hypothesis) vs. building it right (execution)?
- **Learning goal:** Does this iteration validate an assumption or deliver committed value?

**Work type vocabulary:**
- **Experiment / MVP:** Minimum viable product designed to test a specific hypothesis; output is validated learning, not production capability
- **Persevere iteration:** Continue building validated direction; production-bound
- **Pivot:** Change hypothesis based on learning; resets to experiment mode

**Ceremony/process routing:**

| Mode | Process | Output |
|------|---------|--------|
| Experiment/hypothesis | Build cheapest possible test; measure specific metric; learn; decide pivot/persevere | Validated or invalidated assumption |
| Persevere/production | Standard development; delivery to users; optimize | Working product increment |

**Key routing criterion:** The question driving routing is "are we still validating assumptions?" If yes → experiment mode (minimal ceremony, throwaway artifacts acceptable, speed over quality). If no → production mode (quality, maintainability, full delivery process).

**Exploration handling:**
The entire early phase of Lean Startup is exploration. The MVP is not a product; it is an experiment. This is the sharpest vocabulary in any framework for distinguishing exploration from production: the unit of progress during exploration is *validated learning*, not shipped features.

The framework provides an explicit transition gate: pivot-or-persevere decision. After sufficient validated learning, the team transitions from exploration ceremony to production ceremony. This is the clearest routing model found across all frameworks.

**Key distinction from Lean Software Development:**
Lean Software Development assumes you know what to build and optimizes delivery. Lean Startup assumes you do *not* know what to build and structures discovery. These are different frameworks targeting different uncertainty phases.

**Limitations:**
- Designed for product strategy decisions, not individual task classification within a development team
- The MVP/experiment concept scales poorly to small tasks (a 2-hour script investigation is not an "experiment" in the Lean Startup sense)
- No vocabulary for team-internal exploration (technical investigation vs. customer-facing hypothesis testing)
- Pivot-or-persevere decision requires meaningful measurement; hard to apply to internal tooling or infrastructure exploration

**Sources:**
- [The Lean Startup - Methodology](https://theleanstartup.com/principles)
- [Lean startup - Wikipedia](https://en.wikipedia.org/wiki/Lean_startup)
- [Build, Measure, Learn and Lean Analytics - Ben Yoskovitz](https://www.focusedchaos.co/p/build-measure-learn-expanded)
- [Steve Blank: Why Build, Measure, Learn isn't just throwing things against the wall](https://steveblank.com/2015/05/06/build-measure-learn-throw-things-against-the-wall-and-see-if-they-work/)

---

## 7. Gartner Bimodal IT

**Originator:** Gartner (coined 2014)

**Classification dimensions:**
- **Predictability:** Is the outcome predictable and requirements stable?
- **Innovation vs. Reliability:** Is speed or dependability the primary constraint?

**Work type vocabulary:**
- **Mode 1 (Systems of Record / Exploitation):** Predictable, reliability-critical; optimized for stability, correctness, auditability; slower change cycle
- **Mode 2 (Systems of Engagement / Exploration):** Exploratory, uncertainty-tolerant; optimized for rapid feature development; MVP approach; hypothesis-driven

**Ceremony/process routing:**
Mode 1 uses traditional heavyweight process (formal change management, extended testing, slower deployment cycles). Mode 2 uses agile/lean approaches (short iterations, MVPs, frequent deployment, tolerance for defects as trade-off for speed).

**Exploration handling:**
Mode 2 is Gartner's formalization of exploration-oriented work at an organizational/portfolio level. Mode 2 work uses hypothesis-driven development and MVP approaches — mapping directly to Lean Startup methodology.

**Critical critique (Fowler):**
Martin Fowler's critique identifies two structural flaws:
1. **Wrong separation axis:** Bimodal splits by *system* (back office vs. front office) rather than by *work type*. Backend systems require rapid change just as often as frontend systems when implementing new business capabilities.
2. **False quality trade-off:** Bimodal implies Mode 2 tolerates lower quality for speed. Fowler argues high quality *enables* speed — agile teams deliver fewer defects AND faster. The quality trade-off is false.

**Fowler's alternative:** Separate by *business capability type* (utility vs. strategic) rather than by system layer or exploration/production mode. This avoids the organizational dysfunction of two-tier IT.

**Limitations:**
- Organizational framework, not a task-routing model — applies to team structure and portfolio decisions, not individual work item classification
- Fowler's critique substantially undermines the model's prescriptive value
- The Mode 1/Mode 2 distinction conflates "system type" with "work uncertainty level"

**Sources:**
- [Definition of Bimodal - Gartner IT Glossary](https://www.gartner.com/en/information-technology/glossary/bimodal)
- [Bimodal IT - Martin Fowler (critique)](https://martinfowler.com/bliki/BimodalIT.html)
- [What is bimodal IT - TechTarget](https://www.techtarget.com/searchcio/definition/bimodal-IT-bimodal-information-technology)

---

## Cross-Framework Synthesis

### What the frameworks agree on

1. **Exploration and production are categorically different work types.** Every framework distinguishes them — the vocabulary differs (Complex/Complicated, spike/story, Mode 2/Mode 1, probe/sense-analyze) but the distinction is universal.

2. **Uncertainty is the primary routing criterion.** Whether cause-effect is knowable (Cynefin), requirements clarity (Stacey), dominant risk type (Boehm), or hypothesis validation state (Lean Startup) — all frameworks key process routing to uncertainty level.

3. **Exploration deliverables are knowledge, not capability.** XP spikes, Boehm throwaway prototypes, Lean Startup MVPs, and SAFe exploration enablers all share this: the done criteria is "we learned X" not "users can do Y."

4. **Process weight should match uncertainty.** More uncertainty → lighter, faster, more disposable process. Less uncertainty → heavier, more structured, higher-quality-gate process.

### What the frameworks disagree on or leave unaddressed

1. **Transition gates:** How do you know when exploration is done and production begins? Lean Startup has the most explicit gate (pivot-or-persevere decision with measured data). Others leave it implicit or social.

2. **Artifact destination:** None of the frameworks distinguish between "exploratory code that will be discarded" vs. "exploratory code that will evolve into production." This is a key gap for the routing problem at hand.

3. **Task-level vs. project-level applicability:** Cynefin, Stacey, and Boehm operate at project/problem level. XP spikes and SAFe enablers operate at story level. Lean Startup operates at product-strategy level. None provides a complete model for task-level routing within a single development session.

4. **Ceremony graduation:** No framework provides a continuous ceremony spectrum. Most are binary (spike or story, Mode 1 or Mode 2, probe or build). Boehm's spiral is the closest to a graduated model but operates at iteration/project scope.

### Dimensions for a routing model

Synthesizing across frameworks, a classification model for routing exploration vs. production work needs at least:

| Dimension | Key Question | Evidence |
|-----------|-------------|---------|
| **Artifact destination** | Will this artifact enter production, or is it disposable? | Cynefin throwaway prototype vs. production path; Boehm throwaway vs. evolutionary prototype |
| **Uncertainty level** | Is the approach/outcome knowable upfront? | All frameworks use uncertainty as primary axis |
| **Deliverable type** | Knowledge vs. capability? | XP spikes, SAFe enablers, Lean Startup MVPs |
| **Time horizon** | Time-boxed investigation vs. indefinite production commitment? | XP spike time-boxing; Lean Startup iteration cadence |
| **Quality obligation** | What are the done criteria? Production-grade or learning-grade? | SAFe enabler done criteria; Boehm risk resolution criteria |

These five dimensions provide the axes for a routing model that maps work type to ceremony level without the flaws of Bimodal IT's false dichotomy or Cynefin's project-level granularity.
