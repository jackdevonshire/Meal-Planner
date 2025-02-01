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

cart = ShoppingCart()