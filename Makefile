run:
	poetry run dotenv run streamlit run app.py

format:
	poetry run black .

test:
	poetry run dotenv run pytest tests
