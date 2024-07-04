import sqlite3
import argparse

class FoodTable:
    """
    This class represents a table in the food database.
    """
    def __init__(self, a_table_name, a_col_data):
        self.table_name = a_table_name
        self.col_data = a_col_data
        self.last_id = 0

    def create_table(self, cursor, foreign_key=None):
        """
        Creates a table in the database.
        :param cursor: A database cursor.
        :param foreign_key: A dictionary containing foreign key information.
        """
        create_table_query = f"CREATE TABLE IF NOT EXISTS {self.table_name} ("
        create_columns_query = ""
        for col_name, col_type in self.col_data.items():
            create_columns_query += f"{col_name} {col_type},"
        foreign_key_query = ""
        if foreign_key:
            for foreign_key_col, foreign_table_data in foreign_key.items():
                foreign_key_query += f""", FOREIGN KEY ({foreign_key_col})
                    REFERENCES {foreign_table_data[0]}({foreign_table_data[1]})
                    ON DELETE SET NULL ON UPDATE CASCADE
                """
        full_query = create_table_query + create_columns_query[:-1] + foreign_key_query + ')'
        cursor.execute(full_query)

    def insert_a_row(self, cursor, a_row):
        """
        Inserts a row into the table.
        :param a_row: the row.
        :param cursor: the cursor.
        """
        insert_query = f"""INSERT OR IGNORE INTO {self.table_name}
            VALUES (NULL, {','.join(['?' for _ in range(len(a_row))])})
        """
        cursor.execute(insert_query, a_row)
        self.last_id = cursor.lastrowid

    def select_id(self, cursor, a_name):
        """
        Selects the id of a row in the table.
        :param a_name: the name of the row.
        :param cursor: the cursor.
        :return: the id of the row.
        """
        select_query = f"""
            SELECT {self.table_name[:-1]}_id FROM {self.table_name}
            WHERE {self.table_name[:-1]}_name LIKE (?)
        """
        cursor.execute(select_query, (a_name,))
        return cursor.fetchall()

    def select_name(self, cursor, an_id):
        """
        Selects the name of a row in the table.
        :param an_id: the id of the row.
        :param cursor: the cursor.
        :return: the name of the row.
        """
        select_query = f"""
            SELECT {self.table_name[:-1]}_name FROM {self.table_name}
            WHERE {self.table_name[:-1]}_id = (?)
        """
        cursor.execute(select_query, an_id)
        return cursor.fetchall()


class FoodBlog:
    """
    This class represents the food blog application.
    """
    def __init__(self, a_db_name):
        self.conn = sqlite3.connect(a_db_name)
        self.cur = self.conn.cursor()
        self.cur.execute("PRAGMA foreign_keys = 1;")

    def __del__(self):
        self.conn.close()

    def create_table(self, a_table_name, col_name_type: dict, foreign_key=None):
        """
        Creates a table in the database.
        :param a_table_name: the name of the table.
        :param col_name_type: the name of the columns.
        :param foreign_key: the foreign key.
        :return: the table.
        """
        the_table = FoodTable(a_table_name, col_name_type)
        the_table.create_table(self.cur, foreign_key)
        self.conn.commit()
        return the_table

    def populate_table(self, a_table, a_data):
        """
        Populates a table with data.
        :param a_table: the table.
        :param a_data: a list of rows.
        """
        for row in a_data:
            a_table.insert_a_row(self.cur, row)
        self.conn.commit()

    def get_id(self, a_table, a_name):
        """
        Gets the id of a row in the table.
        :param a_table: the table.
        :param a_name: the name of the row.
        :return: the id of the row.
        """
        return a_table.select_id(self.cur, a_name)

    def find_recipe(self, a_table_name, id_col_name, ids_list):
        """
        Finds recipes based on the given ids.
        :param a_table_name: the table name.
        :param ids_list: a list of ids.
        :param id_col_name: the id column name.
        :return: a list of recipes.
        """
        recipes_set_list = list()
        for ids in ids_list:
            select_query = f"""
                SELECT recipe_id FROM {a_table_name}
                WHERE {id_col_name} IN ({ids})
            """
            self.cur.execute(select_query)
            recipes_set_list.append(set(self.cur.fetchall()))

        return recipes_set_list

    def get_name(self, a_table, an_id):
        """
        Gets the name of a recipe in the table.
        :param an_id: the id of the row.
        :param a_table: the table.
        :return: the name of the recipe.
        """
        return a_table.select_name(self.cur, an_id)[0][0]


def add_ingredients(a_recipe_id, ingredient_table, measure_table):
    """
    Adds an ingredient to a recipe.
    :param a_recipe_id: the id of the recipe
    :param ingredient_table: the ingredient table
    :param measure_table: the measure table
    :return:
    """
    while True:
        ingredients = input("Input quantity of ingredient <press enter to stop>:")
        if ingredients == '':
            return

        if len(ingredients.split()) == 2:
            quantity, ingredient = ingredients.split()
            measure = ''
        elif len(ingredients.split()) == 3:
            quantity, measure, ingredient = ingredients.split()

        ingredient_id = app.get_id(ingredient_table, '%' + ingredient + '%')
        if not ingredient_id or len(ingredient_id) > 1:
            print("The ingredient is not conclusive!")
            continue
        else:
            ingredient_id = ingredient_id[0]

        measure_id = app.get_id(measure_table, measure + '%' if measure else measure)
        if not measure_id or len(measure_id) > 1:
            print("The measure is not conclusive!")
            continue
        else:
            measure_id = measure_id[0]

        app.populate_table(quantity_table, ((*measure_id, *ingredient_id, quantity, *a_recipe_id),))


def find_recipes(given_ingredients=None, given_meals=None):
    """
    Finds recipes based on the given ingredients and meals.
    :param given_ingredients:  the given ingredients
    :param given_meals:  the given meals
    :return:
    """
    recipes_with_ingredients = set()
    if given_ingredients:
        print("1")
        given_ingredients_list = given_ingredients.split(',')
        ingredients_ids = list()
        for ingredient in given_ingredients_list:
            ingr_id = app.get_id(tables_list[1], ingredient)
            if ingr_id:
                ingredients_ids.append(*ingr_id[0])
            else:
                print("There are no such recipes in the database.")
                return None

        recipes_with_ingredients = set.union(*app.find_recipe('quantity', 'ingredient_id', ingredients_ids))

    recipes_with_meals = set()
    if given_meals:
        print("2")
        given_meals_list = given_meals.split(',')
        meals_ids = list()
        for meal in given_meals_list:
            meal_id = app.get_id(tables_list[0], meal)
            if meal_id:
                meals_ids.append(*meal_id[0])
            else:
                print("There are no such recipes in the database.")
                return None

        recipes_with_meals = set.union(*app.find_recipe('serve', 'meal_id', meals_ids))

    result_recipes  = set.intersection(recipes_with_ingredients, recipes_with_meals)
    print(recipes_with_ingredients)
    print(recipes_with_meals)
    print(result_recipes)
    if result_recipes:
        print("Recipes selected for you:", ', '.join([app.get_name(recipe_table, a_recipe_id)
                                                      for a_recipe_id in result_recipes]))
    else:
        print("There are no such recipes in the database.")

    return None


if __name__ == '__main__':
    tables = {"meals": {"meal_id": "INTEGER PRIMARY KEY", "meal_name": "TEXT UNIQUE NOT NULL"},
              "ingredients": {"ingredient_id": "INTEGER PRIMARY KEY", "ingredient_name": "TEXT UNIQUE NOT NULL"},
              "measures": {"measure_id": "INTEGER PRIMARY KEY", "measure_name": "TEXT UNIQUE"}}
    data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
            "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
            "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}

    parser = argparse.ArgumentParser()
    parser.add_argument('db_name', type=str)
    parser.add_argument('--ingredients', type=str)
    parser.add_argument('--meals', type=str)

    args = parser.parse_args()
    db_name = args.db_name
    app = FoodBlog(db_name)

    tables_list = []
    for table_name, col_data in tables.items():
        table = app.create_table(table_name, col_data)
        app.populate_table(table, [(row,) for row in data[table_name]])
        tables_list.append(table)

    recipe_table = app.create_table('recipes', {"recipe_id": "INTEGER PRIMARY KEY",
                                                "recipe_name": "TEXT NOT NULL",
                                                "recipe_description": "TEXT"})

    serve_table = app.create_table('serve',
                                   {"serve_id": "INTEGER PRIMARY KEY",
                                    "recipe_id": "INTEGER NOT NULL",
                                    "meal_id": "INTEGER NOT NULL"},
                                   {"recipe_id": ["recipes", "recipe_id"],
                                    "meal_id": ["meals", "meal_id"]})

    quantity_table = app.create_table('quantity',
                                      {"quantity_id": "INTEGER PRIMARY KEY",
                                       "measure_id": "INTEGER NOT NULL",
                                       "ingredient_id": "INTEGER NOT NULL",
                                       "quantity": "INTEGER NOT NULL",
                                       "recipe_id": "INTEGER NOT NULL"},
                                      {"measure_id": ["measures", "measure_id"],
                                       "ingredient_id": ["ingredients", "ingredient_id"],
                                       "recipe_id": ["recipes", "recipe_id"]})

    if args.ingredients or args.meals:
        find_recipes(args.ingredients, args.meals)
    else:
        while True:
            print("Pass the empty recipe name to exit.")
            recipe_name = input("Recipe name:")
            if recipe_name == '':
                break
            else:
                recipe_description = input("Recipe description:")
                app.populate_table(recipe_table, ((recipe_name, recipe_description),))
                print("1) breakfast  2) brunch  3) lunch  4) supper")
                serve_time = input("When the dish can be served:").split()
                recipe_id = app.get_id(recipe_table, recipe_name)[-1]
                app.populate_table(serve_table, tuple((*recipe_id, int(meal_id)) for meal_id in serve_time))
                add_ingredients(recipe_id, tables_list[1], tables_list[2])

    app.__del__()