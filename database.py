from sqlalchemy import Column, ForeignKey, Integer, String, Float, Text, create_engine
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.orm import sessionmaker
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

class Ingredient(Base):
    __tablename__ = 'ingredient'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    unit_type = Column(Integer, nullable=False)
    category_type = Column(Integer, nullable=False)

    def get_all_ingredients(self):
        # Retrieve all ingredients from the database
        ingredients = session.query(Ingredient).all()
        return [
            {
                "id": ingredient.id,
                "name": ingredient.name,
                "unit_type": ingredient.unit_type,
                "category_type": ingredient.category_type
            } for ingredient in ingredients
        ]

    def get_ingredient(self, id):
        # Retrieve a specific ingredient by ID
        ingredient = session.query(Ingredient).filter_by(id=id).first()
        if ingredient:
            return {
                "id": ingredient.id,
                "name": ingredient.name,
                "unit_type": ingredient.unit_type,
                "category_type": ingredient.category_type
            }
        else:
            raise ValueError(f"Ingredient with ID {id} does not exist.")

    def add_ingredient(self, name, unit_type, category_type):
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
            session.delete(ingredient)
            session.commit()
        else:
            raise ValueError(f"Ingredient with ID {id} does not exist.")

class Recipe(Base):
    __tablename__ = 'recipe'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    source = Column(String)
    prep_time = Column(Integer)
    total_time = Column(Integer)

    ingredients = relationship("RecipeIngredient", back_populates="recipe")
    instructions = relationship("RecipeInstruction", back_populates="recipe", uselist=False)
    nutrients = relationship("RecipeNutrient", back_populates="recipe", uselist=False)

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

    def remove_ingredient(self, ingredient_id):
        # Find the recipe-ingredient relation
        recipe_ingredient = session.query(RecipeIngredient).filter_by(
            recipe_id=self.id,
            ingredient_id=ingredient_id
        ).first()
        if recipe_ingredient:
            session.delete(recipe_ingredient)
            session.commit()
        else:
            raise ValueError(f"Ingredient with ID {ingredient_id} is not associated with this recipe.")

    def add_instruction(self, step_number, instruction):
        # Check if the step already exists
        existing_instruction = session.query(RecipeInstruction).filter_by(
            recipe_id=self.id,
            step_number=step_number
        ).first()
        if existing_instruction:
            raise ValueError(f"Step number {step_number} already exists for this recipe.")

        # Add the instruction to the recipe
        new_instruction = RecipeInstruction(
            recipe_id=self.id,
            step_number=step_number,
            instructions=instruction
        )
        session.add(new_instruction)
        session.commit()

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


    def get_all_ingredients(self):
        # Retrieve all ingredients for this recipe
        recipe_ingredients = session.query(RecipeIngredient).filter_by(recipe_id=self.id).order_by(RecipeIngredient.required.desc()).all()
        return [
            {
                "ingredient_id": ingredient.ingredient_id,
                "amount": ingredient.amount,
                "required": bool(ingredientrequired)
            } for ingredient in recipe_ingredients
        ]

    def get_all_steps(self):
        # Retrieve all steps for this recipe in order
        recipe_instructions = session.query(RecipeInstruction).filter_by(recipe_id=self.id).order_by(RecipeInstruction.step_number.asc()).all()
        return [
            {
                "step_number": instruction.step_number,
                "instructions": instruction.instructions
            } for instruction in recipe_instructions
        ]

class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredient'

    recipe_id = Column(Integer, ForeignKey('recipe.id'), primary_key=True, nullable=False)
    ingredient_id = Column(Integer, ForeignKey('ingredient.id'), primary_key=True, nullable=False)
    amount = Column(Float, nullable=False)
    required = Column(Integer, nullable=False)

    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient")


class RecipeInstruction(Base):
    __tablename__ = 'recipe_instruction'

    recipe_id = Column(Integer, ForeignKey('recipe.id'), primary_key=True, autoincrement=True, unique=True, nullable=False)
    step_number = Column(Integer, nullable=False)
    instructions = Column(Text)

    recipe = relationship("Recipe", back_populates="instructions")

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

# Creating an engine for the SQLite database
engine = create_engine('sqlite:///meals.db')

# Create all tables in the database
Base.metadata.create_all(engine)
