# Implementation session cost optimization

## Simple cost analysis model

I use test-driven process to improve design and keep implementation simple.

For each test, I do a full test-red-implement-green cycle. Which is at least 2 tool
calls with proper tool batching and chaining:

1. test-red
2. implement-green.

Any trivial fix is at least one more (implement-green).

Even a simple feature can have about 15 tests. Add a few cycles for lint fixes, type
fixes, possible refactorings, and that makes a lot of tool calls.

Tool calls are expensive, because they add to the context their inputs and outputs and
outputs and imply a system re-run to process the tool output.

Anthropic prompt caching system helps soften the blow: cached reads cost x0.1 normal
reads. My AI told me that Antropic does not document the way `claude` sets cache
breakpoints, so I guess you should assume this is *not* every user input or tool run,
which are the natural breakpoints. So the computations are fuzzy by a linear factor.
That, in a schoolbook case, is dominated by a quadratic factor.

Say:

- I have 10 ktok initial context plan
- that plan takes 100 tool use to implement,
- on average each tool use adds 0.5 ktok to the session context.
- The total write cost is does not matter much either, it groes linearly with:
  - *tests:* the problem definition,
  - *src:* solution size,
  - *tdd cycles:* and implementation granularity.
- Once written to cache, model output becomes part of the recurring read cost.
  - There must be something wrong in my understanding. All model output is either
    thought, tool call, or user answer. Actually, tool call and user prompt interaction
    have the same structure from the model's perspective. All this output becomes part
    of the conversation context on the next tool response or user prompt.
    - So what output is *not* cached? That's unclear. Only output that has not been part
      of a rerun? Clarifications?

The total read cost should be the sum of the read cost of each step:

1. 10k: initial input
2. 1k cached, 500 tok tool command + answer
3. 1k + 50 tok cached, + 500 tok
4. 1k + 100 tok, + 500 tok

- There is a constant 10k read cost for the plan and context. Plus some for initial
  cache write.
- On further runs, this cached context is read for x0.1 read price: 1k. This read cost
  is linear with the number of tool calls.
- There is on average 500 tok cost by tool call. It's a linear term, too.
- The accumulated context from tool calls is bit that hurt. Even cached, it costs:
  - $50 + 100 + 150 ... + (n-1) * 50 = n * (n - 1) * 25$
  - For 100 tools calls, that's: $100 * 99 * 25 tok = 247.5 ktok$
- Compare that with the cost of the meaningful input: system prompt and plan, cached for
  every run after the first one.
  - $10k + 1k * n = 110 ktok$
- In this scenario, the cost of essentially useless accumulated context, is greater than
  the cost of useful input.

I was expecting 100 successive tool uses to cost more than that. We need empirical data
from previous sessions to get a more useful picture.

What that points out, is the shared context for tool calls is the part that must be
minimmized in priority. On example is the lint role, that runs without plan or system
architecture information, which makes multiple iterations relatively cheap.

Say we half / double the number of calls to 50 / 200:

- $50 * 49 * 25 tok = 61.25 ktok$
  - Halved number of calls, divided overhead by four.
- $199 * 200 * 25 tok = 995 ktok$
  - Doubled number of calls, multiplied overhead by four.

It's the reason the core rules of any tool user must insist on planning ahead, and doing
multiple edits in one batch, by ordering edits starting with the end of the file, so
line numbers of following edits are not affected. That makes it possible to turn $n + 1$
model re-runs (n file changes, 1 test run) into one model re-run.

TODO: collect empirical data on tool call cost vs context size from claude code saved
sessions, or maybe ccost.

## Rule files update

- Task Opus to update or write role files.
- Update plan to conform to the new process.

## code.md

- Deslop instruction: omit blank lines and comments that are not important for
  comprehension by an experienced software engineer.
- Instruct specifically to make as few as 2 tool call batches by TDD iteration.
  1. write test, run red test, chained.
  2. write impl, run green test, chained.
- Agent must verify that failure is the expected on.
  - ImportError does not cut it.
- On unexpected success or error:
  - Task agent can try to fix once, trivial fixes only,
  - and terminate if the fix is not successful.

## recover.md

New role for strong agents.

Given plan and failure state, either unexpected passing test or unexpected failure,
provides:

1. fix to execute,
2. and updates plan if necessary.

If the fix is simple, apply immediately. If it's complex, write plan to disk and
reference file in the answer that the orchestrate role transmits to the code role.

To reuse cached context, the same recover agent can be used multiple times in the same
session.

## review.md

New role for strong agents.

- Examine code changes on a clean context, without looking at plan.
- Enforce concision, expressiveness, and factorisation, in particular for tests.

If changes are needed:

- If possible, implement review changes in single tool batch (writes + test),
- or prepare plan for haiku if changes are too complex.

## orchestrate.md

New role for weak agents.

- For each plan phase:
  1. code task, runs the full tdd loop for the phase.
     - If a task stopped early, start a Sonnet agent with *recover* role
     - To prevent thrashing, the recover agent agent has one try to fix the error. If
       the proposed fix did not work, stop execution and request user input.
  2. Lint task
  3. If needed: refactor plan.
  4. Code review by sonnet agent.
