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

## The thread

Everyone posts to **`NX-200 ATA 21 ram air scoop redesign`**. Read it before you post.

## The sequence

Each role does its own part. You do not need to wait for the others to finish — post what
you have, say what you need and from whom, and read the thread for answers.

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
