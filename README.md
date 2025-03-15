# Data Analysis & Visualization Tool

A comprehensive data analysis and visualization tool that combines web scraping capabilities, robust data processing, and an intuitive Streamlit UI.

## Features

- **Web Scraping**: Headless browser automation using Selenium to collect data from websites
- **Data Processing**: Clean, transform, and analyze data with pandas and numpy
- **Data Visualization**: Create insightful visualizations with matplotlib and seaborn
- **User Interface**: Interactive Streamlit application for data exploration
- **Export Options**: Save your data and visualizations in multiple formats

## Installation

### Prerequisites

- Python 3.8 or higher
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/data-analysis-tool.git
   cd data-analysis-tool
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Activate the Poetry environment:
   ```bash
   poetry shell
   ```

## Usage

### Command Line Interface

The scraper and processor can be used directly from the command line:

```bash
# Run the scraper to collect data
python -m src.scraper.scraper --url "https://example.com" --output "data.csv"

# Process data using the analysis module
python -m src.analysis.processor --input "data.csv" --clean --analyze
```

### Streamlit UI

For a more interactive experience, use the Streamlit UI:

```bash
streamlit run src/ui/app.py
```

The UI provides the following features:

1. **Data Upload**: Upload your CSV or Excel files
2. **Data Preview**: View and explore your dataset
3. **Data Cleaning**: Handle missing values and outliers
4. **Analysis**: Generate statistical summaries and correlations
5. **Visualization**: Create various plots to understand your data
6. **Export**: Download processed data and visualizations

## Development Setup

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/data-analysis-tool.git
   cd data-analysis-tool
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unix/MacOS
   # OR
   .\venv\Scripts\activate   # Windows
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   # OR with Poetry
   poetry install --with dev
   ```

### Code Formatting and Linting

We use the following tools for code quality:

```bash
# Format code with Black
black src/ tests/

# Check code style with Flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/
```

## Project Structure

```
data-analysis-tool/
├── src/
│   ├── scraper/
│   │   ├── __init__.py
│   │   └── scraper.py       # Web scraping functionality
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── processor.py     # Data processing and analysis
│   └── ui/
│       ├── __init__.py
│       └── app.py           # Streamlit UI application
├── tests/
│   ├── __init__.py
│   └── test_scraper.py      # Tests for scraper
├── venv/                    # Virtual environment
├── .gitignore               # Git ignore file
├── pyproject.toml           # Project configuration
├── README.md                # This file
└── requirements.txt         # Package dependencies
```

## Contributing

We welcome contributions to improve the project!

### Contribution Guidelines

1. **Fork the Repository**: Create your own fork of the project
2. **Create a Branch**: Make your changes in a new branch
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Follow Code Style**: Adhere to the project's coding standards
4. **Write Tests**: Add tests for new functionality
5. **Document Changes**: Update documentation as needed
6. **Submit a Pull Request**: Open a PR with a clear description of your changes

### Setting Up for Development

```bash
# Clone your fork
git clone https://github.com/yourusername/data-analysis-tool.git

# Add upstream remote
git remote add upstream https://github.com/original/data-analysis-tool.git

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Description of changes"

# Push to your fork
git push origin feature/your-feature-name
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

