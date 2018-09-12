import json
import os
from operator import itemgetter
from google.cloud import spanner

from utils.utils import GPSUtils
from utils.utils import lmap 

class Base:

    def __init__(self, project, instance_id, database_id, table_name, defaults):
        self.s_client = spanner.Client(project=project)
        self.instance = self.s_client.instance(instance_id)
        self.database = self.instance.database(database_id)        
        self.table_name = table_name
        self.defaults = defaults
    
    def get_insert_rows(self, data):
        def get_val(col_type, row):
            k, t = col_type[0], col_type[1]
            if k in row: return [col_type[2](token) for token in row[k].split(' ')] if t == list else t(row[k])
            elif k in self.defaults: return t(self.defaults[k])
            else: return t()
        
        return lmap(
            lambda row : lmap(
                lambda col: get_val(col, row),
                self.cols
            ),
            data
        )

    def get_select_rows(self, fields):
        sql = 'SELECT %s FROM %s' % (','.join(fields), self.table_name)
        if self.defaults:            
            sql +=  ' WHERE %s' % (' AND '.join([str(k) + '=\'' + str(v) + '\'' for (k, v) in self.defaults.items()]))

        print(sql)

        with self.database.snapshot() as snapshot:
            return snapshot.execute_sql(sql)
            
    def insert_rows(self, data):
        key_cols = list(map(itemgetter(0), self.cols))
        rows = self.get_insert_rows(data)
        views = [row[5] for row in rows]
        if not len(rows):
            return
        
        with self.database.batch() as batch:
            batch.insert(table=self.table_name, columns=key_cols, values=rows)    

