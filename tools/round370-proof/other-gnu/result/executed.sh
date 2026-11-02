set -eu
mkdir -p /out/stdio
export ASAN_OPTIONS=halt_on_error=1
export UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1
g++ --version >/out/gcc.txt
g++ -std=c++20 -O3 -g -march=native -Wall -Wextra -Wpedantic -Werror -pthread -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer /repo/.build/round370/source/track-c/main.cpp -o /out/solution
sha256sum /out/solution >/out/solution.sha256
g++ -std=c++20 -O3 -g -march=native -Wall -Wextra -Wpedantic -Werror -pthread -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer /repo/.build/round370/raw_fields_model.cpp -o /out/raw-fields
/out/raw-fields >/out/raw-fields.out 2>/out/raw-fields.err
g++ -std=c++20 -O3 -g -march=native -Wall -Wextra -Wpedantic -Werror -pthread -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer '-DCSV_MODEL_HEADER="/repo/.build/round370/csv_model.hpp"' /repo/tools/test_csv_numeric.cpp -o /out/numeric
/out/numeric >/out/numeric.out 2>/out/numeric.err
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/c/sample-seed3613 --out /out/valid-0 >/out/stdio/0.out 2>/out/stdio/0.err
code=$?
set -e
echo "$code" >/out/stdio/0.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/c/sample-seed3613 --out /out/valid-1 >/out/stdio/1.out 2>/out/stdio/1.err
code=$?
set -e
echo "$code" >/out/stdio/1.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/c/sample-seed3613 --out /out/valid-2 >/out/stdio/2.out 2>/out/stdio/2.err
code=$?
set -e
echo "$code" >/out/stdio/2.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-worked --out /out/valid-3 >/out/stdio/3.out 2>/out/stdio/3.err
code=$?
set -e
echo "$code" >/out/stdio/3.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-worked --out /out/valid-4 >/out/stdio/4.out 2>/out/stdio/4.err
code=$?
set -e
echo "$code" >/out/stdio/4.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-worked --out /out/valid-5 >/out/stdio/5.out 2>/out/stdio/5.err
code=$?
set -e
echo "$code" >/out/stdio/5.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-grammar-eof --out /out/valid-6 >/out/stdio/6.out 2>/out/stdio/6.err
code=$?
set -e
echo "$code" >/out/stdio/6.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-grammar-eof --out /out/valid-7 >/out/stdio/7.out 2>/out/stdio/7.err
code=$?
set -e
echo "$code" >/out/stdio/7.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-grammar-eof --out /out/valid-8 >/out/stdio/8.out 2>/out/stdio/8.err
code=$?
set -e
echo "$code" >/out/stdio/8.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-grammar-bom-eof --out /out/valid-9 >/out/stdio/9.out 2>/out/stdio/9.err
code=$?
set -e
echo "$code" >/out/stdio/9.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-grammar-bom-eof --out /out/valid-10 >/out/stdio/10.out 2>/out/stdio/10.err
code=$?
set -e
echo "$code" >/out/stdio/10.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-grammar-bom-eof --out /out/valid-11 >/out/stdio/11.out 2>/out/stdio/11.err
code=$?
set -e
echo "$code" >/out/stdio/11.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-grammar-lf --out /out/valid-12 >/out/stdio/12.out 2>/out/stdio/12.err
code=$?
set -e
echo "$code" >/out/stdio/12.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-grammar-lf --out /out/valid-13 >/out/stdio/13.out 2>/out/stdio/13.err
code=$?
set -e
echo "$code" >/out/stdio/13.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-grammar-lf --out /out/valid-14 >/out/stdio/14.out 2>/out/stdio/14.err
code=$?
set -e
echo "$code" >/out/stdio/14.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-grammar-crlf --out /out/valid-15 >/out/stdio/15.out 2>/out/stdio/15.err
code=$?
set -e
echo "$code" >/out/stdio/15.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-grammar-crlf --out /out/valid-16 >/out/stdio/16.out 2>/out/stdio/16.err
code=$?
set -e
echo "$code" >/out/stdio/16.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-grammar-crlf --out /out/valid-17 >/out/stdio/17.out 2>/out/stdio/17.err
code=$?
set -e
echo "$code" >/out/stdio/17.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-canonical-quote-forms --out /out/valid-18 >/out/stdio/18.out 2>/out/stdio/18.err
code=$?
set -e
echo "$code" >/out/stdio/18.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-canonical-quote-forms --out /out/valid-19 >/out/stdio/19.out 2>/out/stdio/19.err
code=$?
set -e
echo "$code" >/out/stdio/19.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-canonical-quote-forms --out /out/valid-20 >/out/stdio/20.out 2>/out/stdio/20.err
code=$?
set -e
echo "$code" >/out/stdio/20.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-parallel-resize-and-seams --out /out/valid-21 >/out/stdio/21.out 2>/out/stdio/21.err
code=$?
set -e
echo "$code" >/out/stdio/21.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-parallel-resize-and-seams --out /out/valid-22 >/out/stdio/22.out 2>/out/stdio/22.err
code=$?
set -e
echo "$code" >/out/stdio/22.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-parallel-resize-and-seams --out /out/valid-23 >/out/stdio/23.out 2>/out/stdio/23.err
code=$?
set -e
echo "$code" >/out/stdio/23.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-wide-country-membership --out /out/valid-24 >/out/stdio/24.out 2>/out/stdio/24.err
code=$?
set -e
echo "$code" >/out/stdio/24.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-wide-country-membership --out /out/valid-25 >/out/stdio/25.out 2>/out/stdio/25.err
code=$?
set -e
echo "$code" >/out/stdio/25.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round370-tsan-fresh-sample3853-c-wide-country-membership --out /out/valid-26 >/out/stdio/26.out 2>/out/stdio/26.err
code=$?
set -e
echo "$code" >/out/stdio/26.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-0 --out /out/valid-27 >/out/stdio/27.out 2>/out/stdio/27.err
code=$?
set -e
echo "$code" >/out/stdio/27.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-0 --out /out/valid-28 >/out/stdio/28.out 2>/out/stdio/28.err
code=$?
set -e
echo "$code" >/out/stdio/28.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-0 --out /out/valid-29 >/out/stdio/29.out 2>/out/stdio/29.err
code=$?
set -e
echo "$code" >/out/stdio/29.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-1 --out /out/valid-30 >/out/stdio/30.out 2>/out/stdio/30.err
code=$?
set -e
echo "$code" >/out/stdio/30.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-1 --out /out/valid-31 >/out/stdio/31.out 2>/out/stdio/31.err
code=$?
set -e
echo "$code" >/out/stdio/31.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-1 --out /out/valid-32 >/out/stdio/32.out 2>/out/stdio/32.err
code=$?
set -e
echo "$code" >/out/stdio/32.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-254 --out /out/valid-33 >/out/stdio/33.out 2>/out/stdio/33.err
code=$?
set -e
echo "$code" >/out/stdio/33.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-254 --out /out/valid-34 >/out/stdio/34.out 2>/out/stdio/34.err
code=$?
set -e
echo "$code" >/out/stdio/34.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-254 --out /out/valid-35 >/out/stdio/35.out 2>/out/stdio/35.err
code=$?
set -e
echo "$code" >/out/stdio/35.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-255 --out /out/valid-36 >/out/stdio/36.out 2>/out/stdio/36.err
code=$?
set -e
echo "$code" >/out/stdio/36.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-255 --out /out/valid-37 >/out/stdio/37.out 2>/out/stdio/37.err
code=$?
set -e
echo "$code" >/out/stdio/37.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-255 --out /out/valid-38 >/out/stdio/38.out 2>/out/stdio/38.err
code=$?
set -e
echo "$code" >/out/stdio/38.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-256 --out /out/valid-39 >/out/stdio/39.out 2>/out/stdio/39.err
code=$?
set -e
echo "$code" >/out/stdio/39.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-256 --out /out/valid-40 >/out/stdio/40.out 2>/out/stdio/40.err
code=$?
set -e
echo "$code" >/out/stdio/40.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-256 --out /out/valid-41 >/out/stdio/41.out 2>/out/stdio/41.err
code=$?
set -e
echo "$code" >/out/stdio/41.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-257 --out /out/valid-42 >/out/stdio/42.out 2>/out/stdio/42.err
code=$?
set -e
echo "$code" >/out/stdio/42.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-257 --out /out/valid-43 >/out/stdio/43.out 2>/out/stdio/43.err
code=$?
set -e
echo "$code" >/out/stdio/43.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-257 --out /out/valid-44 >/out/stdio/44.out 2>/out/stdio/44.err
code=$?
set -e
echo "$code" >/out/stdio/44.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-17576 --out /out/valid-45 >/out/stdio/45.out 2>/out/stdio/45.err
code=$?
set -e
echo "$code" >/out/stdio/45.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-17576 --out /out/valid-46 >/out/stdio/46.out 2>/out/stdio/46.err
code=$?
set -e
echo "$code" >/out/stdio/46.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-c-country-width-17576 --out /out/valid-47 >/out/stdio/47.out 2>/out/stdio/47.err
code=$?
set -e
echo "$code" >/out/stdio/47.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-0 --out /out/valid-48 >/out/stdio/48.out 2>/out/stdio/48.err
code=$?
set -e
echo "$code" >/out/stdio/48.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-0 --out /out/valid-49 >/out/stdio/49.out 2>/out/stdio/49.err
code=$?
set -e
echo "$code" >/out/stdio/49.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-0 --out /out/valid-50 >/out/stdio/50.out 2>/out/stdio/50.err
code=$?
set -e
echo "$code" >/out/stdio/50.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-pipeline-c-pipeline-batch-1 --out /out/valid-51 >/out/stdio/51.out 2>/out/stdio/51.err
code=$?
set -e
echo "$code" >/out/stdio/51.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-pipeline-c-pipeline-batch-1 --out /out/valid-52 >/out/stdio/52.out 2>/out/stdio/52.err
code=$?
set -e
echo "$code" >/out/stdio/52.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-pipeline-c-pipeline-batch-1 --out /out/valid-53 >/out/stdio/53.out 2>/out/stdio/53.err
code=$?
set -e
echo "$code" >/out/stdio/53.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-pipeline-c-pipeline-batch-511 --out /out/valid-54 >/out/stdio/54.out 2>/out/stdio/54.err
code=$?
set -e
echo "$code" >/out/stdio/54.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-pipeline-c-pipeline-batch-511 --out /out/valid-55 >/out/stdio/55.out 2>/out/stdio/55.err
code=$?
set -e
echo "$code" >/out/stdio/55.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-pipeline-c-pipeline-batch-511 --out /out/valid-56 >/out/stdio/56.out 2>/out/stdio/56.err
code=$?
set -e
echo "$code" >/out/stdio/56.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-pipeline-c-pipeline-batch-512 --out /out/valid-57 >/out/stdio/57.out 2>/out/stdio/57.err
code=$?
set -e
echo "$code" >/out/stdio/57.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-pipeline-c-pipeline-batch-512 --out /out/valid-58 >/out/stdio/58.out 2>/out/stdio/58.err
code=$?
set -e
echo "$code" >/out/stdio/58.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-pipeline-c-pipeline-batch-512 --out /out/valid-59 >/out/stdio/59.out 2>/out/stdio/59.err
code=$?
set -e
echo "$code" >/out/stdio/59.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-pipeline-c-pipeline-batch-513 --out /out/valid-60 >/out/stdio/60.out 2>/out/stdio/60.err
code=$?
set -e
echo "$code" >/out/stdio/60.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-pipeline-c-pipeline-batch-513 --out /out/valid-61 >/out/stdio/61.out 2>/out/stdio/61.err
code=$?
set -e
echo "$code" >/out/stdio/61.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-pipeline-c-pipeline-batch-513 --out /out/valid-62 >/out/stdio/62.out 2>/out/stdio/62.err
code=$?
set -e
echo "$code" >/out/stdio/62.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-pipeline-c-pipeline-batch-1025 --out /out/valid-63 >/out/stdio/63.out 2>/out/stdio/63.err
code=$?
set -e
echo "$code" >/out/stdio/63.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-pipeline-c-pipeline-batch-1025 --out /out/valid-64 >/out/stdio/64.out 2>/out/stdio/64.err
code=$?
set -e
echo "$code" >/out/stdio/64.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-pipeline-c-pipeline-batch-1025 --out /out/valid-65 >/out/stdio/65.out 2>/out/stdio/65.err
code=$?
set -e
echo "$code" >/out/stdio/65.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-pipeline-c-pipeline-batch-4097 --out /out/valid-66 >/out/stdio/66.out 2>/out/stdio/66.err
code=$?
set -e
echo "$code" >/out/stdio/66.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-pipeline-c-pipeline-batch-4097 --out /out/valid-67 >/out/stdio/67.out 2>/out/stdio/67.err
code=$?
set -e
echo "$code" >/out/stdio/67.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-pipeline-c-pipeline-batch-4097 --out /out/valid-68 >/out/stdio/68.out 2>/out/stdio/68.err
code=$?
set -e
echo "$code" >/out/stdio/68.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-1 --out /out/valid-69 >/out/stdio/69.out 2>/out/stdio/69.err
code=$?
set -e
echo "$code" >/out/stdio/69.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-1 --out /out/valid-70 >/out/stdio/70.out 2>/out/stdio/70.err
code=$?
set -e
echo "$code" >/out/stdio/70.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-1 --out /out/valid-71 >/out/stdio/71.out 2>/out/stdio/71.err
code=$?
set -e
echo "$code" >/out/stdio/71.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-63 --out /out/valid-72 >/out/stdio/72.out 2>/out/stdio/72.err
code=$?
set -e
echo "$code" >/out/stdio/72.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-63 --out /out/valid-73 >/out/stdio/73.out 2>/out/stdio/73.err
code=$?
set -e
echo "$code" >/out/stdio/73.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-63 --out /out/valid-74 >/out/stdio/74.out 2>/out/stdio/74.err
code=$?
set -e
echo "$code" >/out/stdio/74.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-64 --out /out/valid-75 >/out/stdio/75.out 2>/out/stdio/75.err
code=$?
set -e
echo "$code" >/out/stdio/75.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-64 --out /out/valid-76 >/out/stdio/76.out 2>/out/stdio/76.err
code=$?
set -e
echo "$code" >/out/stdio/76.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-64 --out /out/valid-77 >/out/stdio/77.out 2>/out/stdio/77.err
code=$?
set -e
echo "$code" >/out/stdio/77.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-65 --out /out/valid-78 >/out/stdio/78.out 2>/out/stdio/78.err
code=$?
set -e
echo "$code" >/out/stdio/78.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-65 --out /out/valid-79 >/out/stdio/79.out 2>/out/stdio/79.err
code=$?
set -e
echo "$code" >/out/stdio/79.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-65 --out /out/valid-80 >/out/stdio/80.out 2>/out/stdio/80.err
code=$?
set -e
echo "$code" >/out/stdio/80.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-127 --out /out/valid-81 >/out/stdio/81.out 2>/out/stdio/81.err
code=$?
set -e
echo "$code" >/out/stdio/81.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-127 --out /out/valid-82 >/out/stdio/82.out 2>/out/stdio/82.err
code=$?
set -e
echo "$code" >/out/stdio/82.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-127 --out /out/valid-83 >/out/stdio/83.out 2>/out/stdio/83.err
code=$?
set -e
echo "$code" >/out/stdio/83.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-128 --out /out/valid-84 >/out/stdio/84.out 2>/out/stdio/84.err
code=$?
set -e
echo "$code" >/out/stdio/84.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-128 --out /out/valid-85 >/out/stdio/85.out 2>/out/stdio/85.err
code=$?
set -e
echo "$code" >/out/stdio/85.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-128 --out /out/valid-86 >/out/stdio/86.out 2>/out/stdio/86.err
code=$?
set -e
echo "$code" >/out/stdio/86.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-129 --out /out/valid-87 >/out/stdio/87.out 2>/out/stdio/87.err
code=$?
set -e
echo "$code" >/out/stdio/87.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-129 --out /out/valid-88 >/out/stdio/88.out 2>/out/stdio/88.err
code=$?
set -e
echo "$code" >/out/stdio/88.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-129 --out /out/valid-89 >/out/stdio/89.out 2>/out/stdio/89.err
code=$?
set -e
echo "$code" >/out/stdio/89.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-255 --out /out/valid-90 >/out/stdio/90.out 2>/out/stdio/90.err
code=$?
set -e
echo "$code" >/out/stdio/90.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-255 --out /out/valid-91 >/out/stdio/91.out 2>/out/stdio/91.err
code=$?
set -e
echo "$code" >/out/stdio/91.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-255 --out /out/valid-92 >/out/stdio/92.out 2>/out/stdio/92.err
code=$?
set -e
echo "$code" >/out/stdio/92.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-256 --out /out/valid-93 >/out/stdio/93.out 2>/out/stdio/93.err
code=$?
set -e
echo "$code" >/out/stdio/93.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-256 --out /out/valid-94 >/out/stdio/94.out 2>/out/stdio/94.err
code=$?
set -e
echo "$code" >/out/stdio/94.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-256 --out /out/valid-95 >/out/stdio/95.out 2>/out/stdio/95.err
code=$?
set -e
echo "$code" >/out/stdio/95.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-257 --out /out/valid-96 >/out/stdio/96.out 2>/out/stdio/96.err
code=$?
set -e
echo "$code" >/out/stdio/96.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-257 --out /out/valid-97 >/out/stdio/97.out 2>/out/stdio/97.err
code=$?
set -e
echo "$code" >/out/stdio/97.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-257 --out /out/valid-98 >/out/stdio/98.out 2>/out/stdio/98.err
code=$?
set -e
echo "$code" >/out/stdio/98.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-511 --out /out/valid-99 >/out/stdio/99.out 2>/out/stdio/99.err
code=$?
set -e
echo "$code" >/out/stdio/99.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-511 --out /out/valid-100 >/out/stdio/100.out 2>/out/stdio/100.err
code=$?
set -e
echo "$code" >/out/stdio/100.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-511 --out /out/valid-101 >/out/stdio/101.out 2>/out/stdio/101.err
code=$?
set -e
echo "$code" >/out/stdio/101.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-512 --out /out/valid-102 >/out/stdio/102.out 2>/out/stdio/102.err
code=$?
set -e
echo "$code" >/out/stdio/102.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-512 --out /out/valid-103 >/out/stdio/103.out 2>/out/stdio/103.err
code=$?
set -e
echo "$code" >/out/stdio/103.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-512 --out /out/valid-104 >/out/stdio/104.out 2>/out/stdio/104.err
code=$?
set -e
echo "$code" >/out/stdio/104.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-513 --out /out/valid-105 >/out/stdio/105.out 2>/out/stdio/105.err
code=$?
set -e
echo "$code" >/out/stdio/105.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-513 --out /out/valid-106 >/out/stdio/106.out 2>/out/stdio/106.err
code=$?
set -e
echo "$code" >/out/stdio/106.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-513 --out /out/valid-107 >/out/stdio/107.out 2>/out/stdio/107.err
code=$?
set -e
echo "$code" >/out/stdio/107.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-1025 --out /out/valid-108 >/out/stdio/108.out 2>/out/stdio/108.err
code=$?
set -e
echo "$code" >/out/stdio/108.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-1025 --out /out/valid-109 >/out/stdio/109.out 2>/out/stdio/109.err
code=$?
set -e
echo "$code" >/out/stdio/109.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-1025 --out /out/valid-110 >/out/stdio/110.out 2>/out/stdio/110.err
code=$?
set -e
echo "$code" >/out/stdio/110.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-8193 --out /out/valid-111 >/out/stdio/111.out 2>/out/stdio/111.err
code=$?
set -e
echo "$code" >/out/stdio/111.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-8193 --out /out/valid-112 >/out/stdio/112.out 2>/out/stdio/112.err
code=$?
set -e
echo "$code" >/out/stdio/112.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-mixed-8193 --out /out/valid-113 >/out/stdio/113.out 2>/out/stdio/113.err
code=$?
set -e
echo "$code" >/out/stdio/113.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-skew-pressure --out /out/valid-114 >/out/stdio/114.out 2>/out/stdio/114.err
code=$?
set -e
echo "$code" >/out/stdio/114.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-skew-pressure --out /out/valid-115 >/out/stdio/115.out 2>/out/stdio/115.err
code=$?
set -e
echo "$code" >/out/stdio/115.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-skew-pressure --out /out/valid-116 >/out/stdio/116.out 2>/out/stdio/116.err
code=$?
set -e
echo "$code" >/out/stdio/116.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-diverse-pressure --out /out/valid-117 >/out/stdio/117.out 2>/out/stdio/117.err
code=$?
set -e
echo "$code" >/out/stdio/117.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-diverse-pressure --out /out/valid-118 >/out/stdio/118.out 2>/out/stdio/118.err
code=$?
set -e
echo "$code" >/out/stdio/118.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-diverse-pressure --out /out/valid-119 >/out/stdio/119.out 2>/out/stdio/119.err
code=$?
set -e
echo "$code" >/out/stdio/119.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-long-record --out /out/valid-120 >/out/stdio/120.out 2>/out/stdio/120.err
code=$?
set -e
echo "$code" >/out/stdio/120.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-long-record --out /out/valid-121 >/out/stdio/121.out 2>/out/stdio/121.err
code=$?
set -e
echo "$code" >/out/stdio/121.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-c-coop-long-record --out /out/valid-122 >/out/stdio/122.out 2>/out/stdio/122.err
code=$?
set -e
echo "$code" >/out/stdio/122.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-pressure-c-ring-pressure-4095 --out /out/valid-123 >/out/stdio/123.out 2>/out/stdio/123.err
code=$?
set -e
echo "$code" >/out/stdio/123.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-pressure-c-ring-pressure-4095 --out /out/valid-124 >/out/stdio/124.out 2>/out/stdio/124.err
code=$?
set -e
echo "$code" >/out/stdio/124.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-pressure-c-ring-pressure-4095 --out /out/valid-125 >/out/stdio/125.out 2>/out/stdio/125.err
code=$?
set -e
echo "$code" >/out/stdio/125.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-pressure-c-ring-pressure-4096 --out /out/valid-126 >/out/stdio/126.out 2>/out/stdio/126.err
code=$?
set -e
echo "$code" >/out/stdio/126.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-pressure-c-ring-pressure-4096 --out /out/valid-127 >/out/stdio/127.out 2>/out/stdio/127.err
code=$?
set -e
echo "$code" >/out/stdio/127.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-pressure-c-ring-pressure-4096 --out /out/valid-128 >/out/stdio/128.out 2>/out/stdio/128.err
code=$?
set -e
echo "$code" >/out/stdio/128.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-pressure-c-ring-pressure-4097 --out /out/valid-129 >/out/stdio/129.out 2>/out/stdio/129.err
code=$?
set -e
echo "$code" >/out/stdio/129.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-pressure-c-ring-pressure-4097 --out /out/valid-130 >/out/stdio/130.out 2>/out/stdio/130.err
code=$?
set -e
echo "$code" >/out/stdio/130.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-pressure-c-ring-pressure-4097 --out /out/valid-131 >/out/stdio/131.out 2>/out/stdio/131.err
code=$?
set -e
echo "$code" >/out/stdio/131.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-pressure-c-ring-pressure-262161 --out /out/valid-132 >/out/stdio/132.out 2>/out/stdio/132.err
code=$?
set -e
echo "$code" >/out/stdio/132.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-pressure-c-ring-pressure-262161 --out /out/valid-133 >/out/stdio/133.out 2>/out/stdio/133.err
code=$?
set -e
echo "$code" >/out/stdio/133.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-pressure-c-ring-pressure-262161 --out /out/valid-134 >/out/stdio/134.out 2>/out/stdio/134.err
code=$?
set -e
echo "$code" >/out/stdio/134.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/c/full-seed3623 --out /out/valid-135 >/out/stdio/135.out 2>/out/stdio/135.err
code=$?
set -e
echo "$code" >/out/stdio/135.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/c/full-seed3623 --out /out/valid-136 >/out/stdio/136.out 2>/out/stdio/136.err
code=$?
set -e
echo "$code" >/out/stdio/136.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/c/full-seed3623 --out /out/valid-137 >/out/stdio/137.out 2>/out/stdio/137.err
code=$?
set -e
echo "$code" >/out/stdio/137.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/c/public-full-seed1 --out /out/valid-138 >/out/stdio/138.out 2>/out/stdio/138.err
code=$?
set -e
echo "$code" >/out/stdio/138.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/c/public-full-seed1 --out /out/valid-139 >/out/stdio/139.out 2>/out/stdio/139.err
code=$?
set -e
echo "$code" >/out/stdio/139.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/c/public-full-seed1 --out /out/valid-140 >/out/stdio/140.out 2>/out/stdio/140.err
code=$?
set -e
echo "$code" >/out/stdio/140.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/c/full-seed2203 --out /out/valid-141 >/out/stdio/141.out 2>/out/stdio/141.err
code=$?
set -e
echo "$code" >/out/stdio/141.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/c/full-seed2203 --out /out/valid-142 >/out/stdio/142.out 2>/out/stdio/142.err
code=$?
set -e
echo "$code" >/out/stdio/142.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/c/full-seed2203 --out /out/valid-143 >/out/stdio/143.out 2>/out/stdio/143.err
code=$?
set -e
echo "$code" >/out/stdio/143.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/c/full-seed2309 --out /out/valid-144 >/out/stdio/144.out 2>/out/stdio/144.err
code=$?
set -e
echo "$code" >/out/stdio/144.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/c/full-seed2309 --out /out/valid-145 >/out/stdio/145.out 2>/out/stdio/145.err
code=$?
set -e
echo "$code" >/out/stdio/145.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/c/full-seed2309 --out /out/valid-146 >/out/stdio/146.out 2>/out/stdio/146.err
code=$?
set -e
echo "$code" >/out/stdio/146.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/c/full-seed2371 --out /out/valid-147 >/out/stdio/147.out 2>/out/stdio/147.err
code=$?
set -e
echo "$code" >/out/stdio/147.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/c/full-seed2371 --out /out/valid-148 >/out/stdio/148.out 2>/out/stdio/148.err
code=$?
set -e
echo "$code" >/out/stdio/148.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/c/full-seed2371 --out /out/valid-149 >/out/stdio/149.out 2>/out/stdio/149.err
code=$?
set -e
echo "$code" >/out/stdio/149.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/c/sample-seed3851 --out /out/valid-150 >/out/stdio/150.out 2>/out/stdio/150.err
code=$?
set -e
echo "$code" >/out/stdio/150.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/c/sample-seed3851 --out /out/valid-151 >/out/stdio/151.out 2>/out/stdio/151.err
code=$?
set -e
echo "$code" >/out/stdio/151.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/c/sample-seed3851 --out /out/valid-152 >/out/stdio/152.out 2>/out/stdio/152.err
code=$?
set -e
echo "$code" >/out/stdio/152.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/c/sample-seed3853 --out /out/valid-153 >/out/stdio/153.out 2>/out/stdio/153.err
code=$?
set -e
echo "$code" >/out/stdio/153.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/c/sample-seed3853 --out /out/valid-154 >/out/stdio/154.out 2>/out/stdio/154.err
code=$?
set -e
echo "$code" >/out/stdio/154.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/c/sample-seed3853 --out /out/valid-155 >/out/stdio/155.out 2>/out/stdio/155.err
code=$?
set -e
echo "$code" >/out/stdio/155.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/c/full-seed3863 --out /out/valid-156 >/out/stdio/156.out 2>/out/stdio/156.err
code=$?
set -e
echo "$code" >/out/stdio/156.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/c/full-seed3863 --out /out/valid-157 >/out/stdio/157.out 2>/out/stdio/157.err
code=$?
set -e
echo "$code" >/out/stdio/157.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/c/full-seed3863 --out /out/valid-158 >/out/stdio/158.out 2>/out/stdio/158.err
code=$?
set -e
echo "$code" >/out/stdio/158.code
test "$code" -eq 0
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-pipeline-bad-first-id --out /out/error-0 >/out/stdio/error-0.out 2>/out/stdio/error-0.err
code=$?
set -e
echo "$code" >/out/stdio/error-0.code
test "$code" -eq 1
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-pipeline-bad-first-id --out /out/error-1 >/out/stdio/error-1.out 2>/out/stdio/error-1.err
code=$?
set -e
echo "$code" >/out/stdio/error-1.code
test "$code" -eq 1
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-pipeline-bad-mid-money --out /out/error-2 >/out/stdio/error-2.out 2>/out/stdio/error-2.err
code=$?
set -e
echo "$code" >/out/stdio/error-2.code
test "$code" -eq 1
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-pipeline-bad-mid-money --out /out/error-3 >/out/stdio/error-3.out 2>/out/stdio/error-3.err
code=$?
set -e
echo "$code" >/out/stdio/error-3.code
test "$code" -eq 1
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-bad-first-id --out /out/error-4 >/out/stdio/error-4.out 2>/out/stdio/error-4.err
code=$?
set -e
echo "$code" >/out/stdio/error-4.code
test "$code" -eq 1
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-bad-first-id --out /out/error-5 >/out/stdio/error-5.out 2>/out/stdio/error-5.err
code=$?
set -e
echo "$code" >/out/stdio/error-5.code
test "$code" -eq 1
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-bad-first-id --out /out/error-6 >/out/stdio/error-6.out 2>/out/stdio/error-6.err
code=$?
set -e
echo "$code" >/out/stdio/error-6.code
test "$code" -eq 1
set +e
SPEED_DEMON_THREADS=1 /out/solution --data /repo/.data/cases/round356-asan-topology-bad-late-money --out /out/error-7 >/out/stdio/error-7.out 2>/out/stdio/error-7.err
code=$?
set -e
echo "$code" >/out/stdio/error-7.code
test "$code" -eq 1
set +e
SPEED_DEMON_THREADS=6 /out/solution --data /repo/.data/cases/round356-asan-topology-bad-late-money --out /out/error-8 >/out/stdio/error-8.out 2>/out/stdio/error-8.err
code=$?
set -e
echo "$code" >/out/stdio/error-8.code
test "$code" -eq 1
set +e
SPEED_DEMON_THREADS=12 /out/solution --data /repo/.data/cases/round356-asan-topology-bad-late-money --out /out/error-9 >/out/stdio/error-9.out 2>/out/stdio/error-9.err
code=$?
set -e
echo "$code" >/out/stdio/error-9.code
test "$code" -eq 1
