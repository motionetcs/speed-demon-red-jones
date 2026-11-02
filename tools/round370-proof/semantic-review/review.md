# C370 static semantic review

Reviewed candidate main SHA256 `06e04e95334417cb5e969cb19e85381c70e6c3fde4d30241f9e6eec587899d04` against the original363 submitted main SHA256 `8f1703c20ec7e17bb708abff7d7a88945e0dcd8b83acc00b137607a7ceee1b0d`. The binding report records the exact preflight, source files, prior patches and frozen official specification. This is a read-only source review, with no compiler, model, raw-input, solution, timing, image, training, generator, oracle, board or selected-source action by this reviewer.

The actual diff removes the Field.escaped result, scratch/decode arguments and decoding branch, and unused scratch-string objects. It updates all six field() call sites and separates two pre-existing queue statements onto new lines. The raw segmented scanner, bounds tests, pointer transitions and decoded byte count remain unchanged. Names, numeric parsing, comma/newline/BOM handling, quote search, boundary selection, queue ownership, country widths, roles, defaults and PGO flags remain unchanged.

## Raw records and boundary scanning

The original record name/note calls and boundary-tail calls pass decode=false. At each field entry both versions start with the same p/end. For unquoted fields they run the identical delimiter loop and return the same input span and byte length. For a quoted field both set start=segment=++p, begin bytes at zero, locate the same next quote with the unchanged bounded find_quote, and add quote-segment to bytes. For a doubled quote both add one decoded byte and set segment=p=quote+2. For a closing quote both advance p=quote+1, return the complete raw interior [start,quote), and return the same accumulated decoded byte count. Missing closing quotes take the same throw paths. Induction over the quote events preserves p, segment and bytes. The old escaped boolean is never read by a production caller and does not influence the decode=false control path.

Names therefore receive exactly the same raw canonical keys and hash input, not a newly encoded representation. Key views still borrow the immutable input mapping through queue consumption and owner copies. Note and name byte totals still count UTF-8 bytes, each escaped quote once, and delimiters zero times. Boundary-tail consumers use only the resulting p; removing their unused scratch object cannot change the selected record ends.

## Header acceptance

The record header is the sole original decode=true caller. Every expected label (id, name, note, region_id, amount) contains no quote. With no doubled quote the old decoded view is the raw interior, so its comparison is identical. With at least one doubled quote, the old decoded value necessarily contains a literal quote; it cannot equal any expected label. The raw interior also contains quotes and cannot equal a label. Thus raw==expected iff decoded==expected for the actual comparisons. The candidate preserves previously accepted quoted header labels as well as the literal generated header. This argument does not assume that all accepted inputs have a literal unquoted header, and does not claim a general-purpose decoded-value API remains available.

Region header calls already use decode=false and are identical. Comma/newline checks and validation ordering are unchanged. Removing scratch allocations can alter behavior under allocation failure; this review claims successful parsing/output and header acceptance equivalence, not identical allocation counts or resource-exhaustion diagnostics.

## Edge-case checklist

| Case | Source-level result |
| --- | --- |
| Empty unquoted or quoted text | Same empty raw key and zero decoded bytes |
| Commas, CR/LF, BOM, NUL or UTF-8 bytes inside quotes | Same spans and byte counts; no normalization |
| Doubled quotes and long odd/even quote runs | Same pair/closing decisions and pointer transitions |
| Quote at the last accessible byte | Same quote+1<end bound before looking ahead |
| Opening quote or escape pair reaching EOF without closure | Same unterminated-field throw |
| Closed quoted field followed by an invalid delimiter | Same subsequent comma/newline failure |
| Final unquoted field at EOF | Same p=end and unchanged newline acceptance |
| Quoted expected header label with no escapes | Accepted by both |
| Header value containing a decoded quote | Cannot equal a quote-free expected label in either version |
| Literal quote inside an unquoted malformed field | Existing loop behavior unchanged; no expanded validation claim |

These are static checks, not executed test cases. Fresh actual-header raw/count/byte/guard/long/unterminated/header-comparison models and integration checks remain required if the candidate advances. Existing proofs for a different parser must not be relabeled as370 results.

## Duplicate distinction and performance limits

The exact237 patch templates Decode/CountOnly, retains scratch and escaped tracking, and specializes notes to return only their count;241 adds strict queue formatting to that approach. The300 patch adds a second payload-only raw scanner with raw-length-minus-escape-count arithmetic while retaining the original generic decoder. The349 patch returns a string_view with an optional count pointer but retains generic decoding/scratch. C370 instead removes globally unobserved decoding and the unused result flag from the single raw+count parser and preserves its original segmented counting loop. It is a distinct source simplification, not evidence of an unmeasured hot ABI cost. Prior emitted GNU default narrow-reader inspection already found no direct field call; no decoder/hidden-return/call-frequency speed claim is made here.

Smaller Field/source and fewer unused statements are hypotheses. Source-line counts are determined by the official harness, and neither code review nor native timings establish Intel time, charged memory or total K. Root alone owns screening, further proofs, integration and the official board decision. The passing original363 is preserved. Review complete; reviewer returns to HOLD.
