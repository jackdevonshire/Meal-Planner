from database import session, Recipe, Ingredient, RecipeInstruction, RecipeIngredient


class ShoppingCart:
    def __init__(self):
        self.recipe_ids = []

    def get_recipes(self):
        recipes = []
        for id in self.recipe_ids:
            recipe = session.query(Recipe).filter_by(id=id).first()
            recipes.append(recipe.get_for_display())

        return recipes

    def remove_from_cart(self, recipe_id):
        self.recipe_ids.remove(int(recipe_id))

    def add_to_cart(self, recipe_id):
        self.recipe_ids.append(int(recipe_id))

    def get_required_ingredients(self):
        recipes = self.get_recipes()
        shopping_list_items = {}
        for recipe in recipes:
            for ingredient in recipe["Ingredients"]:
                # Handling case when ingredient already in shopping list
                if ingredient["IngredientId"] in shopping_list_items:
                    shopping_list_items[ingredient["IngredientId"]]["Amount"] += ingredient["Amount"]

                    if bool(ingredient["Required"]):
                        shopping_list_items[ingredient["IngredientId"]]["Required"] = True

                else:
                    shopping_list_items[ingredient["IngredientId"]] = {
                        "IngredientId": ingredient["IngredientId"],
                        "Name": ingredient["Ingredient"]["Name"],
                        "Amount": ingredient["Amount"],
                        "Unit": ingredient["Ingredient"]["UnitType"],
                        "Category": ingredient["Ingredient"]["CategoryType"],
                        "Required": bool(ingredient["Required"])
                    }
        # Now we prepare the list for being displayed
        for _, item in shopping_list_items.items():
            if item["Required"]:
                item["Required"] = "Mandatory"
            else:
                item["Required"] = "Optional"
        meat = [i for _, i in shopping_list_items.items() if i["Category"] == "Meat"]
        fish = [i for _, i in shopping_list_items.items() if i["Category"] == "Fish"]
        dairy = [i for _, i in shopping_list_items.items() if i["Category"] == "Dairy"]
        vegetable = [i for _, i in shopping_list_items.items() if i["Category"] == "Vegetable"]
        pantry = [i for _, i in shopping_list_items.items() if i["Category"] == "Pantry"]
        fridge = [i for _, i in shopping_list_items.items() if i["Category"] == "FridgeOther"]
        bread = [i for _, i in shopping_list_items.items() if i["Category"] == "Bread"]

        shopping_list = {
            "Meat": meat,
            "Fish": fish,
            "Dairy": dairy,
            "Vegetables": vegetable,
            "Fridge Misc": fridge,
            "Pantry": pantry,
            "Bread": bread
        }

        print(shopping_list)
        return shopping_list


cart = ShoppingCart()
