from wordfreq import word_frequency

#  get list from data/french_words_raw.txt
with open("data/french_words_raw.txt", "r", encoding="utf-8") as f:
    words = [line.strip() for line in f if line.strip()]

filtered = [w for w in words if word_frequency(w, 'fr') > 1e-7]

print(f"Filtered {len(filtered)} words out of {len(words)} total")
print(filtered)