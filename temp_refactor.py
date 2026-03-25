import json
import os

files = [
    r"c:\Users\Owner\OneDrive\Desktop\Research\n8n\daily_market_trend_agent_n8n.json",
    r"c:\Users\Owner\OneDrive\Desktop\Research\n8n\daily_market_trend_agent_n8n_openai.json"
]

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 1. Remove Hourly nodes
    data['nodes'] = [n for n in data['nodes'] if n['name'] not in ('Get SPX Hourly', 'Get VIX Hourly')]

    for node in data['nodes']:
        if node['name'] == 'Build Request URLs':
            code = node['parameters']['jsCode']
            code = code.replace("const hourlyFrom = shiftDays(now, -75);   // enough history for recent hourly regime\n", "")
            code = code.replace("spxHourlyUrl: aggUrl(spx, 'hour', hourlyFrom, now),\n    ", "")
            code = code.replace("vixHourlyUrl: aggUrl(vix, 'hour', hourlyFrom, now),\n    ", "")
            node['parameters']['jsCode'] = code
            
        elif node['name'] == 'Score Market':
            code = node['parameters']['jsCode']
            code = code.replace("const spxHourly = getBars('Get SPX Hourly');\n", "")
            code = code.replace("const vixHourly = getBars('Get VIX Hourly');\n", "")
            
            code = code.replace("const spxH = momentumZ(spxHourly, 6, 48);   // ~6 trading hours vs 2 trading days of hourly vol\n", "")
            code = code.replace("const vixH = momentumZ(vixHourly, 6, 48);\n", "")
            
            old_score = """const compositeScore =
  (0.40 * spxH) +
  (0.35 * spxD) +
  (0.25 * spxW) -
  (0.25 * vixH) -
  (0.20 * vixD) -
  (0.10 * vixW) +
  (0.20 * (newsSentiment * 3));"""
            new_score = """const compositeScore =
  (0.55 * spxD) +
  (0.35 * spxW) -
  (0.30 * vixD) -
  (0.15 * vixW) +
  (0.20 * (newsSentiment * 3));"""
            code = code.replace(old_score, new_score)
            
            code = code.replace("`• SPX hourly z-score: ${spxH.toFixed(2)}`,\n  ", "")
            code = code.replace("`• VIX hourly z-score: ${vixH.toFixed(2)}`,\n  ", "")
            
            code = code.replace("spx_hourly_z: Number(spxH.toFixed(4)),\n      ", "")
            code = code.replace("vix_hourly_z: Number(vixH.toFixed(4)),\n      ", "")
            
            code = code.replace("'Hourly, daily, and weekly SPX/VIX inputs", "'Daily and weekly SPX/VIX inputs")
            
            node['parameters']['jsCode'] = code

    # 3. Update Connections
    conns = data.get('connections', {})
    if 'Build Request URLs' in conns:
        # Build Request URLs -> Get SPX Daily
        conns['Build Request URLs']['main'][0][0]['node'] = 'Get SPX Daily'
    
    if 'Get SPX Hourly' in conns:
        del conns['Get SPX Hourly']
        
    if 'Get SPX Weekly' in conns:
        conns['Get SPX Weekly']['main'][0][0]['node'] = 'Get VIX Daily'
        
    if 'Get VIX Hourly' in conns:
        del conns['Get VIX Hourly']

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

print("Refactored workflows cleanly.")
