
const WORD_LENGTH = 5;
const MAX_GUESSES = 6;

document.addEventListener('alpine:init', () => {
    Alpine.data('wordleGame', () => ({
        // Constants needing access in template
        keyboardLayout: [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
            ["Enter", "Z", "X", "C", "V", "B", "N", "M", "Delete"]
        ],

        // State
        targetWord: "",
        guesses: [], // Array of completed words
        currentGuess: [],
        focusedIndex: 0,
        gameOver: false,
        animating: false,

        // UI State
        board: [], // 6x5 grid of objects: { letter, state, pop, flip, shake }
        keyStates: {}, // Map of key -> state (correct, present, absent)
        messages: [],
        showHelp: false,
        showStats: false,

        // Stats
        stats: {
            gamesPlayed: 0,
            gamesWon: 0,
            currentStreak: 0,
            maxStreak: 0,
            distribution: [0, 0, 0, 0, 0, 0]
        },

        init() {
            this.loadSettings();
            this.loadStats();
            this.initGame();
        },

        initGame() {
            // Reset Game Logic
            // TARGET_WORDS and VALID_GUESSES are globally available from words.js
            this.targetWord = TARGET_WORDS[Math.floor(Math.random() * TARGET_WORDS.length)];
            console.log("Target:", this.targetWord);

            this.guesses = [];
            this.currentGuess = Array(WORD_LENGTH).fill("");
            this.focusedIndex = 0;
            this.gameOver = false;
            this.animating = false;
            this.showStats = false;
            this.keyStates = {};

            // Initialize Board State
            this.board = Array.from({ length: MAX_GUESSES }, () => ({
                shake: false,
                tiles: Array.from({ length: WORD_LENGTH }, () => ({
                    letter: '',
                    state: 'empty', // empty, active, absent, present, correct
                    pop: false,
                    flip: false
                }))
            }));
        },

        handleKeydown(e) {
            if (this.gameOver || this.animating || e.altKey || e.ctrlKey || e.metaKey) return;

            const key = e.key;
            if (key === "Enter") {
                this.handleInput("Enter");
            } else if (key === "Backspace") {
                this.handleInput("Delete");
            } else if (/^[a-zA-Z]$/.test(key)) {
                this.handleInput(key.toUpperCase());
            }
        },

        handleInput(key) {
            if (this.gameOver || this.animating) return;

            if (key === "Enter") {
                this.submitGuess();
            } else if (key === "Delete") {
                if (this.currentGuess[this.focusedIndex] !== "") {
                    // If current tile has letter, clear it
                    this.currentGuess[this.focusedIndex] = "";
                } else if (this.focusedIndex > 0) {
                    // If current empty, move back and clear previous
                    this.focusedIndex--;
                    this.currentGuess[this.focusedIndex] = "";
                }
                this.updateBoardUI();
            } else {
                // Letter input
                this.currentGuess[this.focusedIndex] = key;
                this.updateBoardUI(this.focusedIndex);

                // Advance cursor if not at end
                if (this.focusedIndex < WORD_LENGTH - 1) {
                    this.focusedIndex++;
                }
            }
        },

        selectTile(rowIndex, tileIndex) {
            if (rowIndex === this.guesses.length && !this.gameOver) {
                this.focusedIndex = tileIndex;
            }
        },

        updateBoardUI(popIndex = -1) {
            const rowIndex = this.guesses.length;
            const row = this.board[rowIndex];

            for (let i = 0; i < WORD_LENGTH; i++) {
                const char = this.currentGuess[i] || "";
                row.tiles[i].letter = char;
                row.tiles[i].state = char ? "active" : "empty";

                if (popIndex === i) {
                    row.tiles[i].pop = true;
                    setTimeout(() => { row.tiles[i].pop = false; }, 100);
                }
            }
        },

        submitGuess() {
            const guessStr = this.currentGuess.join("");
            if (guessStr.length !== WORD_LENGTH || this.currentGuess.includes("")) {
                this.showMessage("Pas assez de lettres");
                this.shakeRow();
                return;
            }

            const guessLower = guessStr.toLowerCase();
            if (!VALID_GUESSES.includes(guessLower) && !TARGET_WORDS.includes(guessLower)) {
                this.showMessage("Ce mot n'est pas dans la liste");
                this.shakeRow();
                return;
            }

            this.evaluateGuess(guessStr);
        },

        shakeRow() {
            const rowIndex = this.guesses.length;
            this.board[rowIndex].shake = true;
            setTimeout(() => {
                this.board[rowIndex].shake = false;
            }, 500);
        },

        evaluateGuess(guessStr) {
            this.animating = true;
            const guess = guessStr.toLowerCase();
            const targetLetters = this.targetWord.split("");
            const guessLetters = guess.split("");
            const result = new Array(WORD_LENGTH).fill("absent");
            const rowIndex = this.guesses.length;

            // First pass: Correct positions
            for (let i = 0; i < WORD_LENGTH; i++) {
                if (guessLetters[i] === targetLetters[i]) {
                    result[i] = "correct";
                    targetLetters[i] = null;
                }
            }

            // Second pass: Present elsewhere
            for (let i = 0; i < WORD_LENGTH; i++) {
                if (result[i] !== "correct") {
                    const index = targetLetters.indexOf(guessLetters[i]);
                    if (index !== -1) {
                        result[i] = "present";
                        targetLetters[index] = null;
                    }
                }
            }

            // Animate reveal
            for (let i = 0; i < WORD_LENGTH; i++) {
                setTimeout(() => {
                    const tile = this.board[rowIndex].tiles[i];
                    tile.flip = true;
                    tile.state = result[i];

                    // Update keyboard state
                    const keyChar = guess[i].toUpperCase();
                    const currentKeyState = this.keyStates[keyChar];

                    if (result[i] === "correct") {
                        this.keyStates[keyChar] = "correct";
                    } else if (result[i] === "present" && currentKeyState !== "correct") {
                        this.keyStates[keyChar] = "present";
                    } else if (result[i] === "absent" && currentKeyState !== "correct" && currentKeyState !== "present") {
                        this.keyStates[keyChar] = "absent";
                    }

                    setTimeout(() => { tile.flip = false; }, 250);
                }, i * 250);
            }

            setTimeout(() => {
                this.guesses.push(guess);

                if (guess === this.targetWord) {
                    this.handleWin();
                } else if (this.guesses.length === MAX_GUESSES) {
                    this.handleLoss();
                } else {
                    this.currentGuess = Array(WORD_LENGTH).fill("");
                    this.focusedIndex = 0;
                    this.animating = false;
                }
            }, WORD_LENGTH * 250);
        },

        handleWin() {
            this.showMessage("Magnifique !", 3000);
            this.gameOver = true;
            this.animating = false;
            this.updateStats(true);
            setTimeout(() => { this.showStats = true; }, 1500);
        },

        handleLoss() {
            // showMessage removed as word is dispayed permanently
            this.gameOver = true;
            this.animating = false;
            this.updateStats(false);
            setTimeout(() => { this.showStats = true; }, 1500);
        },

        showMessage(text, duration = 2000) {
            const id = Date.now();
            this.messages.push({ id, text, fadeOut: false });

            setTimeout(() => {
                const msg = this.messages.find(m => m.id === id);
                if (msg) msg.fadeOut = true;

                setTimeout(() => {
                    this.messages = this.messages.filter(m => m.id !== id);
                }, 500);
            }, duration);
        },

        loadSettings() {
            const isLightMode = localStorage.getItem("wordle-fr-light-mode") === "true";
            if (isLightMode) {
                document.body.classList.add("light-mode");
            }
        },

        toggleTheme() {
            document.body.classList.toggle("light-mode");
            const isLightMode = document.body.classList.contains("light-mode");
            localStorage.setItem("wordle-fr-light-mode", isLightMode);
        },

        loadStats() {
            try {
                const saved = localStorage.getItem("wordle-fr-stats");
                if (saved) {
                    this.stats = JSON.parse(saved);
                }
            } catch (e) {
                console.error("Failed to load stats:", e);
            }
        },

        updateStats(won) {
            this.stats.gamesPlayed++;
            if (won) {
                this.stats.gamesWon++;
                this.stats.currentStreak++;
            } else {
                this.stats.currentStreak = 0;
            }
            localStorage.setItem("wordle-fr-stats", JSON.stringify(this.stats));
        },

        get winPercentage() {
            return this.stats.gamesPlayed > 0
                ? Math.round((this.stats.gamesWon / this.stats.gamesPlayed) * 100)
                : 0;
        }
    }));
});
