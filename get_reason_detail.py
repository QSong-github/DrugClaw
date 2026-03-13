import pickle

with open('/blue/qsong1/wang.qing/AgentLLM/AgenticDrug/query_logs/detailed_logs/query_20260208_095030_358314.pkl', 'rb') as f:
    data = pickle.load(f)

print(type(data))
print(data.keys())
# print(data)
