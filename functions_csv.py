

class Functions_Csv():
    def import_csv_cleaned(path_to_csv):
        print_debug = True
        print(f"--- Functions_Csv().import_csv_cleaned('{path_to_csv}') ---") if (print_debug == True) else False
        with open(path_to_csv, "r") as f:
            lines = f.readlines()
        lines_cleaned = []
        if (lines):
            header_cleaned = [x.strip() for x in lines[0].split(",")]
            lines_len = len(lines)
            if (lines_len > 1):
                for i, line in enumerate(lines[1::]):
                    line_split = line.split(",")
                    line_split_stripped = [x.strip() for x in line_split]
                    lines_cleaned.append(line_split_stripped)
        lines_cleaned_len = len(lines_cleaned)
        print(f"Header Cleaned: {header_cleaned}") if (print_debug == True) else False
        print(f"Lines Cleaned [{lines_cleaned_len}]:") if (print_debug == True) else False
        [print(f"- {x}") for x in lines_cleaned] if (print_debug == True) else False
        return header_cleaned, lines_cleaned_len, lines_cleaned
        