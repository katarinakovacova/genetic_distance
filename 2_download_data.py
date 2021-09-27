import json
import os
import shutil

import requests


mimicry_files = [s for s in os.listdir('mimicry') if s.endswith('.json')]

genus = set()
for mf in mimicry_files:
    path = os.path.join('mimicry', mf)

    with open(path, 'r') as f:
        data = json.loads(f.read())
        
    genus.add(data['mimetic']['genus'])
        
    for model in data['model']:
        genus.add(model['genus'])

for g in genus:
    url = 'http://www.boldsystems.org/index.php/API_Public/combined?taxon={}&format=json'.format(g)
    
    local_path = 'raw_data/{}.json'.format(g)
    
    if os.path.isfile(local_path):
        print('file {} already exists'.format(local_path))
        continue

    with requests.get(url=url, stream=True) as response:
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)
            print('success', g)
        else:
            print('failure', g)
