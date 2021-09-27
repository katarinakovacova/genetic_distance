import os
import json


taxonomy_file = 'taxonomy/ott3.2/taxonomy.tsv'

is_header = True
genus = set()

with open(taxonomy_file, 'r') as f:
    for row in f:
        row = row.strip()
        items = [s.strip() for s in row.split('|')]
        if is_header:
            columns = items
            is_header = False
        else:
            d = dict(zip(columns, items))
            if d['rank'] == 'genus':
                genus.add(d['name'])

mimicry_files = [s for s in os.listdir('mimicry') if s.endswith('.json')]

for mf in mimicry_files:
    path = os.path.join('mimicry', mf)

    with open(path, 'r') as f:
        data = json.loads(f.read())
        
    if not data['mimetic']['genus'] in genus:
        print('mimetic genus not found:', data['mimetic']['genus'])
        
    for model in data['model']:
        if not model['genus'] in genus:
            print('model genus not found:', model['genus'])
