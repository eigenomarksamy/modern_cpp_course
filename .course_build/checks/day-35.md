# day 35 compile checks

Toolchain: MSYS2 g++ 12.1.0 (libstdc++ 12), flags `-std=c++20 -Wall -Wextra -pedantic`, scratch folder outside the repo.

## review question snippets: compiled and run

- Q2: both pipelines compile without a warning. (a) printed `2 4 6`; `load_ids() | std::views::all` is `std::ranges::owning_view<std::vector<int>>` (static_assert passed). (b) printed garbage values (`1211312048 583 ...`), consistent with reading a destroyed temporary (UB; the output is not meaningful).
- Q3: defaulted `<=>` on a struct with a `float` member returns `std::partial_ordering` (static_assert passed); `n == n` with a NaN member prints `0`; `std::strong_order(1.0f, NAN) == std::strong_ordering::less` prints `1`.
- Q6: `std::string_view` from `std::string` temporary and `std::span<const float>` from a `std::vector<float>` temporary compile; `std::span<float> m = make_samples();` fails with "conversion from 'std::vector<float>' to non-scalar type 'std::span<float>' requested".
- Q7: `Frame` with a printing copy constructor and a non-`noexcept` move constructor; growing a `std::vector<Frame>` prints `copy`.

## mini exercise answer: compiled and run (without `<format>`)

The `Numeric` concept, both `rms` overloads, and calls with `std::vector<float>{3, 4}` (`3.536`), `std::array<std::int16_t, 3>{1, 2, 2}` (`1.732`), `std::span<const float>`, `std::span<float>`, and an empty vector (`nullopt`). Output was printed with `printf("%.3f")` in place of `std::format`.

- With only the span overload, `rms(v)` fails: "no matching function for call to 'rms(std::vector<float>&)'" with the note "'std::vector<float>' is not derived from 'std::span<const T>'" (quoted in the lesson).
- `std::vector<bool>` and `std::array<bool, 1>` are both rejected ("no matching function").
- Not checked: the `std::format` line (GCC 12 has no `<format>`); expected `"rms 3.536 over 2 samples"` from the `printf` equivalent.
