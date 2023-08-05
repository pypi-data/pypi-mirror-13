from django.db.migrations.operations.base import Operation


class CreateCompactIndex(Operation):
    '''
    An operation that creates a BTree GIN index. This kind of index is useful
    when the column contains many repeating values, since it results in a much
    smaller index size relative to a regular BTree index.
    See http://www.postgresql.org/docs/9.4/static/btree-gin.html
    See http://leopard.in.ua/2015/04/13/postgresql-indexes/
    '''

    def __init__(self, model_name, field_name, index_name=None):
        self.model_name = model_name
        self.field_name = field_name
        self.index_name = index_name or '%s_%s_btree_gin' % (model_name.lower(), field_name)

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            schema_editor.execute('CREATE EXTENSION IF NOT EXISTS btree_gin')
            schema_editor.execute('CREATE INDEX "%s" ON "%s" USING gin ("%s")' %
                                  (self.index_name, model._meta.db_table, self.field_name))

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            schema_editor.execute('DROP INDEX "%s"' % (self.index_name))

    def describe(self):
        return 'Create BTree GIN index on %s.%s' % (self.model_name, self.index_name)

    def references_model(self, name, app_label=None):
        return name.lower() == self.model_name.lower()

    def references_field(self, model_name, name, app_label=None):
        return self.references_model(model_name, app_label) and name.lower() == self.field_name.lower()


class CreateTrigramIndex(Operation):
    '''
    An operation that creates a trigram index. This kind of index is useful
    for substring matching and fuzzy searches.
    See http://www.postgresql.org/docs/9.4/static/pgtrgm.html
    '''

    def __init__(self, model_name, field_name, index_name=None):
        self.model_name = model_name
        self.field_name = field_name
        self.index_name = index_name or '%s_%s_trgm' % (model_name.lower(), field_name)

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            schema_editor.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')
            schema_editor.execute('CREATE INDEX "%s" ON "%s" USING gin ("%s" gin_trgm_ops)' %
                                  (self.index_name, model._meta.db_table, self.field_name))

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            schema_editor.execute('DROP INDEX "%s"' % (self.index_name))

    def describe(self):
        return 'Create trigram index on %s.%s' % (self.model_name, self.index_name)

    def references_model(self, name, app_label=None):
        return name.lower() == self.model_name.lower()

    def references_field(self, model_name, name, app_label=None):
        return self.references_model(model_name, app_label) and name.lower() == self.field_name.lower()


class SetStatistics(Operation):
    '''
    An operation that sets the statistics target on a column. This controls how much
    information about the column's values will be available for the query planner.
    See http://www.postgresql.org/docs/9.4/static/planner-stats.html
    '''

    def __init__(self, model_name, field_name, target=1000):
        self.model_name = model_name
        self.field_name = field_name
        self.target = target

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            schema_editor.execute('ALTER TABLE %s ALTER COLUMN %s SET STATISTICS %d' %
                                  (model._meta.db_table, self.field_name, self.target))

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            schema_editor.execute('ALTER TABLE %s ALTER COLUMN %s SET STATISTICS 100' %
                                  (model._meta.db_table, self.field_name))

    def describe(self):
        return 'Set statistics target on %s.%s to %d' % (self.model_name, self.field_name, self.target)

    def references_model(self, name, app_label=None):
        return name.lower() == self.model_name.lower()

    def references_field(self, model_name, name, app_label=None):
        return self.references_model(model_name, app_label) and name.lower() == self.field_name.lower()
