# This file describes how tests are organized in the project

## Common fixtures
- ```_database_container_instance``` - creates PostgreSQL Docker container for tests(Optional)
- ```_setup_database``` - removes all tables from test database
- ```_migrate_database``` - applies Alembic migrations for the empty database
- ```_copy_database``` - copies database from the template
- ```test_db``` - create connection to database
- ```test_app``` - creates test FastAPI application
- ```unauthenticated_client``` - builds database and create unauthenticated test client
- ```test_client``` - builds database and create authenticated test client