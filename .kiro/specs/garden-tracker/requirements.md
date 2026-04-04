# Requirements Document

## Introduction

A minimal garden management web application that helps gardeners track their plants and see their current status at a glance. This initial version focuses exclusively on a Plant List View — a simple, text-based list of all tracked plants. The app runs locally in a Docker container on a Raspberry Pi and stores data in SQLite. The goal is to start small and build incrementally.

## Glossary

- **Garden_App**: The web application that manages garden data and presents it to the user.
- **Plant**: A tracked garden item with a name, type, and optional variety.
- **Plant_List**: The view showing all tracked plants and their basic information.
- **SQLite_Store**: The SQLite database file used as the primary data persistence mechanism.
- **Variety**: A named cultivar of a plant type (e.g., "Elsanta", "Honeoye").

## Requirements

### Requirement 1: Plant List View

**User Story:** As a gardener, I want to see a list of all my plants with their basic information, so that I can quickly get an overview of what I'm growing.

#### Acceptance Criteria

1. THE Garden_App SHALL display a Plant_List showing all tracked plants.
2. WHEN the Plant_List is rendered, THE Garden_App SHALL show the plant name, plant type, and Variety (if set) for each Plant.
3. WHEN a user adds a new Plant, THE Garden_App SHALL record the plant name, plant type, and optionally a Variety.
4. WHEN a user removes a Plant, THE Garden_App SHALL remove it from the Plant_List.
5. THE Garden_App SHALL support tracking multiple plants simultaneously.
6. IF no plants have been added, THEN THE Garden_App SHALL display an empty state message indicating no plants are being tracked.

---

### Requirement 3: German User Interface

**User Story:** As a German-speaking gardener, I want the entire application interface to be in German, so that I can use it comfortably in my native language.

#### Acceptance Criteria

1. THE Garden_App SHALL display all labels, buttons, and static text in German.
2. THE Garden_App SHALL display all user-facing messages — including empty state messages and error messages — in German.
3. WHEN a user enters plant names and Variety names, THE Garden_App SHALL accept and display them in German.

---

### Requirement 2: Local Deployment on Raspberry Pi

**User Story:** As a self-hosted user, I want to run the Garden_App in Docker on my Raspberry Pi, so that it is available on my local network without depending on any external hosting.

#### Acceptance Criteria

1. THE Garden_App SHALL be packaged as a container image built for the linux/arm64 architecture.
2. THE Garden_App SHALL expose its web interface on a configurable HTTP port.
3. THE Garden_App SHALL persist all plant data in a SQLite_Store located on a volume mount so that data survives container restarts.
4. IF the SQLite_Store is unavailable at startup, THEN THE Garden_App SHALL log a descriptive error and exit with a non-zero status code.
5. THE Garden_App SHALL operate without requiring elevated privileges on the Docker host.
