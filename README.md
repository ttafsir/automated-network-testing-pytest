# RTP Network & Programmability Meetup - Test and Validate Networks with `pytest`

This repository contains the code for the presentations at the RTP Network & Programmability Meetup:

Meetup Presentations:

* 9-08-2012 - [Test and Validate Networks with Pytest 1](https://www.youtube.com/watch?v=kuPTAca_p8w&t)
* TBD - Test and Validate Networks with Pytest 2

## The Sample tests

The tests for the sessions are separate, depending on the branch. The tests are organized in different branches as follows:

* `main` - includes simple and introductory tests reviewed during the [Test and Validate Networks with Pytest 1](https://www.youtube.com/watch?v=kuPTAca_p8w&t) session. The tests do not require any test infrastructure and are located in the [tests/quickstart](./tests/quickstart) directory. (**Session 1**)
* `pytest_features` - includes examples of tests we reviewed during the discussion of Pytest Features, including introductory examples for some best practices. Some of these tests do require that you have a test infrastructure (See the [Test Infrastructure](#test-infrastructure) section for more details). These tests are located in the [tests/simple](./tests/simple) directory. (**Session 1**)
* `infra_tests` -  includes more advanced and realistic examples for infrastructure tests, including using an existing Ansible inventory and a connection library like `netmiko` with pytest using hooks. It also includes examples of accomplishing the same using the TestInfra plugin with an ansible backend.  (**Session 2**)

## Test Infrastructure

The test infrastructure for some examples in the repository uses the  [EVPN Symmetric IRB](https://github.com/arista-netdevops-community/avd-cEOS-Lab#labs) lab from [https://github.com/arista-netdevops-community/avd-cEOS-Lab](https://github.com/arista-netdevops-community/avd-cEOS-Lab) project (the NOTICE file includes license information). The `inventory` and `playbooks` directories in the root are almost identical, with only a slight modification I needed to make to the [fabric-deploy-config.yaml](./playbooks/fabric-deploy-config.yaml) playbook.

To deploy your own infrastructure using [containerlab](https://containerlab.dev/), please follow the directions from the project.
