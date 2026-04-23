# 1.7.0 2026-04-23

## Feature

- Official prebuilt Ansible Execution Environment available on `quay.io/hewlettpackardenterprise/monkeyble`
- GitHub Actions workflow to build and push the EE on merge to master
- GitHub Actions workflow to build and deploy documentation on merge to master

## Fix

- Prevent filesystem metadata from overwriting mock `result_dict` when `dest` or `path` key exists and the file is present on disk
- Prevent `scenario_extra_vars` mutation across tasks
- Prevent `playbook_vars` mutation during loop `test_input`

## Enhancement

- Refactor templating and version compatibility
- Updated "Do I need Monkeyble?" section in README to clarify the difference with Molecule
- Updated CI/CD documentation with official EE image usage

# 1.6.0 2026-04-20

## Enhancement

- Support Ansible 12 (Core 2.19)

## Fix 

- don't raise when we expected a task to fail (should_fail: true) and it actually failed

# 1.5.0 2025-10-10

## Feature

- Support of Ansible loop in tests
- Support of rescue block 
- Add extra vars at scenario level

# 1.4.4 2024-01-05

## Fix

- monkeyble mock module now work when module defaults are set #36

# 1.4.3 2024-02-27

## Enhancement

- Support of Ansible 11

# 1.4.1 2024-01-05

## Fix

- variable are now handled when using ignore_error
- fix test (new url)

# 1.4.0 2023-03-06

## Feature

- CLI: add `monkeyble list` + `monkeyble test --limit`

## Fix

- Fix error message on should_fail

## Enhancement

- check if task should have failed when actually skipped

# 1.3.0 2023-02-02

## Fix

- exit Monkeyble on missing var

## Feature

- added "❌ MONKEYBLE ERROR ❌" in logs output when scenario failed
- added "monkeyble_shared_tasks"

# 1.2.0 2022-12-02

## Breaking changes

- `should_failed` flag renamed to `should_fail`

## Feature

- add monkeyble_global_extra_vars to the cli config 
- add version to the arg parser

## Enhancement

- print success message only if no failure detected

# 1.1.1 2022-11-29

## Fix

- Stop monkeyble callback if arg name not found during test input

## Enhancement

- Exit error if Monkeyble callback has not started in the test execution
- Add cli execution time
