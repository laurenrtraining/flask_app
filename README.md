# flask_app

# Step 1: Create virtual envrionment

# Run the following commands:

python -m venv my-venv
my-venv\Scripts\activate

# Step 2: Run pip install

pip install src/requirements.txt
pip install pytest

# Step 3: Run the tests

ensure you are in the current directory: C:\Users\laure\flask_app\flask_app\src>

run: pytest tests/test_app.py

# Step 4: Run the program

run: db_init.py first to present test data

ensure you are in the current directory: C:\Users\laure\flask_app\flask_app\src>

run: python src/app.py
