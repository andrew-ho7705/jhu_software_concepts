Operational Notes
=================

This page documents runtime behaviors, guardrails, and troubleshooting tips for both local development and CI environments.

Busy-State Policy
-----------------

**Definition:**  
The app enters a "busy" state when long-running operations (e.g., pulling data, re-analysis) are in progress.

**Policy:**  

- Concurrent requests to ``/update_analysis`` or ``/pull_data`` while busy will return ``409 Conflict``.  

- Clients should retry after a backoff delay.

**Rationale:**  
Prevents double-execution of the same expensive pipeline.

Idempotency Strategy
--------------------

**Pulling data (/pull_data):**  

- Duplication is enforced via unique key on ``url``.  

- Re-pulling will not insert duplicates; only new entries are added.

**Analysis (/update_analysis):**  
- Re-running analysis overwrites existing ``llm_generated_program`` and ``llm_generated_university`` fields. 

- Safe to call multiple times — results are refreshed, not duplicated.

Uniqueness Keys
---------------

**Applicants table (applicants / test in CI):**  

- Primary key = ``p_id``.

- Unique key = ``url``

- Prevents inserting the same GradCafe post multiple times. 

- Other columns (e.g., ``program``, ``degree``, ``comments``) are not unique and may repeat.

Troubleshooting
---------------

Local Development
~~~~~~~~~~~~~~~~~

**Issue: PostgreSQL connection refused**  

- Ensure ``postgres`` service is running locally (``pg_ctl start``).  

- Default connection string assumes ``dbname=postgres user=postgres``. Override via environment variables if needed.

**Issue: Tests fail with NoneType in template rendering**  

- Usually indicates missing aggregate values from ``query_data``.  

- Check your fixture data includes Fall 2025 applicants and numeric fields.

**Issue: Pytest cannot find tables**  

- Make sure the ``connect_to_db`` fixture is included in integration tests.

- Table is created/dropped per test run.

CI
~~

**Issue: Database not available in GitHub Actions**  

- Confirm that the CI config spins up a ``postgres`` service container.  

- Add a wait-for-db step before running tests.

**Issue: Coverage mismatch (100% locally, lower in CI)**  

- Ensure ``pytest`` runs with the same flags in CI.  
