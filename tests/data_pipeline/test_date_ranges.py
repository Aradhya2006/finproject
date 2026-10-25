from src.data.downloader import generate_six_month_ranges


ranges = generate_six_month_ranges(
    "01-01-2015",
    "05-09-2026",
)

print("Generated six-month ranges:")
print()

for start, end in ranges:
    print(start, "→", end)