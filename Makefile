CXX = clang++
CXXFLAGS = -std=c++20 -O3 -DNDEBUG -Wall -Wextra -Wpedantic -pthread
TRACKS = a c d
BUILD_DIR ?= .build
TARGETS = $(addprefix $(BUILD_DIR)/track-,$(TRACKS))

all: $(TARGETS)

$(BUILD_DIR)/track-%: track-%/main.cpp track-%/io.hpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $< -o $@

$(BUILD_DIR)/track-a: track-a/decimal.hpp track-a/endpoint_table.hpp track-a/space_scan.hpp
$(BUILD_DIR)/track-d: track-d/decimal.hpp track-d/radix_heap.hpp track-d/distance_map.hpp track-d/parallel.hpp track-d/edge_store.hpp track-d/load_cursors.hpp
$(BUILD_DIR)/track-a: track-a/parallel.hpp
$(BUILD_DIR)/track-c: track-c/parallel.hpp track-c/names.hpp track-c/quote_scan.hpp

test: all
	python3 tools/verify.py --binary-dir $(BUILD_DIR) --scale tiny --seeds 1 7 31 --report docs/validation-tiny.json

sample: all
	python3 tools/verify.py --binary-dir $(BUILD_DIR) --scale sample --seeds 1 19 --report docs/validation-sample.json

sanitize:
	$(MAKE) BUILD_DIR=.build/sanitize CXXFLAGS='-std=c++20 -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -Wall -Wextra -pthread' all
	python3 tools/verify.py --binary-dir .build/sanitize --scale tiny --seeds 3 13 --report docs/validation-sanitizers.json

.PHONY: all test sample sanitize
