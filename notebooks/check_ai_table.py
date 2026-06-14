import sys, os
sys.path.append(r'C:\Users\daipa\hisi_project')
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('sqlite:///C:/Users/daipa/hisi_project/database/hisi_panel.db')
with engine.connect() as conn:
    df = pd.read_sql('SELECT * FROM ai_vibrancy_readiness LIMIT 5', conn)
    print('Columns:', df.columns.tolist())
    print(df.head())
    count = pd.read_sql('SELECT COUNT(*) as n FROM ai_vibrancy_readiness', conn).iloc[0,0]
    print('Row count:', count)