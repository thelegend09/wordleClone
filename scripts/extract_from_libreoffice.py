#!/usr/bin/env python3
"""
Extract French dictionary from LibreOffice Hunspell dictionary
Finds fr_FR.dic automatically and extracts 5-letter words
"""

import os
import sys
from pathlib import Path
from collections import defaultdict

class LibreOfficeExtractor:
    """Extract French words from LibreOffice Hunspell dictionary"""

    def __init__(self):
        self.stats = defaultdict(int)
        self.words = set()

    def find_libreoffice_dict(self):
        """Find LibreOffice French dictionary"""
        print("🔍 Searching for LibreOffice French dictionary...")
        print(f"📍 Current working directory: {Path.cwd()}")
        print(f"📍 Script directory: {Path(__file__).parent}")

        # Check data directory
        data_dic = Path(__file__).parent.parent / "data" / "fr_FR.dic"
        print(f"🔎 Checking data directory: {data_dic}")
        if data_dic.exists():
            print(f"✅ Found in data directory: {data_dic}")
            return str(data_dic)
            
        # Check current directory
        cwd_dic = Path.cwd() / "fr_FR.dic"
        print(f"🔎 Checking: {cwd_dic}")
        if cwd_dic.exists():
            print(f"✅ Found in current directory: {cwd_dic}")
            return str(cwd_dic)
        
        # Check script directory
        script_dic = Path(__file__).parent / "fr_FR.dic"
        print(f"🔎 Checking script directory: {script_dic}")
        if script_dic.exists():
            print(f"✅ Found in script directory: {script_dic}")
            return str(script_dic)

        search_paths = [
            # Windows common locations
            Path("C:/Program Files/LibreOffice/share/dictionaries/fr_FR"),
            Path("C:/Program Files (x86)/LibreOffice/share/dictionaries/fr_FR"),

            # macOS
            Path.home() / "Applications" / "LibreOffice.app" / "Contents" / "Resources" / "dictionaries" / "fr_FR",
            Path("/Applications/LibreOffice.app/Contents/Resources/dictionaries/fr_FR"),

            # Linux common locations
            Path("/usr/share/hunspell"),
            Path("/usr/share/dict"),
            Path("/opt/libreoffice/share/dictionaries/fr_FR"),
            Path(os.path.expanduser("~/.local/share/hunspell")),
        ]

        print("\n📂 Checking common LibreOffice locations...")

        for path in search_paths:
            if path.exists():
                dic_file = path / "fr_FR.dic"
                if dic_file.exists():
                    print(f"✅ Found: {dic_file}")
                    return str(dic_file)

        print("\n❌ LibreOffice French dictionary not found!")
        print("\n💡 Solutions:")
        print("   1. Place fr_FR.dic in the current directory")
        print("   2. Install LibreOffice: brew install libreoffice (macOS)")
        print("   3. Or: sudo apt-get install libreoffice (Linux)")
        print("   4. Manually: python extract_from_libreoffice.py /path/to/fr_FR.dic")

        return None

    def extract_from_dic(self, dic_file):
        """Extract words from Hunspell .dic file"""
        # Normalize to Path and expand user/resolve relative paths
        dic_path = Path(dic_file).expanduser()
        try:
            dic_path = dic_path.resolve()
        except Exception:
            # If resolve() fails on broken symlinks or special paths, keep expanded path
            pass

        print(f"\n📖 Reading dictionary from: {dic_path}")

        if not dic_path.exists():
            print(f"❌ File not found: {dic_path}")
            return False

        try:
            with dic_path.open('r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            # First line is word count
            word_count = int(lines[0].strip()) if lines else 0
            print(f"   Dictionary contains ~{word_count:,} words")

            # Extract words (remove inflection tags)
            print(f"\n⚙️  Extracting words...")

            processed = 0
            for line in lines[1:]:
                processed += 1

                if processed % 50000 == 0:
                    print(f"   Progress: {processed:,} lines, {len(self.words):,} words")

                # Hunspell format: word/tags
                word = line.strip().split('/')[0].lower()

                if word and len(word) >= 1:
                    self.words.add(word)
                    self.stats['total_extracted'] += 1

            print(f"✅ Extracted {len(self.words):,} total words")
            return True

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def filter_5letter_words(self):
        """Filter to keep only 5-letter words, expanding ligatures first"""
        print(f"\n🔤 Filtering to 5-letter words...")

        five_letter = set()

        for word in self.words:
            # First, expand ligatures
            expanded_word = self._expand_ligatures(word)

            # Check if expanded word is exactly 5 letters
            if len(expanded_word) == 5:
                # Allow French accented characters and expanded ligatures
                if all(c.isalpha() or c in 'àâäéèêëïîôöœùûüæçñ' for c in word):
                    # Store the expanded version
                    five_letter.add(expanded_word)
                    self.stats['five_letter'] += 1

        self.words = five_letter

        print(f"✅ Found {len(self.words):,} five-letter words (ligatures expanded)")
        return True

    def _expand_ligatures(self, word: str) -> str:
        """Expand French ligatures to their multi-character forms"""
        ligature_map = {
            'œ': 'oe',
            'æ': 'ae',
            'ﬁ': 'fi',
            'ﬂ': 'fl',
        }

        expanded = word
        for ligature, expansion in ligature_map.items():
            expanded = expanded.replace(ligature, expansion)

        return expanded

    def save_to_file(self, filename=None):
        """Save extracted words to file"""
        if filename is None:
            # Save to data directory relative to script
            filename = Path(__file__).parent.parent / "data" / "french_words_raw.txt"

        print(f"\n💾 Saving to {filename}...")

        try:
            filename = Path(filename)
            # Ensure parent directory exists
            filename.parent.mkdir(parents=True, exist_ok=True)

            with open(filename, 'w', encoding='utf-8') as f:
                for word in sorted(self.words):
                    f.write(word + '\n')

            print(f"✅ Saved {len(self.words):,} words")
            return True

        except Exception as e:
            print(f"❌ Error saving: {e}")
            return False

    def print_stats(self):
        """Print statistics"""
        print("\n" + "="*70)
        print("EXTRACTION STATISTICS")
        print("="*70)
        print(f"Total words extracted:     {self.stats['total_extracted']:,}")
        print(f"Five-letter words:         {self.stats['five_letter']:,}")
        print(f"Final count:               {len(self.words):,}")
        print("="*70)

    def run(self, dic_path=None):
        """Run complete extraction"""
        print("="*70)
        print("LIBREOFFICE DICTIONARY EXTRACTOR")
        print("="*70)

        if dic_path:
            dic_file = dic_path
            print(f"📖 Using provided path: {dic_file}")
        else:
            dic_file = self.find_libreoffice_dict()

        if not dic_file:
            return False

        if not self.extract_from_dic(dic_file):
            return False

        if not self.filter_5letter_words():
            return False

        self.print_stats()

        if self.save_to_file():
            print("\n✅ DONE!")
            print("\n📝 Next step:")
            print("   cd scripts && python smart_filter.py")
            return True

        return False


if __name__ == "__main__":
    extractor = LibreOfficeExtractor()
    dic_path = sys.argv[1] if len(sys.argv) > 1 else None
    success = extractor.run(dic_path)

    if not success:
        print("\n❌ Extraction failed")
