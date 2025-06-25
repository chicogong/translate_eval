import os
from pathlib import Path

def setup_evaluation_files():
    """
    Creates the directory structure and placeholder files for reference translations.
    """
    print("Setting up directories for reference translations...")
    
    # Define languages
    languages = ["zh", "en", "es", "pt", "ja"]
    
    # Create reference directories and files
    base_ref_path = Path("references")
    base_ref_path.mkdir(exist_ok=True)
    
    for source_lang in languages:
        # Get number of lines from the source test suite
        source_test_suite = Path(f"testcases/{source_lang}/test_suite.txt")
        if not source_test_suite.exists():
            print(f"Warning: Source test suite not found for '{source_lang}', skipping.")
            continue
        
        try:
            with open(source_test_suite, 'r', encoding='utf-8') as f:
                num_lines = len(f.readlines())
        except Exception as e:
            print(f"Error reading {source_test_suite}: {e}")
            continue

        for target_lang in languages:
            if source_lang == target_lang:
                continue
            
            # Create directory like "references/zh-en"
            ref_dir = base_ref_path / f"{source_lang}-{target_lang}"
            ref_dir.mkdir(parents=True, exist_ok=True)
            
            # Create placeholder reference file
            ref_file = ref_dir / "test_suite.txt"
            
            # Do not overwrite if it already exists and has content
            if ref_file.exists() and ref_file.stat().st_size > 0:
                print(f"Skipping {ref_file}, as it already exists with content.")
                continue

            print(f"Creating placeholder reference file: {ref_file}")
            with open(ref_file, 'w', encoding='utf-8') as f:
                for i in range(1, num_lines + 1):
                    f.write(f"[Please add the expert human translation for line {i} here]\n")

    print("\nPlaceholder reference files created.")
    print("Please edit the files in the 'references/' directory to add your ground-truth translations.")

if __name__ == "__main__":
    setup_evaluation_files() 