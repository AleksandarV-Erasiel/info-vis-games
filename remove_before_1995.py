import dash
from dash import dcc
from dash import html
from dash import Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
import csv


with open('90_accuracy_dataset.csv', 'r', encoding='utf-8') as csv_file, open('without_1995_games.csv', 'w', newline='', encoding='utf-8') as output_file:
    reader = csv.DictReader(csv_file)
    writer = csv.DictWriter(output_file, fieldnames=reader.fieldnames)
    writer.writeheader()
    
    for row in reader:
        year_str = row["Year"]
        if year_str:
            year = int(float(year_str))
            if year >= 1995:
                writer.writerow(row)
