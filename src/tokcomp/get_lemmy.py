import json
import urllib.request
import time
import os
import concurrent.futures
import argparse

def fetch_page(page, url, headers, min_words):
    req_url = f"{url}?limit=50&page={page}&sort=Hot"
    req = urllib.request.Request(req_url, headers=headers)
    page_posts = []
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        for item in data.get('posts', []):
            post = item.get('post', {})
            community = item.get('community', {})
            
            body = post.get('body')
            if not body:
                continue
                
            word_count = len(body.split())
            if word_count >= min_words:
                post_data = {
                    "id": f"lemmy.world_{post.get('id')}",
                    "platform": "fediverse/lemmy",
                    "instance": "lemmy.world",
                    "community": community.get('name', ''),
                    "title": post.get('name', ''),
                    "word_count": word_count,
                    "original_text": body
                }
                page_posts.append(post_data)
        return page_posts
    except Exception as e:
        print(f"Error fetching page {page}: {e}")
        return []

def fetch_lemmy_posts(limit=100, min_words=50):
    url = "https://lemmy.world/api/v3/post/list"
    posts_collected = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
    }
    
    print(f"Fetching up to {limit} Lemmy posts with a minimum of {min_words} words...")
    
    page = 1
    batch_size = 16
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
        while len(posts_collected) < limit:
            futures = [executor.submit(fetch_page, p, url, headers, min_words) for p in range(page, page + batch_size)]
            
            for future in concurrent.futures.as_completed(futures):
                page_posts = future.result()
                for post in page_posts:
                    if not any(p['id'] == post['id'] for p in posts_collected):
                        posts_collected.append(post)
                        if len(posts_collected) >= limit:
                            break
                if len(posts_collected) >= limit:
                    break
                    
            print(f"Fetched up to page {page + batch_size - 1}. Collected {len(posts_collected)}/{limit} posts.")
            page += batch_size
            time.sleep(1)
            
    return posts_collected[:limit]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch posts from Lemmy.')
    parser.add_argument('--limit', type=int, default=100, help='Number of posts to fetch')
    parser.add_argument('--min_words', type=int, default=100, help='Minimum words per post')
    args = parser.parse_args()
    
    limit = args.limit
    min_words = args.min_words
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    output_file = os.path.join(project_root, 'data', f'posts_{limit}.json')
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    posts = fetch_lemmy_posts(limit=limit, min_words=min_words)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
        
    print(f"Saved {len(posts)} posts to {output_file}")