import re
import os
import pandas as pd
from tqdm import tqdm




heart_rate_avg_table = pd.DataFrame(columns=['username','user_id', 'date', 'steps', 'during_training'])

steps_table = pd.DataFrame(columns=['username','user_id', 'date', 'steps', 'during_training'])
# group so every day for every user has 1 row, or 2 if they had training that day (requires training times)


print(steps_table)