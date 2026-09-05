from src.data.downloader import save_raw_file , list_raw_files

source_file = "data/raw/nse/Quote-Equity-TCS-EQ-01-01-2015-31-01-2015.csv"

saved_file = save_raw_file(source_file , "TCS")

print("Saved to:")
print(saved_file)


print()
print("TCS raw files:")

for file in list_raw_files("TCS"):
    print(file)