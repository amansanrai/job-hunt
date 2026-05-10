import re

# Simulate the exact error string from the GitHub Actions log
error = (
    'HTTP 422 Unprocessable Entity for https://api.airtable.com/v0/xxx/Applications. '
    'Response body: {"error":{"type":"UNKNOWN_FIELD_NAME","message":"Unknown field name: \\"Notes\\""}}'
)

print("Error string:")
print(error)
print()

patterns = [
    r'Unknown field name: \\"([^\\]+)\\"',
    r'Unknown field name: "([^"]+)"',
    r"UNKNOWN_FIELD_NAME.*?Unknown field name.*?(\w[\w ]+\w)",
]

for i, p in enumerate(patterns):
    m = re.search(p, error)
    if m:
        print(f"Pattern {i} matched: '{m.group(1)}'")
    else:
        print(f"Pattern {i}: no match")

# Also test with "Match Score"
error2 = error.replace("Notes", "Match Score")
print()
for i, p in enumerate(patterns):
    m = re.search(p, error2)
    if m:
        print(f"Pattern {i} (Match Score) matched: '{m.group(1)}'")
