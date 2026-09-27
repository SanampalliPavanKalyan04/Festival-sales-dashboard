# Festival Pulse — India E-commerce Sales Dashboard

Analyzes two years (Jan2023–Dec2024) of daily Amazon.in/Flipkart-style
sales data, focused on how major Indian sale seasons—Republic Day Sale,
Holi Sale, Summer Sale, Independence Day Sale, Big Billion Days/Great
Indian Festival, Diwali Sale, Black Friday/Cyber Monday, and the Year-End
Sale — move revenue, discounting and returns compared to normal days.

The dataset is **synthetically generated** (not real marketplace data), so
you can regenerate it, tweak the festival calendar, or plug in your own CSV.

## What's inside

```
ecommerce-sales-dashboard/
├── data/
│   ├── generate_data.py     # builds the synthetic dataset
│   └── sales_data.csv       # generated output (11.7k rows)
├── analysis/
│   ├── analysis.py          # pandas analysis + chart export
│   └── charts/              # static PNG charts (generated)
├── dashboard/
│   ├── index.html           # interactive dashboard (Plotly.js)
│   └── data.js              # aggregated data consumed by the dashboard (generated)
├── requirements.txt
└── README.md
```

## Run it

```bash
pip install -r requirements.txt

# 1. Generate the dataset
python data/generate_data.py

# 2. Run the analysis (prints a report, saves charts, builds dashboard/data.js)
python analysis/analysis.py

# 3. Open the dashboard — no server needed
open dashboard/index.html        # macOS
xdg-open dashboard/index.html    # Linux
start dashboard/index.html       # Windows
```

Because `dashboard/index.html` loads `dashboard/data.js` as a plain script
tag, the dashboard also works out of the box on **GitHub Pages**: enable
Pages on this repo (Settings → Pages → deploy from the `main` branch, root
folder) and open `https://<you>.github.io/<repo>/dashboard/`.

## Key findings (from the generated sample)

- Festival days are only ~15% of the calendar but drive **~31% of total revenue**.
- **Big Billion Days / Great Indian Festival** and **Diwali Sale** are the two
  biggest revenue events by a wide margin.
- Discounts jump from ~10% on normal days to ~30-45%+ during major sales,
  and return rates roughly double during festival periods.
- **Mobiles** and **Electronics** dominate category revenue and lean most
  heavily on festival-period sales.
- Revenue grew ~14% year-over-year from 2023 to 2024.

## Customizing

- Edit the `FESTIVALS` list in `data/generate_data.py` to change sale dates,
  intensity multipliers, or discount ranges.
- Add/remove categories or adjust their base prices and demand weights in
  the same file.
- Swap in real data: replace `data/sales_data.csv` with your own file using
  the same columns (`date, platform, category, is_festival, festival_name,
  orders, units_sold, avg_discount_pct, revenue_inr, returns`) and re-run
  `analysis/analysis.py`.

