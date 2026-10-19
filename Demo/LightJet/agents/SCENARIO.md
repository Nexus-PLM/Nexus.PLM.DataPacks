# The project the agents execute

**Change request `LSS-ECR-00002` — redesign the ram air inlet scoop for improved pressure
recovery — from change board disposition through to a releasable design.**

It was chosen because it is unfinished and genuinely contested. Ground test measured pack
inlet pressure 3.1 kPa below what the performance model assumed, which eats the hot-day
cooling margin that is a guarantee in the sales specification. The change control board has
already seen it once and refused to disposition it until stress produce the case for the
revised attachment. So the work is real: there is something to decide, something to
substantiate, and something that can legitimately be rejected.

## The objects in play

| Object | What it is |
|---|---|
| `LSS-ECR-00002` | The change request. Under Review, awaiting board disposition. |
| `LSS-21-0012` | Ram air inlet scoop. In Design Review, carbon/epoxy, mass calculated not weighed. |
| `LSS-DWG-21-0012` | Its drawing, in Airworthiness Sign-off. |
| `LSS-21-INST-001` | The ECS installation the scoop sits in. Released; the scoop link follows `latest`. |
| `LSS-REQ-SYS-0001` | Cabin altitude requirement allocated to the ECS. |
| `LSS-CERT-COMP-001` | The compliance item for CS 23.2320, currently Submitted. |
| `NX00200303` | The task "Redesign ram air inlet scoop", At-Risk, 46% complete. |
| `LSS-V-00002` | Air cycle machine, pinned at revision A in the BOM — qualification credit. |

## The threads

**`NX-200 ATA 21 ram air scoop redesign`** is the shared thread, and it is for things the
whole group needs: a decision, a position, a blocker that changes what others should do.
Read it before you post.

**Everything else goes one-to-one.** `me.ask("p.lindqvist", "LSS-21-0014 attachment",
"...")` opens a private thread with one colleague. Most of what you need from each other
is a question for one person, and asking it in front of nine is how a shared thread stops
being readable.

Last time every exchange went into the shared thread and it ran to 340,000 characters —
56 messages averaging five thousand each, every one a finished report. Nobody could find
the decision. `say` now refuses a message over 900 characters; that limit is the point,
not an obstacle. Make one point, name who you need the next thing from, and put the detail
on the OBJECT where it can be navigated to.

## The sequence

Each role does its own part, but this is a conversation and conversations take turns.

**Post one thing, then go and do something else.** Do not write your whole position in one
message and leave. If you asked somebody a question, carry on with work that does not
depend on the answer, and come back and read.

**Answer what was asked.** If somebody asked you a yes/no question, the first word of your
reply is yes or no. An unanswered question in the thread is more urgent than another
statement of your own.

**It is fine to disagree, and fine to be waiting.** "I cannot clear this until stress give
me the allowable" is a real state and worth posting. Nine simultaneous monologues is not a
design review.

1. **Programme manager** — read programme health and what the change costs in weight,
   schedule and certification. Chair the board: disposition `LSS-ECR-00002`, or say
   explicitly what is still missing and leave it Under Review. Your call either way, with
   the reason on the record.
2. **Project manager** — make the work breakdown tell the truth about this change: the
   task's progress, health, forecast and who holds it. Name what is actually blocking, by
   object number.
3. **Stress and loads** — the board asked for the attachment case. Review the revised
   scoop, record the substantiation, and clear or reject the stress step.
4. **Designer** — bring `LSS-21-0012` to a releasable state: honest mass and mass status,
   material and process fields, and the drawing consistent with it. Submit for release when
   it is genuinely ready, not before.
5. **Systems engineer** — does this change touch `LSS-REQ-SYS-0001` or the compliance item?
   Check the trace links for anything gone suspect and update verification status with a
   reason.
6. **Quality** — decide whether revision B of the scoop needs a first article, and which
   kind. If it does, say which characteristics it covers.
7. **Supply chain** — the scoop changes from glass to carbon laminate. What does that do to
   the source, the lead time and the approved-source position?
8. **Customer support** — three aircraft are flying. Does this change reach them? If it
   does, say what the service bulletin would have to carry.
9. **FAA DER** — review what is offered for approval. Approve only against evidence that
   exists and is referenced. If the compliance item is still open or a report is unreleased,
   reject and say exactly why.

## What finishing looks like

Not "the change is approved". Finishing means every role has done its part honestly, the
record says who decided what and on what basis, and the disagreements are visible rather
than smoothed over. A well-argued rejection is a better outcome than an approval nobody
could defend.

Report every security, usability and missing-functionality finding as you go.

---

# Wave 2 — the change processes themselves

Wave 1 established the position on the scoop. Wave 2 exercises the design and engineering
change processes a certified programme actually runs, on the data wave 1 left behind.

An approved revision never moves backwards. That is not a limitation to work around, it is
the point: you do not un-release a drawing that aeroplanes were built to. The legitimate
moves are all here, and each role runs the ones that belong to it.

## The six drills

**1. Revise and re-release.** `LSS-21-0004` is at revision B, Released. Raise revision C
through the proper route: revise the object, change what the change requires, submit for
release, and let the approval route set Released. The old revision becomes Superseded, not
deleted — parts built to it are in service.

**2. Re-run an invalidated test.** `LSS-F-00010` went to revision B with the swivel
interlock, and the dynamic test report `LSS-CERT-QUAL-002` is still in Airworthiness
Sign-off. Decide whether the existing test credit still stands, and if it does not, say
what has to be re-run and against which configuration.

**3. New part number, and supersede.** The ram air scoop changes from glass to carbon. Is
that a revision of `LSS-21-0012` or a new part number? Make the call on the
interchangeability rule — one-way interchangeable is still the same part; not
interchangeable is a new number — and if it is a new number, create it and supersede the
old one.

**4. The full change chain.** `LSS-ECR-00002` is Under Review. Carry it through: board
disposition, an ECO that implements it with effectivity, the affected items, and an ECN
that tells manufacturing, supply chain, quality and customer support.

**5. Deviation or waiver.** Raise a nonconformance against a real condition in the data and
take it to disposition. Use-as-is on type design data needs airworthiness concurrence; a
waiver on product already delivered is a different decision from a deviation on product
still in the factory, and the record has to say which.

**6. Delta first article.** A changed characteristic needs a delta FAI covering only what
changed, against the ballooned issue of the drawing. Decide what revision C of
`LSS-21-0004` would need.

## Releasing anything

Nobody releases by hand any more, and that is correct. The route is:

```python
me.invoke_action(part, "SubmitForRelease")   # starts the type design release workflow
me.my_tasks()                                # approvers find their task here
me.decide(task_id, "Approved" | "Rejected", "the basis for the decision")
```

Design check and airworthiness both have to approve before the workflow sets Released. A
rejection returns it to the originator with your comment on the trail. If you are asked to
approve something whose evidence does not exist, reject it and say why — that is the whole
reason the step exists.

---

# Wave 3 — an in-service problem that forces a design AND a material change

This is the one that has to hold together end to end, because it is the hardest thing a
PLM system is asked to do: a fault found on a delivered aeroplane, traced to a cause that
is BOTH a design detail and a material choice, changed through the proper route, re-tested
where the change invalidated the evidence, re-approved by the people whose approval it
invalidated, and told to the fleet — with the whole chain navigable afterwards.

Nothing here is pre-written. The objects below are the starting conditions; what the
record ends up saying is whatever the roles decide it says.

## The report

**`f.mbeki` raises it.** Two of the three delivered aeroplanes show corrosion products at
the pack bay firewall penetration after roughly 400 flight hours — at the interface
between the titanium seal plate `LSS-21-0014` and the surrounding aluminium structure.
Operators found it at the 400-hour inspection. No flight has been affected and nothing has
failed, but it is the second aircraft, and the first was dismissed as a one-off.

Raise it as a `ProblemReport`, properly: what was found, where, by whom, on which
aeroplanes, detection phase, severity, and the affected item. Do not diagnose it — that is
engineering's job, and a problem report that contains its own conclusion usually contains
the wrong one.

## What investigation should find

The roles work this out between them; it is written here so the scenario has a true answer
to converge on, not so anyone can skip to it.

The titanium plate and the 2024 aluminium structure are a galvanic couple. The joint is
sealed with `LSS-CM-0001` (polysulphide, `LSS-MAT-00014`, AMS 3277 Class B-2), whose max
service temperature is **120 °C**. The pack bay runs hotter than that at the penetration
during bleed operation. The sealant degrades, stops being a barrier, moisture reaches the
couple, and the aluminium corrodes.

So neither change works alone:

* **A material change.** AMS 3277 is the wrong sealant for this location. A
  high-temperature sealant is needed, with its own qualification, allowables position,
  shelf life, storage and approved sources — a new `Material` object, not an edit to the
  old one. The old sealant stays qualified for everywhere else it is used.
* **A design change.** The new sealant needs a different joint: a sealing land and an
  isolation detail that separates the two metals rather than relying on the sealant alone.
  That is a new revision of `LSS-21-0014` and of its drawing.

## What each role owns

1. **`f.mbeki`** — raise the problem report. Later: assess fleet impact and prepare the
   service bulletin for the two affected aeroplanes and the third.
2. **`h.okafor`** — convene the board, disposition the change request, judge it against
   cost, weight, schedule and certification.
3. **`m.sandoval`** — the design change: revision B of `LSS-21-0014` and its drawing, with
   the isolation detail and the new sealing land.
4. **`y.cheng`** — the material change: source the new sealant, its approved sources, its
   obsolescence and counterfeit position, and what it does to lead time.
5. **`t.brennan`** — the process: `LSS-PS-0006` governs sealant application and its
   parameters no longer fit. Say what changes.
6. **`p.lindqvist`** — whether the isolation detail changes the joint structurally, and
   whether corrosion already found on two aeroplanes affects the substantiation.
7. **`r.achebe`** — which requirements and compliance items this touches, and which trace
   links go suspect when the plate is revised.
8. **`k.tanaka`** — a nonconformance against the two affected aeroplanes, its disposition,
   and what first article the revised plate needs.
9. **`c.delacroix`** — the re-approval. `LSS-CERT-COMP-006` (flammable fluid fire
   protection at this penetration) rests on a firewall penetration test run on the OLD
   joint with the OLD sealant. Decide whether that evidence still stands.

## What "fully documented" means here

Not prose in a discussion thread. Every one of these, as objects and links:

* the problem report, linked to the affected item;
* a change request that names the problem report as its source, and a change order with
  effectivity that names the change request;
* the new material object, and the part referencing it instead of the old one;
* the revised part and drawing, released through the approval route, with the old
  revision Superseded rather than deleted;
* the re-run test evidence, or a recorded decision that the existing evidence still
  stands and why;
* a change notice to the functions that have to act;
* a service bulletin with effectivity, compliance period, labour and kit;
* a nonconformance covering the aeroplanes already affected.

## The traceability test

When it is finished, the administrator will ask the system one question and expect the
answer in clicks, not prose:

> *Starting from the corrosion found on aeroplane 002, show me every object that changed
> because of it, who approved each change and on what basis, and what the fleet was told.*

Build the record so that question answers itself. If some link in that chain cannot be
made because the system has nowhere to put it, that is a `missing` finding and it is more
valuable than the workaround — report it and say which link broke.

Thread: **`NX-200 ATA 21 firewall penetration corrosion`**.
