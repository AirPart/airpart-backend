# AirPart Backend

Backend service for the AirPart project.

## Clone

```bash
git clone git@github.com:AirPart/airpart-backend.git
cd airpart-backend
```

## Documentation

For setup, environment variables, development workflow, and dependency management, see:

- [Backend Setup](https://github.com/AirPart/airpart-docs/blob/dev/backend/setup.md)
- [Backend Environment Variables](https://github.com/AirPart/airpart-docs/blob/dev/backend/environment-variables.md)
- [Git Workflow](https://github.com/AirPart/airpart-docs/blob/dev/development/git-strategy.md)
- [Dependency Management](https://github.com/AirPart/airpart-docs/blob/dev/development/dependency-managment.md)

# TODO

- [x] Add comprehensive backend tests for services, repositories, and core business logic (test) #120260621
- [ ] Separate development and production dependency management with pip-tools (ci) #120260622
  - [x] Audit and classify runtime vs development dependencies (ci) #120260807
  - [x] Refactor pip-tools requirement files into base and dev locks (ci) #220260807
  - [ ] Update CI and deployment to install environment-specific dependencies (ci) #320260807
- [ ] seperate countribute part from readme (create CONTRIBUTE.md file and link in readme file) (docs) #120260707
- [ ] seperate TODO part from readme and add in github issues (docs) #120260709
