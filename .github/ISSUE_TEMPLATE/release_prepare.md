---
name: Release Preparation
about: Track tasks for preparing a new release
title: 'Release Preparation: vX.X.X'
labels: release
assignees: ''

---

**Release Version**
Specify the version number for the release (e.g., v0.7.1):

**What is changed?**
TODO: please at least copy the release note here, afterwards

**Checklist**
Following steps will be checked:
- [ ] Revise the changelog if necessary
- [ ] Update the version tag in:
  - [ ] `filip/__init__.py`
  - [ ] `Changelog`
- [ ] Check dependencies in `setup.py`, especially when a new library is introduced
- [ ] Check other information in `setup.py`

After that, create a pull request and merge it (merge commit) to `master` branch with a commit message containing `[PYPI-RELEASE]`.


**Additional Context**
Add any other context or notes related to the release preparation here.
