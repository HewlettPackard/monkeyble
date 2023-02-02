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
