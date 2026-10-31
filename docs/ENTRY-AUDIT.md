# Entry audit — 31 October 2026

Observable checks passed in `ENTRY-AUDIT.json`; this is not an organizer-issued eligibility certificate. The live board lists Red Jones with A/C/D counted and an overall rank. The screenshot showing rows11–25 simply omits our row below it; B is blank because it is not entered. Cosmetic reactions/effects are not an entry requirement.

Verified: correct repository/required branch; GitHub-detected MIT license and original attribution; all observed commit author/committer timestamps after kickoff; per-track metadata and required files; pinned allowlisted Docker policy; no datasets or binaries in track build contexts; repository-only read access for the board app; successful real A/C/D gate records. Current official specs and Docker-policy files match the pinned revision after fetching the official repository on this date.

Reviewed runtime code computes all answers from the current input. There are no cached outputs, input hash recognition, imported pre-event private solution files, forbidden task-solving libraries, network calls, or attempts to manipulate the harness. The standard-library/OS implementation keeps D=1. Tests include independent generator seeds and adversarial cases, not just seed1. AI assistance is allowed and is disclosed honestly in the owner briefing.

Individual registration is entrant-confirmed; team registration is evidenced by the accepted, scored live entry. Neither is mislabeled as an independent organizer certification. Judges may request a written explanation; `OWNER-BRIEFING.md` provides a plain-language account without inventing an attestation of understanding.

Still required: preserve a final passing `speed-demon` commit at November2,2026,15:00 UTC /20:30 IST, and make that recorded source public under MIT by16:00 UTC /21:30 IST. The repository is correctly private now. No future publication or monitoring automation has been scheduled.

Sources: https://speeddemon.dev/#rules ; https://speeddemon.dev/#submission ; https://speeddemon.dev/board/ ; https://github.com/hackathon-raptors/speed-demon-2026 . Reproduce observable checks with `python3 tools/audit_entry.py`.

Profile-guided training is explicitly permitted in the official rules and harness. A and D retain measured PGO gains. The current candidate also retests C with an independent full-scale training seed; its retention is pending the actual board result. All current generator copies are byte-identical official sources. Only generated execution counts guide compilation; training inputs/outputs/profiles remain in builder stages. No precomputed answer recognition is introduced. Independent Linux cases at1/6/12 workers and the full public hashes pass after training. The audit tool admits this source-copy exception only when its bytes match the pinned official generator.
