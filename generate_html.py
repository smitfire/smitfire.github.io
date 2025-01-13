import csv

def csv_to_html(csv_file, html_file):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)

        rows = [row for row in reader]

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Saved Jobs</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    </head>
    <body class="bg-gray-100">
        <div class="container mx-auto py-8">
            <h1 class="text-3xl font-bold mb-6">Saved Jobs</h1>
            <div class="overflow-x-auto">
                <table class="min-w-full bg-white border border-gray-200">
                    <thead>
                        <tr>
    """

    for header in headers:
        html_content += f'<th class="py-2 px-4 border-b">{header}</th>'

    html_content += """
                        </tr>
                    </thead>
                    <tbody>
    """

    for row in rows:
        html_content += '<tr>'
        for i, cell in enumerate(row):
            if i == 3:  # Assuming the URL is in the 4th column
                html_content += f'<td class="py-2 px-4 border-b"><a href="{cell}" class="text-blue-500 hover:underline">{cell}</a></td>'
            else:
                html_content += f'<td class="py-2 px-4 border-b">{cell}</td>'
        html_content += '</tr>'

    html_content += """
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """

    with open(html_file, 'w') as f:
        f.write(html_content)

# Example usage
csv_to_html('saved_jobs.csv', 'index.html')