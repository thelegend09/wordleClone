#!/usr/bin/env python3
"""
Smart Filter v2: Advanced filtering with spell-check validation
Rejects invalid words but validates them against French spell-checker
Keeps accents during filtering, removes them at the end
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Set

class SmartFilterV2:
    """Advanced filter with spell-check validation"""

    def __init__(self):
        self.words_raw = set()
        self.words_accepted = set()
        self.words_rejected = set()
        self.words_spellcheck_validated = set()
        self.stats = defaultdict(int)
        self.spellchecker = None
        self._init_spellchecker()

    def _init_spellchecker(self):
        """Initialize French spell-checker (pyenchant)"""
        print("📚 Initializing spell-checker...")

        try:
            import enchant
            self.spellchecker = enchant.Dict("fr_FR")
            print("✅ French spell-checker loaded (enchant)")
            return True
        except Exception as e:
            print(f"⚠️  Spell-checker validation disabled: {e}")
            print("   (Running with heuristics only)")
            self.spellchecker = None
            return False

    def load_words(self, filename=None):
        """Load raw words from file"""
        if filename is None:
            filename = Path(__file__).parent.parent / "data" / "french_words_raw.txt"
        
        print(f"\n📖 Loading words from {filename}...")

        if not Path(filename).exists():
            print(f"❌ File not found: {filename}")
            return False

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word:
                        self.words_raw.add(word)

            print(f"✅ Loaded {len(self.words_raw)} words")
            return True

        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return False

    # ... (other methods) ...

    def generate_js(self, filename='../words_smart_filtered.js'):
        """Generates the JavaScript file for the game"""
        print(f"\n💾 Generating JavaScript file: {filename}...")
        # ... (implementation) ...

    def save_rejected_words(self, filename='../data/words_rejected.txt'):
        """Save rejected words to file for review"""
        print(f"\n💾 Saving rejected words to: {filename}...")
        # ... (implementation) ...

    def save_validated_words(self, filename='../data/words_spellcheck_validated.txt'):
        """Save spell-check validated words for review"""
        print(f"\n💾 Saving spell-check validated words to: {filename}...")

    def _is_valid_word(self, word: str) -> bool:
        """Check if word passes initial heuristics"""

        # Criterion 1: Reject proper nouns (starts with uppercase)
        if word and word[0].isupper():
            self.stats['rejected_proper_noun'] += 1
            return False

        # Criterion 2: Length check
        if len(word) < 3 or len(word) > 5:
            self.stats['rejected_length'] += 1
            return False

        # Criterion 3: Must contain at least one vowel
        if not re.search(r'[aeiouyàâäéèêëïîôöœùûüæ]', word):
            self.stats['rejected_no_vowel'] += 1
            return False

        # Criterion 4: Reject excessive consonant clusters (>3)
        # if re.search(r'[bcdfghjklmnpqrstvwxyz]{4,}', word):
        #     self.stats['rejected_consonant_cluster'] += 1
        #     return False

        # Criterion 5: Reject excessive vowel clusters (>3)
        # if re.search(r'[aeiouyàâäéèêëïîôöœùûüæ]{4,}', word):
        #     self.stats['rejected_vowel_cluster'] += 1
        #     return False

        # Criterion 6: Reject double letters at start
        if len(word) > 1 and word[0] == word[1]:
            self.stats['rejected_double_start'] += 1
            return False

        # Criterion 7: Reject bad endings
        bad_endings = ['nm', 'bd', 'fh', 'jk', 'qx', 'zz', 'ww']
        if any(word.endswith(e) for e in bad_endings):
            self.stats['rejected_bad_ending'] += 1
            return False

        # Criterion 8: Must start with vowel OR consonant+vowel
        if not re.match(r'^([aeiouyàâäéèêëïîôöœùûüæ]|[bcdfghjklmnpqrstvwxyz]{1,3}[aeiouyàâäéèêëïîôöœùûüæ])', word):
            self.stats['rejected_bad_start'] += 1
            return False    

        return True

    def _normalize_word(self, word: str) -> str:
        """Remove accents from word (final step)"""
        accent_map = {
            'à': 'a', 'â': 'a', 'ä': 'a',
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'ï': 'i', 'î': 'i',
            'ô': 'o', 'ö': 'o', 'œ': 'oe',
            'ù': 'u', 'û': 'u', 'ü': 'u',
            'ç': 'c',
            'æ': 'ae'
        }

        normalized = ""
        for char in word.lower():
            normalized += accent_map.get(char, char)

        return normalized

    def _check_spellcheck(self, word: str) -> bool:
        """Check word against spell-checker"""
        if not self.spellchecker:
            return False

        try:
            return self.spellchecker.check(word)
        except:
            return False

    def filter_words(self):
        """Filter words with heuristics and spell-check validation"""
        print("\n⚙️  Filtering words with heuristics...")

        initial_accepted = set()
        to_spellcheck = set()

        for word in self.words_raw:
            if self._is_valid_word(word):
                initial_accepted.add(word)
            else:
                to_spellcheck.add(word)

        self.stats['initial_accepted'] = len(initial_accepted)
        self.words_accepted = initial_accepted

        # Spell-check validation for rejected words
        if self.spellchecker and to_spellcheck:
            print(f"\n🔤 Validating {len(to_spellcheck)} rejected words with spell-checker...")

            validated = 0
            for i, word in enumerate(to_spellcheck):
                if i % 500 == 0:
                    print(f"  Progress: {i}/{len(to_spellcheck)} checked, {validated} validated")

                if self._check_spellcheck(word):
                    self.words_spellcheck_validated.add(word)
                    self.words_accepted.add(word)
                    self.stats['spellcheck_validated'] += 1
                    validated += 1
                else:
                    self.words_rejected.add(word)

            print(f"✅ Spell-check validation complete: {validated} words validated")
        else:
            self.words_rejected = to_spellcheck

        # Final step: Remove accents
        print(f"\n🔤 Normalizing accents...")
        normalized_words = set()
        for word in self.words_accepted:
            normalized = self._normalize_word(word)
            normalized_words.add(normalized)

        self.words_accepted = normalized_words

        # Normalize rejected words too
        normalized_rejected = set()
        for word in self.words_rejected:
            normalized = self._normalize_word(word)
            normalized_rejected.add(normalized)

        self.words_rejected = normalized_rejected

        print(f"✅ Normalization complete")

    def print_stats(self):
        """Print filtering statistics"""
        print("\n" + "="*70)
        print("FILTERING STATISTICS")
        print("="*70)

        total_rejected = sum(v for k, v in self.stats.items() if k.startswith('rejected_'))
        total_heuristic_accepted = self.stats.get('initial_accepted', 0)
        total_spellcheck_validated = self.stats.get('spellcheck_validated', 0)

        print(f"\n📊 HEURISTIC FILTERING:")
        print(f"   ✅ Accepted by heuristics:  {total_heuristic_accepted:,}")
        print(f"   ❌ Rejected by heuristics:  {total_rejected:,}")

        if self.spellchecker:
            print(f"\n🔤 SPELL-CHECK VALIDATION:")
            print(f"   ✅ Validated and added:     {total_spellcheck_validated:,}")
            print(f"   ❌ Still rejected:          {len(self.words_rejected):,}")

        print(f"\n🎯 FINAL RESULT:")
        print(f"   ✅ Total accepted words:    {len(self.words_accepted):,}")
        print(f"   ❌ Total rejected words:    {len(self.words_rejected):,}")

        print("\n" + "="*70)

    def generate_js(self, filename=None):
        """Generates the JavaScript file for the game"""
        if filename is None:
            filename = Path(__file__).parent.parent / "words_smart_filtered.js"

        print(f"\n💾 Generating JavaScript file: {filename}...")

        words_sorted = sorted(self.words_accepted)

        js_content = "// French Wordle Words - Smart Filtered with Spell-Check\n"
        js_content += "// Generated automatically from LibreOffice dictionary\n"
        js_content += f"// Total words: {len(words_sorted)}\n"
        js_content += f"// (Accents normalized)\n\n"
        js_content += "const TARGET_WORDS = " + json.dumps(words_sorted, ensure_ascii=False) + ";\n\n"
        js_content += "const VALID_GUESSES = TARGET_WORDS;\n\n"
        js_content += "// Stats\n"
        js_content += f"console.log('Loaded {len(words_sorted)} French words (spell-check validated)');\n"
        js_content += f"console.log('Target words: ' + TARGET_WORDS.length);\n"
        js_content += f"console.log('Valid guesses: ' + VALID_GUESSES.length);\n"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(js_content)

            print(f"✅ Generated: {filename}")
            print(f"   Words: {len(words_sorted):,}")
            return True

        except Exception as e:
            print(f"❌ Error generating JS: {e}")
            return False

    def save_rejected_words(self, filename=None):
        """Save rejected words to file for review"""
        if filename is None:
            filename = Path(__file__).parent.parent / "data" / "words_rejected.txt"

        print(f"\n💾 Saving rejected words to: {filename}...")

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for word in sorted(self.words_rejected):
                    f.write(word + '\n')

            print(f"✅ Saved {len(self.words_rejected):,} rejected words")
            return True

        except Exception as e:
            print(f"❌ Error saving rejected words: {e}")
            return False

    def save_validated_words(self, filename=None):
        """Save spell-check validated words for review"""
        if filename is None:
            filename = Path(__file__).parent.parent / "data" / "words_spellcheck_validated.txt"

        print(f"\n💾 Saving spell-check validated words to: {filename}...")

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for word in sorted(self.words_spellcheck_validated):
                    f.write(word + '\n')

            print(f"✅ Saved {len(self.words_spellcheck_validated):,} validated words")
            return True

        except Exception as e:
            print(f"❌ Error saving validated words: {e}")
            return False

    def run(self):
        """Run complete filtering pipeline"""
        print("="*70)
        print("SMART FILTER v2 - French Words (with Spell-Check)")
        print("="*70)

        # Load
        if not self.load_words():
            return False

        # Filter
        self.filter_words()

        # Stats
        self.print_stats()

        # Save files
        success = True
        success = self.generate_js() and success
        success = self.save_rejected_words() and success

        if self.words_spellcheck_validated:
            success = self.save_validated_words() and success

        if success:
            print("\n✅ DONE!")
            print("\nFiles generated:")
            print("  • words_smart_filtered.js    - Ready to use in your game")
            print("  • words_rejected.txt         - Words that didn't pass (for review)")
            if self.words_spellcheck_validated:
                print("  • words_spellcheck_validated.txt - Words validated by spell-checker")

            print("\nYou can now use: <script src=\"words_smart_filtered.js\"></script>")
            return True

        return False


if __name__ == "__main__":
    filter_obj = SmartFilterV2()
    success = filter_obj.run()

    if not success:
        print("\n❌ Filtering failed")
