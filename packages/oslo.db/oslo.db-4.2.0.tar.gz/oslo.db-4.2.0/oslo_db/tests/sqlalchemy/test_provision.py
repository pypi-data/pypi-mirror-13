#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslotest import base as oslo_test_base
from sqlalchemy import inspect
from sqlalchemy import schema
from sqlalchemy import types

from oslo_db import exception
from oslo_db.sqlalchemy import provision
from oslo_db.sqlalchemy import test_base


class DropAllObjectsTest(test_base.DbTestCase):

    def setUp(self):
        super(DropAllObjectsTest, self).setUp()

        self.metadata = metadata = schema.MetaData()
        schema.Table(
            'a', metadata,
            schema.Column('id', types.Integer, primary_key=True),
            mysql_engine='InnoDB'
        )
        schema.Table(
            'b', metadata,
            schema.Column('id', types.Integer, primary_key=True),
            schema.Column('a_id', types.Integer, schema.ForeignKey('a.id')),
            mysql_engine='InnoDB'
        )
        schema.Table(
            'c', metadata,
            schema.Column('id', types.Integer, primary_key=True),
            schema.Column('b_id', types.Integer, schema.ForeignKey('b.id')),
            schema.Column(
                'd_id', types.Integer,
                schema.ForeignKey('d.id', use_alter=True, name='c_d_fk')),
            mysql_engine='InnoDB'
        )
        schema.Table(
            'd', metadata,
            schema.Column('id', types.Integer, primary_key=True),
            schema.Column('c_id', types.Integer, schema.ForeignKey('c.id')),
            mysql_engine='InnoDB'
        )

        metadata.create_all(self.engine, checkfirst=False)
        # will drop nothing if the test worked
        self.addCleanup(metadata.drop_all, self.engine, checkfirst=True)

    def test_drop_all(self):
        insp = inspect(self.engine)
        self.assertEqual(
            set(['a', 'b', 'c', 'd']),
            set(insp.get_table_names())
        )

        self.db.backend.drop_all_objects(self.engine)

        insp = inspect(self.engine)
        self.assertEqual(
            [],
            insp.get_table_names()
        )


class MySQLDropAllObjectsTest(
        DropAllObjectsTest, test_base.MySQLOpportunisticTestCase):
    pass


class PostgreSQLDropAllObjectsTest(
        DropAllObjectsTest, test_base.PostgreSQLOpportunisticTestCase):
    pass


class RetainSchemaTest(oslo_test_base.BaseTestCase):
    DRIVER = "sqlite"

    def setUp(self):
        super(RetainSchemaTest, self).setUp()

        metadata = schema.MetaData()
        self.test_table = schema.Table(
            'test_table', metadata,
            schema.Column('x', types.Integer),
            schema.Column('y', types.Integer),
            mysql_engine='InnoDB'
        )

        def gen_schema(engine):
            metadata.create_all(engine, checkfirst=False)
        self._gen_schema = gen_schema

    def test_once(self):
        self._run_test()

    def test_twice(self):
        self._run_test()

    def _run_test(self):
        try:
            database_resource = provision.DatabaseResource(self.DRIVER)
        except exception.BackendNotAvailable:
            self.skip("database not available")

        schema_resource = provision.SchemaResource(
            database_resource, self._gen_schema)
        transaction_resource = provision.TransactionResource(
            database_resource, schema_resource)

        engine = transaction_resource.getResource()

        with engine.connect() as conn:
            rows = conn.execute(self.test_table.select())
            self.assertEqual(rows.fetchall(), [])

            trans = conn.begin()
            conn.execute(
                self.test_table.insert(),
                {"x": 1, "y": 2}
            )
            trans.rollback()

            rows = conn.execute(self.test_table.select())
            self.assertEqual(rows.fetchall(), [])

            trans = conn.begin()
            conn.execute(
                self.test_table.insert(),
                {"x": 2, "y": 3}
            )
            trans.commit()

            rows = conn.execute(self.test_table.select())
            self.assertEqual(rows.fetchall(), [(2, 3)])

        transaction_resource.finishedWith(engine)


class MySQLRetainSchemaTest(RetainSchemaTest):
    DRIVER = "mysql"


class PostgresqlRetainSchemaTest(RetainSchemaTest):
    DRIVER = "postgresql"
