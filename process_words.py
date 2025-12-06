
import json
import unicodedata

def remove_accents(input_str):
    # Handle ligatures manually
    input_str = input_str.replace('œ', 'oe').replace('æ', 'ae')
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def is_likely_proper_noun(word):
    # Common French proper nouns (names, cities, countries) to filter out
    # This list is manually curated based on common entries found in dictionaries
    proper_nouns = {
        # Cities (France & World)
        "paris", "lyon", "brest", "nancy", "lille", "metz", "rouen", "tours", "reims", "caen", 
        "dijon", "nimes", "arles", "evron", "melun", "naves", "nesle", "oiron", "royan", "sedan",
        "tulle", "ugine", "ussel", "yenne", "allos", "cluse", "dinan", "ernee", "isola", "trets",
        "tunis", "dubai", "tokyo", "milan", "vaduz", "sofia", "osaka", "turku", "dacca", "hanoi",
        "kyoto", "doha", "lima", "oslo", "riga", "rome", "seoul", "bern", 
        
        # Countries / Regions / Demonyms
        "italy", "chine", "grece", "japon", "maroc", "suede", "suisse", "syrie", "tchad", "yemen",
        "perse", "indes", "galles", "exode", "tibet", "nepal", "texas", "maine", 
        "kanak", "tutsi", "slave", "sarde", "maure", "kurde", "latino", "khmer", "azteque", "incas",
        
        # Names (Female)
        "alice", "chloe", "clara", "elena", "julia", "livia", "maeva", "sarah", "sofia", "adele",
        "ambre", "anais", "annie", "anouk", "marie", "leila", "lydie", "laure", "linda", "paola",
        "katia", "sonya", "helen", "greta", "sandy", "nancy", "lucie", "julie", "celia", "diane",
        "fanny", "flora", "manon", "ninon", "tanya", "kelly", "joyce", "eliza", "daisy", "cathy",
        "betty", "alida", "aglae", "irene", "edith", "ester", "agathe", "jeanne", "louise",
        
        # Names (Male)
        "angel", "bruno", "denis", "emile", "ethan", "felix", "henri", "james", "jules", "louis",
        "lucas", "nolan", "aaron", "david", "kevin", "steve", "serge", "cyril", "jason", "johan",
        "marco", "mateo", "oscar", "sacha", "simon", "teddy", "timon", "tommy", "willy", "yanis",
        "brian", "cedric", "damien", "dylan", "edwin", "frank", "gilles", "hervé", "jerry", "jimmy",
        "jonas", "keith", "larry", "maud", "mulan", "peter", "ralph", "robin", "ruben", "samuel",
        "tanguy", "terry", "walter", "wayne", "xavier", "yves", "alain", "boris", "colin", 
        
        # Mythology / Religion
        "allah", "jesus", "judas", "moise", "noel", "paques", "satan", "venus", "zeus", "hades", "thor",
        "shiva", "brahma", "vishnu", "buddha", "christ", "islam", "coran", "bible", "torah", "vada",
        
        # Misc Proper Nouns
        "pepsi", "coke", "fanta", "apple", "google", "linux", "skype", "twitter", "yahoo", "zoile",
        "boeing", "airbus", "nasa", "esa", "nato", "otan", "unesco",
        "navel", "diesel", "caddie", "scotch", "frigo", "karcher", "klaxon", "sopalin", "velux", "postit"
    }
    
    # Check strict match
    if word in proper_nouns:
        return True
        
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
            normalized_word = remove_accents(word)
            
            if len(normalized_word) != 5:
                continue
                
            if is_likely_proper_noun(normalized_word):
                continue
            
            # Now using normalized word for everything
            valid_guesses.append(normalized_word)
            
            if not is_likely_plural_or_conjugated(normalized_word):
                target_words.append(normalized_word)
        
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
