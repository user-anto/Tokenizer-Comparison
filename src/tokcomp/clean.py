import json
import os
import re
import csv
import string
import nltk

# Ensure stopwords are downloaded
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords

def clean_text(text):
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)
    # Remove words starting with @ or #
    text = re.sub(r'[@#]\w+', '', text)
    
    # Tokenize by splitting on whitespace to be safe and robust
    tokens = text.split()
        
    # Remove punctuation and stop words
    stop_words = set(stopwords.words('english'))
    punctuation = set(string.punctuation)
    
    cleaned_tokens = []
    for token in tokens:
        # Strip punctuation from the ends of the token
        token_clean = token.strip(string.punctuation)
        if not token_clean:
            continue
            
        token_lower = token_clean.lower()
        if token_lower in stop_words:
            continue
            
        cleaned_tokens.append(token_clean)
        
    return ' '.join(cleaned_tokens)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    data_file = os.path.join(project_root, 'data', 'posts_100.json')
    output_csv = os.path.join(project_root, 'data', 'cleaned_posts.csv')
    
    if not os.path.exists(data_file):
        print(f"Data file not found: {data_file}")
        import sys
        sys.exit(1)
        
    with open(data_file, 'r', encoding='utf-8') as f:
        posts = json.load(f)
        
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['original_text', 'cleaned_text'])
        
        for post in posts:
            orig = post.get('original_text', '')
            # Match compare_tokenizer behavior by slicing the first 512 chars if needed
            # The prompt says "takes all the 'original_text'". I will just use the full original text.
            cleaned = clean_text(orig)
            writer.writerow([orig, cleaned])
            
    print(f"Cleaned {len(posts)} posts and saved to {output_csv}")

if __name__ == '__main__':
    main()
