# Active Context: Mira AI Agent

## Current Focus
- **Phase 5: Documentation Update**
- **Current Task**: Update all project documentation to reflect the new native Python deployment architecture.

## Next Steps
1.  Update `memory-bank/progress.md`.
2.  Update `how_it_works.md`.
3.  Commit all documentation changes.

## Active Decisions
- **Deployment Strategy**: The project has officially moved away from a Docker-based deployment. The new standard is a native Python runtime on Render, managed by a `render.yaml` file. This decision was made after significant deployment challenges with the Docker/Gunicorn approach.
- **Scheduler**: The scheduler is implemented via a webhook called by an external cron service, due to the limitations of Render's free tier.
