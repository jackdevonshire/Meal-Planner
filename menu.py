from database import Category, UnitType, Recipe, Ingredient
from prettytable import PrettyTable
import os
import time

def get_menu_option():
    option = input("==> ")
    if option == "":
        return -1

    return int(option)

def get_menu_option_float():
    option = input("==> ")
    if option == "":
        return -1

    return float(option)
def main_menu():
    os.system('cls' if os.name == 'nt' else 'clear')

    print("=== Main Menu ===")
    print("1. Recipe Manager ")
    print("2. Ingredient Manager")
    print("3. Shopping List Generator - TODO")

    option = get_menu_option()
    if option == 1:
        return recipe_manager_menu()
    elif option == 2:
        return ingredient_manager_menu()
    elif option == 3:
        return None # TODO
    else:
        return main_menu()

def ingredient_manager_menu(ingredients=None):
    os.system('cls' if os.name == 'nt' else 'clear')

    print("Ingredients")
    if not ingredients:
        ingredients = Ingredient().get_all_ingredients()

    table = PrettyTable()
    table.field_names = ["Ingredient ID", "Name", "Unit Type", "Category"]
    for ingredient in ingredients:
        table.add_row([
            ingredient.id,
            ingredient.name,
            f"{UnitType(ingredient.unit_type).name}",
            f"{Category(ingredient.category_type).name}",
        ])

    print(table)

    print("\n=== Ingredients Manager Menu ===")
    print("1. Add Ingredient")
    print("2. Remove Ingredient")
    print("3. Main Menu")

    option = input("==> ")
    try:
        option = int(option)
        if option == 1:
            return add_ingredient_menu()
        elif option == 2:
            return remove_ingredient_menu()
        else:
            return main_menu()
    except:
        query = option
        results = Ingredient().search(query)
        ingredient_manager_menu(results)




def add_ingredient_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=== Add Ingredient ===")
    ingredient_name = input("Ingredient Name: ")

    print("Select a Unit Type:")
    print("1. Whole")
    print("2. Milliliters")
    print("3. Grams")
    print("4. Teaspoon")
    print("5. Tablespoon")
    unit_type = get_menu_option()
    if not (unit_type >= 1 and unit_type <= 5):
        return ingredient_manager_menu()

    print("\nSelect a Cateogry Type:")
    print("1. Meat")
    print("2. Fish")
    print("3. Dairy")
    print("4. Vegetable")
    print("5. Pantry")
    print("6. Fridge Other")
    print("7. Bread")
    category_type = get_menu_option()
    if not (category_type >= 1 and category_type <= 7):
        return ingredient_manager_menu()

    try:
        Ingredient().add_ingredient(ingredient_name, unit_type, category_type)
        print("\nIngredient Added!")
    except:
        print("\nIngredient already exists!")
    time.sleep(2)
    return ingredient_manager_menu()

def remove_ingredient_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Ingredients")
    ingredients = Ingredient().get_all_ingredients()
    table = PrettyTable()
    table.field_names = ["Ingredient ID", "Name", "Unit Type", "Category"]
    valid_ingredients = []
    for ingredient in ingredients:
        valid_ingredients.append(ingredient.id)
        table.add_row([
            ingredient.id,
            ingredient.name,
            f"{UnitType(ingredient.unit_type).name}",
            f"{Category(ingredient.category_type).name}",
        ])
    print(table)

    print("\n=== Remove Ingredient ===")
    ingredient_id = int(input("Enter Ingredient Id: "))
    if ingredient_id not in valid_ingredients:
        return ingredient_manager_menu()

    Ingredient().remove_ingredient(ingredient_id)
    print("\nIngredient Removed!")
    time.sleep(1)

    return ingredient_manager_menu()


def recipe_manager_menu():
    os.system('cls' if os.name == 'nt' else 'clear')

    print("=== Recipe Manager Menu ===")
    print("1. View Recipes")
    print("2. Add Recipe")
    print("3. Main Menu")

    option = get_menu_option()
    if option == 1:
        return view_recipes_menu()
    elif option == 2:
        return add_recipe_menu()
    else:
        return main_menu()

def add_recipe_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=== Add Recipe ===")
    recipe_name = input("Enter recipe name: ")
    source = input("Enter recipe source: ")
    prep_time = int(input("Enter recipe prep time (mins): "))
    total_time = int(input("Enter total recipe time (mins): "))

    recipe_id = Recipe().add_recipe(recipe_name, source, prep_time, total_time)
    return recipe_menu(recipe_id)

def view_recipes_menu():
    os.system('cls' if os.name == 'nt' else 'clear')

    recipes = Recipe().get_recipes()

    print("=== Recipes ===")

    if not recipes:
        print("\nNo recipes available.")
        time.sleep(1)
        return recipe_manager_menu()

    # Create a PrettyTable instance
    table = PrettyTable()
    table.field_names = ["Recipe ID", "Name", "Source", "Preparation Time", "Total Time"]

    # Populate the table with recipe data
    valid_ids = []
    for recipe in recipes:
        valid_ids.append(recipe.id)
        table.add_row([
            recipe.id,
            recipe.name,
            recipe.source,
            f"{recipe.prep_time} min",
            f"{recipe.total_time} min"
        ])

    print(table)
    print("\nType a recipe number, or enter to go back")
    option = get_menu_option()
    if option in valid_ids:
        return recipe_menu(option)
    else:
        return recipe_manager_menu()


def recipe_menu(recipe_id):
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        recipe = Recipe().get_recipe(recipe_id)
    except:
        return view_recipes_menu()

    print("Recipe Details")
    recipe_table = PrettyTable()
    recipe_table.field_names = ["Recipe ID", "Name", "Source", "Preparation Time", "Total Time"]
    recipe_table.add_row([
        recipe.id,
        recipe.name,
        recipe.source,
        f"{recipe.prep_time} min",
        f"{recipe.total_time} min"
    ])
    print(recipe_table)
    print("\nRecipe Ingredients")
    ingredients_table = PrettyTable()
    ingredients_table.field_names = ["Ingredient", "Amount", "Required"]
    for ingredient in recipe.get_all_ingredients():
        ingredients_table.add_row([
            ingredient.name,
             f"{ingredient.amount} {UnitType(ingredient.unit_type).name}",
            f"{Category(ingredient.category_type).name}"
        ])
    print(ingredients_table)
    print("\nRecipe Instructions")
    instructions_table = PrettyTable()
    instructions_table.field_names = ["Step", "Instruction"]
    for instruction in recipe.get_all_steps():
        instructions_table.add_row([
            instruction.step_number,
            instruction.instructions
        ])
    print(instructions_table)

    print("\n=== Recipe Menu ===")
    print("1. Add Ingredient")
    print("2. Add Instruction")
    print("3. Remove Recipie")
    print("4. Recipe Manager Menu")

    option = get_menu_option()
    if option == 1:
        return add_recipe_ingredient_menu(recipe_id)
    elif option == 2:
        return add_instruction_menu(recipe_id)
    elif option == 3:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=== Confirm Delete ===")
        print("1. Remove Recipe")
        print("2. Enter to cancel")
        option = get_menu_option()
        if option == 1:
            print("\nRecipe Removed!")
            time.sleep(1)
            Recipe().remove_recipe(recipe_id)
        return view_recipes_menu()
    else:
        return view_recipes_menu()

def add_instruction_menu(recipe_id):
    os.system('cls' if os.name == 'nt' else 'clear')
    recipe = Recipe().get_recipe(recipe_id)
    instructions = recipe.get_all_steps()
    max_step = 0
    for step in instructions:
        if step.step_number >= max_step:
            max_step = step.step_number

    new_step_number = max_step

    print("== Add Instruction ==")
    for instruction in instructions:
        print(f"{instruction.step_number}. {instruction.instructions}")

    print("\n")
    print("Enter new instruction, or press enter to exit: ")
    while True:
        new_step_number += 1
        new_instruction = input("==> ")
        if new_instruction == "":
            return recipe_menu(recipe_id)

        recipe.add_instruction(new_step_number, new_instruction)


def add_recipe_ingredient_menu(recipe_id):
    os.system('cls' if os.name == 'nt' else 'clear')
    ingredients = Ingredient().get_all_ingredients()

    print("=== Available Ingredients ===")
    table = PrettyTable()
    table.field_names = ["Ingredient ID", "Name", "Unit Type", "Category Type"]
    valid_ingredients = []
    for ingredient in ingredients:
        valid_ingredients.append(ingredient.id)
        table.add_row([
            ingredient.id,
            ingredient.name,
            UnitType(ingredient.unit_type).name,
            Category(ingredient.category_type).name
        ])

    print(table)
    print("\n")
    print("Select an ingredient to add")
    ingredient_id = get_menu_option()
    if ingredient_id not in valid_ingredients:
        return recipe_menu(recipe_id)

    ingredient = Ingredient().get_ingredient(ingredient_id)
    print(f"\nSelected {ingredient.name}. Unit type: {UnitType(ingredient.unit_type).name}")
    print("\nEnter amount required")
    amount = get_menu_option_float()
    if not amount or amount <= 0:
        return recipe_menu(recipe_id)

    print("\nIs this required?")
    print("1. Yes")
    print("2. No")
    required = get_menu_option()
    if required != 1:
        required = 0

    recipe = Recipe().get_recipe(recipe_id)
    recipe.add_ingredient(ingredient_id, amount, required)

    print("\nIngredient Added!")
    time.sleep(1)

    return recipe_menu(recipe_id)


main_menu()