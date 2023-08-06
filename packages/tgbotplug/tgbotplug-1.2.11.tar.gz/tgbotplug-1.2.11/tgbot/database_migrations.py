from playhouse.migrate import SchemaMigrator, migrate as pmigrate


def migrate(db):
    migrator = SchemaMigrator.from_database(db)
    from database import model_factory
    models = model_factory(db)

    migrate_001(migrator, models)


def migrate_001(migrator, models):
    pmigrate(
        # Make `last_name` allow NULL values.
        migrator.drop_not_null('user', 'last_name'),
        # Add username field
        migrator.add_column('user', 'username', models.User.username),
    )
