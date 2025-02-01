from sqlalchemy import Column, ForeignKey, Integer, String, Float, Text, create_engine
from sqlalchemy.orm import relationship, declarative_base, aliased, sessionmaker
from enum import Enum

Base = declarative_base()
engine = create_engine('sqlite:///meals.db')
Session = sessionmaker(bind=engine)
session = Session()


class UnitType(Enum):
    Whole = 1
    Milliliters = 2
    Grams = 3
    Teaspoon = 4
    TableSpoon = 5


class Category(Enum):
    Meat = 1
    Fish = 2
    Dairy = 3
    Vegetable = 4
    Pantry = 5
    FridgeOther = 6
    Bread = 7

class RecipeType(Enum):
    Breakfast = 1
    Main = 2
    Side = 3
    Dessert = 4


class Ingredient(Base):
    __tablename__ = 'ingredient'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    unit_type = Column(Integer, nullable=False)
    category_type = Column(Integer, nullable=False)

    def get_for_display(self):
        return {
            "Id": self.id,
            "Name": self.name,
            "UnitType": UnitType(self.unit_type).name,
            "CategoryType": Category(self.category_type).name
        }

    def get_all_ingredients(self):
        # Retrieve all ingredients from the database
        ingredients = session.query(Ingredient).order_by(Ingredient.category_type.asc(), Ingredient.name.asc()).all()
        return ingredients

    def get_ingredient(self, id):
        # Retrieve a specific ingredient by ID
        ingredient = session.query(Ingredient).filter_by(id=id).first()
        if ingredient:
            return ingredient
        else:
            raise ValueError(f"Ingredient with ID {id} does not exist.")

    def add_ingredient(self, name, unit_type, category_type):
        for ingredient in self.get_all_ingredients():
            if name.lower() == ingredient.name.lower():
                raise ValueError("This ingredient already exists!")

        # Add a new ingredient to the database
        new_ingredient = Ingredient(
            name=name,
            unit_type=unit_type,
            category_type=category_type
        )
        session.add(new_ingredient)
        session.commit()

    def remove_ingredient(self, id):
        # Remove an ingredient by ID from the database
        ingredient = session.query(Ingredient).filter_by(id=id).first()
        if ingredient:
            recipes = session.query(RecipeIngredient).filter_by(ingredient_id=ingredient.id).all()
            if len(recipes) > 0:
                raise ValueError("Remove ingredient from recipes before removing!")

            session.delete(ingredient)
            session.commit()
        else:
            raise ValueError(f"Ingredient with ID {id} does not exist.")

    def search(self, query):
        if query == "":
            return self.get_all_ingredients()
        # Perform a case-insensitive search with partial matching using 'ilike'
        ingredients = session.query(Ingredient).filter(Ingredient.name.ilike(f"%{query}%")).all()

        # If ingredients are found, return them
        if ingredients:
            return ingredients
        else:
            return []


class Recipe(Base):
    __tablename__ = 'recipe'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    source = Column(String)
    prep_time = Column(Integer)
    total_time = Column(Integer)
    type = Column(Integer)

    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    instructions = relationship("RecipeInstruction", back_populates="recipe", uselist=False,
                                cascade="all, delete-orphan")
    nutrients = relationship("RecipeNutrient", back_populates="recipe", uselist=False, cascade="all, delete-orphan")

    def get_for_display(self):
        nutrients = session.query(RecipeNutrient).filter_by(recipe_id=self.id).first()
        instructions = session.query(RecipeInstruction).filter_by(recipe_id=self.id).order_by(RecipeInstruction.step_number.asc()).all()
        ingredients = session.query(RecipeIngredient).filter_by(recipe_id=self.id)

        if not nutrients:
            self.update_nutrients(0, 0, 0, 0, 0, 0, 0, 0)
            nutrients = session.query(RecipeNutrient).filter_by(recipe_id=self.id).first()

        return {
            "Id": self.id,
            "Name": self.name,
            "Source": self.source,
            "PrepTime": self.prep_time,
            "TotalTime": self.total_time,
            "Type": RecipeType(self.type).name,
            "Nutrients": nutrients.get_for_display(),
            "Instructions": [ins.get_for_display() for ins in instructions],
            "Ingredients": [ing.get_for_display() for ing in ingredients]
        }

    def get_recipes(self):
        # Retrieve all recipes from the database
        recipes = session.query(Recipe).all()
        return recipes

    def get_recipe(self, id):
        # Retrieve a specific recipe by ID, including its ingredients and instructions
        r = session.query(Recipe).filter_by(id=id).first()
        if r:
            return r
        else:
            raise ValueError(f"Recipe with ID {id} does not exist.")

    def add_recipe(self, name, source, prep_time, total_time):
        # Add a new recipe to the database
        new_recipe = Recipe(
            name=name,
            source=source,
            prep_time=prep_time,
            total_time=total_time
        )
        session.add(new_recipe)
        session.commit()
        self.update_nutrients(0, 0, 0, 0, 0, 0, 0, 0)
        return new_recipe.id  # Return the ID of the newly added recipe

    def update_recipe(self, id, name=None, source=None, prep_time=None, total_time=None):
        recipe = session.query(Recipe).filter_by(id=id).first()
        if not recipe:
            raise ValueError(f"Recipe with ID {id} does not exist.")

        print(name, source, prep_time, total_time)

        if name:
            recipe.name = name
        if source:
            recipe.source = source
        if prep_time is not None:
            recipe.prep_time = prep_time
        if total_time is not None:
            recipe.total_time = total_time

        session.commit()
        return recipe

    def remove_recipe(self, id):
        to_remove = []
        to_remove += session.query(RecipeIngredient).filter_by(recipe_id=id).all()
        to_remove += session.query(RecipeNutrient).filter_by(recipe_id=id).all()
        to_remove += session.query(RecipeInstruction).filter_by(recipe_id=id).all()
        to_remove += session.query(Recipe).filter_by(id=id).all()

        for item in to_remove:
            session.delete(item)

        session.commit()

    def add_ingredient(self, ingredient_id, amount, required):
        # Check if the ingredient exists
        ingredient = session.query(Ingredient).filter_by(id=ingredient_id).first()
        if not ingredient:
            raise ValueError(f"Ingredient with ID {ingredient_id} does not exist.")

        # Add the ingredient to the recipe
        new_recipe_ingredient = RecipeIngredient(
            recipe_id=self.id,
            ingredient_id=ingredient_id,
            amount=amount,
            required=required
        )
        session.add(new_recipe_ingredient)
        session.commit()

    def remove_ingredient(self, recipe_id, ingredient_id):
        # Find the recipe-ingredient relation
        recipe_ingredient = session.query(RecipeIngredient).filter_by(
            recipe_id=recipe_id,
            ingredient_id=ingredient_id
        ).first()
        if recipe_ingredient:
            session.delete(recipe_ingredient)
            session.commit()
        else:
            raise ValueError(f"Ingredient with ID {ingredient_id} is not associated with this recipe.")

    def add_instruction(self, instruction):
        # Get maximum step number
        existing_instruction = session.query(RecipeInstruction).filter_by(
            recipe_id=self.id
        ).order_by(RecipeInstruction.step_number.desc()).first()

        if existing_instruction:
            step_number = existing_instruction.step_number + 1
        else:
            step_number = 1

        # Add the instruction to the recipe
        new_instruction = RecipeInstruction(
            recipe_id=self.id,
            step_number=step_number,
            instructions=instruction
        )
        session.add(new_instruction)
        session.commit()

    def update_instruction(self, recipe_id, new_instruction):
        recipe = session.query(Recipe).filter_by(id=recipe_id).first()
        if not recipe:
            raise ValueError(f"Recipe with ID {recipe_id} does not exist.")

        if not recipe.instructions:
            raise ValueError(f"No instructions found for Recipe ID {recipe_id}.")

        recipe.instructions.text = new_instruction
        session.commit()
        return recipe.instructions

    def remove_instruction(self, step_number):
        # Find the instruction for the given step
        instruction = session.query(RecipeInstruction).filter_by(
            recipe_id=self.id,
            step_number=step_number
        ).first()
        if instruction:
            session.delete(instruction)
            session.commit()
        else:
            raise ValueError(f"Step number {step_number} does not exist for this recipe.")

        # Now rejig all the step numbers
        instructions = session.query(RecipeInstruction).filter_by(
            recipe_id=self.id,
            step_number=step_number
        ).order_by(RecipeInstruction.step_number.asc()).all()
        count = 1
        for instruction in instructions:
            instruction.step_number = count
            count += 1

        session.commit()

    def move_instruction(self, step_number, amount):
        instruction = session.query(RecipeInstruction).filter_by(
            recipe_id=self.id,
            step_number=step_number
        ).first()

        to_swap = session.query(RecipeInstruction).filter_by(
            recipe_id=self.id,
            step_number=step_number + amount
        ).first()

        if not instruction or not to_swap:
            return

        instruction.step_number = to_swap.step_number
        to_swap.step_number = step_number

        session.commit()


    def update_nutrients(self, calories, fat, sat_fat, carbs, sugar, fibre, protein, salt):
        nutrients = session.query(RecipeNutrient).filter_by(
            recipe_id=self.id
        ).first()
        if nutrients:
            session.delete(nutrients)

        new_nutrients = RecipeNutrient(
            recipe_id=self.id,
            calories=calories,
            fat=fat,
            sat_fat=sat_fat,
            carbs=carbs,
            sugar=sugar,
            fibre=fibre,
            protein=protein,
            salt=salt
        )
        session.add(new_nutrients)
        session.commit()

    def get_all_ingredients(self):
        # Create an alias for the Ingredient table
        ingredient_alias = aliased(Ingredient)

        # Retrieve all ingredients for this recipe with an inner join
        recipe_ingredients = session.query(
            ingredient_alias.id.label('ingredient_id'),
            ingredient_alias.name,
            ingredient_alias.unit_type,
            ingredient_alias.category_type,
            RecipeIngredient.amount,
            RecipeIngredient.required
        ).join(
            RecipeIngredient, RecipeIngredient.ingredient_id == ingredient_alias.id
        ).filter(
            RecipeIngredient.recipe_id == self.id
        ).order_by(RecipeIngredient.required.desc()).all()

        return recipe_ingredients

    def get_all_steps(self):
        # Retrieve all steps for this recipe in order
        recipe_instructions = session.query(RecipeInstruction).filter_by(recipe_id=self.id).order_by(
            RecipeInstruction.step_number.asc()).all()
        return recipe_instructions

    def search(self, query):
        if query == "":
            return self.get_recipes()
        # Perform a case-insensitive search with partial matching using 'ilike'
        recipes = session.query(Recipe).filter(Recipe.name.ilike(f"%{query}%")).all()

        # If ingredients are found, return them
        if recipes:
            return recipes
        else:
            return []


class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredient'

    recipe_id = Column(Integer, ForeignKey('recipe.id'), primary_key=True, nullable=False)
    ingredient_id = Column(Integer, ForeignKey('ingredient.id'), primary_key=True, nullable=False)
    amount = Column(Float, nullable=False)
    required = Column(Integer, nullable=False)

    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient")

    def get_for_display(self):
        ingredient = session.query(Ingredient).filter_by(id=self.ingredient_id).first()
        return {
            "RecipeId": self.recipe_id,
            "IngredientId": self.ingredient_id,
            "Amount": self.amount,
            "Required": self.required,
            "Ingredient": ingredient.get_for_display()
        }


class RecipeInstruction(Base):
    __tablename__ = 'recipe_instruction'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    recipe_id = Column(Integer, ForeignKey('recipe.id'), nullable=False)
    step_number = Column(Integer, nullable=False)
    instructions = Column(Text)

    recipe = relationship("Recipe", back_populates="instructions")

    def get_for_display(self):
        return {
            "Id": self.id,
            "RecipeId": self.recipe_id,
            "StepNumber": self.step_number,
            "Instructions": self.instructions
        }

class RecipeNutrient(Base):
    __tablename__ = 'recipe_nutrient'

    recipe_id = Column(Integer, ForeignKey('recipe.id'), primary_key=True, nullable=False)
    calories = Column(Integer)
    fat = Column(Integer)
    sat_fat = Column(Integer)
    carbs = Column(Integer)
    sugar = Column(Integer)
    fibre = Column(Integer)
    protein = Column(Integer)
    salt = Column(Integer)

    recipe = relationship("Recipe", back_populates="nutrients")

    def get_for_display(self):
        return {
            "RecipeId": self.recipe_id,
            "Calories": self.calories,
            "Fat": self.fat,
            "SatFat": self.sat_fat,
            "Carbs": self.carbs,
            "Sugar": self.sugar,
            "Fibre": self.fibre,
            "Protein": self.protein,
            "Salt": self.salt
        }


# Creating an engine for the SQLite database
engine = create_engine('sqlite:///meals.db')

# Create all tables in the database
Base.metadata.create_all(engine)
