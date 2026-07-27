# Contribute Guide

Thank you for your interest in contributing to the **"Project Name"**.Following these steps ensures a smooth setup and a consistent workflow for everyone.

---

## 📑 Table of Contents

- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [Clone the Repository](#1-clone-the-repository)
  - [Environment Setup](#2-environment-setup)
  - [Install Dependencies](#3-install-dependencies)
- [Environment Variables](#environment-variables)
- [Development Workflow](#development-workflow)
  - [Dependency Management](#dependency-management)
  - [Code Quality(pre-commit, lint/format)](#code-quality)
  - [Branch Strategy](#branch-strategy)
- [TODO](#todo)

---

## 🛠 Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.10+**
- **Git** (configured with SSH)
- **Virtualenv** (optional but recommended)

---

## 🚀 Installation

### 1. Clone the Repository

We recommend using **SSH** for a secure and seamless connection. Make sure your SSH key is added to your GitHub account.

```bash
git clone git@github.com:Mohammadhoseinajorloo/aestock-aircraft-port-backend.git
cd aestock-aircraft-port-backend
```

### 2. Environment Setup

Create and activate a virtual environment to isolate project dependencies:

On Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

Once the virtual environment is active, install the required packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Environment Variables

The application requires certain environment variables to function correctly.

Copy the sample environment file:

```bash
cp .test.env.sample .test.env
```

Open .test.env and update the following variables as needed:

|     Variable     |            Description             |    Default     |
| :--------------: | :--------------------------------: | :------------: |
|    DB_ADDRESS    | Connection string for the database | (Check sample) |
| DB_PRODUCT_IMAGE |  Path/Storage for product images   | (Check sample) |
| DB_PRODUCT_DOCS  | Path/Storage for product documents | (Check sample) |

## Development Workflow

### Dependency Management

for add package in project in roadmap Effective dependency management is crucial for maintaining a stable and reproducible development environment. We use pip-tools to achieve this by keeping our dependencies organized and up-to-date.develope add package name in `requirements.in` file.

**Adding New Packages**

To add a new package to your project, you should append its name to the `requirements.in` file. This file serves as the source of truth for your project’s direct dependencies.

**Updating Dependencies**

To update your requirements.txt file, which lists all direct and transitive dependencies with pinned versions, follow these steps:

1. Install pip-tools: If you haven’t already, install the pip-tools package:

```bash
pip install pip-tools
```

2.Compile `requirements.in`: Run the following command to generate or update your requirements.txt file:
bash

```bash
pip-compile requirements.in
```

This command will process `requirements.in`, resolve all dependency versions, and generate a comprehensive requirements.txt file. It’s recommended to commit both `requirements.in` and requirements.txt to your version control system.

### Code Quality

We use `pre-commit` to run automated code quality checks before each commit.

Install the git hooks:

```bash
pre-commit install
```

Run all hooks manually on the entire repository:

```bash
pre-commit run --all-files
```

Update hook versions in .pre-commit-config.yaml:

```bash
pre-commit autoupdate
```

### Branch Strategy

This project follows the **Git Flow** branching strategy.

Branches used in the project:

- **main** → Production-ready code
- **dev** → Integration branch for development
- **feature/`<feature-name>`** → New features
- **bugfix/`<issue-name>`** → Bug fixes

Typical workflow:

1. Pull the latest changes from `dev`

`git checkout dev`

`git pull origin dev`

2. Create a new feature branch

`git checkout -b feature/your-feature-name`

3. Commit your changes with clear commit messages conventional and use task tag and branch name in commit message.

   > e.g type(scop) commit title (Closes or Not Closes)
   >
   > > commit body
   > > branch: branch name
   > > Closes or Refs : task tag

4. Push the branch to the remote repository.

`git push origin feature/your-feature-name`

5. Open a **Pull Request** targeting the `dev` branch.

# TODO

- [x] add issuing an inovice api (feature) #120260603
- [x] add get all invoice list api (feature) #220260606
- [x] add delete action for invoice api (feature) #320260606
- [x] add get a invoice by id api (feature) #420260606
- [x] add readme roadmap for developers and user or deploy state in (docs) #520260606
- [x] clean structure project (refactoring) #620260608
- [x] add json response utils in get inovice api (chore) #720260608
- [x] create model invoice (feature) #820260608
- [x] add edit action for invoice api (feature) #320260606
- [x] fixed save invoice in database { save tow record for tow product} (bug) #120260609
- [x] manageing packages with pip-compile and setup in project (refactoring) #120260611
- [x] seperate service and repository logic in app (refactoring) #220260611
- [x] fixed 200 response document flassger for all api (document) #120260613
- [x] add continus integration in project (commit checker, formatter, linter for python )(ci) #120260614
- [ ] create base model abstract method for to dict function in each model (refactor) #220260614
- [ ] use invoice model in apis (chore) #320260614
- [ ] chenge route name in add invoice (chore) #420260614
- [ ] seperate wiki document from readme file (document) #120260615 ref:https://gapgpt.app/chat/3e094ad7-5f2e-47e2-9972-a4d6ad8998b2
- [ ] add product docs flassger (document) #120260617
- [ ] add test apis (test) #120260621
- [ ] seperate dev and production package mangeing wiht pip-compine (ci) #120260622
- [ ] seperate countribute part from readme (create CONTRIBUTE.md file and link in readme file) (docs) #120260707
- [ ] seperate TODO part from readme and add in github issues (docs) #120260709
