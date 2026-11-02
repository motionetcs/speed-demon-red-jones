# D379: local replay ELF inspection

Read-only original local PGO ELF inspection: compact ordinary-cursor query function6060B, get309B/improve913B remain emitted as fallback symbols. BUT the query body has no direct get calls and only TWO improve calls at source/target initialization; all per-edge uses were already inlined. Reject forced-inline proposal before source/compile because the claimed hot call overhead is absent in this body. Also reject blanket unroll/peel suppression before source/compile: the assumed giant >32KB query body is unsupported. Neither static fact establishes dynamic frequencies/cache misses or target speed. No candidate380 attributes were created.

Reproduce offline with inspect.py and the immutable original image. No compiler/model/program/data/reference/training/benchmark or board run. No production runtime edit.
