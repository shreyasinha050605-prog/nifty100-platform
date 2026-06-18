load:
	python src/etl/loader.py

ratios:
	python src/analytics/ratios.py

test:
	pytest

report:
	python src/analytics/report.py

dashboard:
	streamlit run src/dashboard/app.py

api:
	python src/api/main.py

clean:
	rm -f db/nifty100.db