import json
import os
import csv

def calculate_averages(data):
    if not data:
        return 0, 0, 0
    total_compression = sum(item.get("compression_ratio", 0) for item in data)
    total_oov = sum(item.get("OOV_rate", 0) for item in data)
    total_speed = sum(item.get("processing_speed", 0) for item in data)
    
    count = len(data)
    return total_compression / count, total_oov / count, total_speed / count

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    data_dir = os.path.join(project_root, 'data')
    readme_path = os.path.join(project_root, 'README.md')
    
    tokenizers = ["BPE", "WordPiece", "SentencePiece", "Unigram", "Twokenize"]
    
    table_lines = [
        "## Tokenizer Comparison",
        "",
        "| Tokenizer | Avg Compression Ratio (Tokens/Word) | Avg OOV Rate | Avg Processing Speed (tokens/s) |",
        "|---|---|---|---|"
    ]
    
    for name in tokenizers:
        filename = f"tokenized_{name.lower()}.json"
        filepath = os.path.join(data_dir, filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            avg_comp, avg_oov, avg_speed = calculate_averages(data)
            
            # Format the values: OOV as percentage, others as float
            row = f"| {name} | {avg_comp:.4f} | {avg_oov:.4%} | {avg_speed:,.2f} |"
            table_lines.append(row)
        else:
            table_lines.append(f"| {name} | N/A | N/A | N/A |")
            
    table_content = "\n".join(table_lines) + "\n\n"
    
    # Calculate average compression ratio from cleaning
    cleaned_csv_path = os.path.join(data_dir, 'cleaned_posts.csv')
    if os.path.exists(cleaned_csv_path):
        total_ratio = 0
        count = 0
        with open(cleaned_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                orig = row['original_text']
                cleaned = row['cleaned_text']
                if len(orig) > 0:
                    total_ratio += len(cleaned) / len(orig)
                    count += 1
        
        if count > 0:
            avg_clean_ratio = total_ratio / count
            clean_info = f"### Data Cleaning Metrics\n* **Average Text Compression Ratio (Cleaned / Original length):** {avg_clean_ratio:.2%}\n\n"
            table_content += clean_info
            
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(table_content)
        
    print(f"Table appended to {readme_path}")

if __name__ == "__main__":
    main()
