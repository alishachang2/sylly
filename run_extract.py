import sys, json
from backend.extract_parse import extract_pdf

if len(sys.argv) < 2:
    print(json.dumps({"error": "No file path"}))
    sys.exit(1)

file = sys.argv[1]

result = extract_pdf(file)

print(json.dumps(result))
