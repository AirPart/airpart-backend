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
- [ ] create model invoice (feature) #820260608 _[IN PROGRESS]_
- [ ] add edit action for invoice api (feature) #320260606
- [x] fixed save invoice in database { save tow record for tow product} (bug) #120260609
- [ ] manageing packages with pip-compile and setup in project (refactoring) #120260611 ref:https://gapgpt.app/chat/80f4ef40-a534-4ddf-8f7d-235e46f021c8
- [ ] seperate service and repository logic in app (refactoring) #220260611
- [ ] fixed 200 response document flassger for all api (document) #120260613
- [ ] add continus integration in project (commit checker, formatter, linter for python )(ci) #120260614
