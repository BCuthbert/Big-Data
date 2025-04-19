# Makefile to automate summary generation and GUI launch

# Default target
.PHONY: all
all: run

# Ensure summary exists before running the app
.PHONY: run
run: simulation_summary.csv
	@echo "\033[1mPlease input simulation_summary.csv into the site to see metrics.\033[0m \n"
	@echo "Launching Streamlit app..."
	streamlit run visualize_sims.py

# Build summary CSV from raw results
simulation_summary.csv: simulation_results.csv simulation_analysis.py
	@echo "Generating simulation_summary.csv from simulation_results.csv..."
	python3 simulation_analysis.py

# If raw results are missing, alert the user
.PHONY: check-results
check-results:
	@if [ ! -f simulation_results.csv ]; then \
	  echo "Error: simulation_results.csv not found. Please run your simulation first."; \
	  exit 1; \
	fi

# Clean generated files
.PHONY: clean
clean:
	@echo "Cleaning up..."
	rm -f simulation_summary.csv *.png


