import json
import os
from collections import Counter 
import random
import subprocess
import sqlite3


random.seed(8)

MAX_ORIGIN = 200


def alignment(o1, o2):
    return subprocess.check_output(['alignment', o1['coi5p'], o2['coi5p']]).decode('utf-8').replace('.', '-').split('\n')[:2]


def is_same_area(o1, o2):
    a1 = o1['area']
    a2 = o2['area']

    if isinstance(a1, str) and isinstance(a2, str):
        return a1 == a2
    elif isinstance(a1, list) and isinstance(a2, str):
        return a2 in a1
    elif isinstance(a1, str) and isinstance(a2, list):
        return a1 in a2
    elif isinstance(a1, list) and isinstance(a2, list):
        return any(a in a2 for a in a1)
    else:
        raise Exception('Unknown area type')


def common_area(o1, o2):
    a1 = o1['area']
    a2 = o2['area']

    if isinstance(a1, str) and isinstance(a2, str):
        return a1
    elif isinstance(a1, list) and isinstance(a2, str):
        return a2
    elif isinstance(a1, str) and isinstance(a2, list):
        return a1
    elif isinstance(a1, list) and isinstance(a2, list):
        return ','.join(sorted(a1))
    else:
        raise Exception('Unknown area type')


mimicry = [f[:-5] for f in os.listdir('mimicry') if f.endswith('.json')]

mimicry_dict = {}

for file in mimicry:
    with open('mimicry/{}.json'.format(file), 'r') as f:
        data = json.load(f)

    mimetic = data['mimetic']['genus']
    models = [m['genus'] for m in data['model']]
    
    if mimetic in mimicry_dict.keys():
        for model in models:
            mimicry_dict[mimetic].append(model)
    else:
        mimicry_dict[mimetic] = models

conn = sqlite3.connect('database.db')
cur = conn.cursor()

genus = [f[:-5] for f in os.listdir('cooked_data') if f.endswith('.json')]

for i1 in range(len(genus)):
    g1 = genus[i1]
    
    with open('cooked_data/{}.json'.format(g1), 'r') as f:
        data1 = json.load(f)
        
    for i2 in range(i1, len(genus)):
        g2 = genus[i2]

        if g1 == g2:
            pass
        elif (g1 in mimicry_dict.keys()) or (g2 in mimicry_dict.keys()):
            if g1 in mimicry_dict.keys():
                mimetic = g1
                model = g2
            else:
                mimetic = g2
                model = g1
            
            if model not in mimicry_dict[mimetic]:
                continue        
        else:
            continue
        
        with open('cooked_data/{}.json'.format(g2), 'r') as f:
            data2 = json.load(f)

        print('{} {}'.format(g1, g2))

        table_id = '{}_{}'.format(g1.lower(), g2.lower())
        
        sql_table = "CREATE TABLE IF NOT EXISTS {} (pair_id TEXT UNIQUE, area TEXT, seq1 TEXT, seq2 TEXT);".format(table_id)
        
        cur.execute(sql_table)
        
        cur.execute('BEGIN;')

        # two small groups
        if (len(data1) < MAX_ORIGIN) and (len(data2) < MAX_ORIGIN):
            for j1 in range(len(data1)):
                origin1 = data1[j1]
                for j2 in range(len(data2)):
                    origin2 = data2[j2]
                    
                    if origin1['id'] == origin2['id']:
                        continue
                    
                    if is_same_area(origin1, origin2):
                        seq1, seq2 = alignment(origin1, origin2)
                        pair_id = '{}_{}'.format(*sorted([origin1['id'], origin2['id']]))
                        sql = 'INSERT INTO {} VALUES (?, ?, ?, ?) ON CONFLICT DO NOTHING;'.format(table_id)
                        cur.execute(sql, [pair_id, common_area(origin1, origin2), seq1, seq2])
                             
                    
        # one small and one big group
        elif (len(data1) < MAX_ORIGIN) or (len(data2) < MAX_ORIGIN):
            if len(data1) < len(data2):
                smaller = data1
                bigger = data2
            else:
                smaller = data2
                bigger = data1
                
            for origin1 in smaller:
                for _ in range(50):
                    origin2 = random.choice(bigger)
                    
                    if origin1['id'] == origin2['id']:
                        continue
                    
                    if is_same_area(origin1, origin2):
                        seq1, seq2 = alignment(origin1, origin2)
                        pair_id = '{}_{}'.format(*sorted([origin1['id'], origin2['id']]))
                        sql = 'INSERT INTO {} VALUES (?, ?, ?, ?) ON CONFLICT DO NOTHING;'.format(table_id)
                        cur.execute(sql, [pair_id, common_area(origin1, origin2), seq1, seq2])
                        break
                        
        # two big groups 
        else:
            step = int(len(data1) / MAX_ORIGIN)
            
            for origin1 in data1[::step]:
                for _ in range(50):
                    origin2 = random.choice(data2)
                    
                    if origin1['id'] == origin2['id']:
                        continue
                    
                    if is_same_area(origin1, origin2):
                        seq1, seq2 = alignment(origin1, origin2)
                        pair_id = '{}_{}'.format(*sorted([origin1['id'], origin2['id']]))
                        sql = 'INSERT INTO {} VALUES (?, ?, ?, ?) ON CONFLICT DO NOTHING;'.format(table_id)
                        cur.execute(sql, [pair_id, common_area(origin1, origin2), seq1, seq2])
                        break
        
        cur.execute('COMMIT;')
