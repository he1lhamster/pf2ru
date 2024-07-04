import codecs
import json
import os
import sys
import sqlite3
import aiosqlite
import csv

from sqlalchemy import select

sys.path.append(os.path.join(sys.path[0], 'pf2'))
from database import async_session_maker
from routers.converters import d_type


async def truncate_tables(table_list: list | None = None):
    if table_list is None:
        # table_list = [Action, Class_]
        table_list = [x[1] for x in d_type.values()]
    else:
        table_list = [d_type[x][1] for x in table_list]

    async with async_session_maker() as session:
        for table in table_list:
            await session.execute(table.__table__.delete())
        await session.commit()
    print('tables Truncated')


def update_csv(table_list: list):
    sqlite_db_path = f"{os.path.abspath(os.path.join(os.getcwd(), os.pardir))}\\db.db"
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    cursor = sqlite_conn.cursor()

    for table in table_list:

        # Get the column names
        cursor.execute(f"PRAGMA table_info({table})")
        headers = [col[1] for col in cursor.fetchall()]

        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()

        with open(f'{os.path.abspath(os.path.join(os.getcwd(), os.pardir))}\\csvs\\{table.__tablename__}.csv', 'w',
                  newline='', encoding='utf-8') as csv_out:
            csv_writer = csv.writer(csv_out, delimiter=';')
            csv_writer.writerow(headers)
            csv_writer.writerows(rows)

        # df = pd.read_sql_query(query, sqlite_conn)
        # df.to_csv(f'{os.path.abspath(os.path.join(os.getcwd(), os.pardir))}\\csvs\\{table}.csv', index=False, sep=';')

    sqlite_conn.close()
    print('table updated')


async def insert_tables(table_list=None):
    sqlite_db_path = f"db.db"

    async with aiosqlite.connect(sqlite_db_path) as db:
        for table in table_list:
            print(table)
            async with async_session_maker() as session:
                cursor = await db.execute(f"PRAGMA table_info({table})")
                rows = await cursor.fetchall()
                headers = [col[1] for col in rows]
                cursor = await db.execute(f"SELECT * FROM {table}")

                rows = await cursor.fetchall()
                table_model = d_type[table][1]

                for row in rows:
                    try:
                        row = {k: v for k, v in zip(headers, row)}
                        row['is_legacy'] = bool(row['is_legacy'])
                        row['id'] = int(row['id'])

                        for x in row:
                            if row[x] == 0 and x not in ['is_multiclass', 'hp', 'is_legacy',]:
                                row[x] = '0'
                            elif x == 'parent_id':
                                row[x] = int(row[x])
                            elif not row[x]:
                                row[x] = None
                            elif str(row[x]).endswith('.0'):
                                row[x] = str(row[x])[:-2]
                            elif x == 'hp' and table not in ['shield', 'hazard']:
                                row['hp'] = int(row['hp'])
                            elif x == 'hp' and table in ['shield', 'hazard']:
                                row['hp'] = str(row['hp'])
                            elif x == 'is_multiclass' and row['is_multiclass'] != 1:
                                row['is_multiclass'] = 0
                            elif x not in ['hp', 'id', 'is_legacy', 'is_multiclass']:
                                row[x] = str(row[x])

                        exist_item = await session.get(table_model, row['id'])

                        if not exist_item:
                            current_row = table_model(**row)
                            session.add(current_row)
                        else:
                            for key, value in row.items():
                                setattr(exist_item, key, value)

                    except Exception as e:
                        print(table, row['id'], x, e)
                await session.commit()
            await cursor.close()


async def create_compendium():
    comp = {}
    async with async_session_maker() as session:
        for table in d_type:
            current_model = d_type[table][1]
            temp_d = []
            all_items = await session.execute(select(current_model.id, current_model.name,
                                                     current_model.source, current_model.rus_name)
                                              )
            items = [x.__dict__ for x in all_items.scalars().all()]
            for item in items:
                temp_d.append({"id": item['id'],
                               "eng": item['name'].lower(),
                               "rus": item['rus_name'].lower(),
                               "source": item['source'],
                               })
            comp[table] = temp_d

        with codecs.open('compendium.json', 'w', encoding='utf-8') as j_out:
            json.dump(comp, j_out, ensure_ascii=False)
