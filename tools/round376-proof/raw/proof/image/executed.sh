set -eu
mkdir -p /out/stdio
export ASAN_OPTIONS=halt_on_error=1
export UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/a/sample-seed3541 --out /out/valid-0 >/out/stdio/0.out 2>/out/stdio/0.err
code=$?
set -e
echo "$code" >/out/stdio/0.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/a/sample-seed3541 --out /out/valid-1 >/out/stdio/1.out 2>/out/stdio/1.err
code=$?
set -e
echo "$code" >/out/stdio/1.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/a/sample-seed3541 --out /out/valid-2 >/out/stdio/2.out 2>/out/stdio/2.err
code=$?
set -e
echo "$code" >/out/stdio/2.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/a/sample-seed3547 --out /out/valid-3 >/out/stdio/3.out 2>/out/stdio/3.err
code=$?
set -e
echo "$code" >/out/stdio/3.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/a/sample-seed3547 --out /out/valid-4 >/out/stdio/4.out 2>/out/stdio/4.err
code=$?
set -e
echo "$code" >/out/stdio/4.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/a/sample-seed3547 --out /out/valid-5 >/out/stdio/5.out 2>/out/stdio/5.err
code=$?
set -e
echo "$code" >/out/stdio/5.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-worked --out /out/valid-6 >/out/stdio/6.out 2>/out/stdio/6.err
code=$?
set -e
echo "$code" >/out/stdio/6.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-worked --out /out/valid-7 >/out/stdio/7.out 2>/out/stdio/7.err
code=$?
set -e
echo "$code" >/out/stdio/7.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-worked --out /out/valid-8 >/out/stdio/8.out 2>/out/stdio/8.err
code=$?
set -e
echo "$code" >/out/stdio/8.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-official-edge-cases --out /out/valid-9 >/out/stdio/9.out 2>/out/stdio/9.err
code=$?
set -e
echo "$code" >/out/stdio/9.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-official-edge-cases --out /out/valid-10 >/out/stdio/10.out 2>/out/stdio/10.err
code=$?
set -e
echo "$code" >/out/stdio/10.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-official-edge-cases --out /out/valid-11 >/out/stdio/11.out 2>/out/stdio/11.err
code=$?
set -e
echo "$code" >/out/stdio/11.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.build/round376/dynamic-fixtures/empty --out /out/valid-12 >/out/stdio/12.out 2>/out/stdio/12.err
code=$?
set -e
echo "$code" >/out/stdio/12.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.build/round376/dynamic-fixtures/empty --out /out/valid-13 >/out/stdio/13.out 2>/out/stdio/13.err
code=$?
set -e
echo "$code" >/out/stdio/13.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.build/round376/dynamic-fixtures/empty --out /out/valid-14 >/out/stdio/14.out 2>/out/stdio/14.err
code=$?
set -e
echo "$code" >/out/stdio/14.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-count-error-wrap-65535 --out /out/valid-15 >/out/stdio/15.out 2>/out/stdio/15.err
code=$?
set -e
echo "$code" >/out/stdio/15.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-count-error-wrap-65535 --out /out/valid-16 >/out/stdio/16.out 2>/out/stdio/16.err
code=$?
set -e
echo "$code" >/out/stdio/16.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-count-error-wrap-65535 --out /out/valid-17 >/out/stdio/17.out 2>/out/stdio/17.err
code=$?
set -e
echo "$code" >/out/stdio/17.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-count-error-wrap-65536 --out /out/valid-18 >/out/stdio/18.out 2>/out/stdio/18.err
code=$?
set -e
echo "$code" >/out/stdio/18.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-count-error-wrap-65536 --out /out/valid-19 >/out/stdio/19.out 2>/out/stdio/19.err
code=$?
set -e
echo "$code" >/out/stdio/19.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-count-error-wrap-65536 --out /out/valid-20 >/out/stdio/20.out 2>/out/stdio/20.err
code=$?
set -e
echo "$code" >/out/stdio/20.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-count-error-wrap-140000 --out /out/valid-21 >/out/stdio/21.out 2>/out/stdio/21.err
code=$?
set -e
echo "$code" >/out/stdio/21.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-count-error-wrap-140000 --out /out/valid-22 >/out/stdio/22.out 2>/out/stdio/22.err
code=$?
set -e
echo "$code" >/out/stdio/22.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-count-error-wrap-140000 --out /out/valid-23 >/out/stdio/23.out 2>/out/stdio/23.err
code=$?
set -e
echo "$code" >/out/stdio/23.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-nearest-rank-101 --out /out/valid-24 >/out/stdio/24.out 2>/out/stdio/24.err
code=$?
set -e
echo "$code" >/out/stdio/24.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-nearest-rank-101 --out /out/valid-25 >/out/stdio/25.out 2>/out/stdio/25.err
code=$?
set -e
echo "$code" >/out/stdio/25.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-nearest-rank-101 --out /out/valid-26 >/out/stdio/26.out 2>/out/stdio/26.err
code=$?
set -e
echo "$code" >/out/stdio/26.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-many-endpoints-partitions --out /out/valid-27 >/out/stdio/27.out 2>/out/stdio/27.err
code=$?
set -e
echo "$code" >/out/stdio/27.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-many-endpoints-partitions --out /out/valid-28 >/out/stdio/28.out 2>/out/stdio/28.err
code=$?
set -e
echo "$code" >/out/stdio/28.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/cases/round342-tsan-sample-a-many-endpoints-partitions --out /out/valid-29 >/out/stdio/29.out 2>/out/stdio/29.err
code=$?
set -e
echo "$code" >/out/stdio/29.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/a/full-seed3557 --out /out/valid-30 >/out/stdio/30.out 2>/out/stdio/30.err
code=$?
set -e
echo "$code" >/out/stdio/30.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/a/full-seed3557 --out /out/valid-31 >/out/stdio/31.out 2>/out/stdio/31.err
code=$?
set -e
echo "$code" >/out/stdio/31.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/a/full-seed3557 --out /out/valid-32 >/out/stdio/32.out 2>/out/stdio/32.err
code=$?
set -e
echo "$code" >/out/stdio/32.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/cases/round342-tsan-a-latency-escape-partitions --out /out/valid-33 >/out/stdio/33.out 2>/out/stdio/33.err
code=$?
set -e
echo "$code" >/out/stdio/33.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/cases/round342-tsan-a-latency-escape-partitions --out /out/valid-34 >/out/stdio/34.out 2>/out/stdio/34.err
code=$?
set -e
echo "$code" >/out/stdio/34.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/cases/round342-tsan-a-latency-escape-partitions --out /out/valid-35 >/out/stdio/35.out 2>/out/stdio/35.err
code=$?
set -e
echo "$code" >/out/stdio/35.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/cases/round342-tsan-a-endpoint-id-4095 --out /out/valid-36 >/out/stdio/36.out 2>/out/stdio/36.err
code=$?
set -e
echo "$code" >/out/stdio/36.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/cases/round342-tsan-a-endpoint-id-4095 --out /out/valid-37 >/out/stdio/37.out 2>/out/stdio/37.err
code=$?
set -e
echo "$code" >/out/stdio/37.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/cases/round342-tsan-a-endpoint-id-4095 --out /out/valid-38 >/out/stdio/38.out 2>/out/stdio/38.err
code=$?
set -e
echo "$code" >/out/stdio/38.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/cases/round342-tsan-a-method-hours-ordered --out /out/valid-39 >/out/stdio/39.out 2>/out/stdio/39.err
code=$?
set -e
echo "$code" >/out/stdio/39.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/cases/round342-tsan-a-method-hours-ordered --out /out/valid-40 >/out/stdio/40.out 2>/out/stdio/40.err
code=$?
set -e
echo "$code" >/out/stdio/40.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/cases/round342-tsan-a-method-hours-ordered --out /out/valid-41 >/out/stdio/41.out 2>/out/stdio/41.err
code=$?
set -e
echo "$code" >/out/stdio/41.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/cases/round342-tsan-a-method-hours-shuffled --out /out/valid-42 >/out/stdio/42.out 2>/out/stdio/42.err
code=$?
set -e
echo "$code" >/out/stdio/42.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/cases/round342-tsan-a-method-hours-shuffled --out /out/valid-43 >/out/stdio/43.out 2>/out/stdio/43.err
code=$?
set -e
echo "$code" >/out/stdio/43.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/cases/round342-tsan-a-method-hours-shuffled --out /out/valid-44 >/out/stdio/44.out 2>/out/stdio/44.err
code=$?
set -e
echo "$code" >/out/stdio/44.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-first-hour-lag --out /out/valid-45 >/out/stdio/45.out 2>/out/stdio/45.err
code=$?
set -e
echo "$code" >/out/stdio/45.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=2 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-first-hour-lag --out /out/valid-46 >/out/stdio/46.out 2>/out/stdio/46.err
code=$?
set -e
echo "$code" >/out/stdio/46.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=3 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-first-hour-lag --out /out/valid-47 >/out/stdio/47.out 2>/out/stdio/47.err
code=$?
set -e
echo "$code" >/out/stdio/47.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=4 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-first-hour-lag --out /out/valid-48 >/out/stdio/48.out 2>/out/stdio/48.err
code=$?
set -e
echo "$code" >/out/stdio/48.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=5 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-first-hour-lag --out /out/valid-49 >/out/stdio/49.out 2>/out/stdio/49.err
code=$?
set -e
echo "$code" >/out/stdio/49.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-first-hour-lag --out /out/valid-50 >/out/stdio/50.out 2>/out/stdio/50.err
code=$?
set -e
echo "$code" >/out/stdio/50.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=7 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-first-hour-lag --out /out/valid-51 >/out/stdio/51.out 2>/out/stdio/51.err
code=$?
set -e
echo "$code" >/out/stdio/51.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=8 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-first-hour-lag --out /out/valid-52 >/out/stdio/52.out 2>/out/stdio/52.err
code=$?
set -e
echo "$code" >/out/stdio/52.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=9 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-first-hour-lag --out /out/valid-53 >/out/stdio/53.out 2>/out/stdio/53.err
code=$?
set -e
echo "$code" >/out/stdio/53.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=10 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-first-hour-lag --out /out/valid-54 >/out/stdio/54.out 2>/out/stdio/54.err
code=$?
set -e
echo "$code" >/out/stdio/54.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=11 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-first-hour-lag --out /out/valid-55 >/out/stdio/55.out 2>/out/stdio/55.err
code=$?
set -e
echo "$code" >/out/stdio/55.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-first-hour-lag --out /out/valid-56 >/out/stdio/56.out 2>/out/stdio/56.err
code=$?
set -e
echo "$code" >/out/stdio/56.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-empty-prefix-and-holes --out /out/valid-57 >/out/stdio/57.out 2>/out/stdio/57.err
code=$?
set -e
echo "$code" >/out/stdio/57.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=2 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-empty-prefix-and-holes --out /out/valid-58 >/out/stdio/58.out 2>/out/stdio/58.err
code=$?
set -e
echo "$code" >/out/stdio/58.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=3 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-empty-prefix-and-holes --out /out/valid-59 >/out/stdio/59.out 2>/out/stdio/59.err
code=$?
set -e
echo "$code" >/out/stdio/59.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=4 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-empty-prefix-and-holes --out /out/valid-60 >/out/stdio/60.out 2>/out/stdio/60.err
code=$?
set -e
echo "$code" >/out/stdio/60.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=5 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-empty-prefix-and-holes --out /out/valid-61 >/out/stdio/61.out 2>/out/stdio/61.err
code=$?
set -e
echo "$code" >/out/stdio/61.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-empty-prefix-and-holes --out /out/valid-62 >/out/stdio/62.out 2>/out/stdio/62.err
code=$?
set -e
echo "$code" >/out/stdio/62.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=7 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-empty-prefix-and-holes --out /out/valid-63 >/out/stdio/63.out 2>/out/stdio/63.err
code=$?
set -e
echo "$code" >/out/stdio/63.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=8 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-empty-prefix-and-holes --out /out/valid-64 >/out/stdio/64.out 2>/out/stdio/64.err
code=$?
set -e
echo "$code" >/out/stdio/64.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=9 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-empty-prefix-and-holes --out /out/valid-65 >/out/stdio/65.out 2>/out/stdio/65.err
code=$?
set -e
echo "$code" >/out/stdio/65.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=10 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-empty-prefix-and-holes --out /out/valid-66 >/out/stdio/66.out 2>/out/stdio/66.err
code=$?
set -e
echo "$code" >/out/stdio/66.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=11 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-empty-prefix-and-holes --out /out/valid-67 >/out/stdio/67.out 2>/out/stdio/67.err
code=$?
set -e
echo "$code" >/out/stdio/67.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-empty-prefix-and-holes --out /out/valid-68 >/out/stdio/68.out 2>/out/stdio/68.err
code=$?
set -e
echo "$code" >/out/stdio/68.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-unordered-publish --out /out/valid-69 >/out/stdio/69.out 2>/out/stdio/69.err
code=$?
set -e
echo "$code" >/out/stdio/69.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=2 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-unordered-publish --out /out/valid-70 >/out/stdio/70.out 2>/out/stdio/70.err
code=$?
set -e
echo "$code" >/out/stdio/70.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=3 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-unordered-publish --out /out/valid-71 >/out/stdio/71.out 2>/out/stdio/71.err
code=$?
set -e
echo "$code" >/out/stdio/71.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=4 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-unordered-publish --out /out/valid-72 >/out/stdio/72.out 2>/out/stdio/72.err
code=$?
set -e
echo "$code" >/out/stdio/72.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=5 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-unordered-publish --out /out/valid-73 >/out/stdio/73.out 2>/out/stdio/73.err
code=$?
set -e
echo "$code" >/out/stdio/73.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-unordered-publish --out /out/valid-74 >/out/stdio/74.out 2>/out/stdio/74.err
code=$?
set -e
echo "$code" >/out/stdio/74.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=7 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-unordered-publish --out /out/valid-75 >/out/stdio/75.out 2>/out/stdio/75.err
code=$?
set -e
echo "$code" >/out/stdio/75.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=8 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-unordered-publish --out /out/valid-76 >/out/stdio/76.out 2>/out/stdio/76.err
code=$?
set -e
echo "$code" >/out/stdio/76.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=9 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-unordered-publish --out /out/valid-77 >/out/stdio/77.out 2>/out/stdio/77.err
code=$?
set -e
echo "$code" >/out/stdio/77.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=10 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-unordered-publish --out /out/valid-78 >/out/stdio/78.out 2>/out/stdio/78.err
code=$?
set -e
echo "$code" >/out/stdio/78.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=11 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-unordered-publish --out /out/valid-79 >/out/stdio/79.out 2>/out/stdio/79.err
code=$?
set -e
echo "$code" >/out/stdio/79.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/cases/round342-tsan-ordered-a-unordered-publish --out /out/valid-80 >/out/stdio/80.out 2>/out/stdio/80.err
code=$?
set -e
echo "$code" >/out/stdio/80.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/a/public-full-seed1 --out /out/valid-81 >/out/stdio/81.out 2>/out/stdio/81.err
code=$?
set -e
echo "$code" >/out/stdio/81.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/a/public-full-seed1 --out /out/valid-82 >/out/stdio/82.out 2>/out/stdio/82.err
code=$?
set -e
echo "$code" >/out/stdio/82.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/a/public-full-seed1 --out /out/valid-83 >/out/stdio/83.out 2>/out/stdio/83.err
code=$?
set -e
echo "$code" >/out/stdio/83.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/a/full-seed1951 --out /out/valid-84 >/out/stdio/84.out 2>/out/stdio/84.err
code=$?
set -e
echo "$code" >/out/stdio/84.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/a/full-seed1951 --out /out/valid-85 >/out/stdio/85.out 2>/out/stdio/85.err
code=$?
set -e
echo "$code" >/out/stdio/85.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/a/full-seed1951 --out /out/valid-86 >/out/stdio/86.out 2>/out/stdio/86.err
code=$?
set -e
echo "$code" >/out/stdio/86.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/a/full-seed2221 --out /out/valid-87 >/out/stdio/87.out 2>/out/stdio/87.err
code=$?
set -e
echo "$code" >/out/stdio/87.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/a/full-seed2221 --out /out/valid-88 >/out/stdio/88.out 2>/out/stdio/88.err
code=$?
set -e
echo "$code" >/out/stdio/88.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/a/full-seed2221 --out /out/valid-89 >/out/stdio/89.out 2>/out/stdio/89.err
code=$?
set -e
echo "$code" >/out/stdio/89.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/a/full-seed3911 --out /out/valid-90 >/out/stdio/90.out 2>/out/stdio/90.err
code=$?
set -e
echo "$code" >/out/stdio/90.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/a/full-seed3911 --out /out/valid-91 >/out/stdio/91.out 2>/out/stdio/91.err
code=$?
set -e
echo "$code" >/out/stdio/91.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/a/full-seed3911 --out /out/valid-92 >/out/stdio/92.out 2>/out/stdio/92.err
code=$?
set -e
echo "$code" >/out/stdio/92.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.build/round376/dynamic-fixtures/shuffled-all-ids --out /out/valid-93 >/out/stdio/93.out 2>/out/stdio/93.err
code=$?
set -e
echo "$code" >/out/stdio/93.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=2 /app/solution --data /repo/.build/round376/dynamic-fixtures/shuffled-all-ids --out /out/valid-94 >/out/stdio/94.out 2>/out/stdio/94.err
code=$?
set -e
echo "$code" >/out/stdio/94.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=3 /app/solution --data /repo/.build/round376/dynamic-fixtures/shuffled-all-ids --out /out/valid-95 >/out/stdio/95.out 2>/out/stdio/95.err
code=$?
set -e
echo "$code" >/out/stdio/95.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=4 /app/solution --data /repo/.build/round376/dynamic-fixtures/shuffled-all-ids --out /out/valid-96 >/out/stdio/96.out 2>/out/stdio/96.err
code=$?
set -e
echo "$code" >/out/stdio/96.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=5 /app/solution --data /repo/.build/round376/dynamic-fixtures/shuffled-all-ids --out /out/valid-97 >/out/stdio/97.out 2>/out/stdio/97.err
code=$?
set -e
echo "$code" >/out/stdio/97.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.build/round376/dynamic-fixtures/shuffled-all-ids --out /out/valid-98 >/out/stdio/98.out 2>/out/stdio/98.err
code=$?
set -e
echo "$code" >/out/stdio/98.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=7 /app/solution --data /repo/.build/round376/dynamic-fixtures/shuffled-all-ids --out /out/valid-99 >/out/stdio/99.out 2>/out/stdio/99.err
code=$?
set -e
echo "$code" >/out/stdio/99.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=8 /app/solution --data /repo/.build/round376/dynamic-fixtures/shuffled-all-ids --out /out/valid-100 >/out/stdio/100.out 2>/out/stdio/100.err
code=$?
set -e
echo "$code" >/out/stdio/100.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=9 /app/solution --data /repo/.build/round376/dynamic-fixtures/shuffled-all-ids --out /out/valid-101 >/out/stdio/101.out 2>/out/stdio/101.err
code=$?
set -e
echo "$code" >/out/stdio/101.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=10 /app/solution --data /repo/.build/round376/dynamic-fixtures/shuffled-all-ids --out /out/valid-102 >/out/stdio/102.out 2>/out/stdio/102.err
code=$?
set -e
echo "$code" >/out/stdio/102.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=11 /app/solution --data /repo/.build/round376/dynamic-fixtures/shuffled-all-ids --out /out/valid-103 >/out/stdio/103.out 2>/out/stdio/103.err
code=$?
set -e
echo "$code" >/out/stdio/103.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.build/round376/dynamic-fixtures/shuffled-all-ids --out /out/valid-104 >/out/stdio/104.out 2>/out/stdio/104.err
code=$?
set -e
echo "$code" >/out/stdio/104.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=2 /app/solution --data /repo/.build/round376/dynamic-fixtures/empty --out /out/valid-105 >/out/stdio/105.out 2>/out/stdio/105.err
code=$?
set -e
echo "$code" >/out/stdio/105.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=3 /app/solution --data /repo/.build/round376/dynamic-fixtures/empty --out /out/valid-106 >/out/stdio/106.out 2>/out/stdio/106.err
code=$?
set -e
echo "$code" >/out/stdio/106.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=4 /app/solution --data /repo/.build/round376/dynamic-fixtures/empty --out /out/valid-107 >/out/stdio/107.out 2>/out/stdio/107.err
code=$?
set -e
echo "$code" >/out/stdio/107.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=5 /app/solution --data /repo/.build/round376/dynamic-fixtures/empty --out /out/valid-108 >/out/stdio/108.out 2>/out/stdio/108.err
code=$?
set -e
echo "$code" >/out/stdio/108.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=7 /app/solution --data /repo/.build/round376/dynamic-fixtures/empty --out /out/valid-109 >/out/stdio/109.out 2>/out/stdio/109.err
code=$?
set -e
echo "$code" >/out/stdio/109.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=8 /app/solution --data /repo/.build/round376/dynamic-fixtures/empty --out /out/valid-110 >/out/stdio/110.out 2>/out/stdio/110.err
code=$?
set -e
echo "$code" >/out/stdio/110.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=9 /app/solution --data /repo/.build/round376/dynamic-fixtures/empty --out /out/valid-111 >/out/stdio/111.out 2>/out/stdio/111.err
code=$?
set -e
echo "$code" >/out/stdio/111.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=10 /app/solution --data /repo/.build/round376/dynamic-fixtures/empty --out /out/valid-112 >/out/stdio/112.out 2>/out/stdio/112.err
code=$?
set -e
echo "$code" >/out/stdio/112.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=11 /app/solution --data /repo/.build/round376/dynamic-fixtures/empty --out /out/valid-113 >/out/stdio/113.out 2>/out/stdio/113.err
code=$?
set -e
echo "$code" >/out/stdio/113.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/a/sample-seed3563 --out /out/valid-114 >/out/stdio/114.out 2>/out/stdio/114.err
code=$?
set -e
echo "$code" >/out/stdio/114.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/a/sample-seed3563 --out /out/valid-115 >/out/stdio/115.out 2>/out/stdio/115.err
code=$?
set -e
echo "$code" >/out/stdio/115.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/a/sample-seed3563 --out /out/valid-116 >/out/stdio/116.out 2>/out/stdio/116.err
code=$?
set -e
echo "$code" >/out/stdio/116.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/a/sample-seed3923 --out /out/valid-117 >/out/stdio/117.out 2>/out/stdio/117.err
code=$?
set -e
echo "$code" >/out/stdio/117.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/a/sample-seed3923 --out /out/valid-118 >/out/stdio/118.out 2>/out/stdio/118.err
code=$?
set -e
echo "$code" >/out/stdio/118.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/a/sample-seed3923 --out /out/valid-119 >/out/stdio/119.out 2>/out/stdio/119.err
code=$?
set -e
echo "$code" >/out/stdio/119.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.data/a/sample-seed3929 --out /out/valid-120 >/out/stdio/120.out 2>/out/stdio/120.err
code=$?
set -e
echo "$code" >/out/stdio/120.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.data/a/sample-seed3929 --out /out/valid-121 >/out/stdio/121.out 2>/out/stdio/121.err
code=$?
set -e
echo "$code" >/out/stdio/121.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.data/a/sample-seed3929 --out /out/valid-122 >/out/stdio/122.out 2>/out/stdio/122.err
code=$?
set -e
echo "$code" >/out/stdio/122.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.build/round376/dynamic-fixtures/late-invalid-latency --out /out/error-0 >/out/stdio/error-0.out 2>/out/stdio/error-0.err
code=$?
set -e
echo "$code" >/out/stdio/error-0.code
test "$code" -eq 1
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.build/round376/dynamic-fixtures/late-invalid-latency --out /out/error-1 >/out/stdio/error-1.out 2>/out/stdio/error-1.err
code=$?
set -e
echo "$code" >/out/stdio/error-1.code
test "$code" -eq 1
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.build/round376/dynamic-fixtures/late-invalid-latency --out /out/error-2 >/out/stdio/error-2.out 2>/out/stdio/error-2.err
code=$?
set -e
echo "$code" >/out/stdio/error-2.code
test "$code" -eq 1
mkdir -p /out/error-3/summary.txt
set +e
SPEED_DEMON_THREADS=1 /app/solution --data /repo/.build/round376/dynamic-fixtures/empty --out /out/error-3 >/out/stdio/error-3.out 2>/out/stdio/error-3.err
code=$?
set -e
echo "$code" >/out/stdio/error-3.code
test "$code" -eq 1
mkdir -p /out/error-4/summary.txt
set +e
SPEED_DEMON_THREADS=6 /app/solution --data /repo/.build/round376/dynamic-fixtures/empty --out /out/error-4 >/out/stdio/error-4.out 2>/out/stdio/error-4.err
code=$?
set -e
echo "$code" >/out/stdio/error-4.code
test "$code" -eq 1
mkdir -p /out/error-5/summary.txt
set +e
SPEED_DEMON_THREADS=12 /app/solution --data /repo/.build/round376/dynamic-fixtures/empty --out /out/error-5 >/out/stdio/error-5.out 2>/out/stdio/error-5.err
code=$?
set -e
echo "$code" >/out/stdio/error-5.code
test "$code" -eq 1
