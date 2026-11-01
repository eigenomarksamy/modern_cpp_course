---
title: architectural decisions and their tradeoffs
standard: C++17
objective: replace subsystems incrementally with the strangler pattern, decide what not to refactor, and record architectural tradeoffs so they can be revisited
prerequisites: legacy-refactoring, data-oriented-design
difficulty: 2
---

### the idea

"we should rewrite the tracker" is a sentence that has started many projects that took three times longer than planned, while the old tracker kept shipping fixes the new one did not have. most architectural change is better done the way the previous lesson changed one function: incrementally, with the old and the new side by side, and with the reasons written down so the next engineer can revisit the decision instead of rediscovering it.

### understanding the concept

the **strangler pattern** replaces a subsystem without a big bang: put an interface in front of the old implementation, build the new one behind the same interface, route a growing share of traffic to it, and delete the old one when nothing uses it. in robotics this often means running the new module in shadow mode on recorded data and comparing its outputs with the old one before it ever drives a motor.

the decisions behind such changes are tradeoffs rather than improvements: maintainability against performance, abstraction against overengineering, compile-time against run-time flexibility, object-oriented against data-oriented layout. each side has real costs, and the course has met all four. what turns them from arguments into decisions is writing down the context, the alternatives, and the consequences accepted, in a place the next person will look.

### in code

the refactors that need judgment get written down. a lightweight architecture decision record (ADR) fits in a file next to the code:

```text
ADR-017: track storage layout
status:       accepted
context:      tracker misses its frame budget at high detection counts; perf counters
              show the association loop is dominated by cache misses.
decision:     store tracks as struct-of-arrays inside TrackTable; public API unchanged.
alternatives: keep AoS with hot/cold split (measured, not enough);
              pooled Track objects (fewer allocations, same misses).
consequences: + association loop within budget on recorded sessions
              - a new track field touches three places in TrackTable
              - debugger shows arrays, not tracks (pretty-printer added)
revisit if:   per-track behavior grows (polymorphic motion models) or counts drop.
```

### in practice

modernization campaigns across a whole codebase are architectural work too, and the same rule applies: small, reviewable steps. tools beat people at mechanical edits:

mechanical modernization is where tools beat people. `clang-tidy` has a family of `modernize-*` checks (`use-nullptr`, `use-override`, `make-unique`, `loop-convert`, `use-using`, `pass-by-value`, and more) that rewrite code with fixes:

```sh
# one check per commit: each diff is large but trivially reviewable
run-clang-tidy -p build -checks='-*,modernize-use-nullptr' -fix
run-clang-tidy -p build -checks='-*,modernize-use-override' -fix
# reformat once, in its own commit, then hide it from blame
clang-format -i $(git ls-files '*.cpp' '*.h')
git rev-parse HEAD >> .git-blame-ignore-revs     # git config blame.ignoreRevsFile ...
```

the format matters less than the habit: context, the decision, the alternatives considered, the costs accepted, and when to revisit. the classic tradeoffs (maintainability versus performance, abstraction versus overengineering, compile-time versus runtime flexibility, object-oriented versus data-oriented layout) stop being religious arguments once each side has to write down its consequences.

not everything should be refactored. code that works, rarely changes, and is scheduled for retirement is cheapest left alone. prioritize by change frequency times pain: `git log` tells you which files churn, and the bug tracker tells you which ones hurt.

### watch out for

**the second-system effect.** a replacement designed to fix every complaint about the old system tends to become larger, slower, and later than anyone planned, because every stakeholder adds the feature the old design could not support. the strangler pattern is the antidote: the new component must reach parity with the old one on recorded data, one route at a time, before it gets new features. scope that is explicitly deferred in the decision record is scope that does not silently creep in.

### the takeaway

replace subsystems incrementally behind a stable interface, refactor where change frequency and pain are highest, and record each architectural decision with its alternatives and costs.

### optional challenge

your team wants to replace a legacy obstacle detector with a new one. using the strangler pattern, list the steps from today to deleting the old code, and say which observability signals tell you each step is safe.

<details>
<summary>answer</summary>

put an interface in front of the old detector (a seam, if there is none yet) and route all callers through it. build the new detector behind the same interface and run it in shadow mode on live or recorded data, comparing its outputs with the old one's: metrics for detection counts, disagreement rates, and per-frame latency histograms tell you when it is at parity. then route a growing share of real traffic to it (one robot, one site, one sensor configuration), watching the same metrics plus field reports. when nothing uses the old detector for a release cycle, delete it, together with the comparison code. at every step the system works and the switch can be reverted.

</details>
