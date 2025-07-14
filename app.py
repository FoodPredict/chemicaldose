from flask import Flask, render_template, request, jsonify, g
import sqlite3
import os

app = Flask(__name__)

# Define database file
DATABASE = 'pesticide_recommendations.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Return rows as dict-like objects
    return db

@app.teardown_appcontext
def close_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Function to create the database tables (for initial setup)
def create_tables():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Crops (
            crop_id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_name_en TEXT UNIQUE NOT NULL,
            crop_name_hi TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS PestsDiseases (
            pest_disease_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pest_disease_name_en TEXT UNIQUE NOT NULL,
            pest_disease_name_hi TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Chemicals (
            chemical_id INTEGER PRIMARY KEY AUTOINCREMENT,
            chemical_name_en TEXT UNIQUE NOT NULL,
            chemical_name_hi TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Recommendations (
            recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_id INTEGER,
            pest_disease_id INTEGER,
            chemical_id INTEGER,
            recommended_dose REAL NOT NULL,
            unit TEXT NOT NULL,
            source TEXT,
            FOREIGN KEY(crop_id) REFERENCES Crops(crop_id),
            FOREIGN KEY(pest_disease_id) REFERENCES PestsDiseases(pest_disease_id),
            FOREIGN KEY(chemical_id) REFERENCES Chemicals(chemical_id)
        )
    """)

    db.commit()

# Example data insertion (replace with actual data loading)
def insert_example_data():
    db = get_db()
    cursor = db.cursor()

    # Insert example crops
    cursor.execute("INSERT OR IGNORE INTO Crops (crop_name_en, crop_name_hi) VALUES (?, ?)", ('Rice', 'चावल'))
    cursor.execute("INSERT OR IGNORE INTO Crops (crop_name_en, crop_name_hi) VALUES (?, ?)", ('Wheat', 'गेहूं'))

    # Insert example pests/diseases
    cursor.execute("INSERT OR IGNORE INTO PestsDiseases (pest_disease_name_en, pest_disease_name_hi) VALUES (?, ?)", ('Stem Borer', 'तना छेदक'))
    cursor.execute("INSERT OR IGNORE INTO PestsDiseases (pest_disease_name_en, pest_disease_name_hi) VALUES (?, ?)", ('Rust', 'रतुआ'))

    # Insert example chemicals
    cursor.execute("INSERT OR IGNORE INTO Chemicals (chemical_name_en, chemical_name_hi) VALUES (?, ?)", ('Chlorpyrifos', 'क्लोरपायरीफॉस'))
    cursor.execute("INSERT OR IGNORE INTO Chemicals (chemical_name_en, chemical_name_hi) VALUES (?, ?)", ('Mancozeb', 'मैन्कोजेब'))

    # Insert example recommendations
    # Assuming crop_id=1 for Rice, pest_disease_id=1 for Stem Borer, chemical_id=1 for Chlorpyrifos
    cursor.execute("""
        INSERT OR IGNORE INTO Recommendations (crop_id, pest_disease_id, chemical_id, recommended_dose, unit, source)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (1, 1, 1, 0.5, 'liter/acre', 'Example Source 1'))

    # Assuming crop_id=2 for Wheat, pest_disease_id=2 for Rust, chemical_id=2 for Mancozeb
    cursor.execute("""
        INSERT OR IGNORE INTO Recommendations (crop_id, pest_disease_id, chemical_id, recommended_dose, unit, source)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (2, 2, 2, 750, 'grams/acre', 'Example Source 2'))

    db.commit()


# Function to get recommendations based on crop and pest/disease
def get_recommendation(crop_name_en, pest_disease_name_en):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT
            c.chemical_name_en, c.chemical_name_hi,
            r.recommended_dose, r.unit, r.source
        FROM Recommendations r
        JOIN Crops crop ON r.crop_id = crop.crop_id
        JOIN PestsDiseases pd ON r.pest_disease_id = pd.pest_disease_id
        JOIN Chemicals c ON r.chemical_id = c.chemical_id
        WHERE crop.crop_name_en = ? AND pd.pest_disease_name_en = ?
    """, (crop_name_en, pest_disease_name_en))
    return cursor.fetchone()

# Function to perform unit conversions and dose calculations
def calculate_dose(recommended_dose, recommended_unit, area, area_unit, desired_output_unit):
    # Convert area to acres if in hectares
    if area_unit.lower() == 'hectares':
        area_in_acres = area * 2.47105  # 1 hectare = 2.47105 acres
    else: # assume acres
        area_in_acres = area

    calculated_dose = None
    unit = desired_output_unit

    # Convert recommended dose to a common unit (e.g., grams or ml per acre)
    dose_in_common_unit = None
    common_unit = None

    if recommended_unit.lower() == 'liter/acre':
        dose_in_common_unit = recommended_dose * 1000 # convert to ml/acre
        common_unit = 'ml/acre'
    elif recommended_unit.lower() == 'grams/acre':
        dose_in_common_unit = recommended_dose
        common_unit = 'grams/acre'
    elif recommended_unit.lower() == 'kg/acre':
         dose_in_common_unit = recommended_dose * 1000 # convert to grams/acre
         common_unit = 'grams/acre'
    elif recommended_unit.lower() == 'ml/acre':
        dose_in_common_unit = recommended_dose
        common_unit = 'ml/acre'
    # Add more base conversions as needed (e.g., for ppm, ppb, % solution - requires more context like density)
    # For simplicity, we'll handle conversions between g/acre, kg/acre, ml/acre, liter/acre

    if dose_in_common_unit is not None:
        # Calculate total dose based on area in acres
        total_dose_for_area = dose_in_common_unit * area_in_acres

        # Convert total dose to desired output unit
        if desired_output_unit.lower() == common_unit.lower():
            calculated_dose = total_dose_for_area
        elif common_unit == 'ml/acre' and desired_output_unit.lower() == 'liter/acre':
            calculated_dose = total_dose_for_area / 1000
        elif common_unit == 'grams/acre' and desired_output_unit.lower() == 'kg/acre':
             calculated_dose = total_dose_for_area / 1000
        elif common_unit == 'grams/acre' and desired_output_unit.lower() == 'ml/acre':
             # This conversion requires chemical density, which is not available.
             # For now, handle simple conversions where density is not needed.
             pass # Cannot convert grams to ml without density
        elif common_unit == 'ml/acre' and desired_output_unit.lower() == 'grams/acre':
             # Cannot convert ml to grams without density
             pass # Cannot convert ml to grams without density
        else:
            # Handle other conversions or indicate unsupported conversion
            calculated_dose = None
            unit = "Unsupported Unit Conversion"


    return calculated_dose, unit

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_crops', methods=['GET'])
def get_crops():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT crop_name_en, crop_name_hi FROM Crops")
    crops = cursor.fetchall()
    # Convert rows to list of dictionaries
    crops_list = [{"name_en": row['crop_name_en'], "name_hi": row['crop_name_hi']} for row in crops]
    return jsonify(crops_list)

@app.route('/get_pests_diseases', methods=['GET'])
def get_pests_diseases():
    crop_name_en = request.args.get('crop_en')
    db = get_db()
    cursor = db.cursor()
    # Join with Recommendations table to get pests/diseases relevant to the crop
    cursor.execute("""
        SELECT DISTINCT pd.pest_disease_name_en, pd.pest_disease_name_hi
        FROM PestsDiseases pd
        JOIN Recommendations r ON pd.pest_disease_id = r.pest_disease_id
        JOIN Crops c ON r.crop_id = c.crop_id
        WHERE c.crop_name_en = ?
    """, (crop_name_en,))
    pests_diseases = cursor.fetchall()
    # Convert rows to list of dictionaries
    pd_list = [{"name_en": row['pest_disease_name_en'], "name_hi": row['pest_disease_name_hi']} for row in pests_diseases]
    return jsonify(pd_list)


@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    crop_en = data.get('crop_en') # Use English name for database query
    pest_disease_en = data.get('pest_disease_en') # Use English name for database query
    area = float(data.get('area'))
    area_unit = data.get('area_unit')
    desired_output_unit = data.get('desired_output_unit')
    language = data.get('language', 'en') # Default to English

    recommendation = get_recommendation(crop_en, pest_disease_en)

    if recommendation:
        recommended_dose = recommendation['recommended_dose']
        recommended_unit = recommendation['unit']
        source = recommendation['source']

        calculated_dose, calculated_unit = calculate_dose(
            recommended_dose, recommended_unit, area, area_unit, desired_output_unit
        )

        if calculated_dose is not None:
            chemical_name = recommendation[f'chemical_name_{language}']
            response = {
                'chemical': chemical_name,
                'calculated_dose': calculated_dose,
                'unit': calculated_unit,
                'source': source,
                'error': None
            }
        else:
             response = {
                'chemical': None,
                'calculated_dose': None,
                'unit': None,
                'source': None,
                'error': f"Unsupported unit conversion from {recommended_unit} to {desired_output_unit}"
            }

    else:
        response = {
            'chemical': None,
            'calculated_dose': None,
            'unit': None,
            'source': None,
            'error': f"No recommendation found for {crop_en} and {pest_disease_en}"
        }

    return jsonify(response)

# Helper function to set up the database and insert initial data
def init_db():
    with app.app_context():
        db = get_db()
        create_tables()
        insert_example_data()
        print("Database initialized and example data inserted.")

# Initialize the database when the script starts
init_db()
