# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.2] - 2023-12-19

### Added

- db_util: Return queue element when calling create_queue_element.
- OrchestratorConnection: Return queue element when calling create_queue_element.

### Fixed

- OrchestratorConnection: Bug in get_queue_elements.

## [1.0.1] - 2023-11-29

### Added

- Changelog!

### Fixed

- db_util: get_next_queue_trigger should only count 'NEW' queue elements.

## [1.0.0] - 2023-11-16

- Initial release

[Unreleased]: https://github.com/itk-dev-rpa/OpenOrchestrator/compare/1.0.2...HEAD
[1.0.2]: https://github.com/itk-dev-rpa/OpenOrchestrator/releases/tag/1.0.2
[1.0.1]: https://github.com/itk-dev-rpa/OpenOrchestrator/releases/tag/1.0.1
[1.0.0]: https://github.com/itk-dev-rpa/OpenOrchestrator/releases/tag/1.0.0