# Tasks

- [x] Task 1: Fix typo in auth.py
  - [x] SubTask 1.1: Change `settings.ALgorithm` to `settings.ALGORITHM` on line 36

- [x] Task 2: Fix invalid enum in auth.py
  - [x] SubTask 2.1: Change `HierarchyLevel.DPD` to `HierarchyLevel.NONE` on line 327

- [x] Task 3: Fix phone column size in models.py
  - [x] SubTask 3.1: Change `String(15)` to `String(100)` for phone column

- [x] Task 4: Update database schema
  - [x] SubTask 4.1: Run ALTER TABLE to increase phone column size

- [x] Task 5: Rebuild and restart Docker containers
  - [x] SubTask 5.1: Rebuild backend container
  - [x] SubTask 5.2: Rebuild frontend container

# Task Dependencies
- Task 2 depends on Task 1
- Task 4 depends on Task 3
- Task 5 depends on Task 1, Task 2, Task 3, Task 4
