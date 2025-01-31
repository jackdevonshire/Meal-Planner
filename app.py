from flask import Flask, request, jsonify, render_template
from database import session, Recipe, Ingredient, RecipeInstruction

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

@app.route('/recipe/<recipe_id>', methods=['GET'])
def recipe_page(recipe_id):
    recipe = Recipe().get_recipe(recipe_id).get_for_display()
    ingredients = Ingredient().get_all_ingredients()
    data = {
        "Recipe": recipe,
        "Ingredients": [ing.get_for_display() for ing in ingredients]
    }
    return render_template('recipe.html', data=data)

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


@app.route('/api/recipe/<int:id>/instruction', methods=['POST'])
def add_instruction(id):
    data = request.json
    instruction = RecipeInstruction(recipe_id=id, step_number=data['step_number'], instructions=data['instructions'])
    session.add(instruction)
    session.commit()
    return jsonify({'message': 'Instruction added successfully'})


@app.route('/api/recipe/<int:id>/instruction/<int:step>', methods=['PUT'])
def update_instruction(id, step):
    data = request.json
    instruction = session.query(RecipeInstruction).filter_by(recipe_id=id, step_number=step).first()
    if not instruction:
        return jsonify({'error': 'Instruction not found'}), 404
    instruction.instructions = data['instructions']
    session.commit()
    return jsonify({'message': 'Instruction updated successfully'})


@app.route('/api/recipe/<int:id>/instruction/<int:step>', methods=['DELETE'])
def delete_instruction(id, step):
    instruction = session.query(RecipeInstruction).filter_by(recipe_id=id, step_number=step).first()
    if not instruction:
        return jsonify({'error': 'Instruction not found'}), 404
    session.delete(instruction)
    session.commit()
    return jsonify({'message': 'Instruction deleted successfully'})


if __name__ == '__main__':
    app.run(debug=True)
