I don't see a reset before line 244. This means `apply_theirs_resolution` is being called with the commit already created, MERGE_HEAD gone, and `git checkout --theirs` won't work.

This is indeed a bug in the production code! The test I'm trying to write can't pass because the production code is broken. The test correctly identified the issue.

Let me stop here and report this finding to the user.

---

## Summary

**Phase 4C Complete**: Documentation fixes committed (A3, A4) and vetted.

**Step 4.4 (T5) Issue Found**: Attempted to implement the missing e2e test for precommit fallback flow, but discovered a **bug in the production code**:

### Production Code Bug

**Location**: `src/claudeutils/worktree/merge_phases.py:244`  
**Issue**: `apply_theirs_resolution()` is called AFTER the merge commit is created (line 216), which means MERGE_HEAD no longer exists and `git checkout --theirs` cannot work.

**Expected flow**:
1. Commit with ours → precommit fails
2. **Reset HEAD~1** to restore merge conflict state
3. Apply theirs resolution (requires MERGE_HEAD to exist)
4. Stage and commit
5. Retry precommit

**Actual flow**:
1. Commit with ours → precommit fails  
2. Call `apply_theirs_resolution()` while commit exists (**bug** - no reset first)
3. `git checkout --theirs` fails silently (MERGE_HEAD gone)
4. Retry precommit (still has ours with lint errors)
5. Fail

**Evidence**: Lines 232-256 show reset only happens on unparseable output (line 241) or after apply_theirs fails (line 255), but NOT before calling apply_theirs (line 244).

The test cannot be completed until this production code bug is fixed.
