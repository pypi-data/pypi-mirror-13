list = ["id","444_check"," fffgggorder","*order","s*order","order:","order:s","ord::er","ord:er","spec__i666es","-Access","ACID","    Column","COMMIT","Cursor","Data","DELETE","INSERT","Isolatio___n","JOIN","Query","Row","SELECT","Table","UPDATE","date","kk-kk"," kp:yu"]



# ==['"id"', '"checked"', '"fffgggorder"', '"ordered"', '"s_order"', '"ordered"', '"order_s"', '"ord_er"', '"ord_er"', '"spec_i666es"', '"access"', '"acid"', '"columns"', '"commit"', '"cursors"', '"data"', '"deleted"', '"inserted"', '"isolatio_n"', '"joins"', '"query"', '"row"', '"selects"', '"tables"', '"update"', '"record_date"', '"kk_kk"', '"kp_yu"']
def clean_column_name(column_name):
    """Replace sql ley words with no sql key words

        Makes sure a column name is formatted correctly by removing reserved
        words, symbols, numbers, etc.
        """
    replace_columns = []
    column_name = column_name.lower().strip()
    replace_columns = {old.lower(): new.lower()
                       for old, new in replace_columns}
    column_name = replace_columns.get(column_name, column_name).strip()
    replace = [
    ("%", "percent"),
    ("&", "and"),
    ("\xb0", "degrees"),
    ("?", ""),
    ]

    replace += [(x, '') for x in (")", "\n", "\r", '"', "'")]
    replace += [(x, '_') for x in (" ", "(", "/", ".", "-", "*", ":")]
    column_name = reduce(lambda x, y: x.replace(*y), replace, column_name)

    while "__" in column_name:
        column_name = column_name.replace("__", "_")
    column_name = column_name.lstrip("0123456789_").rstrip("_")

    replace_dict ={
        "group": "grp",
        "order": "ordered",
        "check": "checked",
        "references": "refs",
        "long": "lon",
        "column": "columns",
        "cursor": "cursors",
        "delete": "deleted",
        "insert": "inserted",
        "join": "joins",
        "select": "selects",
        "table": "tables",
        "date": "record_date"
    }

    for x in (")", "\n", "\r", '"', "'"):
        replace_dict[x] = ''
    for x in (" ", "(", "/", ".", "-"):
        replace_dict[x] = '_'

    if column_name in replace_dict:
        column_name = replace_dict[column_name]

    return column_name


# updatedlist =[]
# for items in list:
#     updatedlist += ["\""+clean_column_name(items)+"\""]
# print(updatedlist)

from time import sleep
import sys

for i in range(21):
    sys.stdout.write('\r')
    # the exact output you're looking for:
    sys.stdout.write("[%-50s] %d%%" % ('#'*i*5, 5*i))
    sys.stdout.flush()
    sleep(0.25)
