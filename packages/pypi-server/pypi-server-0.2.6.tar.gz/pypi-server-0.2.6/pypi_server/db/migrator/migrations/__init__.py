# encoding: utf-8
from pypi_server.db.migrator.migrations import create_tables
from pypi_server.db.migrator.migrations import create_default_user
from pypi_server.db.migrator.migrations import create_package_tables
from pypi_server.db.migrator.migrations import packagefile_add_url_and_fetched
from pypi_server.db.migrator.migrations import packagefile_basename_unique
from pypi_server.db.migrator.migrations import packageversion_license_textfield
