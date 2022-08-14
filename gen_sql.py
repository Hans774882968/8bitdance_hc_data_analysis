import sqlite3

create_table = '''
CREATE TABLE HC
    (ID VARCHAR(20) PRIMARY KEY NOT NULL,
    JOB VARCHAR(80) NOT NULL,
    CITY VARCHAR(10) NOT NULL,
    HC INT NOT NULL,
    MIN_SALARY INT,
    MAX_SALARY INT);'''

insert_data = '''
INSERT INTO HC (ID, JOB, CITY, HC, MIN_SALARY, MAX_SALARY) \
    VALUES (?, ?, ?, ?, ?, ?)
'''


def get_excel_data():
    import xlrd
    work_book = xlrd.open_workbook('字节跳动hc.xlsx')
    sheet = work_book.sheet_by_index(0)
    data = [sheet.row_values(row) for row in range(sheet.nrows)]
    return data[1:]


if __name__ == '__main__':
    conn = sqlite3.connect('字节跳动hc.db')
    c = conn.cursor()
    c.execute(create_table)
    data = get_excel_data()
    for row in data:
        c.execute(insert_data, (row[2], row[0], row[1], *map(int, row[3:])))
    conn.commit()
    conn.close()
