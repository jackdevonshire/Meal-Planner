from flask import Flask, request, jsonify, render_template
from database import session, Recipe, Ingredient, RecipeInstruction, RecipeIngredient

app = Flask(__name__)

"""
MAIN ROUTES
"""


@app.route('/', methods=['GET'])
def dashboard():
    recipes = Recipe().get_recipes()
    data = {
        "Recipes": [r.get_for_display() for r in recipes]
    }
    return render_template('dashboard.html', data=data)

@app.route('/ingredients', methods=['GET'])
def ingredients():
    ingredients = Ingredient().get_all_ingredients()
    recipes = Recipe().get_recipes()
    data = {
        "Ingredients": [i.get_for_display() for i in ingredients],
        "Recipes": [r.get_for_display() for r in recipes]
    }
    return render_template('ingredients.html', data=data)

@app.route('/recipe/<recipe_id>', methods=['GET'])
def recipe_page(recipe_id):
    recipe = Recipe().get_recipe(recipe_id).get_for_display()
    ingredients = Ingredient().get_all_ingredients()
    data = {
        "Recipe": recipe,
        "Ingredients": [ing.get_for_display() for ing in ingredients]
    }
    return render_template('recipe.html', data=data, editable=False)


@app.route('/recipe/<recipe_id>/edit', methods=['GET'])
def recipe_page_editable(recipe_id):
    recipe = Recipe().get_recipe(recipe_id).get_for_display()
    ingredients = Ingredient().get_all_ingredients()
    data = {
        "Recipe": recipe,
        "Ingredients": [ing.get_for_display() for ing in ingredients]
    }
    return render_template('recipe.html', data=data, editable=True)


"""
API ENDPOINTS
"""


@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    recipes = session.query(Recipe).all()
    return jsonify([{'id': r.id, 'name': r.name, 'source': r.source} for r in recipes])


@app.route('/api//recipe/<int:id>', methods=['GET'])
def get_recipe(id):
    recipe = session.query(Recipe).filter_by(id=id).first()
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404
    return jsonify({'id': recipe.id, 'name': recipe.name, 'source': recipe.source, 'prep_time': recipe.prep_time,
                    'total_time': recipe.total_time})


@app.route('/api/recipe', methods=['POST'])
def add_recipe():
    data = request.json
    new_recipe = Recipe(name=data.get('name'), source=data.get('source'), prep_time=data.get('prep_time'),
                        total_time=data.get('total_time'), type=data.get('type'))
    session.add(new_recipe)
    session.commit()
    return jsonify({'id': new_recipe.id, 'message': 'Recipe added successfully'})


@app.route('/api/recipe/<int:id>', methods=['PUT'])
def update_recipe(id):
    data = request.json
    recipe = session.query(Recipe).filter_by(id=id).first()
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404

    recipe.name = data.get('name', recipe.name)
    recipe.source = data.get('source', recipe.source)
    recipe.prep_time = data.get('prep_time', recipe.prep_time)
    recipe.total_time = data.get('total_time', recipe.total_time)
    session.commit()
    return jsonify({'message': 'Recipe updated successfully'})


@app.route('/api/recipe/<int:id>', methods=['DELETE'])
def delete_recipe(id):
    recipe = session.query(Recipe).filter_by(id=id).first()
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404
    session.delete(recipe)
    session.commit()
    return jsonify({'message': 'Recipe deleted successfully'})


@app.route('/api/recipe/<int:recipe_id>/ingredient', methods=['POST'])
def add_ingredient_to_recipe(recipe_id):
    data = request.json

    # Validate the required fields
    ingredient_id = data.get('ingredient_id')
    amount = data.get('amount')
    required = data.get('required', False)  # Defaults to False if not provided

    if not ingredient_id or not amount:
        return jsonify({"error": "Ingredient ID and amount are required"}), 400

    # Check if the recipe exists
    recipe = session.query(Recipe).filter_by(id=recipe_id).first()
    if not recipe:
        return jsonify({"error": f"Recipe with ID {recipe_id} not found"}), 404

    # Check if the ingredient exists
    ingredient = session.query(Ingredient).filter_by(id=ingredient_id).first()
    if not ingredient:
        return jsonify({"error": f"Ingredient with ID {ingredient_id} not found"}), 404

    # Recipe Ingredient
    recipe_ingredient = session.query(RecipeIngredient).filter_by(recipe_id=recipe_id,
                                                                  ingredient_id=ingredient_id).first()
    if recipe_ingredient:
        return jsonify({"error": f"Recipe already has this ingredient!"}), 400

    # Create a new RecipeIngredient entry
    new_recipe_ingredient = RecipeIngredient(
        recipe_id=recipe_id,
        ingredient_id=ingredient_id,
        amount=amount,
        required=required
    )

    # Add to session and commit
    session.add(new_recipe_ingredient)
    session.commit()

    return jsonify({
        "message": f"Ingredient {ingredient_id} added to Recipe {recipe_id} successfully",
        "recipe_id": recipe_id,
        "ingredient_id": ingredient_id,
        "amount": amount,
        "required": required
    }), 201


@app.route('/api/recipe/<int:recipe_id>/ingredient/<int:ingredient_id>', methods=['DELETE'])
def delete_recipe_ingredient(recipe_id, ingredient_id):
    instruction = session.query(RecipeIngredient).filter_by(recipe_id=recipe_id, ingredient_id=ingredient_id).first()
    if not instruction:
        return jsonify({'error': 'Recipe ingredient not found'}), 404

    session.delete(instruction)
    session.commit()
    return jsonify({'message': 'Recipe ingredient deleted successfully'})


@app.route('/api/recipe/<int:recipe_id>/step', methods=['POST'])
def add_recipe_step(recipe_id):
    data = request.json
    recipe = session.query(Recipe).filter_by(id=recipe_id).first()
    recipe.add_instruction(data.get("Step"))
    session.commit()
    return jsonify({'message': 'Step added successfully'})


@app.route('/api/recipe/<int:recipe_id>/step/<int:step_number>', methods=['DELETE'])
def remove_recipe_step(recipe_id, step_number):
    recipe = session.query(Recipe).filter_by(id=recipe_id).first()
    recipe.remove_instruction(step_number)
    session.commit()
    return jsonify({'message': 'Step removed successfully'})


@app.route('/api/recipe/<int:recipe_id>/step/<int:step_number>/move/<amount>', methods=['PUT'])
def move_recipe_step(recipe_id, step_number, amount):
    recipe = session.query(Recipe).filter_by(id=recipe_id).first()
    recipe.move_instruction(step_number, int(amount))
    session.commit()
    return jsonify({'message': 'Step moved successfully'})


if __name__ == '__main__':
    app.run(debug=True)
