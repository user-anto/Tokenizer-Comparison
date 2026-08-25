import json
import os
import time
import tiktoken
from transformers import AutoTokenizer
from nltk.tokenize import TweetTokenizer

def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def tokenize_and_measure(name, tokenizer_func, texts, is_twokenize=False):
    results = []
    
    for text in texts:
        words = text.split()
        num_words = len(words)
        if num_words == 0:
            continue
            
        start_time = time.perf_counter()
        tokens = tokenizer_func(text)
        end_time = time.perf_counter()
        
        processing_speed = end_time - start_time
        num_tokens = len(tokens)
        compression_ratio = num_tokens / num_words if num_words > 0 else 0
        
        oov_count = 0
        if not is_twokenize:
            # For tiktoken, OOV is 0. For transformers, count [UNK] or <unk>
            oov_count = sum(1 for t in tokens if t in ['[UNK]', '<unk>'])
        oov_rate = oov_count / num_tokens if num_tokens > 0 else 0
        
        results.append({
            "original_text": text,
            "tokenized_text": tokens,
            "compression_ratio": compression_ratio,
            "OOV_rate": oov_rate,
            "processing_speed": processing_speed
        })
        
    return results

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    data_file = os.path.join(project_root, 'data', 'posts_100.json')
    
    if not os.path.exists(data_file):
        print(f"Data file not found: {data_file}")
        import sys
        sys.exit(1)
        
    posts = load_data(data_file)
    texts = [p['original_text'][:512] for p in posts]
    
    print("Loading tokenizers...")
    
    # 1. BPE (tiktoken cl100k_base)
    enc = tiktoken.get_encoding("cl100k_base")
    def bpe_tokenize(text):
        token_ids = enc.encode(text)
        return [enc.decode([t]) for t in token_ids]
        
    # 2. WordPiece (bert-base-uncased)
    wp_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    def wp_tokenize(text):
        return wp_tokenizer.tokenize(text)
        
    # 3. SentencePiece (t5-base)
    sp_tokenizer = AutoTokenizer.from_pretrained("t5-base")
    def sp_tokenize(text):
        return sp_tokenizer.tokenize(text)
        
    # 4. Unigram (albert-base-v2)
    ug_tokenizer = AutoTokenizer.from_pretrained("albert-base-v2")
    def ug_tokenize(text):
        return ug_tokenizer.tokenize(text)
        
    # 5. Twokenize (NLTK TweetTokenizer)
    tweet_tokenizer = TweetTokenizer()
    def tw_tokenize(text):
        return tweet_tokenizer.tokenize(text)
        
    tokenizers = {
        "BPE": (bpe_tokenize, False),
        "WordPiece": (wp_tokenize, False),
        "SentencePiece": (sp_tokenize, False),
        "Unigram": (ug_tokenize, False),
        "Twokenize": (tw_tokenize, True)
    }
    
    for name, (tok_func, is_twok) in tokenizers.items():
        print(f"Tokenizing with {name}...")
        res = tokenize_and_measure(name, tok_func, texts, is_twokenize=is_twok)
        out_file = os.path.join(project_root, 'data', f'tokenized_{name.lower()}.json')
        save_json(res, out_file)
        print(f"Saved {len(res)} results to {out_file}")