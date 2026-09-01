# SQLite Bug Taxonomy (v3.54.0)

Corpus: **277** forum threads -> **271** valid bugs (6 filtered invalid; 11 near-duplicate clusters covering 26 bugs).


## Bug classes (type axis)

| family | class | count |
|---|---|---:|
| correctness | `logic_wrong_result` | 75 |
| memory_safety | `buffer_overflow` | 73 |
| other | `unknown` | 25 |
| memory_safety | `null_deref` | 25 |
| memory_safety | `integer_overflow` | 16 |
| memory_safety | `stack_overflow` | 13 |
| memory_safety | `use_after_free` | 12 |
| corruption | `data_corruption` | 8 |
| assertion | `assertion_failure` | 7 |
| memory_safety | `uninitialized` | 5 |
| crash | `crash_generic` | 4 |
| undefined_behavior | `undefined_behavior` | 4 |
| resource | `memory_leak` | 3 |
| resource | `infinite_loop_hang` | 1 |

## Modules (location axis)

| layer | module | bugs |
|---|---|---:|
| extension | `ext_misc` | 64 |
| extension | `ext_fts5` | 27 |
| codegen | `codegen_core` | 21 |
| extension | `ext_fts3` | 19 |
| optimizer | `optimizer` | 19 |
| codegen | `codegen_dml` | 16 |
| types_functions | `json` | 12 |
| types_functions | `functions` | 10 |
| vdbe | `vdbe` | 8 |
| codegen | `expr` | 7 |
| extension | `ext_rtree` | 6 |
| extension | `ext_session` | 6 |
| tooling | `build` | 6 |
| codegen | `window` | 5 |
| os | `os_vfs` | 5 |
| tooling | `cli` | 4 |
| extension | `ext_rbu` | 4 |
| extension | `ext_icu` | 3 |
| extension | `ext_recover` | 3 |
| extension | `ext_expert` | 3 |
| extension | `ext_intck` | 3 |
| api | `main_api` | 3 |
| storage | `btree` | 3 |
| extension | `ext_qrf` | 2 |
| frontend | `parser` | 2 |
| storage | `pcache` | 2 |
| storage | `wal` | 2 |
| storage | `pager` | 2 |
| ? | `unattributed` | 1 |
| util | `util` | 1 |
| vtab | `vtab` | 1 |
| extension | `ext_wasm` | 1 |

## Module x bug-class matrix

| module \ class | `logic_wrong_result` | `buffer_overflow` | `unknown` | `null_deref` | `integer_overflow` | `stack_overflow` | `use_after_free` | `data_corruption` | `assertion_failure` | `uninitialized` | `crash_generic` | `undefined_behavior` | `memory_leak` | `infinite_loop_hang` | **tot** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ext_misc` | 11 | 24 | 1 | 13 | 3 | 6 | 3 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | **64** |
| `ext_fts5` | 4 | 11 | 1 | 0 | 5 | 1 | 1 | 0 | 2 | 1 | 0 | 1 | 0 | 0 | **27** |
| `codegen_core` | 5 | 2 | 4 | 1 | 0 | 1 | 1 | 4 | 0 | 1 | 0 | 1 | 1 | 0 | **21** |
| `ext_fts3` | 2 | 8 | 2 | 2 | 2 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **19** |
| `optimizer` | 14 | 1 | 3 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | **19** |
| `codegen_dml` | 9 | 0 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | **16** |
| `json` | 9 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **12** |
| `functions` | 3 | 1 | 2 | 0 | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | **10** |
| `vdbe` | 1 | 1 | 0 | 4 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | **8** |
| `expr` | 6 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **7** |
| `ext_rtree` | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | **6** |
| `ext_session` | 0 | 4 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **6** |
| `build` | 1 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | **6** |
| `window` | 4 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **5** |
| `os_vfs` | 0 | 3 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **5** |
| `cli` | 1 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **4** |
| `ext_rbu` | 0 | 2 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **4** |
| `ext_icu` | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | **3** |
| `ext_recover` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | **3** |
| `ext_expert` | 0 | 2 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **3** |
| `ext_intck` | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **3** |
| `main_api` | 0 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **3** |
| `btree` | 0 | 1 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **3** |
| `ext_qrf` | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **2** |
| `parser` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | **2** |
| `pcache` | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **2** |
| `wal` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | **2** |
| `pager` | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | **2** |
| `unattributed` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | **1** |
| `util` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **1** |
| `vtab` | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **1** |
| `ext_wasm` | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **1** |

## Per-cell bug lists


### ext_misc (64)

- **buffer_overflow** (24):
  - [Vuln7: Signed Integer Overflow and Heap Out-of-Bounds Read in fossildelta delta_parse INSERT iNext Computation](https://sqlite.org/bugs/info/73b028c98f09df994b1cfef396d949542a32bd03c11b43a6612ec99ac2cc62b4)
  - [Vuln10: Signed Integer Overflow in spellfix editDist3Core Wagner Matrix Sizing Causes Heap Buffer Overflow](https://sqlite.org/bugs/info/d96fdf752dc192f9a83d3e3c34a19d05422b7ee27e3a0be7f569e4038ad5b356)
  - [Vuln16: Unsigned Integer Overflow in spellfix editdist1 Wagner Matrix Allocation](https://sqlite.org/bugs/info/d4750a4af136e32aaf6d74cfe9f96179b118ff4e2629b5660d17330007a3fab3)
  - [zipfile heap info leak when rewriting ZIP with embedded NUL in filename](https://sqlite.org/bugs/info/7ecb781635bf4b3199dda0df505d8ed8e651adccb74e534c610d86a8a0a1de85)
  - [Vuln30-11: Integer Truncation in zipfile() Aggregate zipfileBufferGrow Causes Heap Buffer Overflow](https://sqlite.org/bugs/info/de2fc03adf55d8b353ad0337a4f7e6dfd5f7b7a26761aa609ff2dea8276412da)
  - [Vuln31-12: Integer Overflow in spellfix transliterate() Output Sizing Causes Heap Buffer Overflow](https://sqlite.org/bugs/info/2cd74c197f5808b3506adb60f9c0bbb17707ced6fc4dd4fda0226cc9bea094ce)
  - [Vuln38-19: decimal_round Loses the Carry-Out Digit and Returns Wrong Result on Carry-Past-MSD Inputs](https://sqlite.org/bugs/info/c29b7bb9408e8890af13e545e6ba560501a01f58cc63fe1469b31da07c5ea8f4)
  - [sqlite3 -zip malformed ZIP input triggers heap-buffer-overflow reads in zipfile virtual table](https://sqlite.org/bugs/info/f6f7ccaa6b8ad7249226bfc1838725379fae17ad7fa08d59d60c5d14a2eb47bf)
  - [Vuln40-21: qpvtab xBestIndex Reads azColname[-1] When Constraint Targets rowid](https://sqlite.org/bugs/info/321fe2a567ea31c23702b235cb15ffb174204581ca8a6ca5080fa6fbb3478c74)
  - [Vuln41-22: prefixes prefix_length Loop Uses max(nL,nR) Causing Heap Buffer Over-Read Past the Shorter String](https://sqlite.org/bugs/info/88b1c64b5b36ea6b46f4f64976aafc981419e9d8b1354f2090fde61b32805c74)
  - [Out-of-bounds read in deltaGetInt() when input contains no in-buffer terminator (ext/misc/fossildelta.c)](https://sqlite.org/bugs/info/4746029c060b57973fce4adbbcd6df37769c4fa90ab1b37ca9834fc98df831ae)
  - [Vuln61-42: CSV Virtual Table csvtabOpen 32-bit size_t Integer Overflow in nByte Allocation Causes Heap OOB](https://sqlite.org/bugs/info/652036e977cf4d7a53adc8149dd52718f756047afd4cf99aa9bb02c8da7bc226)
  - [Vuln73-54: Heap Buffer Overflow in ext/misc/decimal.c decimal_round via decimal_expand with Hardcoded nFrac=0](https://sqlite.org/bugs/info/10292ab9f2886076cf311d2f597a5c84840b117ff22f7e1c819c5c4a40ee14cf)
  - [Vuln75-56: Heap Out-of-Bounds Read in ext/misc/nextchar.c findNextChars via Non-Deterministic Field Expression](https://sqlite.org/bugs/info/b0f9c92083e826c74dea24c220ca16a471adc7614076a982d9e6776f06b5e469)
  - [Vuln77-58: Heap Out-of-Bounds Read in ext/misc/fuzzer.c fuzzerDequote Missing NUL Terminator](https://sqlite.org/bugs/info/d64214e87575962ec65cedb53f3c29f255e18269ab00c6c114ccba39ddcd7e82)
  - [Out-of-Bounds Read in qpvtab via Unmapped Rowid Sentinel in xBestIndex()](https://sqlite.org/bugs/info/3c36906ec39a3aff082a607626c7cb056af53d4c6a9abb91f7bdca5ec764abcb)
  - [Vuln79-60: Heap Out-of-Bounds Read in ext/misc/spellfix.c spellfix1FilterForMatch Missing nPattern>0 Guard](https://sqlite.org/bugs/info/1f0bc10cda5922b87fe07544893b0f3e526604efda5ab97bbab9385671045ca4)
  - [Vuln84-65: closure closureDequote Missing NUL Terminator Heap Over-read](https://sqlite.org/bugs/info/3d5cf0476250d43db2a75ef8ae60b420cf8be57687d6814fc4a2c0221f709d95)
  - [Vuln85-66: decimal decimalNewFromText Unbounded Whitespace-skip Over-read](https://sqlite.org/bugs/info/84d14f1eb0378c2c22ce7f8866f330aaca96c61f15603694ae794d1b6e553961)
  - [Vuln87-68: spellfix1Dequote Unbounded Heap Overflow on Unbalanced-quote Command Value](https://sqlite.org/bugs/info/e49a4b750f9269ca0d9b6c2520b2e5c5366ca9618a827178abba58325fe25a71)
  - [Vuln95-76: fossildelta delta_apply() Heap Over-read via Non-NUL-terminated Delta Blob](https://sqlite.org/bugs/info/265d87572858b07f63be7e68b05633788a3792f878a57ac0dea3060000b3a6e7)
  - [Vuln106-87: normalize sqlite3_normalize 1-byte Heap Underflow on Leading "in("](https://sqlite.org/bugs/info/922e44fa119068ace2c7fa45246a5ead4db81943d106d94c3debe4161147c60c)
  - [lifelineVuln5: apndWrite size-limit check ignores prefix offset, silently breaking the documented 1GiB total-file cap](https://sqlite.org/bugs/info/72b7e1821e32bc7c77761a08c8fd5d8452d32cd5707d55dc3556ef0641f6255b)
  - [`ext/misc/compress.c:uncompressFunc` size-header wrap into `sqlite3_malloc` then zlib write past the buffer](https://sqlite.org/bugs/info/fa268f7c08d758659fe6da5c065d220ff73bb27e8c5d5371229c68ec19470940)
- **null_deref** (13):
  - [Vuln9: NULL Pointer Dereference in prefixes prefix_length on SQL NULL Argument](https://sqlite.org/bugs/info/43bd5b0820506c787cf76e08d378e2acfc8f5c85cd9428b992984d6ac426ea2e)
  - [Vuln22-3: NULL Pointer Dereference in diskused .diskused on Autoindex Record With NULL tbl_name](https://sqlite.org/bugs/info/f4a4690d4b4f7a27c9e9ed8bfb5af4ee51e2c3b785fe2c157c0504dfeb62f55e)
  - [Vuln29-10: prefixes xBestIndex Returns a Degenerate Plan Instead of No-Solution, Causing a NULL VDBE Cursor Dereference](https://sqlite.org/bugs/info/b6c6fad96c4404d146fa9343223c70bcadb8fda79e85e6b31d2219c49fd54fa7)
  - [SQLite uuid_str()/uuid_blob() TEXT Conversion OOM NULL Dereference DoS](https://sqlite.org/bugs/info/c4985c9a864221601e3c6f637308bff1e00d44674041a5ed15fa5dbfc25251c8)
  - [Vuln55-36: fossildelta delta_create Missing OOM Check Causes NULL Dereference](https://sqlite.org/bugs/info/b9826317d874abe67b15288e44a46a76039f463e20d82efd169d40a7adf7e764)
  - [Vuln56-37: fileio realpath() Missing OOM Check on mprintf Result Causes strlen(NULL) Crash](https://sqlite.org/bugs/info/42bd07707a0bef18cecc6cd9369cb0af4b78589db5d2bc410236ad608ea82fe6)
  - [sha1_query Zeroblob NULL Pointer Dereference DoS](https://sqlite.org/bugs/info/bf2babfb6e34c55a30ccde9c6d238660be2a80d58ef99f9dc52d58fb083f1435)
  - [Vuln74-55: NULL Pointer Dereference in ext/misc/explain.c explainFilter Reads argv[0] with argc==0](https://sqlite.org/bugs/info/e518553ad4ff1a98475474e4f922003b32528e44877cabbf4d0cd548987589e9)
  - [Vuln76-57: NULL Pointer Dereference in ext/misc/unionvtab.c via NULL Table Name From Source Query](https://sqlite.org/bugs/info/d19e69584cafe909de393433fa11e2baeb599069e92d53f82f617e73a0692386)
  - [Vuln92-73: fuzzer Extension NULL Pointer Dereference on MATCH NULL](https://sqlite.org/bugs/info/0e0f6e429f5078f3a5cf168dc6aab4b9a3a10fedb99ffd906fb0b2d2038bcc09)
  - [ext/misc/normalize.c: __GCC__ typo leaves deliberate_fall_through inactive](https://sqlite.org/bugs/info/85431ae78eb352fb3dd80a525d011862818d6c65fbd12d80b3da50a3580a2e18)
  - [NULL pointer dereference on a SQL NULL vocabulary entry in amatchNext() (ext/misc/amatch.c)](https://sqlite.org/bugs/info/583996c178c36683fa67d27cf2137e57568745629e7c5d077c6eb0d0158663e5)
  - [Unchecked NULL from sqlite3_vmprintf() in sqlite3_fprintf() and sqlite3_vfprintf() (ext/misc/sqlite3_stdio.c)](https://sqlite.org/bugs/info/c6df944177e24ae5e5f91b229b5e19bfa0a9a0bbfe7f16462ad37e9bdbba1206)
- **logic_wrong_result** (11):
  - [Vuln63-44: generate_series() Drops WHERE value >= X / > X When X Is a Float Above INT64_MAX](https://sqlite.org/bugs/info/55ced616e2df8dac1f260fbf2445761b371a1dd580b000e02c2a65e2f6230574)
  - [Vuln86-67: diskused Side-effecting Function Mis-tagged SQLITE_INNOCUOUS](https://sqlite.org/bugs/info/b121e126d8bcbe28451396f649216c688e82f32d72e0c84f1f0acb92dd527b19)
  - [lifelineVuln6: Generic substitution rule cost bypasses documented 1..1000 range check](https://sqlite.org/bugs/info/2845187cf0a8958abac3e9a80091d3f6ca5f5c3f7ef4616eb68e4573ad044196)
  - [lifelineVuln9: multitype_text() silently truncates BLOB values containing embedded NUL bytes](https://sqlite.org/bugs/info/1b849c6e73ae00dbc73a2437ffab8121ba1de052b7097730bab2d3f9dcffc017)
  - [lifelineVuln10: sha1() and sha1b() silently return NULL for zero-length BLOB input instead of the empty-string hash](https://sqlite.org/bugs/info/74628508cd684b9828da7f84f9905ae997058451cc49924dd954bc34abd695b0)
  - [DBVuln15: approximate_match virtual table truncates 64-bit distance< bound via sqlite3_value_int()](https://sqlite.org/bugs/info/dd39eaec7b3371716a0e172c08853233a03725977454700e6aa101d2dd01e294)
  - [DBVuln17: Truncation of 64-bit depth bound to a 32-bit int in closureFilter() causes the transitive_closure virtual table](https://sqlite.org/bugs/info/091309387180508dde57b707f4297a101a8db980e138686cfa660c3e8712d7c4)
  - [DBVuln37: templatevtab returns only 9 of the documented 10 rows due to off-by-one in xEof](https://sqlite.org/bugs/info/b97c2a3c759489f4fe75b0bc7b0c7cdd448e5dda54e7e5ae7e1e165ec81fcff4)
  - [DBVuln38: vtablogColumn silently returns empty string for column index 25](https://sqlite.org/bugs/info/73979b583bc78a7d276f59d1f6e6bcf47a7fcf94f1082933d11cd2b18670d328)
  - [DBVuln39: ROLLBACK on a zipfile virtual table is silently implemented as COMMIT, permanently persisting data](https://sqlite.org/bugs/info/e60667ebdb3f77268fe237b33b2dfd673b846980f78b23916454a2c2250ff7b1)
  - [`qpvtab.c:qpvtabColumn` indexes `zData` with a negative `iRowid` after embedded-NUL `strlen` truncation](https://sqlite.org/bugs/info/ef517cd37a41cbcaa3b3af4aee06597e1f46c86742eb8523fddb0486bdb1906f)
- **stack_overflow** (6):
  - [Vuln39-20: percentSort Unbounded Recursion on Adversarial Median-of-Three Pivot Causes Stack Overflow](https://sqlite.org/bugs/info/63c8bf77deb0db2ec7931be64ab212f037c5805224f795fe2a294b2eec927774)
  - [lifelineVuln1: Repeated cksumvfs initialization makes the global VFS self-referential and causes infinite recursion](https://sqlite.org/bugs/info/0b0cf9578344c3f59fee46dc254d44c88973950865eae4f72f8e2394f2909243)
  - [lifelineVuln2: Repeated vfsstat initialization makes the default VFS wrapper self-referential](https://sqlite.org/bugs/info/b4aa946c4f8c66cc2cf621fce317743a5f9ed2a1881f1ac72b24ea6cb061e9a6)
  - [lifelineVuln3: Unbounded recursion in eval() causes C stack overflow and crash](https://sqlite.org/bugs/info/47b81cda8cecdca9f45e391b9fdabf440a125845c089306706a1c1fdcf75466a)
  - [lifelineVuln4: Uncontrolled recursion in sha3_query lets attacker-controlled SQL text crash the process via stack exhaustion](https://sqlite.org/bugs/info/640f91b13f18dc8cc4ba9827a4246f62b46a70965f50bf9592b4bf0b33dd31ed)
  - [DBVuln16: Self-referential tablename in transitive_closure causes unbounded recursion through closureFilter](https://sqlite.org/bugs/info/1da54815ad03b8fca9084ea37e060dc7396f60cb2c6235bf762ec7d6820c0c51)
- **integer_overflow** (3):
  - [Vuln19: Unbounded B-tree Traversal in btreeinfo binfoCompute Hangs on Cyclic Child Pointers](https://sqlite.org/bugs/info/a369443f7ecd6e811c7a695ed8676ecce6fc59a81aea887f13da061429579e26)
  - [wholenumberFilter() INT64 Bound Signed Overflow DoS](https://sqlite.org/bugs/info/bd5a87740024f31b4b57cd9e12ecd03df63873dd987daed093cdc5b3c1a8fbaf)
  - [Vuln88-69: Signed Integer Overflow in zipfile() Aggregate Size Computation](https://sqlite.org/bugs/info/eb86e10086b31680f0385078323e973069de61e7bb0c4d2bb65393873e1b91a8)
- **use_after_free** (3):
  - [Vuln42-13 zipfile Vtab zipfileResetCursor Leaves Dangling pFreeEntry After Free Causing Use-After-Free on Cursor Reuse](https://sqlite.org/bugs/info/6d1a1c58e943bfcf0766e1ce17be4a522a4db864b05fcf43acc0217fc9984e3c)
  - [Vuln91-72: amatch 16-bit Truncation of amatch_word.nMatch Causes Negative-index Heap Over-read](https://sqlite.org/bugs/info/d05ff1cc77ae0e34849b2a042a83e36379187f72bbac64477dead1c560c1dc85)
  - [Bug107-88: spellfix editDist3Install OOM-Triggered Use-After-Free](https://sqlite.org/bugs/info/c6ac702fff93cd0af18f4c9fe21d4464617960a2545b0b712f0fac56d99f9671)
- **assertion_failure** (1):
  - [Vuln8: Unsigned Integer Wraparound and Assertion Failure in fossildelta deltaparsevtabColumn Bounds Check](https://sqlite.org/bugs/info/66e69d8c58f362143342080bf401e6060f75186606588a239b16e569aa04d478)
- **uninitialized** (1):
  - [Vuln100-81: fileio fsdir() Uninitialized Stack Read / Info-leak on readlink() Failure](https://sqlite.org/bugs/info/4dee27083dbe2c03b433d865ee7e78e6e10f793f005b8d7c546085b6176baefc)
- **unknown** (1):
  - [DBVuln11: diskused() emits malformed "NaN.0%" percentage values when a subreport matches zero rows](https://sqlite.org/bugs/info/090e9990d61e139972c33632054e0342417bb3a56ea870f9e2ecc83acb02d502)
- **crash_generic** (1):
  - [`ext/misc/zipfile.c:zipfileUpdate` cursor advanced onto sibling freed by UPDATE OR REPLACE](https://sqlite.org/bugs/info/db922518e4a4e8afa0dca6e863251e3b7ca608d55ac867634c2797613bb7bab3)

### ext_fts5 (27)

- **buffer_overflow** (11):
  - [Vuln4: Assertion Failure in FTS5 fts5IndexExtractColset Buffer Append Caused by Unbounded Varint Continuation Loop](https://sqlite.org/bugs/info/c75be5e402ab4f0173d1a4696991728d11f230251b10c72f8e70c808e074574b)
  - [Vuln28-9: fts5 Index Iteration Logic Errors Yield Wrong Query Results on Corrupt Databases](https://sqlite.org/bugs/info/38e75aa4f9f0c9a1ebf4ce5188f5c0f7be7b699cd2e8d001c21e8ac42603fd21)
  - [Vuln34-15: FTS5 fts5PoslistFilterCallback Inner Varint Loop Missing Bounds Check Causes Heap Buffer Overflow](https://sqlite.org/bugs/info/e932a43ff2d3aafa1ea99d3f5c28a8a65694b5ed1437171c74505719235b9a2b)
  - [Vuln35-16: FTS5 fts5DoSecureDelete Heap Over-Read via Unvalidated first-rowid-offset on detail=none Continuation Page](https://sqlite.org/bugs/info/13f0df4e846ffd2d38fa338ca20e2b7f0094bf00b6d6621fa056aa33fad620de)
  - [Vuln49-30: FTS5 Reverse Iterator Heap Buffer Over-Read via Unvalidated szLeaf on Corrupt Segment Leaf](https://sqlite.org/bugs/info/4c4c1821a602acd4274ef1cb72ee7b64c59e89c117d4a9cf8774140715eb9cf7)
  - [Vuln50-31: FTS5 integrity-check Heap Buffer Over-Read in fts5IndexIntegrityCheckSegment](https://sqlite.org/bugs/info/be90cc59a5e398b016e18fadd5dd4bccb2de6182c5ee6dfa7ad26e4420ee9051)
  - [Vuln59-40: FTS5 fts5StructureDecode 32-bit Integer Overflow in nTotal Allocation Causes Heap OOB Write](https://sqlite.org/bugs/info/2ef8a3bce06c182ef99f04bf2bb853826883eb86b53af649f29ee96b42d62842)
  - [Vuln90-71: FTS5 Integrity-Check Signed Integer Overflow Bypasses Leaf-Term Bound Check](https://sqlite.org/bugs/info/c56223e904a76e8a4e338ce79726541160f276560187e5ac9f10b05e537eb4e4)
  - [Vuln94-75: FTS5 fts5SecureDeleteOverflow Heap Over-read via Unvalidated szLeaf](https://sqlite.org/bugs/info/d6382b0cf934d05a397fa29f17335d81898c323331e8693681b039dcadacc24f)
  - [Vuln105-86: FTS5 xPhraseFirstColumn Missing iPhrase Bound Check (detail=columns) Heap Over-read](https://sqlite.org/bugs/info/f747b60245eae927bbe69c0739fbd56e37644fa7090eceb2921b8bd8d6777dc1)
  - [PTP - FTS5 detail=none prefix merge underallocates the merged rowid doclist](https://sqlite.org/bugs/info/f08a04413a70909eda7e9cfb98dbb1fa1142ff8cc9d2420f38f5bb5fcf3a78ab)
- **integer_overflow** (5):
  - [Vuln47-28: FTS5 snippet() Signed Integer Overflow on Attacker-Controlled nToken Argument](https://sqlite.org/bugs/info/2127980d206974f642c02116899709ceb9de66cca44c4070a43c00a663f793a1)
  - [Vuln51-32: FTS5 in-Memory Hash Signed Integer Overflow on Doclist Doubling Reachable Under Raised SQLITE_MAX_LENGTH](https://sqlite.org/bugs/info/01688014ed1c9a5723d53b019ed8b400c1218f0c70c904c4013ecfa46197c608)
  - [Vuln53-34: FTS5 fts5IndexTombstoneRebuild Signed Integer Overflow on Corrupt Tombstone nElem Field](https://sqlite.org/bugs/info/b11de62beccae088f925e952191634bba1ad01627f497d82b7c6b8859c0d9dad)
  - [Denial of Service in FTS5 via Corrupted nPgTombstone Integer Overflow in Tombstone Rebuild](https://sqlite.org/bugs/info/a9a1088daa2108a34ffac305b6f9289ae854ec89c32441d03bd9cf6fdd15feaf)
  - [Signed integer overflow in fts5SegmentSize() (ext/fts5/fts5_index.c)](https://sqlite.org/bugs/info/ee608caf98b82525328b24e365470f93c5cec0f2b0cf8b8c47bbd8db417a5355)
- **logic_wrong_result** (4):
  - [Vuln58-39: FTS5 fts5ParseTokenize Sets nQueryTerm=0 for Colocated Synonym Tokens When tokendata=1](https://sqlite.org/bugs/info/be92b8833f6a0dece3b8f933892f67178488828bc79b9a2bbfaecda13e8b0976)
  - [Bug69-50: FTS5 Content Table Creation Fails with Duplicate Column Name When locale=1 and nCol >= 115](https://sqlite.org/bugs/info/365cd3399a1636b815ac1aa4558faba7075e5943e583baad76839c58c6a47455)
  - [Unexpected results when comparing fts5vocab.term with a numeric value](https://sqlite.org/bugs/info/9d60b0c997fff50865cb9c2e9050a7b3d29af0f8cb026374043c7ffab8984c61)
  - [Unexpected results when comparing fts5vocab.term with COLLATE NOCASE](https://sqlite.org/bugs/info/4c1c0d5f05a26516e73928ae764c978790c920298c08dc6bd5d095176aa2c00f)
- **assertion_failure** (2):
  - [`fts5DlidxIterInit` does not cap `nLvl`; `NextR` / `PrevR` recurse once per planted `%_data` height](https://sqlite.org/bugs/info/ec75490afaf90a47eba3ac6a6fbb13e967b82760906283cdbfd586a75b57edc1)
  - [bug(corruption): FTS5 detail='none' and 'secure-delete' loses index entries, rows unfindable by `match`, index corrupted](https://sqlite.org/bugs/info/97ed877f66f54ace56e10511b24a93bcea766943989f3f28316315c732208ce2)
- **stack_overflow** (1):
  - [Vuln5: Stack Overflow in FTS5 Porter Tokenizer via Unbounded Wrapper Chaining](https://sqlite.org/bugs/info/eb539c3654cd3165d5ab59f8cc3da46fa88474152f1587f68ac076602439c273)
- **use_after_free** (1):
  - [Vuln48-29: FTS5 NEAR Query Heap Use-After-Free via In-Place Poslist Rewrite Realloc](https://sqlite.org/bugs/info/16bb36f7e8eabe9dba6547d7549e92236df269cf1bb9e3b80f549929c60967c1)
- **unknown** (1):
  - [Vuln89-70: FTS5 fts5SegIterNextInit Unvalidated iTermOff Heap Over-read (tokendata=1)](https://sqlite.org/bugs/info/f6bae832a0a154069a0ab9a1f0bb07c2e5536d9919a4682eca1aa35b5ae9bbdb)
- **uninitialized** (1):
  - [FTS5 Uninitialized Memory Read in `fts5DataRead`](https://sqlite.org/bugs/info/925cfe21197a1475869a37e59fc9c03b21436963ad07dd2108351d84cefdd257)
- **undefined_behavior** (1):
  - [UBSan reports undefined behavior in FTS5 xSetAuxdataInt testcase](https://sqlite.org/bugs/info/2ffb3dcbddc6ec35bd9b9c05c59e440839bf0c31eb844a93454934d9cea6e55b)

### codegen_core (21)

- **logic_wrong_result** (5):
  - [Vuln14: PRAGMA defer_foreign_keys=OFF Zeroes Deferred FK Violation Counters Allowing COMMIT of Orphaned Rows](https://sqlite.org/bugs/info/c6bf0db6fa6947aecd9a8b8040925aea80f497e667aaae552ff4ded9abb2e8b8)
  - [ALTER TABLE ... ALTER ... DROP NOT NULL only removes one not null constraint](https://sqlite.org/bugs/info/bd653711d54514b88c1a0650fad02d5c2f5fdd543407a344bd839f11c4702b2f)
  - [Vuln62-43: ALTER TABLE DROP CONSTRAINT Silently Retains DEFAULT, COLLATE and GENERATED Clause Values in the Stored Schema](https://sqlite.org/bugs/info/f08a7826381825bbd9a5e2f9b920d3c177b7e076d96637dd29f0b6a82e5d3b8b)
  - [SQLite: duplicate GROUP BY expressions are not eliminated and force a temporary B-tree](https://sqlite.org/bugs/info/5987ad8bbf669f5fc08f5bb0acdfac4cd7862ae241e9161da36a8154df58e3dd)
  - [SQLite: empty INTERSECT and EXCEPT branches are not folded to an empty result](https://sqlite.org/bugs/info/3d413d0c501b487a9a63beff95238c42a146561a0681f0421d30245be8cac531)
- **data_corruption** (4):
  - [integrity_check fails to detect a specifc kind of index corruption](https://sqlite.org/bugs/info/0899f14d32145d09a8ae1fb1c052dc55443bf68984bf7c204ac7658eba42aee2)
  - [SQLite3 Non-deterministic Function Bypass in CREATE INDEX Expression Validation](https://sqlite.org/bugs/info/9486aa70efecba8d9c9b3911b357f6c177c585d282603fc608cb00389c2375e1)
  - [CREATE INDEX with LIKE accepted, then SQLITE_CORRUPT after `PRAGMA case_sensitive_like` change](https://sqlite.org/bugs/info/f1ec01dd25037e2d8c1600a038ac1639a8c9dd75ad85e7269eb3b769c2f646a8)
  - [Internal Function Execution Bypass via DEFAULT() Expression in Schema](https://sqlite.org/bugs/info/c2e60996021d622a7c6ba63860ea71994dd20d503498c4a592549f6a5718dadd)
- **unknown** (4):
  - [UPSERT RealAffinity Register Mapping Bug with Virtual Generated Columns](https://sqlite.org/bugs/info/b0469913bc1ddd75e57b48fbb1f54c899de7cf6186baeae1d8f23a2f4cca241a)
  - [PTP - Late vtab module registration leaves shadow tables writable](https://sqlite.org/bugs/info/49d0598fd0968fa851ee72edcdb8bc75dcecc16d03b7a3d5845b20b30ee8bb05)
  - [bug(constraints): ALTER TABLE ADD COLUMN REAL DEFAULT <large integer> desynchronises table and index](https://sqlite.org/bugs/info/26a45166b3c5c73b9c67f7559985c5141a4d563f776f5836bf9a0e45bd59082d)
  - [bug(constraints): `ALTER TABLE` silently changes meaning of SQL it doesn't rewrite, leaving a stale partial index](https://sqlite.org/bugs/info/9713e01799b2e37bb4733b7ddef06f93d904cfdf75ef4a6c015275e36bd446f2)
- **buffer_overflow** (2):
  - [Vuln67-48: STAT4 loadStatTbl 32-bit size_t Multiplication Overflow Causes Heap Buffer Overflow](https://sqlite.org/bugs/info/ffce0cecef6b87f12df81b7b37343f73171bb8adba3da0b28565d939a29090db)
  - [PTP - Odd UTF-16 prepare length reads past caller buffer](https://sqlite.org/bugs/info/c0995ef94d632e786bbe21c467f80832c8e6c3be2af1e33f25ead629ee906b41)
- **uninitialized** (1):
  - [Vuln17: Format String Vulnerability in analyze() Extension via Attacker-Controlled Table Names](https://sqlite.org/bugs/info/d9975c5b9930bfdb3729912b300904c61290eeab3fb895a44404f6ec6386c872)
- **stack_overflow** (1):
  - [Vuln66-47: View Linear-Chain Stack Overflow via `selectExpander` -> `viewGetColumnNames` Mutual Recursion](https://sqlite.org/bugs/info/3689e7f67eae58d9ac7d896ce19597f9dc61a697ac20d370937eb927af9d5c91)
- **use_after_free** (1):
  - [Heap Use-After-Free in sqlite3_backup_step() via Attached Database Realloc](https://sqlite.org/bugs/info/bde44146a585734004e28a490c66e5f826195986510586955358494f3ed99492)
- **null_deref** (1):
  - [Vuln80-61: Stale Backup Source Index (Type Confusion / NULL Pointer Dereference) in src/backup.c](https://sqlite.org/bugs/info/15d015ecd3a880b6f2864c8fe5e6c8bbeddb0f7fa537637d23cc3fc25d8e0a77)
- **memory_leak** (1):
  - [PTP - Generated expressions bypass SQLITE_FUNCTION authorizer denials](https://sqlite.org/bugs/info/27feb3f287d0701e472d8630b8c6911c37568d5d53daa91ac1d603af2f44114f)
- **undefined_behavior** (1):
  - [Inconsistent behaviour with PRAGMA writable_schema=1](https://sqlite.org/bugs/info/e45a318542d28524f20ca2bcad1ff58f0948544e8a1926bb9d1037174e2b1a26)

### ext_fts3 (19)

- **buffer_overflow** (8):
  - [Vuln1: Signed Integer Overflow and Out-of-Bounds Write in FTS3 fts3auxNextMethod Column Index](https://sqlite.org/bugs/info/0840561013e6c62419f554845bb1a002ba9e5bd8e906dd239ed2ec8e64aadf4c)
  - [Vuln3: Heap Out-of-Bounds Write in FTS3 matchinfo('b') Bitmap Index (Off-by-One)](https://sqlite.org/bugs/info/5336ffc6f9e2e4ce7f12c2e9111993ae8fd27ffd4273857502d4653a2316dbf1)
  - [Vuln37-18: fts3auxGrowStatArray size_t Overflow on 32-bit size_t Causes Heap Buffer Overflow via fts4aux Query](https://sqlite.org/bugs/info/7b1abd646e46bd4590071f98fc67d9bdbdd5a069fd2b973cd034a25d2a20a718)
  - [FTS3 `fts3EvalNearTrim()` can overflow the position-list buffer during an in-place NEAR merge](https://sqlite.org/bugs/info/54f8f2a75c10126c5e06119ab49525589875ab4f338896eb4a61222d0b4c2548)
  - [Vuln57-38: FTS3 matchinfo() Heap Buffer Overflow via 32-bit size_t Wraparound in fts3MatchinfoSize](https://sqlite.org/bugs/info/e0a5b419d4888b66c796ce1ce1e25f23efa933c715f529d2eb5e52cc8042d7bd)
  - [Bug70-51: FTS3 fts3IncrmergeLoad (int) Cast Truncates nLeafEst, Suppressing Leaf Flush During Incremental Merge](https://sqlite.org/bugs/info/f45915403cb85069f3ca387d9813aa2da4efc0bc6f891092d2d9eabee9fc8969)
  - [Vuln81-62: Heap Buffer Overflow in FTS3/FTS4 fts3EvalDeferredPhrase](https://sqlite.org/bugs/info/5c1ac854ee679682ba6117257084de536d2dc10137c93bd6df237946f247bf88)
  - [Vuln93-74: Signed Integer Overflow in FTS3/FTS4 fts3StringAppend Grow Test Bypasses Realloc](https://sqlite.org/bugs/info/9f00d3f8850fa75d501e0158091947512e119fd247221f86d372b4cab785cb3d)
- **integer_overflow** (2):
  - [Vuln2: Signed Integer Overflow in FTS3 NEAR Operator Distance Parsing](https://sqlite.org/bugs/info/79bb572d76ef2503c9d7d1b5f98badade4f62f8c8c4671c89b4d019036567f0c)
  - [FTS3 `fts3ReadEndBlockField()` negates INT64_MIN text and triggers signed integer overflow](https://sqlite.org/bugs/info/b2f8021f27973c225f9430ab069fec553e5341438b6af6374e2290ba94737f67)
- **stack_overflow** (2):
  - [Vuln33-14: Unbounded fts3SelectLeaf Recursion on Crafted FTS3 Segment Tree Triggers Stack Overflow](https://sqlite.org/bugs/info/69c0162d57f64645a7924e0b828283cad88c8fc2cb96db49a106d659e95a6500)
  - [DBVuln3: Stack exhaustion (unbounded recursion) in fts3 exprToString() and the fts3_exprtest() debug SQL function](https://sqlite.org/bugs/info/d225906ecca974408715c1bbea018f9b96dbd15ad9be43cf615c6394825eb895)
- **unknown** (2):
  - [lifelineVuln7: snippet() column-index argument not bounds-checked against actual column count](https://sqlite.org/bugs/info/4d5b2048644b864629880c9cef7762bd70ff131d9a3396aeff85ad0125b8b4cc)
  - [Database disk image is malformed when querying fts4aux](https://sqlite.org/bugs/info/2a3f211ecdd751229e004d061e333428bf33abdb1ab36087948cb64d348f2b3a)
- **logic_wrong_result** (2):
  - [lifelineVuln8: simple tokenizer silently ignores the sole delimiter argument (argv[0]) and falls back to default delimiters](https://sqlite.org/bugs/info/999a6b8ed3e9efa36fc287575428e0533340abc3799d8816d37377bbcf73fba0)
  - [Unexpected results when comparing fts4aux.term with a numeric value](https://sqlite.org/bugs/info/5c1922e4bbdf471169779762bec35e5e4b909c4479671528943d5fb0f1f1af43)
- **null_deref** (2):
  - [DBVuln2: NULL pointer dereference in fts3 expression parser (getNextNode) via NULL column-name argument to fts3_exprtest](https://sqlite.org/bugs/info/32ae924550017c26bb8e5227e85bc20700292cb7ee3054d055af3ec76dbb559c)
  - [Unchecked NULL from sqlite3_column_name() strlen'd in fts3ContentColumns() (ext/fts3/fts3.c)](https://sqlite.org/bugs/info/7b98fbc6c268bc47527e36ca0066e805354b2a12baaff6fe939cd81c52831d6c)
- **use_after_free** (1):
  - [UAF in FTS3/FTS4 snippet()](https://sqlite.org/bugs/info/0fc59b195cff5e3a1fe8552076425b4b7b9238a3a7e10cd48030d40b49bd4c54)

### optimizer (19)

- **logic_wrong_result** (14):
  - [Vuln13: Transitive Constraint Optimization Drops Valid Rows on Mixed Collation Equality](https://sqlite.org/bugs/info/1693eb8cfd53eb92d5c377808a2f93c7ff80c7570760e61e8adb4b83deae6e66)
  - [Contradictory WHERE conditions return identical result set in table-view cross join](https://sqlite.org/bugs/info/0f682b9d07f8f1af9d717e0c00a1be3b123f75765d2fcdd9e670c1ee938692a7)
  - [Invalid complementary filtering result for rtree virtual table left join query](https://sqlite.org/bugs/info/b31aed21645d5657b986fffda46545ab92ab710ce6dd4db8d4f85675e89367a8)
  - [Vuln46-27: WhereTerm.nChild u8 Wraparound Skips Verification of Vector IN Components Past Index Width](https://sqlite.org/bugs/info/76fab37f2b916f47660e96f066c233ccc790b4a9eab943aaf9926f602643c9ef)
  - [SELECT DISTINCT ORDER BY returns different row order depending on index usage](https://sqlite.org/bugs/info/9df89d3ccf82be9faba1878d94b7ffdc6b6a92ee947b4790b885f748d06aee34)
  - [Vuln68-49: OR-to-IN Conversion Loses Column Collation in src/whereexpr.c exprAnalyzeOrTerm](https://sqlite.org/bugs/info/0064c25b3f0dcb30d1b58b1d8011ab97085e8e6421482b92b372d17325f7de1e)
  - [SQLite: duplicate ORDER BY terms are not eliminated and force a temporary sort](https://sqlite.org/bugs/info/703ba0ce1994423abb19fe9f5cbc11a2feb4418d3a20d430acf01b1e3ed21c60)
  - [Unexpected result by RIGHT JOIN with a UNIQUE INDEX](https://sqlite.org/bugs/info/b924e9dbb8bc957d01e2aa4c36ed13a2e4d3fb3c9ef950355413c1a7cbfe226f)
  - [Unexpected results when filtering a RIGHT JOIN over a subquery reading a VIRTUAL generated column](https://sqlite.org/bugs/info/7f7431180a3b08d1d5583fd784738ce9a4ebf2dc872762c3f50a9757a513bc29)
  - [Unexpected results of row-value IN with a multi-column index after ANALYZE](https://sqlite.org/bugs/info/e7a615f18ed95648c0914ed09ca1d4a43579ebe51f5b32582ed1278344ac6281)
  - [Unexpected results when filtering a RIGHT JOIN by a row-value IN](https://sqlite.org/bugs/info/0a60e04dc0353e33c5f28ad654ace0d1c065762bad6d79cd695bfe5f61d88f12)
  - [bug(correctness): a DESC index makes IN / NOT IN ignore a NULL in the right hand set](https://sqlite.org/bugs/info/c2482038ced6a5156e7e54ef7c77f4ff9e6e5a08f0f59115aa62f625f40e061f)
  - [Unexpected results of a row-value IN over a PRIMARY KEY column](https://sqlite.org/bugs/info/b829afc27da7d0eec010a8865847766f2260a08dcf04f6bf2379123224723046)
  - [bug(correctness): nested RIGHT JOIN and WHERE give erroneous extra row in result](https://sqlite.org/bugs/info/e1d039e2cabbf83cbf3930d4919b44085d0b007b0baac804bb45004d576b433c)
- **unknown** (3):
  - [SQLite: adding OR FALSE disables an otherwise usable index search](https://sqlite.org/bugs/info/a364afa0095895926aa0fee08e89f7efa769a327eef9dd98b82e9c74afdc6601)
  - ["ON clause references tables to its right" is wrong in both directions for recursive CTEs](https://sqlite.org/bugs/info/27c5714bd0f7d41e3ead99165a9c4e2333e88dedc68e03c01b95334cef99fcb0)
  - [Right Join Subroutine Depth Assert](https://sqlite.org/bugs/info/0318b1699f3b9cb225b419443e148e838a7e25998ef382853b2aea3606d68d14)
- **buffer_overflow** (1):
  - [Vuln20-1: Heap Buffer Over-Read in scrub scrubBackupVarint on Interior B-tree Cell](https://sqlite.org/bugs/info/995b884793bf201f20fad73e41eacf6b3b61cb9fca6141b23a649370b55ab6ba)
- **data_corruption** (1):
  - [Vuln27-8: Transitive Optimization Discards Explicit COLLATE During pLeft Substitution, Dropping Valid Rows](https://sqlite.org/bugs/info/ffddcd361700df082690169e23bc3e8e6e3b6ecf011c660e32531f8d455a0f6b)

### codegen_dml (16)

- **logic_wrong_result** (9):
  - [NUMERIC cast extreme underflow becomes integer](https://sqlite.org/bugs/info/2d9a91ad81898e8c860cd0b5c904e88bc855c6829fa3c0b7e56c44b980b0e061)
  - [NULL key value causes json_group_object returns incorrect result with window function](https://sqlite.org/bugs/info/0de87b23b3459019e1333872fe43ccab502e69c3c8df10a77859bcb781d91cd6)
  - [Vuln12: xfer Optimization Bypasses Authorizer SQLITE_SELECT and SQLITE_READ Checks on Source Table](https://sqlite.org/bugs/info/8770b3c5f61227ae14c30830e04df609d8c08818fc798061485038bc65afd85d)
  - [Subquery returning a non-null value in WHERE clause incorrectly evaluates to FALSE and returns zero rows](https://sqlite.org/bugs/info/9d5f89c6971c32255e59485316e9a7801375920e87aea896290005dda9b84ecb)
  - [Scalar subquery in HAVING clause returns incorrect empty results](https://sqlite.org/bugs/info/8114efffcc4744daaffc3e7e730ea05418a2db13de41c2ab658af918a11e5e61)
  - [Aggregated scalar subquery in HAVING clause returns empty set for all contradictory conditions](https://sqlite.org/bugs/info/7ccfbc5db87e4ef415772f42234ad12aac5998fd8883939a47b2382c2299d2f4)
  - [SQLite: redundant ORDER BY inside EXISTS prevents a covering-index lookup](https://sqlite.org/bugs/info/d680c9e02f41a5fc8d0585b11dbb08a98f29e09e8dd0801141e322ba005d2655)
  - [Unexpected result by WHERE on a GROUP BY view with two IN](https://sqlite.org/bugs/info/ba3d0409d62caa0b902933f9423e29cf9275baf86d1c2ef6bf486213bf78278b)
  - [bug: ordered correlated scalar subquery mixing integer and text values gives wrong result](https://sqlite.org/bugs/info/ae5511151892f7fde12646c9d1115342e5e81029ba7a04dacdc60a2f0c8078e6)
- **null_deref** (1):
  - [GROUP BY + HAVING + IS NULL Returns Incorrect Result When Using NOT INDEXED](https://sqlite.org/bugs/info/fb66cf28f04dcd13232da2d7360b31937e54e832b3c40c77ca064058704da267)
- **stack_overflow** (1):
  - [Vuln65-46: Compile-Time Trigger Chain Stack Overflow in `codeRowTrigger`](https://sqlite.org/bugs/info/e8d7bbd97bfd913739d1903faa74254e785748f190ee7b8875c8ae5d16fe7f57)
- **uninitialized** (1):
  - [SQLite 3.53.2 - MSan(MemorySanitizer) use-of-uninitialized-value in sqlite3ProcessJoin (union misuse)](https://sqlite.org/bugs/info/04896d1a7db11aea252fc37fbf2b0801824e9556f1116cae9a831ea483318aba)
- **integer_overflow** (1):
  - [Possible signed integer overflow in sqlite3Update() with extreme number of indexes](https://sqlite.org/bugs/info/b7fda33439dca90b7c96f1907b4273cd8a5c4622651280c5f39b1bde271b3e1f)
- **unknown** (1):
  - [SQLite: redundant DISTINCT on a primary-key IN subquery disables the ROWID IN-operator optimization](https://sqlite.org/bugs/info/ff6a89a1d1e9f60f20c6c6ee517a538a30779f3598dc0feff339fd08ce2df28b)
- **undefined_behavior** (1):
  - [Geopoly accepts non-finite polygons and its RTree optimization misses rows](https://sqlite.org/bugs/info/b420bf201519a0dd062dadd5c6831a464fa1fe99ef6efab0f8c07890956a52a6)
- **crash_generic** (1):
  - [bug(correctness): UNIQUE index violation on recursive trigger update, debug build aborts from sqlite3VdbeExec's memIsValid()](https://sqlite.org/bugs/info/158cf0cdc569c5578153000a9da753bea4451863d8c56c4346b1389f67f09acc)

### json (12)

- **logic_wrong_result** (9):
  - [json_set() can construct invalid JSON from a quoted path containing an invalid escape](https://sqlite.org/bugs/info/dd9d1fbb74776734aed354a1c1f28a745d8ef416083c9730b0e8716528ed8c4b)
  - [Incorrect result of json_extract when the key contains NUL](https://sqlite.org/bugs/info/0a3523b2671202245ca3d6947e68d6f9de451d7945d22907516f11507ddcf00b)
  - [json_extract returns different subtype under index](https://sqlite.org/bugs/info/8de44412fd6dfef4f48e9cf1b3ba68cf2a17088b33075575ac50880ca08a0bc1)
  - [Incorrect result of max() on json_each](https://sqlite.org/bugs/info/8825c33ffe30c01a93ae70b7236995dd14688ba9f18970a5d9ca020b37f0540e)
  - [In json, abbreviated form works inconsistently from the full-path form when there is double quote in the key](https://sqlite.org/bugs/info/a5a024f2b614f3d098127e19a05ac351a02ed37149437fcb9ffb97815cf9d729)
  - [Vuln64-45: JSONB-to-Text Translator Discards Payload Size for NULL/TRUE/FALSE, Injecting Phantom Array Elements](https://sqlite.org/bugs/info/9040008d4c6728d2d631f6b91b0a18cbbfa51c4a6ed3301017aa244fbcdd8501)
  - [Unexpected Results from json_array() with an Indexed json_extract() Expression](https://sqlite.org/bugs/info/57ddd77b2a4e87fbc3246b7f43c8a43134386f3321bbc5e1aeb915a28e9eef6b)
  - [Unexpected result by JSON functions](https://sqlite.org/bugs/info/48d987dd6dc37ac7e37d504165eceb84e8bea373bf76800affcb74d9f0455768)
  - [Unexpected results of JSON functions with a partial index](https://sqlite.org/bugs/info/277dc6934d6a1d2ef095c69c77f7d07197e2fece333013549b52b532a48b48fd)
- **buffer_overflow** (3):
  - [Vuln96-77: json_each/json_tree Heap Over-read via JSONB Object with Dangling Trailing Label](https://sqlite.org/bugs/info/d792fc7bea75a97d88fa37b3e58b6092b9a6c05b1eef847e4bb3a9e607b26c90)
  - [Vuln97-78: json() Heap Over-read in jsonTranslateBlobToText FLOAT5 "-" Branch](https://sqlite.org/bugs/info/4e31bb96bb76a68019625d128479e8320e8b586c7e777c7c23d0a5e7cc6e6f8e)
  - [3.53.3: SIGBUS](https://sqlite.org/bugs/info/01650268045e2cebe7f500dec791a0dc2146bf57008248dedbcf005ce76d0d56)

### functions (10)

- **logic_wrong_result** (3):
  - [CHECK(changes()=0) constraint can be bypassed and insert rows that should have been rejected](https://sqlite.org/bugs/info/f39a2a2ae7ac368b57fdfa474559a38b93ed9ef94343ca613e9e1c0154ee552d)
  - [SQL function "format('')" returns NULL](https://sqlite.org/bugs/info/c9b4fadf767f00bf8633ab2d601c2d86ae45518c96b52bc72d5e2f84006e128d)
  - [PTP - %!J UTF-8 precision expansion narrows four-gigabyte input](https://sqlite.org/bugs/info/3f6960b1773953acf4f271c8f48c377bfd5392da431b55770eef941d623c3a23)
- **unknown** (2):
  - [SQLite: redundant IS NOT NULL after BETWEEN recomputes an expensive expression](https://sqlite.org/bugs/info/3646885a31e2777a3de67d6714879834121dcf2ac5cab69606e8baebe610c1b2)
  - [sqlite3_rsync: REPLICA_READY debug message passes an extra variadic argument](https://sqlite.org/bugs/info/87bf6e70e306ac636b98cfde2bd24e547cae5a962d3829e3f6c749ca17255b37)
- **buffer_overflow** (1):
  - [Vuln24-5: Unsigned Integer Overflow in printf %#Q and %#q Quote Sizing Causes Heap Buffer Overflow](https://sqlite.org/bugs/info/1f44ed92f8ea1ad278926ca42d82f66378f830035432cc941a62336be1225921)
- **integer_overflow** (1):
  - [Vuln52-33: replace() Bounds-Check Assert Signed Integer Overflow on Large Strings Under Raised SQLITE_MAX_LENGTH](https://sqlite.org/bugs/info/2e805964cda0b7ec0cf69ec08d37154bbfb6006af1d15798023af1dcc7461d9a)
- **data_corruption** (1):
  - [PTP - Malformed UTF-8 precision in %!s allows oversized memcpy](https://sqlite.org/bugs/info/e9f36fdb36a313c71babd64c94946c763e20a0718d1ae8c520fb4a322e3e56ef)
- **memory_leak** (1):
  - [PTP - Side-effect sqlite_log() is treated as innocuous](https://sqlite.org/bugs/info/3311f8d5b87444b6889ac7960e472b9d348203463d48dfda41980889480dcdff)
- **assertion_failure** (1):
  - [PTP - Negative sqlite3_str_append() length corrupts heap state](https://sqlite.org/bugs/info/86ae24f7a19271c3d1afbc734f5cd5bf847ddc357b4755fb929a947b3e76b5c4)

### vdbe (8)

- **null_deref** (4):
  - [SQLite `compress()` UDF unchecked allocation NULL write DoS](https://sqlite.org/bugs/info/eb30fc441806621d3f5b6605849f0cc1195cbfd0bcb6ddc250046c461b9859e0)
  - [`ext/misc/sha1.c:sha1QueryFunc` NULL-source `memcpy` after zeroblob expand failure](https://sqlite.org/bugs/info/51ebea6e89fc9ed0e4e694d7d4dffc837c28e67192e1afd17ee9647c5c7cc210)
  - [`ext/misc/vtablog.c:vtablogQuote` null dereference after `sqlite3_value_blob` fails to expand a zeroblob](https://sqlite.org/bugs/info/88b51562e624efdf88786179fe112db2604e40ee85881db49b5816067c996374)
  - [scanstatus2.test 5.x crashes the testfixture on every Windows build: `ptr:%p` key vs `format "ptr:0x%llx"` lookup](https://sqlite.org/bugs/info/97cd29ca44624113c73b30f5d2504729e6ffc5c5ebcba137078ea1a868cd97c9)
- **crash_generic** (1):
  - [Calling sqlite3_value_numeric_type() on a value returned by sqlite3_value_dup() can crash SQLite when the duplicated value is](https://sqlite.org/bugs/info/15c4a323bb19af87e6b57914c08cc6e1c4151e6c8d59b2877b0f185bfad994b0)
- **buffer_overflow** (1):
  - [Stack overflow in sqlite3_rsync driven by compromised origin server](https://sqlite.org/bugs/info/e2dfadf51209f12b06bcb4f3c16b9e2f89fd6cf782da65cc06403eba5f43ecae)
- **logic_wrong_result** (1):
  - [Bloom Filter on TEXT-Only Indexed Join Adds Work but Prunes Nothing](https://sqlite.org/bugs/info/220b11f0b048b10fa85a5bce878d1204f1706969f0d4864317d8a620f6b2d04a)
- **assertion_failure** (1):
  - [Specialized sorter comparator for REAL leading keys (~10% on speedtest1 fp)](https://sqlite.org/bugs/info/908805c8fd238fdb7e870cfefe9fdd8ddd86f7361484bada079be097feafa358)

### expr (7)

- **logic_wrong_result** (6):
  - [Vuln26-7: Vector IN Step-6 Collation Mismatch Returns FALSE Instead of NULL and Bypasses Blacklist Filters](https://sqlite.org/bugs/info/0785f45e67fb48d7020694d9bff7c3a00dfb995dd75670c4bf214690c2feb923)
  - [Vuln44-25: Vector IN Step-6 Ignores aiMap Permutation When the Engine Uses an Index With Reordered Columns](https://sqlite.org/bugs/info/ce1287198daec49d6e4bb42efdb081d9b77104c4a5c7dd1017227bb6a25734f9)
  - [sqlite3ExprAffinity() Fails to Traverse TK_UPLUS, Causing Wrong Query Results](https://sqlite.org/bugs/info/5c4882cd7005f4482e635073b6f3c8a440a16516d0b10b89a0a29b6525a8589f)
  - [Unexpected Results When Comparing Rowid with a Large Floating-Point Value](https://sqlite.org/bugs/info/d0b1e08683d6433086d6e1ae61eb63415fa4f2195cfe256fb1a7ab2822c53f2b)
  - [Unexpected result from row-value IN with min()](https://sqlite.org/bugs/info/659a04218982b66facd92691d9b21cdd78269991b080067eb273d7e8f5c9deb8)
  - [Inconsistent results for an OR of IN predicates in projection and WHERE](https://sqlite.org/bugs/info/abf92c35c17c3a048c5fab8c97112ceebb8f48cacc659d42d83df9b1d22fe14f)
- **use_after_free** (1):
  - [BUG: Reproducible SIGSEGV via readline in REPL](https://sqlite.org/bugs/info/1e750d1e04d318b1b457e693c4613859fa70c8f6f7e89502558548b8453071d4)

### ext_rtree (6)

- **buffer_overflow** (4):
  - [Vuln11: Assertion Failure in R-Tree rtreeStepToLeaf Caused by u8 iCell Overflow](https://sqlite.org/bugs/info/be56f2161c58e1dfd9f1370e18385e2e9fda49ce2ea6c9730db1037d4665675f)
  - [Vuln23-4: Missing RTREE_MAX_AUX_COLUMN Bound in geopoly geopolyInit Causes u8 nAux Wraparound](https://sqlite.org/bugs/info/dac1e43da9ee668c6a92cc04c917d6007e94681362be95a0703907a09445b543)
  - [SQLite RTree Off-by-One OOB Heap Write in anQueue](https://sqlite.org/bugs/info/618ba683eaac4ef1dc6a1d74f255e6d9b69f8225e6decf20c32e049dddbc5699)
  - [Off-by-one OOB heap write in R-tree extension (anQueue array)](https://sqlite.org/bugs/info/e81a18c0cbcef492a9c8455ebe4fa1dd6c032cc691b250215394338cc43058d7)
- **assertion_failure** (1):
  - [Vuln43-24: R-Tree nodeRowidIndex Assertion Failure on Oversized Leaf Node via xConnect Accepting Unbounded Node Size](https://sqlite.org/bugs/info/b86ce5c20fa33f6000c1e4f5c8c06b3fe73195b6f1fde306cdbda66e5b2880b7)
- **logic_wrong_result** (1):
  - [Potential unexpected result for an rtree rowid comparison with numeric text](https://sqlite.org/bugs/info/20d3bd0016dc43a85c6a8e75551b421ba942be0aeeec8635382b8e3d52c4bded)

### ext_session (6)

- **buffer_overflow** (4):
  - [Heap Buffer Overflow in sqlite3changegroup_change_blob via Negative Length Parameter](https://sqlite.org/bugs/info/a100d593016354e3148b44cbe7459f3d66f7d0238cf5b6b38a0462b10245b860)
  - [SQLite Session Rebaser Integer Overflow → Heap Buffer Overflow](https://sqlite.org/bugs/info/11d69317e1a55b4e9d79d699e0611ae59de934da66a9bb5a96ce0c7c4610b317)
  - [Vuln101-82: session sessionAppendPartialUpdate Heap Over-read on Rebase Column-count Mismatch](https://sqlite.org/bugs/info/70e16d367d3d0731a4a2e9f633166979c66e0f78681608b2afaf2d33ad97ab2c)
  - [heap OOB write in sqlite3changeset_apply()](https://sqlite.org/bugs/info/6a06b0a1781eeef0e4daffa4dd09d10e31ac9fdf75dd5f433c57daa77aa2ae04)
- **unknown** (1):
  - [sqlite3changeset_apply_v3(FKNOACTION) makes later sqlite3session_diff() return SQLITE_SCHEMA](https://sqlite.org/bugs/info/269f1e9cef6f9f4f794db4b8ff194bb7015d4465e5d38f542386e43318257c69)
- **null_deref** (1):
  - [Unchecked sqlite3_mprintf() NULL fed to libc printf("%s") for zSQLTabName in main() (ext/session/changeset.c)](https://sqlite.org/bugs/info/0833f0f4ecbd3ca45f02a31f318ed1885e0be796d1bca40ffcb76b4311f28562)

### build (6)

- **unknown** (4):
  - [shell.c: function sayAbnormalExit() needs SQLITE_CDECL](https://sqlite.org/bugs/info/4b09d7af14f82f30ea3f93c6f3f2c1c26774fcb498f10d96f76fa25d5bde5c16)
  - [FIX: testsuite fails to run on BSDs](https://sqlite.org/bugs/info/470173c49ac900313311921ec76e1bfb62e5a489a7661df9c70faa0d350126c0)
  - [FIX: Name collision in variables for building Tcl extension](https://sqlite.org/bugs/info/ac648080780a6dd8cceeeb9ab120c643d793b1c3fe65a934b781a6293efc6725)
  - [FIX: Autosetup find_tclconfig.tcl can't find tclConfig.sh](https://sqlite.org/bugs/info/778223d22549a1a160ed26fbbc8611974d36b7d6c739b65bf0adca1937de7ec8)
- **logic_wrong_result** (1):
  - [SQLITE_OMIT_FLOATING_POINT causes compilation error](https://sqlite.org/bugs/info/8c3df4da0de9f607df91808d936585d7a3a28f86f6f4c42bc7ff484130bf0659)
- **crash_generic** (1):
  - [sqlite3 -Ac command crashes on Windows](https://sqlite.org/bugs/info/5ee5440e1cefc431c7f73bd4d0eaea59b900922290ccbaaa09828ef444d3257b)

### window (5)

- **logic_wrong_result** (4):
  - [Incorrect result of windows function](https://sqlite.org/bugs/info/1a531c5a8137a3107be121ebe019452bb8c1474fb409b0aa94cb0f23f2567624)
  - [format('%!.0J') treats zero precision as unlimited](https://sqlite.org/bugs/info/277c67d8eb158686e12e4a806c5ca97b9599cd6a28d22df6535b293cd90ab573)
  - [Incorrect result of window function, maybe related to OR-to-IN collection](https://sqlite.org/bugs/info/329521b269fdcc95ed39daeda0dae7656386e3a6b80ba80840c86082eee3d231)
  - [Index makes window function return incorrect result](https://sqlite.org/bugs/info/ba8084256bef003639b3f37d23c03aa7e66681f3237b4ff7746b8db965a6ac4f)
- **integer_overflow** (1):
  - [sum() function has different return type as window function and aggregate function](https://sqlite.org/bugs/info/3625548dac7e0d80c06d7fb71cccd232de344c85bb5b30fdfb40a7867ccc29fc)

### os_vfs (5)

- **buffer_overflow** (3):
  - [Heap buffer overflow (write) in kvvfsDecode() in os_kv.c](https://sqlite.org/bugs/info/89c1bd74a8483b609a09e76088926feb7b8d1f48902a30704e5f7276126ca56a)
  - [Bug72-53: Integer Overflow in src/os_kv.c kvvfsDecode Zero-Run Counter Bypasses Bounds Check for Heap Buffer Overflow](https://sqlite.org/bugs/info/76acc88b573e3a1699db65e997110ae2c4b29dd7d20c1be54e31795c89844dee)
  - [Vuln78-59: Heap Out-of-Bounds Read in src/os_kv.c kvvfsDecodeJournal Base-26 Length Parser Missing Separator Guard](https://sqlite.org/bugs/info/f4d88886e68ebf197b5de6c2bbada849105770609028f51a614f165d9e6699ff)
- **integer_overflow** (1):
  - [Vuln15: Signed Integer Overflow in unixShmMap nByte Computation](https://sqlite.org/bugs/info/eae13dd041c2edc699271d416f8ae63885f4dadc8158652f4a17574da2c620ad)
- **use_after_free** (1):
  - [Bug71-52: kvvfsDecodeJournal Off-by-One in Base-26 Size Decode Causes Permanent Data Loss on Crash Recovery](https://sqlite.org/bugs/info/20e208fe172cae4fbc875acf5cb221ddbedce198143a1a453a34de7ac53cafb1)

### cli (4)

- **unknown** (3):
  - [CLI `.prompt show` emits error but continues when .bail set to on](https://sqlite.org/bugs/info/99cd9319f893d7836df7e5eb92cba8b37d2fe60790e52fd6db6102f00a2490a4)
  - [CSV output on Windows uses "\r\r\n" as a row separator](https://sqlite.org/bugs/info/17f29446b37d1ce7e7ad42a1a1530abf0aa69e26b828f58365c8c82484c4a166)
  - [Recent version (3.53.4) sqlite3 seems to always shorten column names in .mode column](https://sqlite.org/bugs/info/003c4765c60d64d22dbbbb529ce31e4d096086876ae2ccbbac769a92c6911a9f)
- **logic_wrong_result** (1):
  - [Backward incompatible output: Order of command-line options "-header" and "-csv" changes output](https://sqlite.org/bugs/info/8f7e8082bd7bcdc6508871269cb6317ddbf48b5a0ec270374984a3a3bd936cf5)

### ext_rbu (4)

- **buffer_overflow** (2):
  - [Vuln103-84: RBU rbuGetUpdateStmt Heap Over-read via Short rbu_control Mask](https://sqlite.org/bugs/info/32f9250e8cfab724d36ef953e5e59ee7a7db9281d2626cd2a7003b96af570c16)
  - [Vuln104-85: RBU Negative rbu_state ROW Value Yields aFrame[-1] Out-of-bounds Read](https://sqlite.org/bugs/info/0953edb916df6db039dda619feb941f4528fccc8640894b9a7d4158731502ff9)
- **integer_overflow** (1):
  - [Vuln54-35: RBU rbu_fossil_delta Signed Integer Overflow on Crafted Delta Output Size](https://sqlite.org/bugs/info/3888ce4cd731a7bd71f6b14a863822accc56058b06b2eabf835b2d70de08586d)
- **unknown** (1):
  - [Vuln102-83: RBU rbuDeltaApply Wrong Operator Breaks Copy Deltas and Reads 1 Byte Past the Delta Blob](https://sqlite.org/bugs/info/8123aba97f0e6e845cda5f31077170d439860f59eb830f0df6c322b18509ab46)

### ext_icu (3)

- **use_after_free** (1):
  - [Vuln6: Integer Overflow and Double Free in ICU Extension icuCaseFunc16](https://sqlite.org/bugs/info/2477f5e8f0c16546851af24cadb5acab5a00472948c5c1119d6c2e645c7192b4)
- **memory_leak** (1):
  - [Vuln18: ICU Extension icu_load_collation Direct-Leaks UCollator on Invalid Strength Argument](https://sqlite.org/bugs/info/ba155572cff312c796d5a3cb2a60f623fe35a19ba5e5453483f7418694afbd65)
- **logic_wrong_result** (1):
  - [Vuln36-17: ICU LIKE Overlong UTF-8 Sequences Decode to Real Wildcards Bypassing Byte-Level Pattern Sanitization](https://sqlite.org/bugs/info/da89d9a3dc06eb2f4882334e4c8478ac6528eb89cc7e65a796579c22e1f822a3)

### ext_recover (3)

- **infinite_loop_hang** (1):
  - [Vuln21-2: Infinite Loop in scrub scrubBackupFreelist on Cyclic Freelist Trunk Chain](https://sqlite.org/bugs/info/323854b8eb4532246515f267fc1e7a58fd50694d21cf9719281b161bef0b8609)
- **logic_wrong_result** (1):
  - [.import CSV files: treatment of scientific notation has changed](https://sqlite.org/bugs/info/3b4b93a29aa4e50f70358843fce809453b3a20129e9434c6e9e626871fba36ae)
- **undefined_behavior** (1):
  - [Lemon: no--D invocation triggers glibc qsort() nonnull diagnostic in a downstream UBSan build](https://sqlite.org/bugs/info/1a6429fcdaaf4fcb036555ae7f6a18d29d1cb3128f19865e55b9af283514a3aa)

### ext_expert (3)

- **buffer_overflow** (2):
  - [Vuln32-13: COLLATE %s Injection in sqlite3expert idxPopulateOneStat1 Causes idxRemFunc Heap OOB Access](https://sqlite.org/bugs/info/5eaf453243d8104d70e4bde132d742b713c5db25e545a26fe96d70a6ae0d7d3e)
  - [Vuln82-63: FTS5 Integrity-Check Heap Over-read via Unvalidated Leaf Term Length](https://sqlite.org/bugs/info/449fdcd1b1cee5a52d6db69ef9d577e3498c1271b164042d15b85e9a0afa4a6c)
- **null_deref** (1):
  - [NULL pointer write on allocation failure in readSqlFromFile() (ext/expert/expert.c)](https://sqlite.org/bugs/info/ac1aa914b085ea718b118a6fdb6b9fc4db77e90168bfebfb23f24f40a48c17ea)

### ext_intck (3)

- **buffer_overflow** (3):
  - [Heap Buffer Overflow Read in intckGetToken() via Unterminated Bracket Identifier](https://sqlite.org/bugs/info/466277fbbc796a2638a8a1766d38f026246def6279b9b6ab043fa8693c8dfc74)
  - [Vuln83-64: Heap Over-read in intck intckGetToken Bracket-quoted Token Scan](https://sqlite.org/bugs/info/58f81f9b0147c834ed66280f6c2834850d8537a160fde948624f472bb47f53e2)
  - [Vuln99-80: intck intckParseCreateIndex Heap/Global Over-read on Empty Index Text](https://sqlite.org/bugs/info/58038f8cd923d88b4a3ec537398e0dd651bf46ad3bfeb336551389c68398e889)

### main_api (3)

- **use_after_free** (2):
  - [External-content FTS5 index corrupted by a second AFTER UPDATE trigger issuing a nested UPDATE on the content tab](https://sqlite.org/bugs/info/552f36384c7900ef72448f71118f9c6fe8aa2553e7ef617ef7323c3d0f54b104)
  - [Bug in test suite](https://sqlite.org/bugs/info/f00eb527e9988c997b59f1bca04b47c65170ffcf02bcd28eaacf94363229841f)
- **buffer_overflow** (1):
  - [PTP - Heap buffer overflow in sqlite3ParseUri for over-1GiB file: URI filenames](https://sqlite.org/bugs/info/fdcc0d34a1f7804964ba6fc79c61f1e0f3e8cce0bd1392d34ed9f677506d8a8b)

### btree (3)

- **stack_overflow** (2):
  - [`btree.c:checkTreePage` recursive walk of a linear interior-page chain](https://sqlite.org/bugs/info/5e16d4dc9a269b5fec41a2b883f988c5b8ef970e603142b12c71d8befe0b8397)
  - [`btree.c:clearDatabasePage` unbounded recursive descent on a crafted interior-page chain](https://sqlite.org/bugs/info/5d82716e0f8b6861a74947914c6d4a6171163c032aeb67cb53bcfe793fe9db97)
- **buffer_overflow** (1):
  - [PTP - Corrupt index cell pointer crosses page boundary](https://sqlite.org/bugs/info/3b558727b141f90bbc40619e82e8aac51eabdadb2beebe4ab8af1486928c1898)

### ext_qrf (2)

- **logic_wrong_result** (1):
  - [Shell quotes incorrectly symbol "greater than" in HTML mode](https://sqlite.org/bugs/info/f72dfbdeff2002ce8351102b49813ed8ac46dad932a4ee2d99a542f0fb561dbb)
- **null_deref** (1):
  - [NULL pointer dereference on a scan with no addrExplain in qrfEqpStats() (ext/qrf/qrf.c)](https://sqlite.org/bugs/info/7259ac0c6d82153aa08f5dcc9288fffa5da6a9a43e8df8fad3d275679772e266)

### parser (2)

- **logic_wrong_result** (1):
  - [Vuln25-6: FULL JOIN USING and NATURAL FULL JOIN Bypass Column-Level Authorizer Checks](https://sqlite.org/bugs/info/36773162f087c792f7de27e17aed18cd60206fe8c2820297e42ac427af572d90)
- **assertion_failure** (1):
  - [Vuln98-79: resolve.c lookupName() Column-level Authorizer Bypass on FULL JOIN USING](https://sqlite.org/bugs/info/d8ac2c607497fd6603c8a27493973c2901e3b9ea5d039ab32617864df92e5375)

### pcache (2)

- **buffer_overflow** (1):
  - [Vuln45-26: pcache1InitBulk do-while Loop Heap Buffer Overflow When -pagecache N=-1 Produces nBulk=0](https://sqlite.org/bugs/info/5d30ea149cc18443a83e6437a066a93782858822dc843e7d1fbbdaec3d66116d)
- **unknown** (1):
  - [Include guard in src/pcache.h never defines its own macro](https://sqlite.org/bugs/info/22434040cba800f81cfdd91695fd75e20d47c1e742b7ebd26211a0c8aebfcedf)

### wal (2)

- **buffer_overflow** (1):
  - [WAL read-only `readonly_shm` path accepts page-size 0 and over-reads in `walChecksumBytes()`](https://sqlite.org/bugs/info/d1ec6fecacde3ce5413c3a5144e6ba6d82035a4922afb09d07d231836aef38bd)
- **uninitialized** (1):
  - [Uninitialized page-buffer disclosure via WAL/DB page-size mismatch (3.53.4)](https://sqlite.org/bugs/info/7595f49741512330502f66bbd916c7da104d77ac7d784a8c2fee057ec1667314)

### pager (2)

- **data_corruption** (1):
  - [PTP - Crafted Rollback Journal Can Delete an Arbitrary File](https://sqlite.org/bugs/info/0903b836fdae69784a53ebb31a697a6cf025b2c4f0232054fd992c74ee4aaefc)
- **unknown** (1):
  - [immutable URI flag opening files read-write](https://sqlite.org/bugs/info/b55092f6b04bc4975d8d85c342fbc29f65896b4fe29065fcd75234719b0de488)

### unattributed (1)

- **data_corruption** (1):
  - [sqlite_dbpage accepts an out-of-range pgno on write and wraps it to page 1, corrupting the database header instead of rejecti](https://sqlite.org/bugs/info/f363b34881ce58e419291d47c12296dc549e0d5eeaa76cce61e8e2186f2a45cd)

### util (1)

- **null_deref** (1):
  - [Vuln60-41: blobio Extension readblob/writeblob NULL Column Argument Dereferences NULL Pointer in sqlite3StrICmp](https://sqlite.org/bugs/info/9c30d4669998b12e43a9818bcb556ff89db7c14a367ee3d8701e04c52d6139b4)

### vtab (1)

- **use_after_free** (1):
  - [PTP - sqlite3_drop_modules() races module hash iteration](https://sqlite.org/bugs/info/4b86a2e82409ac7779ed5c68d899cbd22eced6a31875cbd27c01bf07073ab084)

### ext_wasm (1)

- **integer_overflow** (1):
  - [Signed integer overflow in WebAssembly pstack allocation](https://sqlite.org/bugs/info/4dbd096fe335f974ac175841ed06a346a466698dada1617f01abeff8160ef46e)