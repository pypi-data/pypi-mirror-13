# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http:# mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from copy import copy
from itertools import product

from pyLibrary.meta import use_settings, DataClass
from pyLibrary.queries import qb
from pyLibrary.queries.query import Query
from pyLibrary.debugs.logs import Log
from pyLibrary.dot.dicts import Dict
from pyLibrary.dot import coalesce, set_default, Null, literal_field, listwrap, split_field, join_field
from pyLibrary.dot import wrap
from pyLibrary.thread.threads import Queue, Thread
from pyLibrary.times.dates import Date
from pyLibrary.times.durations import HOUR, MINUTE
from pyLibrary.times.timer import Timer


_elasticsearch = None

ENABLE_META_SCAN = False
DEBUG = True
TOO_OLD = 2*HOUR
singlton = None


class FromESMetadata(object):
    """
    QUERY THE METADATA
    """

    def __new__(cls, *args, **kwargs):
        global singlton
        if singlton:
            return singlton
        else:
            singlton = object.__new__(cls)
            return singlton

    @use_settings
    def __init__(self, host, index, alias=None, name=None, port=9200, settings=None):
        global _elasticsearch
        if hasattr(self, "settings"):
            return

        from pyLibrary.queries.containers.lists import ListContainer
        from pyLibrary.env import elasticsearch as _elasticsearch

        self.settings = settings
        self.default_name = coalesce(name, alias, index)
        self.default_es = _elasticsearch.Cluster(settings=settings)
        self.todo = Queue("refresh metadata", max=100000, unique=True)

        table_columns = metadata_tables()
        column_columns = metadata_columns()
        self.tables = ListContainer("meta.tables", [], wrap({c.name: c for c in table_columns}))
        self.columns = ListContainer("meta.columns", [], wrap({c.name: c for c in column_columns}))
        self.columns.insert(column_columns)
        self.columns.insert(table_columns)
        # TODO: fix monitor so it does not bring down ES
        if ENABLE_META_SCAN:
            self.worker = Thread.run("refresh metadata", self.monitor)
        else:
            self.worker = Thread.run("refresh metadata", self.not_monitor)
        return

    @property
    def query_path(self):
        return None

    @property
    def url(self):
        return self.default_es.path + "/" + self.default_name.replace(".", "/")

    def get_table(self, table_name):
        with self.tables.locker:
            return self.tables.query({"where": {"eq": {"name": table_name}}})

    def upsert_column(self, c):
        existing_columns = filter(lambda r: r.table == c.table and r.abs_name == c.abs_name, self.columns.data)
        if not existing_columns:
            self.columns.add(c)
            cols = filter(lambda r: r.table == "meta.columns", self.columns.data)
            for cc in cols:
                cc.partitions = cc.cardinality = cc.last_updated = None
            self.todo.add(c)
            self.todo.extend(cols)
        else:
            set_default(existing_columns[0], c)
            self.todo.add(existing_columns[0])

            # TEST CONSISTENCY
            for c, d in product(list(self.todo.queue), list(self.todo.queue)):
                if c.abs_name==d.abs_name and c.table==d.table and c!=d:
                    Log.error("")


    def _get_columns(self, table=None):
        # TODO: HANDLE MORE THEN ONE ES, MAP TABLE SHORT_NAME TO ES INSTANCE
        alias_done = set()
        index = split_field(table)[0]
        query_path = split_field(table)[1:]
        metadata = self.default_es.get_metadata(index=index)
        for index, meta in qb.sort(metadata.indices.items(), {"value": 0, "sort": -1}):
            for _, properties in meta.mappings.items():
                columns = _elasticsearch.parse_properties(index, None, properties.properties)
                columns = columns.filter(lambda r: not r.abs_name.startswith("other."))  #TODO: REMOVE WHEN jobs PROPERTY EXPLOSION IS CONTAINED
                with Timer("upserting {{num}} columns", {"num":len(columns)}, debug=DEBUG):
                    with self.columns.locker:
                        for c in columns:
                            # ABSOLUTE
                            c.table = join_field([index]+query_path)
                            self.upsert_column(c)

                            for alias in meta.aliases:
                                # ONLY THE LATEST ALIAS IS CHOSEN TO GET COLUMNS
                                if alias in alias_done:
                                    continue
                                alias_done.add(alias)
                                c = copy(c)
                                c.table = join_field([alias]+query_path)
                                self.upsert_column(c)

    def query(self, _query):
        return self.columns.query(Query(set_default(
            {
                "from": self.columns,
                "sort": ["table", "name"]
            },
            _query.as_dict()
        )))

    def get_columns(self, table):
        """
        RETURN METADATA COLUMNS
        """
        with self.columns.locker:
            columns = qb.sort(filter(lambda r: r.table == table, self.columns.data), "name")
            if columns:
                return columns

        self._get_columns(table=table)
        with self.columns.locker:
            columns = qb.sort(filter(lambda r: r.table == table, self.columns.data), "name")
            if columns:
                return columns

        # self._get_columns(table=table)
        Log.error("no columns for {{table}}", table=table)

    def _update_cardinality(self, c):
        """
        QUERY ES TO FIND CARDINALITY AND PARTITIONS FOR A SIMPLE COLUMN
        """
        if c.type in ["object", "nested"]:
            Log.error("not supported")
        try:
            if c.table == "meta.columns":
                with self.columns.locker:
                    partitions = qb.sort([g[c.abs_name] for g, _ in qb.groupby(self.columns, c.abs_name) if g[c.abs_name] != None])
                    self.columns.update({
                        "set": {
                            "partitions": partitions,
                            "count": len(self.columns),
                            "cardinality": len(partitions),
                            "last_updated": Date.now()
                        },
                        "where": {"eq": {"table": c.table, "abs_name": c.abs_name}}
                    })
                return
            if c.table == "meta.tables":
                with self.columns.locker:
                    partitions = qb.sort([g[c.abs_name] for g, _ in qb.groupby(self.tables, c.abs_name) if g[c.abs_name] != None])
                    self.columns.update({
                        "set": {
                            "partitions": partitions,
                            "count": len(self.tables),
                            "cardinality": len(partitions),
                            "last_updated": Date.now()
                        },
                        "where": {"eq": {"table": c.table, "name": c.name}}
                    })
                return

            es_index = c.table.split(".")[0]
            result = self.default_es.post("/"+es_index+"/_search", data={
                "aggs": {c.name: _counting_query(c)},
                "size": 0
            })
            r = result.aggregations.values()[0]
            count = result.hits.total
            cardinality = coalesce(r.value, r._nested.value)
            if cardinality == None:
                Log.error("logic error")

            query = Dict(size=0)
            if c.type in ["object", "nested"]:
                Log.note("{{field}} has {{num}} parts", field=c.name, num=cardinality)
                with self.columns.locker:
                    self.columns.update({
                        "set": {
                            "count": count,
                            "cardinality": cardinality,
                            "last_updated": Date.now()
                        },
                        "clear": ["partitions"],
                        "where": {"eq": {"table": c.table, "name": c.name}}
                    })
                return
            elif cardinality > 1000 or (count >= 30 and cardinality == count) or (count >= 1000 and cardinality / count > 0.99):
                Log.note("{{field}} has {{num}} parts", field=c.name, num=cardinality)
                with self.columns.locker:
                    self.columns.update({
                        "set": {
                            "count": count,
                            "cardinality": cardinality,
                            "last_updated": Date.now()
                        },
                        "clear": ["partitions"],
                        "where": {"eq": {"table": c.table, "name": c.name}}
                    })
                return
            elif c.type in _elasticsearch.ES_NUMERIC_TYPES and cardinality > 30:
                Log.note("{{field}} has {{num}} parts", field=c.name, num=cardinality)
                with self.columns.locker:
                    self.columns.update({
                        "set": {
                            "count": count,
                            "cardinality": cardinality,
                            "last_updated": Date.now()
                        },
                        "clear": ["partitions"],
                        "where": {"eq": {"table": c.table, "name": c.name}}
                    })
                return
            elif c.nested_path:
                query.aggs[literal_field(c.name)] = {
                    "nested": {"path": listwrap(c.nested_path)[0]},
                    "aggs": {"_nested": {"terms": {"field": c.abs_name, "size": 0}}}
                }
            else:
                query.aggs[literal_field(c.name)] = {"terms": {"field": c.abs_name, "size": 0}}

            result = self.default_es.post("/"+es_index+"/_search", data=query)

            aggs = result.aggregations.values()[0]
            if aggs._nested:
                parts = qb.sort(aggs._nested.buckets.key)
            else:
                parts = qb.sort(aggs.buckets.key)

            Log.note("{{field}} has {{parts}}", field=c.name, parts=parts)
            with self.columns.locker:
                self.columns.update({
                    "set": {
                        "count": count,
                        "cardinality": cardinality,
                        "partitions": parts,
                        "last_updated": Date.now()
                    },
                    "where": {"eq": {"table": c.table, "abs_name": c.abs_name}}
                })
        except Exception, e:
            if "IndexMissingException" in e and c.table.startswith("testing"):
                Log.alert("{{col.table}} does not exist", col=c)
            else:
                self.columns.update({
                    "set": {
                        "last_updated": Date.now()
                    },
                    "clear":[
                        "count",
                        "cardinality",
                        "partitions",
                    ],
                    "where": {"eq": {"table": c.table, "abs_name": c.abs_name}}
                })
                Log.warning("Could not get {{col.table}}.{{col.abs_name}} info", col=c, cause=e)

    def monitor(self, please_stop):
        please_stop.on_go(lambda: self.todo.add(Thread.STOP))
        while not please_stop:
            try:
                if not self.todo:
                    with self.columns.locker:
                        old_columns = filter(
                            lambda c: (c.last_updated == None or c.last_updated < Date.now()-TOO_OLD) and c.type not in ["object", "nested"],
                            self.columns
                        )
                        if old_columns:
                            self.todo.extend(old_columns)
                            # TEST CONSISTENCY
                            for c, d in product(list(self.todo.queue), list(self.todo.queue)):
                                if c.abs_name==d.abs_name and c.table==d.table and c!=d:
                                    Log.error("")


                        else:
                            Log.note("no more metatdata to update")

                column = self.todo.pop(timeout=10*MINUTE)
                if column:
                    if column.type in ["object", "nested"]:
                        continue
                    elif column.last_updated >= Date.now()-TOO_OLD:
                        continue
                    try:
                        self._update_cardinality(column)
                        Log.note("updated {{column.name}}", column=column)
                    except Exception, e:
                        Log.warning("problem getting cardinality for  {{column.name}}", column=column, cause=e)
            except Exception, e:
                Log.warning("problem in cardinality monitor", cause=e)

    def not_monitor(self, please_stop):
        Log.warning("metadata scan has been disabled")
        please_stop.on_go(lambda: self.todo.add(Thread.STOP))
        while not please_stop:
            c = self.todo.pop()
            if c == Thread.STOP:
                break
            with self.columns.locker:
                self.columns.update({
                    "set": {
                        "last_updated": Date.now()
                    },
                    "clear":[
                        "count",
                        "cardinality",
                        "partitions",
                    ],
                    "where": {"eq": {"table": c.table, "abs_name": c.abs_name}}
                })
            Log.note("Could not get {{col.table}}.{{col.abs_name}} info", col=c)


def _counting_query(c):
    if c.nested_path:
        return {
            "nested": {
                "path": listwrap(c.nested_path)[0]  # FIRST ONE IS LONGEST
            },
            "aggs": {
                "_nested": {"cardinality": {
                    "field": c.name,
                    "precision_threshold": 10 if c.type in _elasticsearch.ES_NUMERIC_TYPES else 100
                }}
            }
        }
    else:
        return {"cardinality": {
            "field": c.name
        }}


def metadata_columns():
    return wrap(
        [
            Column(
                table="meta.columns",
                name=c,
                abs_name=c,
                type="string",
                nested_path=Null,
            )
            for c in [
                "name",
                "type",
                "nested_path",
                "relative",
                "abs_name",
                "table"
            ]
        ] + [
            Column(
                table="meta.columns",
                name=c,
                abs_name=c,
                type="object",
                nested_path=Null,
            )
            for c in [
                "domain",
                "partitions"
            ]
        ] + [
            Column(
                table="meta.columns",
                name=c,
                abs_name=c,
                type="long",
                nested_path=Null,
            )
            for c in [
                "count",
                "cardinality"
            ]
        ] + [
            Column(
                table="meta.columns",
                name="last_updated",
                abs_name="last_updated",
                type="time",
                nested_path=Null,
            )
        ]
    )

def metadata_tables():
    return wrap(
        [
            Column(
                table="meta.tables",
                name=c,
                abs_name=c,
                type="string",
                nested_path=Null
            )
            for c in [
                "name",
                "url",
                "query_path"
            ]
        ]
    )





class Table(DataClass("Table", [
    "name",
    "url",
    "query_path"
])):
    @property
    def columns(self):
        return FromESMetadata.singlton.get_columns(table=self.name)


Column = DataClass(
    "Column",
    [
        "name",
        "abs_name",
        "table",
        "type",
        {"name": "useSource", "default": False},
        {"name": "nested_path", "nulls": True},  # AN ARRAY OF PATHS (FROM DEEPEST TO SHALLOWEST) INDICATING THE JSON SUB-ARRAYS
        {"name": "relative", "nulls": True},
        {"name": "count", "nulls": True},
        {"name": "cardinality", "nulls": True},
        {"name": "partitions", "nulls": True},
        {"name": "last_updated", "nulls": True}
    ]
)



