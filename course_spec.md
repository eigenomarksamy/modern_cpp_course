> **status (curriculum 2.0):** this is the original specification the 56-day course (1.0) was written against, kept for its educational requirements. the course has since been restructured: its length now follows the material (119 days in 17 modules, each day with one objective and 5 to 10 minutes of core reading), prose follows a lowercase editorial style, and the website has a dashboard, a one-lesson reader, and a full-course page. see `README.md`, `.course_build/authoring.md`, and `.course_build/site_upgrade/plan.md` for what changed and why; the structural requirements below that fix the course at 56 days and 8 weeks are superseded.

# task: create a complete 8-week modern c++ study course

Act as a senior C++ engineer, software architect, language specialist, and technical educator.

Create a **complete, self-contained, 56-day study course** focused on modern C++17 and C++20, while revisiting important fundamentals, language mechanics, software design principles, concurrency, performance, and practical engineering techniques.

**The entire course must be created in one execution and delivered as one finished document.** Do not stop after an outline, generate only sample lessons, or require additional prompts to finish subsequent weeks.

The course should be designed for 5 to 10 minutes of reading per day over 8 weeks.

## 1. target audience

The reader is an experienced C++ software engineer with a background in systems programming, robotics, DevOps, and production software.

Assume practical professional experience, but do not assume perfect understanding of the language's underlying mechanics.

The goal is to revisit fundamentals, fill knowledge gaps, strengthen engineering intuition, and confidently apply modern C++17/20 in production.

## 2. teaching philosophy

Follow these principles throughout the document:

- **concise but meaningful:** Each daily lesson should require approximately 5 to 10 minutes of reading, including code.
- **example-driven:** Prefer concrete code demonstrations over lengthy abstract explanations.
- **fundamentals first:** Explain underlying mechanics when they help make sense of modern features.
- **theory with purpose:** Introduce language rules, memory models, compiler behavior, or mathematical concepts only where they add understanding.
- **engineering-oriented:** Connect lessons to real production problems and software architecture.
- **progressive:** Build on earlier concepts without unnecessary repetition.
- **critical:** Explain tradeoffs, limitations, misconceptions, and when a feature should not be used.
- **self-contained:** The reader should not need external resources to understand the daily lesson.

Prefer teaching through small problems, comparing approaches, and explaining why one implementation might be better.

Do not sacrifice technical accuracy for simplicity.

## 3. complete 56-day curriculum

Organize the course into 8 weeks, each containing 6 instructional lessons and 1 lightweight review day.

### week 1: rediscovering c++ fundamentals

Compilation and linking, types and initialization, scope and lifetime, pointers and references, value categories, undefined behavior, and common misconceptions.

### week 2: ownership and object-oriented c++

RAII, constructors and destructors, Rule of Zero/Five, copy and move semantics, smart pointers, polymorphism, composition, and resource safety.

### week 3: standard library and generic programming

Containers, iterators, algorithms, lambdas, templates, perfect forwarding, exception safety, and expressive programming.

### week 4: modernizing with c++17

Structured bindings, `if constexpr`, `std::optional`, `std::variant`, `std::any`, `std::string_view`, fold expressions, filesystem, and practical refactoring.

By the end of week 4, the reader should have completed a useful standalone refresher.

### week 5: the c++20 toolbox

Concepts, constraints, ranges, views, `std::span`, three-way comparison, compile-time programming, `std::format`, and selected standard-library improvements.

### week 6: concurrency and multithreading

Threads, `std::jthread`, mutexes, condition variables, futures, promises, atomics, synchronization, the memory model, deadlocks, and data races.

### week 7: software design and deeper c++

SOLID, dependency injection, design patterns, coupling and cohesion, static versus dynamic polymorphism, type erasure, API design, modules, and coroutines.

### week 8: production engineering and integration

Performance, benchmarking, cache locality, allocation costs, testing, observability, refactoring legacy code, architectural tradeoffs, and a small integrated example.

You may redistribute topics between individual days to improve progression. Preserve the overall coverage and ensure that all 56 days are present.

## 4. daily lesson format

Every lesson must contain:

**day XX: [engaging title]**

**reading time:** approximately 5 to 10 minutes

**the idea**

A short question, observation, practical problem, or misconception that introduces the topic.

**understanding the concept**

A concise explanation of the feature or principle, including relevant underlying theory.

**in code**

Usually 2 to 3 small, purposeful C++ examples showing how the idea works.

Where appropriate, demonstrate a naive implementation followed by an improved implementation.

**in practice**

One concrete example of where the idea matters in real software, such as robotics, radar processing, multithreading, libraries, or large codebases.

**watch out for**

One common mistake, subtle behavior, or important tradeoff.

**the takeaway**

One memorable conclusion.

**optional challenge**

One small thought experiment or code question, requiring no more than a few minutes.

Keep the structure consistent without forcing unnecessary sections into lessons where they add no value.

## 5. examples and technical standards

Use numerous short, carefully selected C++17/20 examples.

Include:
- Before-and-after modernization.
- Buggy code followed by corrected code.
- Alternative designs and their tradeoffs.
- Predict-the-output questions.
- Object lifetime and ownership demonstrations.
- Practical concurrency patterns.
- Small production-inspired engineering scenarios.

Examples must be technically correct, with clear language-version requirements.

Do not accidentally use C++23 features as if they were C++20.

Distinguish undefined behavior, unspecified behavior, and implementation-dependent behavior.

Never make unsupported performance claims. Explain complexity and relevant measurement considerations.

Where tools allow, compile representative examples using the correct language standard.

## 6. design thinking throughout the course

Integrate software design concepts naturally, not just during week 7.

Include discussion of:

- Encapsulation and abstraction.
- Composition versus inheritance.
- Ownership and API contracts.
- Cohesion and coupling.
- Dependency injection and testing.
- SOLID and its limitations.
- Strategy, Factory, Observer, and other useful patterns.
- Compile-time versus runtime tradeoffs.
- Data-oriented versus object-oriented design.
- Error handling and exception safety.
- Maintainability versus performance.
- Abstraction versus overengineering.

Teach engineering judgment rather than rigid rules.

## 7. weekly reinforcement

Every seventh day should be a lightweight review day containing:

- A compact recap.
- Three to five conceptual review questions.
- One optional miniature coding exercise.
- Answers with brief explanations.
- Connections to previously studied material.

Keep review days within the same 5 to 10 minute reading limit.

Include occasional spaced-repetition questions across weeks.

## 8. final document format

Create a single Markdown document called:

`modern_cpp_daily_course.md`

It must contain, in this order:

1. Introduction and learning philosophy.
2. Complete 8-week course overview.
3. Clickable table of contents.
4. A 56-day progress checklist.
5. All 56 daily lessons, fully written.
6. Weekly reviews integrated into the course.
7. A concise modern C++17/20 cheat sheet.
8. A curated list of authoritative references for deeper study.

Use concise paragraphs, syntax-highlighted code blocks, occasional comparison tables, and small diagrams when helpful.

Use lowercase section headings and avoid em dashes.

The writing should feel like one experienced engineer sharing useful insights with another, rather than a formal textbook.

## 9. critical requirement: one-shot creation

This is a non-negotiable requirement.

**Generate the complete course in one execution, as one finished artifact.**

Follow these rules:

1. Do not ask me to approve the outline.
2. Do not stop after the first week.
3. Do not deliver a sample chapter instead of the full course.
4. Do not use placeholders such as "lesson to be added later", "continue here", or "remaining weeks forthcoming".
5. Do not shorten later weeks to compensate for output limitations.
6. Do not require me to send "continue" or another prompt to finish the course.
7. Do not claim the document is complete unless all 56 entries contain their intended material.
8. If possible, write the artifact directly to the filesystem instead of printing the entire course in chat.

You are permitted to organize the generation process internally into multiple stages or temporary files, but those stages must happen as part of this same execution.

If agent delegation or parallel processing is available, you may use it to generate and review independent weeks, ensuring a consistent teaching style and curriculum.

If necessary, create intermediate files for individual weeks and combine them into the final document. This is an internal implementation detail, not a request for separate deliveries.

**The final deliverable must be one coherent and complete document.**

If there are output-size limitations, prioritize writing the artifact directly using the available file-creation tools rather than truncating the course to fit a chat response.

If the environment cannot produce the complete document in one execution, state the actual limitation rather than presenting an incomplete artifact as finished.

## 10. validation before delivery

Perform a final completeness and quality review.

Verify that:

- All 56 days exist.
- All 8 weekly reviews exist.
- Every day contains substantive instructional material.
- The reading time remains approximately 5 to 10 minutes.
- Code examples match the indicated C++ standard.
- Later weeks receive the same attention as earlier weeks.
- There are no unfinished sections or placeholders.
- The table of contents and internal references work.
- The final document reads as a coherent learning progression.
- The original source document is suitable for later editing and expansion.

Use cppreference, the C++ Core Guidelines, and authoritative language references when necessary. Never claim verification steps were performed if tools were unavailable.

## 11. future maintenance

Treat this document as **version 1.0 of a reusable learning resource**.

The initial version must be complete and usable on its own.

Future requests may involve:
- Expanding individual explanations.
- Adding more code examples.
- Updating lessons for newer C++ standards.
- Introducing optional advanced chapters.
- Correcting technical inaccuracies.
- Adjusting the depth of particular topics.

Design the structure to support such modifications without requiring the entire document to be regenerated.

## 12. begin execution

Create the curriculum internally, write all 56 lessons, perform validation, and deliver the finished `modern_cpp_daily_course.md` file.

Do not ask for clarification or approval before creating it.

**Your task is to deliver the course, not to propose how it could be written.**

## 13. persistent checkpoints, interruption recovery, and session-independent resumption

The course must support reliable generation across independent Claude Code sessions without depending on conversation history, cached context, or the previous instance's memory.

**Primary objective:** Complete the entire 56-day course in one execution whenever possible.

**Recovery objective:** If execution is interrupted for any reason, a completely new Claude Code instance must be able to continue from the last successfully completed checkpoint without regenerating existing work.

Implement the following persistent generation system.

### 13.1. persistent project structure

Use the following directory structure:

```text
modern_cpp_course/
├── course_spec.md
├── modern_cpp_daily_course.md
└── .course_build/
    ├── curriculum.md
    ├── state.json
    ├── handoff.md
    └── lessons/
        ├── day-01.md
        ├── day-02.md
        ├── ...
        └── day-56.md
```

Responsibilities:

**course_spec.md**
- Contains the complete original course-generation instructions.
- Serves as the authoritative specification for all future sessions.
- Must be written before lesson generation begins.
- Never rely on previous conversation history to recover these requirements.

**curriculum.md**
- Contains the complete 56-day lesson plan.
- Includes day numbers, lesson titles, learning objectives, and dependencies.
- Establishes the curriculum before generation begins.
- Acts as the authoritative topic map during generation.
- Must not be silently changed during resumption.

**state.json**
- Contains machine-readable generation progress.
- Records every lesson's completion status.
- Identifies the next required action.
- Tracks assembly and validation status.
- Is updated after each successfully completed lesson.

**handoff.md**
- Contains a concise summary for the next Claude instance.
- Includes the current generation phase.
- Describes what has already been completed.
- Identifies the exact next lesson or operation.
- Records important cross-lesson decisions and unresolved issues.
- Must remain short enough to read cheaply in a fresh context window.

**lessons/day-XX.md**
- Contains one completed daily lesson.
- Is independently reusable.
- Should not be rewritten during normal resumption.
- Uses consistent headings and formatting.

**modern_cpp_daily_course.md**
- Is the final, consolidated deliverable.
- Must contain all 56 lessons and supplementary sections.
- Should only be published as complete after successful assembly and validation.

The intermediate files exist to enable recovery. The final user-facing artifact remains one complete Markdown document.

### 13.2. checkpoint manifest

Create a `state.json` file with a structure similar to:

```json
{
  "project": "modern_cpp_daily_course",
  "spec_version": "1.0",
  "phase": "generation",
  "total_days": 56,
  "completed_days": 0,
  "next_day": 1,
  "lessons": {
    "01": {
      "status": "pending",
      "path": ".course_build/lessons/day-01.md"
    }
  },
  "assembly": "pending",
  "validation": "pending",
  "last_successful_action": "curriculum_created"
}
```

Populate the lessons object with entries for all 56 days.

Supported lesson states:
- `pending`
- `in_progress`
- `complete`
- `needs_repair`

Supported project phases:
- `initialization`
- `generation`
- `assembly`
- `validation`
- `complete`

A lesson may only be marked `complete` when:
1. Its file exists.
2. The content is fully written.
3. No required lesson sections are missing.
4. The file passes basic structural checks.

Do not count an incomplete or partially written lesson as completed.

### 13.3. checkpointing procedure

After generating each lesson:

1. Write the complete lesson to a temporary file.
2. Validate its structure and content.
3. Atomically rename the temporary file to `day-XX.md`.
4. Update `state.json` using an atomic file replacement.
5. Update `handoff.md` with the current position and necessary continuity notes.
6. Continue immediately to the next lesson.

Never wait until the end of a week to save progress.

A process interruption should result in the loss of no more than the currently unfinished lesson.

Treat successfully completed lesson files as immutable during normal generation.

### 13.4. automatic recovery detection

At the beginning of every execution, including the first execution:

1. Check whether `course_spec.md` and `.course_build/state.json` exist.
2. If neither exists, initialize the project.
3. If they exist, enter resume mode automatically.
4. Read the persisted specification, manifest, curriculum, and handoff.
5. Inspect only the files necessary to confirm the current checkpoint.
6. Reconcile the manifest with the actual filesystem.
7. Resume from the earliest incomplete or invalid lesson.

Do not regenerate completed lessons.

Do not recreate the curriculum if a valid curriculum already exists.

Do not rebuild the entire document merely because a new Claude session has started.

If the manifest indicates a lesson is complete but the actual file is missing or invalid, mark that lesson `needs_repair` and regenerate only that lesson.

If a valid lesson exists but the manifest was not updated before an interruption, recover the lesson and update the manifest rather than generating a duplicate.

The filesystem is the durable source of truth. The manifest is a progress index that must remain consistent with it.

### 13.5. context-efficient resumption

When resuming in a new Claude Code instance, minimize context usage.

Load only:

1. The persistent course specification.
2. The complete curriculum outline.
3. The checkpoint manifest.
4. The short handoff document.
5. The most recent one or two completed lessons, if needed for style continuity.

Do not load every completed lesson into the model's context unless required for a specific validation or repair.

Use filesystem operations and scripts to inspect, count, assemble, and validate files whenever possible.

Avoid repeating previous analysis, planning, or research unless the persistent artifacts indicate that the information is missing or unreliable.

A fresh instance should recover the project state from files, not from conversation reconstruction.

### 13.6. explicit resume command

Recognize the following user instruction:

`resume modern cpp course`

When this instruction is received:

- Locate the existing project in the current working directory.
- Read the persisted specification and checkpoint information.
- Determine the next required operation.
- Continue execution immediately.
- Preserve completed lessons.
- Do not ask for the original prompt again.
- Do not ask for confirmation or approval.
- Do not restart the generation from day 1 unless no valid project state exists.

This command must also work when the previous Claude session is no longer accessible.

### 13.7. handling interruptions at different stages

**If interrupted during initialization:**

Recover valid specification and curriculum files. Complete only the missing initialization steps.

**If interrupted while generating a lesson:**

Discard or repair the unfinished temporary lesson, preserving all previously completed lessons.

**If interrupted between lessons:**

Continue with the next pending lesson.

**If interrupted during final assembly:**

Reconstruct the consolidated Markdown document from the existing completed lesson files. Do not regenerate the lessons.

**If interrupted during validation:**

Resume validation using existing artifacts. Repair only verified problems.

**If the course is already complete:**

Do not regenerate anything. Report that generation is complete and identify the final document.

### 13.8. deterministic final assembly

Once all 56 lessons are complete:

1. Read the completed lesson files in numerical order.
2. Generate the introduction, course overview, progress tracker, and table of contents.
3. Integrate all daily lessons and weekly reviews.
4. Append the final cheat sheet and references.
5. Write the assembled document to a temporary file.
6. Validate the assembled document.
7. Atomically publish it as `modern_cpp_daily_course.md`.
8. Mark the project as `complete`.

Use scripts where practical for deterministic ordering, file combination, and structural validation.

Ensure that every day appears exactly once.

Never overwrite a valid completed document with a partially assembled one.

### 13.9. safe regeneration and future updates

Support three distinct operating modes.

**create**
- Initialize a new course only if a course does not already exist.
- Generate the complete course.

**resume**
- Continue an existing interrupted generation.
- Preserve existing completed content.

**revise**
- Modify an already completed course based on explicit user instructions.
- Change only the affected lessons unless broader changes are required.
- Reassemble and revalidate the final document.
- Preserve all unaffected lesson files.

Default to automatic create-or-resume behavior.

Never interpret a resume request as permission to regenerate the entire course.

### 13.10. completion criteria

Generation is complete only when:

- All 56 lesson files exist and are validated.
- All 8 review days are present.
- The introduction and course overview exist.
- The progress checklist is complete.
- The final cheat sheet and reference sections exist.
- The consolidated Markdown document contains no missing lessons.
- The final document passes structural validation.
- `state.json` reports `"phase": "complete"`.

Do not mark the project complete prematurely.

### 13.11. important execution rules

- The first attempt should generate everything in a single execution.
- Checkpointing must happen continuously during that execution.
- Checkpointing must not introduce unnecessary pauses or require user interaction.
- No explicit approval is needed between lessons or weeks.
- A new instance must be able to recover from persistent files alone.
- Never rely on session memory for correctness.
- Never discard valid completed work.
- If recovery is impossible because required files are missing or inaccessible, report exactly what is missing.
- Do not silently restart the entire course.

**The objective is an uninterrupted one-shot generation when possible, combined with reliable, idempotent, low-context recovery when necessary.**
