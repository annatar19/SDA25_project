# Just to check if the headers are consistent.
import csv
import glob
import re

ATP_PATH = "../../data/tennis_atp_data/unaltered_data/*"
WTA_PATH = "../../data/tennis_wta_data/unaltered_data/*"
TML_PATH = "../../data/tennis_tml_data/unaltered_data/*"
PATHS=[ATP_PATH, WTA_PATH, TML_PATH]
# Matches any filename and stores the name in an fn capture group.
match_fn_pattern = re.compile(r"/(?P<fn>[^/]*).csv")

header_groups=dict()
for path in PATHS:
    fns = glob.glob(path)
    for fn in fns:
        match = re.search(match_fn_pattern, fn)
        if match:
            try:
                with open(fn, 'r', newline='') as file:
                    reader = csv.reader(file)
                    column_names = next(reader)
                    column_names.sort()
                    column_names=",".join(column_names)
                    # print(f"Extracted columns from {match.group("fn")}: {column_names}")
                    if column_names not in header_groups:
                        header_groups[column_names] = []
                    header_groups[column_names].append(match.group("fn"))
            except Exception as e:
                        print(f"Error processing {fn}: {e}")
    print(f"Groups in {path}:")
    for k, column_group in header_groups.items():
        group_name=[]
        for column_name in column_group:
            for i, c in enumerate(column_name):
                if i == len(group_name):
                    group_name.append(c)
                else:
                    if group_name[i]!="c":
                        group_name[i]="X"
        print(f"{"".join(group_name)} {len(column_group)} files.")
