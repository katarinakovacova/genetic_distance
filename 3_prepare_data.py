import json
import os
from collections import Counter


genus = [f[:-5] for f in os.listdir('raw_data') if f.endswith('.json')]

with open('area.json', 'r') as f:
    areas = json.load(f)

for g in genus:
    with open('raw_data/{}.json'.format(g), 'r') as f:
        data = json.load(f)
    
    genus_data = []
    
    with open('cooked_data/{}.json'.format(g), 'w') as f:
        for t in data['bold_records']['records'].keys():
            if 'sequences' in data['bold_records']['records'][t].keys():
                sequences = data['bold_records']['records'][t]['sequences']['sequence']
                
                coi5p_sequences = [s for s in sequences if s['markercode'].upper() == 'COI-5P']
                
                assert len(coi5p_sequences) < 2
                
                if len(coi5p_sequences) == 1:
                    coi5p = coi5p_sequences[0]['nucleotides'].upper()

                    if 'collection_event' in data['bold_records']['records'][t].keys():
                        country = data['bold_records']['records'][t]['collection_event']['country']

                        if country != '':
                            info = {'id': t, 'coi5p': coi5p, 'area': areas[country]}
                            genus_data.append(info)
                            
        f.write(json.dumps(genus_data))
