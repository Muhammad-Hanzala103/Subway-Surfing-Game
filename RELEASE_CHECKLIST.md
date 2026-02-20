# Release Checklist

## 1. Version Bump
- [ ] Update version string in `setup.py` or relevant config file
- [ ] Ensure `CHANGELOG.md` has the new version properly sectioned and dated

## 2. Testing
- [ ] Run automated tests locally (`pytest`) and ensure 100% pass rate
- [ ] Review CI pipeline in GitHub Actions for green status
- [ ] Perform manual end-to-end playthrough
  - Verify state transitions (Menu -> Shop -> Play -> Pause -> Game Over -> Menu)
  - Verify purchases and coin deduction
  - Verify score and total coins saving and legacy migration
  - Verify settings correctly apply (High Contrast, Particles, Shake, Rebinding)

## 3. Building
- [ ] Verify `PyInstaller` is installed (`pip install pyinstaller`)
- [ ] Run `python build.py`
- [ ] Validate the executable launches without terminal window
- [ ] Create a ZIP archive of the `dist/RailRunners` folder

## 4. Release
- [ ] Tag the release in Git (`git tag vX.Y.Z`)
- [ ] Push tags to origin (`git push origin vX.Y.Z`)
- [ ] Create a new GitHub Release with the tag
- [ ] Upload the built ZIP archive as a release asset
- [ ] Copy the newest `CHANGELOG.md` section into the release description
