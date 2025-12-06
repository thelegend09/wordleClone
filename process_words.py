
import json

def is_likely_proper_noun(word):
    # Heuristic: mostly already lowercase in file, but just in case
    return False

def is_likely_plural_or_conjugated(word):
    # Very basic heuristics for 5-letter French words
    # Ends in 's': Plurals (pommes) or tu-form verbs (joues) or singulars (temps, corps)
    # Ends in 'ez': Vous form (jouez) or noun (nez - 3 letters)
    # Ends in 'nt': Plural verbs (rient)
    
    if word.endswith('s'):
        # Exception list of common singular words ending in s
        exceptions = ["temps", "corps", "repas", "moisc", "cours", "souris", "velours", "tapis", "puits", "chaos", "os", "as", "buis"] # some are not 5 letters, handled by length check
        if word not in exceptions:
            return True
            
    if word.endswith('ez'):
        # Exception: assez, chez, nez (3)
        exceptions = ["assez"]
        if word not in exceptions:
            return True

    return False

def main():
    try:
        with open('words_raw.txt', 'r', encoding='utf-8') as f:
            raw_content = f.read()
            
        # The file seems to be new-line separated, maybe some lines have cleanup needed
        words = [w.strip().lower() for w in raw_content.splitlines() if w.strip()]
        
        valid_guesses = []
        target_words = []
        
        for word in words:
            if len(word) != 5:
                continue
            
            # Allow only a-z and accented chars (which should be in utf-8)
            # But converting accents to normal might be needed if we want strict [a-z]
            # Wordle usually maps accents to base letters for input, but displays them?
            # Or standard French Wordle keeps accents? 
            # "Le Mot" keeps accents on keyboard or maps them? 
            # For simplicity in this clone, let's normalize to no-accents for logic?
            # Or keep accents? The user didn't specify. 
            # Prompt: "French Wordle clone".
            # Standard French wordles often handle accents by accepting the non-accented char.
            # Let's keep accents in the word list for display, but logic might handle them.
            
            valid_guesses.append(word)
            
            if not is_likely_plural_or_conjugated(word):
                target_words.append(word)
        
        # Remove duplicates
        valid_guesses = sorted(list(set(valid_guesses)))
        target_words = sorted(list(set(target_words)))
        
        js_content = f"""
// Auto-generated word lists
const TARGET_WORDS = {json.dumps(target_words, ensure_ascii=False)};
const VALID_GUESSES = {json.dumps(valid_guesses, ensure_ascii=False)};
"""
        
        with open('words.js', 'w', encoding='utf-8') as f:
            f.write(js_content)
            
        print(f"Processed {len(valid_guesses)} valid guesses.")
        print(f"Filtered down to {len(target_words)} target words.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
