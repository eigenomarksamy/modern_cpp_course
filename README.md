# modern c++ daily course

A 56-day course on modern C++17 and C++20 for working engineers: 8 weeks, 5 to 10 minutes of reading a day, with a review every seventh day. Read it at [cpp.eigenomar.com](https://cpp.eigenomar.com), or read [`modern_cpp_daily_course.md`](modern_cpp_daily_course.md) directly.

## layout

```text
modern_cpp_daily_course.md   the course, one document (generated, do not edit by hand)
course_spec.md               the requirements the course was written against
.course_build/               the sources: one file per lesson, sections, curriculum, compile-check notes
  tools/course.py            checks lessons, assembles and validates the document
scripts/build.mjs            renders the document into dist/index.html for the website
wrangler.jsonc               Cloudflare Worker config (static assets only)
```

## editing the course

Change a lesson in `.course_build/lessons/day-XX.md` (or a section in `.course_build/sections/`), then:

```sh
python .course_build/tools/course.py check .course_build/lessons/day-XX.md
python .course_build/tools/course.py assemble
```

`assemble` rebuilds `modern_cpp_daily_course.md` and publishes it only if it validates. `.course_build/handoff.md` has the full workflow.

## the website

Requires Node 22.12 or newer.

| command           | what it does                                         |
| :---------------- | :--------------------------------------------------- |
| `npm install`     | install dependencies                                 |
| `npm run build`   | render the course into `dist/`                       |
| `npm run preview` | build and serve it locally with wrangler             |
| `npm run deploy`  | build and deploy to Cloudflare from your machine     |

Deploys go to the `modern-cpp-course` Worker, which serves `dist/` and attaches `cpp.eigenomar.com`. With the repo connected in the Cloudflare dashboard (build command `npm run build`, deploy command `npx wrangler deploy`), every push to `main` goes live.
