from flask import Flask, render_template_string, Response
import matplotlib.pyplot as plt
import io
import os
import numpy as np
import pandas as pd

app = Flask(__name__)

CASE_PATHS = [
    f'../cases/case{i}/result_train/' for i in range(1, 4)
]

def get_avg_results(case_path):
    avg_results = []
    
    for file_name in sorted(os.listdir(case_path)):
        with open(os.path.join(case_path, file_name), 'r') as f:
            values = [float(line.strip()) for line in f.readlines()]
            avg_results.append(np.mean(values))
    
    return avg_results

@app.route('/plot/<int:case_number>')
def plot(case_number):
    if case_number not in [1, 2, 3]:
        return "Invalid case number. Please select 1, 2 or 3.", 400

    fig, ax = plt.subplots(figsize=(8, 6))
    avg_results = get_avg_results(CASE_PATHS[case_number - 1])
    avg_series = pd.Series(avg_results)
    
    # Trend using rolling average
    trend = avg_series.rolling(window=5).mean()

    # Detect outliers using IQR
    Q1 = avg_series.quantile(0.25)
    Q3 = avg_series.quantile(0.75)
    IQR = Q3 - Q1
    outliers = avg_series[(avg_series < (Q1 - 1.5 * IQR)) | (avg_series > (Q3 + 1.5 * IQR))]
    
    ax.plot(range(len(avg_results)), avg_results, label=f'Case {case_number}', color='blue')
    ax.plot(range(len(avg_results)), trend, label='Trend', color='green')
    ax.scatter(outliers.index, outliers.values, color='red', s=50)
    for idx in outliers.index:
        ax.text(idx, outliers[idx], str(idx), fontsize=10)

    ax.set_title(f'Средние результаты обучения для Case {case_number}')
    ax.set_xlabel('Номер файла')
    ax.set_ylabel('Среднее значение')
    ax.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    return Response(buf, content_type='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5602)
