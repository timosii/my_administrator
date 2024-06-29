from app.database.insert_dicts.insert_dicts import DictsInsert

# накатить алембик сначала
DictsInsert().insert_dicts_to_db()
# DictsUpdate().update_dicts_to_db()
# asyncio.get_event_loop().run_until_complete(clear_data())
# asyncio.get_event_loop().run_until_complete(insert_data_user())
# asyncio.run(insert_data_user())

# drop table dicts.mos , dicts.filials , dicts.problems , dicts.violations , dicts.zones, "data"."check" , data."user" , data.violation_found cascade;
