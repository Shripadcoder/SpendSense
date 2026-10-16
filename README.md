
# SpendSense 💰

A personal expense analysis dashboard built with Python,
Streamlit, Pandas, and Plotly.

## Demo

![SpendSense Dashboard](Screenshot(263).png)
![SpendSense Analysis1](Screenshot(264).png)
![SpendSense Trend](Screenshot(265).png)
![SpendSense Transaction History](Screenshot(266).png)

## Features

- Upload expense data from CSV files
- Clean and validate expense records
- View total, average, and largest expenses
- Analyze spending by category
- Explore monthly spending trends
- Filter by dates and categories
- Export filtered transactions to CSV
- View automatic spending insights

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly

## Installation

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

   `python -m pip install -r requirements.txt`

4. Run the application:

   `python -m streamlit run app.py`

## CSV Format

Your CSV must contain these columns:

- date
- category
- description
- amount

See `sample_expenses.csv` for an example.

## Limitations

SpendSense analyzes user-provided expense records.
It does not connect to bank accounts or provide
professional financial advice.

## Future Improvements

- Monthly budget tracking
- Budget limit alerts
- Spending forecasts using machine learning
- PDF reports
- Persistent expense storage

## License

MIT
