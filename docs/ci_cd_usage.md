# CI/CD usage

This is an example script you could use to test a playbook against all your scenarios

```bash
#!/bin/bash
set -e # exit when any command fails

ANSIBLE_CMD="ANSIBLE_CONFIG='ansible.cfg' ansible-playbook -v"

function test_all_scenario () {
  # $1: playbook path
  # $2: vars path
  # $3: list scenario

  local  PLAYBOOK_PATH=$1
  local  VARS_PATH=$2
  shift # Shift all arguments to the left (original $1 gets lost)
  shift # Shift all arguments to the left (original $2 gets lost)
  local LIST_SCENARIO=("$@") # Represents the remaining parameters

  for scenario in "${LIST_SCENARIO[@]}"; do  
    echo "Run Monkeyble scenario: $scenario"
    $ANSIBLE_CMD \
    $PLAYBOOK_PATH \
    -e "@${VARS_PATH}" \
    -e "monkeyble_scenario=$scenario"
  done
}

echo "Monkeyble test playbook start..."
LIST_SCENARIO=(
  "validate_scenario_1"
  "validate_scenario_2"
  "validate_scenario_3"
)
PLAYBOOK_PATH="playbook.yml"
VARS_PATH="monkeyble.yml"
test_all_scenario $PLAYBOOK_PATH $VARS_PATH "${LIST_SCENARIO[@]}"
```
