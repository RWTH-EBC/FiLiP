# **CI Workflow for FiLiP**

This repository uses **GitHub Actions** to automate the **Continuous Integration (CI)** process for FiLiP. The workflow ensures that the code is properly tested across multiple **Python versions** and validates the interaction with **FIWARE APIs**.


- [Workflow Overview](#workflow-overview)
- [Workflow Triggers](#workflow-triggers)
- [Workflow Configuration](#workflow-configuration)
  - [GitHub Actions Workflow File](#github-actions-workflow-file)
- [Workflow Steps](#workflow-steps)
  - [Checkout Repository](#checkout-repository)
  - [Debug - Verify Repository Structure](#debug---verify-repository-structure)
  - [Set Up Python](#set-up-python)
  - [Create and Store Environment Variables](#create-and-store-environment-variables)
  - [Start FIWARE Services](#start-fiware-services)
  - [Wait for FIWARE Services](#wait-for-fiware-services)
  - [Install Dependencies](#install-dependencies)
  - [Show Running Docker Containers](#show-running-docker-containers)
  - [Navigate to Root Directory](#navigate-to-root-directory)
  - [Run Tests](#run-tests)
- [Workflow Features](#workflow-features)
- [How to Use This Workflow](#how-to-use-this-workflow)
  - [Store Environment Variables in GitHub](#store-environment-variables-in-github)
  - [Push Code to Any Branch](#push-code-to-any-branch)
  - [View Result](#view-result)


---

## **Workflow Overview**
This is the main features of this **CI pipeline**:
1. **Checks out** the repository.
2. **Sets up Python** (versions **3.8 - 3.12**).
3. **Loads environment variables** dynamically from [GitHub environment](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/store-information-in-variables).
4. **Starts FIWARE services** using `docker compose`.
5. **Waits for FIWARE services** to initialize.
6. **Installs dependencies** via `setup.py`.
7. **Runs unit tests** using `pytest`.
8. **Ensures all Python versions execute, even if one fails** by setting `fail-fast: false`

---

## **Workflow Triggers**
The workflow runs on:
- **Push** to any branch.
- **Pull requests** targeting `main`.

---

## **Workflow Configuration**
### **GitHub Actions Workflow File**
The workflow is defined in `.github/workflows/unittest.yml`.

```yaml
name: CI for FiLiP

on:
  push:
    branches:
      - "**"
  pull_request:
    branches:
      - main

jobs:
  setup:
    runs-on: ubuntu-latest
    environment: unittests  # Unit test environment
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]
      fail-fast: false  # Ensure all setups run even if one fails
```

---

## **Workflow Steps**
### **Checkout Repository**
```yaml
- name: Checkout Code
  uses: actions/checkout@v3
  with:
    ref: ${{ github.ref }}  # check out the committed branch
```
- Ensures the workflow pulls the correct **branch**.

### **Debug - Verify Repository Structure**
```yaml
- name: Debug - Verify Repository Structure
  run: |
    pwd
    ls -la
```
- Lists all files for debugging.

### **Set Up Python**
```yaml
- name: Set up Python ${{ matrix.python-version }}
  uses: actions/setup-python@v4
  with:
    python-version: ${{ matrix.python-version }}
```
- Runs tests across **Python 3.8 - 3.12**.

### **Create and Store Environment Variables**
```yaml
- name: Create .env file
  run: |
    cat <<EOF > .env
    LOG_LEVEL="INFO"
    CB_URL=${{ vars.CB_URL }}
    ORION_LD_URL=${{ vars.ORION_LD_URL }}
    IOTA_JSON_URL=${{ vars.IOTA_JSON_URL }}
    IOTA_UL_URL=${{ vars.IOTA_UL_URL }}
    QL_URL=${{ vars.QL_URL }}
    MQTT_BROKER_URL=${{ vars.MQTT_BROKER_URL }}
    MQTT_BROKER_URL_INTERNAL=${{ vars.MQTT_BROKER_URL_INTERNAL }}
    LD_MQTT_BROKER_URL=${{ vars.LD_MQTT_BROKER_URL }}
    LD_MQTT_BROKER_URL_INTERNAL=${{ vars.LD_MQTT_BROKER_URL_INTERNAL }}
    FIWARE_SERVICE=${{ vars.FIWARE_SERVICE }}
    FIWARE_SERVICEPATH=${{ vars.FIWARE_SERVICEPATH }}
    EOF
```
- Pulls **FIWARE-related variables** from GitHub **repository variables**.

### **Start FIWARE Services**
```yaml
- name: Start FIWARE Services
  run: |
    cd docker
    docker compose up -d
```
- Starts FIWARE services using **docker-compose**.

### **Wait for FIWARE Services**
```yaml
- name: Wait for FIWARE Services
  run: |
    for i in {1..30}; do
      curl -s http://localhost:1026/version &&       
      curl -s http://localhost:4041/iot/about &&       
      curl -s http://localhost:8668/version && break || sleep 5
    done
```
- Ensures FIWARE services are **ready before tests start**.

### **Install Dependencies**
```yaml
- name: Install dependencies (if needed)
  run: |
    python -m pip install --upgrade pip
    pip install setuptools wheel
    pip install .
    pip install pytest
```
- Install project dependencies.
- Install dependencies from setup.py

### **Show Running Docker Containers**
```yaml
- name: Debug - Show Running Docker Containers
  run: docker ps -a
```
- Verifies **running Docker containers**.

### **Navigate to Root Directory**
```yaml
- name: Navigate to Tests Folder
  run: |
    cd $GITHUB_WORKSPACE
    ls -la
```
- Moves to the Root directory before running tests.

### **Run Tests**
```yaml
- name: Run tests with unittest and pytest
  run: |
    python -m pytest tests
```
- Runs **all tests** using `pytest`.

---

## **Workflow Features**
- **Matrix Testing** - Runs tests across **Python 3.8 - 3.12**.  
- **Environment Variables Management** - Uses **GitHub environment variables** instead of hardcoded values.  

  ```yml
  environment: unittests  # Environment for unit tests
  ```

  - Add this line to find all environment variables 
- **Waits for FIWARE Services** - Ensures all FIWARE components are **running before tests**.  
- **Fail-Fast Disabled** - **Other tests continue** even if one fails.  
- **Logs Key Debugging Information** - Shows **repository structure**, **running containers**, and **environment file**.  

---

## **How to Use This Workflow**
### **Store Environment Variables in GitHub**
Go to **Settings > Environments > unittests** and add:
- `CB_URL`: `"http://localhost:1026"`
- `FIWARE_SERVICE`: `"filip"`
- `FIWARE_SERVICEPATH`: `"/testing"`
- Other FIWARE-related URLs (`IOTA_URL`, `QL_URL`, etc.).

### **Push Code to Any Branch**
- The workflow **automatically runs** when you push changes.

### **View Result**
- Navigate to **Github Actions** in your repository:
  ```
  GitHub > Actions > CI for FiLiP
  ```
---
