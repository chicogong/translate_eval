import re
import os

def setup_project():
    """
    Creates directories and extracts prompts from README.md.
    """
    print("Setting up project structure...")
    # Create directories
    os.makedirs("../evaluation/prompts", exist_ok=True)
    os.makedirs("testcases", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: README.md not found. Please make sure the file is in the root directory.")
        return

    lang_map = {
        "中文": "zh",
        "英文": "en",
        "西班牙语": "es",
        "葡萄牙语": "pt",
        "日语": "ja",
    }

    # Regex to find prompts
    prompt_regex = re.compile(r"### \d+\. ([\u4e00-\u9fa5]+)→([\u4e00-\u9fa5]+)\s*```\s*(.*?)\s*```", re.DOTALL)

    prompts = prompt_regex.finditer(content)

    count = 0
    for match in prompts:
        source_lang_zh, target_lang_zh, prompt_text = match.groups()
        source_lang = lang_map.get(source_lang_zh)
        target_lang = lang_map.get(target_lang_zh)

        if source_lang and target_lang:
            filename = f"../evaluation/prompts/{source_lang}-{target_lang}.txt"
            
            # Clean up the prompt text and replace the placeholder
            cleaned_prompt = re.sub(r"SOURCE TEXT:\s*\{\{.*?\}\}", "SOURCE TEXT:\n{{source_text}}", prompt_text)
            
            with open(filename, "w", encoding="utf-8") as pf:
                pf.write(cleaned_prompt.strip())
            count += 1
    
    print(f"Successfully extracted and created {count} prompt files in 'evaluation/prompts/' directory.")

    # Create placeholder test cases
    print("Creating placeholder test cases...")
    test_cases = {
        "zh": "你好世界！",
        "en": "Hello, world!",
        "es": "¡Hola, mundo!",
        "pt": "Olá, Mundo!",
        "ja": "こんにちは、世界！"
    }
    for lang_code, text in test_cases.items():
        test_dir = f"testcases/{lang_code}"
        os.makedirs(test_dir, exist_ok=True)
        with open(f"{test_dir}/sample.txt", "w", encoding="utf-8") as tf:
            tf.write(text)
    
    print("Placeholder test cases created in 'testcases/' directory. You can now add your own test files.")

if __name__ == "__main__":
    setup_project() 