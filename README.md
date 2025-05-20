# Housing Cost Analysis 

## Introduction

This project analyzes residential construction cost trends over the past two decades, with a particular focus on how these costs contribute to rising home prices. Using data from the National Association of Home Builders (NAHB), this analysis breaks down the components of new home construction costs, identifies key drivers of price increases, and highlights areas where cost-saving innovations could potentially improve housing affordability.

## Data Sources

This project utilizes data from several sources:

- **[NAHB's Cost of Constructing a Home-2024](https://www.nahb.org/-/media/NAHB/news-and-economics/docs/housing-economics-plus/special-studies/2025/special-study-cost-of-constructing-a-home-2024-january-2025.pdf?rev=00a42a1ce63b4a22a4dba9bda8af954b)** A survey of 4,000 US home builders on relevant costs associated with building single-family homes in the US.
- **[US Census All Households Income](https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-income-households/)** Median household income in the United States by year.

## Project Structure

The project follows a structure based on the Cookiecutter Data Science template:

```
├── LICENSE
├── Makefile           <- Makefile with convenience commands
├── README.md          <- This README file.
├── data
│   ├── external       <- Data from third party sources (if used).
│   ├── interim        <- Intermediate transformed data.
│   ├── processed      <- Final, canonical data sets.
│   └── raw            <- Original, immutable data dump.
│
├── notebooks          <- Jupyter notebooks for EDA and analysis.
│
├── pyproject.toml     <- Project configuration (dependencies, tools).
├── requirements.txt   <- pip requirements file (consider generating from pyproject.toml).
│
└─── housing_cost       <- Source code for this project.
    ├── __init__.py
    ├── config.py      <- Configuration settings.
    ├── dataset.py     <- Scripts for data download/generation.
    ├── pdf.py         <- PDF data extraction utilities.
    └── process/       <- Data processing and transformation scripts.
```


## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd housing_cost
    ```

2.  **Set up a Python virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Setup AWS**
This project uses AWS for extracting data from PDFs. For this to work, you need to install and configure the AWS CLI. Visit the [AWS documentation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) for detailed instructions.

## Usage

This project user Typer to provide a simple CLI interface for executing analysis workflows.

### Data Processing
All commands for downloading and processing the datasets can be found in `housing_cost/dataset.py`. To prepare the final, cleaned datasets execute the following commands from the root directory:

1) **download**: Download the source datasets.
```python
python housing_cost/dataset.py download
```

2) **parse**: Parse table data from PDF files.
```python
python housing_cost/dataset.py parse 
```

3) **process**: Process the collected data into cleaned datasets in the `data/processed` directory.
```python
python housing_cost/dataset.py process 
```

## Key Findings

- Construction Costs Dominate Home Prices: Construction costs account for 64.4% of new home sales prices in 2024, with these costs having grown 33.8% in inflation-adjusted terms over the past two decades.
- Cost Concentration: Nearly 50% of all construction costs are concentrated in just a few categories, with framing, foundations, and major systems rough-ins (electrical, plumbing, and HVAC) representing the largest components.
- Specialized Trade Cost Surge: The most dramatic cost increases over the past decade have been in specialized trades, with major systems rough-ins (electrical, plumbing, and HVAC) nearly doubling in inflation-adjusted terms from 2013 to 2024.
- Affordability Implications: The analysis suggests that innovations targeting the highest-cost components (particularly framing, foundations, and specialized systems) could have the greatest impact on improving housing affordability.