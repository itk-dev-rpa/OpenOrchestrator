# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


### Added

- Automated tests of the Orchestrator ui
- Added argument to manually set Orchestrator port.
- Added argument to prevent Orchestrator from opening in the browser automatically.
- Added 'Scheduler' tab with overview of running schedulers
- Raise error if git is not installed when trying to clone a git repo

### Changed

- Changed cli to use argparser.
- Trigger status 'Paused' is now colored orange in the trigger tab.

## [1.3.0] - 2024-06-19

### Added

- 'Abandoned' status to queue elements.
- 'Pausing' status added to triggers.
- Disabling a 'Running' trigger in Orchestrator will set its status to 'Pausing'.
- Scheduler will change a 'Pausing' trigger to 'Paused' when the process is done.
- Queue elements can now be filtered by 'Created Date'.

### Fixed

- Refactoring for more correct typing.
- Get-functions in db_util now works in SQLITE.
- DatetimeInput tried to update before the UI was ready.
- Credentials made with an old encryption key couldn't be edited.

### Changed

- Sort triggers & queues by name by default.
- Log messages over 8000 characters are now truncated preserving the beginning and end.

## [1.2.0] - 2024-02-27

### Changed

- Scheduler run tab refactored to OOP design.
- Run tab design cleaned up.
- Cloned repo folders are removed when the respective processes are done/failed.
- Scheduled triggers no longer try to catch up to missed runs.
- Orchestrator port number made dynamic allowing multiple instances.
- Default pagination increased on trigger and queue tables.

### Fixed

- Scheduler doesn't freeze when connection is momentarily lost.

## [1.1.0] - 2024-01-25

### Changed

- Orchestrator rewritten to use NiceGui instead of TKinter for its UI.
- Lots and lots of UI changes and upgrades.
- All UI logic removed from db_util.
- Refactoring and renaming of files.
- Scheduler log area limited to 1000 lines.
- Updated Github Workflows

### Added

- Queues tab in Orchestrator to monitor queues.
- Scheduler logs errors when a robot returns a non-zero return code.
- Ability to change the next run time on Scheduled triggers.
- Automated tests of database functionality and OrchestratorConnection.
- Orchestrator auto updates data when in focus.


### Fixed

- Scheduler doesn't spam "File not found" anymore.
- Type hints on db functions.


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

[Unreleased]: https://github.com/itk-dev-rpa/OpenOrchestrator/compare/1.3.0...HEAD
[1.3.0]: https://github.com/itk-dev-rpa/OpenOrchestrator/releases/tag/1.3.0
[1.2.0]: https://github.com/itk-dev-rpa/OpenOrchestrator/releases/tag/1.2.0
[1.1.0]: https://github.com/itk-dev-rpa/OpenOrchestrator/releases/tag/1.1.0
[1.0.2]: https://github.com/itk-dev-rpa/OpenOrchestrator/releases/tag/1.0.2
[1.0.1]: https://github.com/itk-dev-rpa/OpenOrchestrator/releases/tag/1.0.1
[1.0.0]: https://github.com/itk-dev-rpa/OpenOrchestrator/releases/tag/1.0.0
