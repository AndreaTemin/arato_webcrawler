

def save_page(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)