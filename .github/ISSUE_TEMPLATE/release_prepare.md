---
name: Release Preparation
about: Track tasks for preparing a new release
title: 'Release Preparation: vX.X.X'
labels: release
assignees: ''

---

**Release Version**
Specify the version number for the release (e.g., v0.7.1):

**Checklist**
Following steps will be checked:
- [ ] Revise the changelog if necessary
- [ ] Update the version tag in:
  - [ ] `setup.py`
  - [ ] `filip/__init__.py`
  - [ ] `Changelog`
- [ ] Check dependencies in `setup.py`, especially when a new library is introduced
- [ ] Check other information in `setup.py`

After that, this can this branch will be merged the branch to `master` with a commit message containing `[PYPI-RELEASE]`


**Additional Context**
Add any other context or notes related to the release preparation here.
