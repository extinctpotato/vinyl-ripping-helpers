from vriphelper.term import ReorderableTable

def _reorderable_star_wars_table():
    t = ReorderableTable(
            title="Star Wars Movies",
            columns=["Released", "Title", "Box Office"],
            rows=[
                ["Dec 20, 2019", "Star Wars: The Rise of Skywalker", "$952,110,690"],
                ["May 25, 2018", "Solo: A Star Wars Story", "$393,151,347"],
                ["Dec 15, 2017", "Star Wars Ep. V111: The Last Jedi", "$1,332,539,889"],
                ["Dec 16, 2016", "Rogue One: A Star Wars Story", "$1,332,439,889"],
                ]
            )
    t.inquire()
    return t.rows

def sw_table_demo():
    print('\033[1m', end='') # Bold
    print("♖ To grab an element, press space and move the element with arrows.")
    print("♜ Press CTRL-C once you're with reordering the elements.")
    print('\033[0m', end='') # Reset
    for idx, row in enumerate(_reorderable_star_wars_table()):
        for element in row:
            print(f"Row {idx}: {element}")

# For now we only have one demo
if __name__ == '__main__':
    sw_table_demo()
