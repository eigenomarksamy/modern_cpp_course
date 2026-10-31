# day 49 compile checks

Toolchain: MSYS2 g++ 12.1.0, flags `-std=c++20 -Wall -Wextra -pedantic`, scratch folder outside the repo. Code blocks were extracted from the lesson by script.

- Review question 5 (`fields(std::string_view)` generator fed from `read_line()`): the declarations and calls compiled against day 48's `Generator` with `use` and `read_line` declared only. Compile-only, since the snippet is UB by design and has no definitions.
- Mini exercise "before" `TelemetryUploader`: compiled and ran with stub `HttpClient` and `serialize`, no warnings.
- Mini exercise solution (`BatchSink`, `TelemetryUploader` with injected sink and `std::function` clock, `FakeSink`, test `main`): compiled verbatim, no warnings; both asserts passed (buffer kept on failure, cleared on success, payload `"0\nbattery=24.1\n"`).
- Not compiled: answers 6 and 7 describe behavior already checked on days 46 (forwarding-reference constructor selected over the copy constructor) and 45 (snapshot-based `emit` with reentrant unsubscribe).
