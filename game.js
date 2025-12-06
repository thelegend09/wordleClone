
const WORD_LENGTH = 5;
const MAX_GUESSES = 6;
const FLIP_ANIMATION_DURATION = 500;
const DANCE_ANIMATION_DURATION = 500;

const keyboardLayout = [
    ["A", "Z", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["Q", "S", "D", "F", "G", "H", "J", "K", "L", "M"],
    ["Enter", "W", "X", "C", "V", "B", "N", "Delete"]
];

let targetWord = "";
let guesses = [];
let currentGuess = "";
let gameOver = false;
let animating = false;

// Statistics
let stats = {
    gamesPlayed: 0,
    gamesWon: 0,
    currentStreak: 0,
    maxStreak: 0,
    distribution: [0, 0, 0, 0, 0, 0]
};

document.addEventListener("DOMContentLoaded", () => {
    try {
        loadSettings();
    } catch (e) {
        console.error("Error loading settings:", e);
    }

    try {
        loadStats();
    } catch (e) {
        console.error("Error loading stats:", e);
    }

    try {
        initGame();
    } catch (e) {
        console.error("Error initializing game:", e);
    }

    setupKeyboard();
    setupEventListeners();
});

function initGame() {
    const gameBoard = document.getElementById("game-board");
    gameBoard.innerHTML = "";

    // Create grid
    for (let i = 0; i < MAX_GUESSES; i++) {
        const row = document.createElement("div");
        row.className = "row";
        for (let j = 0; j < WORD_LENGTH; j++) {
            const tile = document.createElement("div");
            tile.className = "tile";
            row.appendChild(tile);
        }
        gameBoard.appendChild(row);
    }

    // Pick random word
    // TARGET_WORDS and VALID_GUESSES are globals from words.js
    targetWord = TARGET_WORDS[Math.floor(Math.random() * TARGET_WORDS.length)];
    console.log("Target:", targetWord); // For debugging

    guesses = [];
    currentGuess = "";
    gameOver = false;
    animating = false;

    // Reset keyboard
    document.querySelectorAll(".key").forEach(key => {
        key.className = "key";
        if (key.dataset.key === "Enter" || key.dataset.key === "Delete") {
            key.classList.add("large");
        }
    });

    // Close modal if open
    document.getElementById("stats-modal").classList.add("hidden");
}

function setupKeyboard() {
    const keyboard = document.getElementById("keyboard");
    keyboard.innerHTML = "";

    keyboardLayout.forEach(rowKeys => {
        const row = document.createElement("div");
        row.className = "keyboard-row";

        rowKeys.forEach(key => {
            const button = document.createElement("button");
            button.textContent = key === "Delete" ? "⌫" : key;
            button.dataset.key = key;
            button.className = "key";
            if (key === "Enter" || key === "Delete") {
                button.classList.add("large");
            }
            button.addEventListener("click", () => handleInput(key));
            row.appendChild(button);
        });

        keyboard.appendChild(row);
    });
}

function setupEventListeners() {
    document.addEventListener("keydown", (e) => {
        if (gameOver || animating || e.altKey || e.ctrlKey || e.metaKey) return;

        const key = e.key;
        if (key === "Enter") {
            handleInput("Enter");
        } else if (key === "Backspace") {
            handleInput("Delete");
        } else if (/^[a-zA-Z]$/.test(key)) {
            handleInput(key.toUpperCase());
        }
    });

    document.getElementById("stats-btn").addEventListener("click", showStats);
    document.getElementById("help-btn").addEventListener("click", showHelp);
    document.getElementById("theme-btn").addEventListener("click", toggleTheme);

    document.querySelectorAll(".close-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".modal").forEach(m => m.classList.add("hidden"));
        });
    });

    document.getElementById("play-again-btn").addEventListener("click", initGame);
}

function showHelp() {
    document.getElementById("help-modal").classList.remove("hidden");
}

function handleInput(key) {
    if (gameOver || animating) return;

    if (key === "Enter") {
        submitGuess();
    } else if (key === "Delete") {
        if (currentGuess.length > 0) {
            currentGuess = currentGuess.slice(0, -1);
            updateGrid();
        }
    } else {
        if (currentGuess.length < WORD_LENGTH) {
            currentGuess += key;
            updateGrid();
        }
    }
}

function updateGrid() {
    const currentRow = document.getElementsByClassName("row")[guesses.length];
    const tiles = currentRow.getElementsByClassName("tile");

    for (let i = 0; i < WORD_LENGTH; i++) {
        tiles[i].textContent = currentGuess[i] || "";
        tiles[i].dataset.state = currentGuess[i] ? "active" : "empty";
        if (currentGuess[i]) {
            tiles[i].classList.add("pop");
            setTimeout(() => tiles[i].classList.remove("pop"), 100);
        }
    }
}

function showMessage(msg, duration = 2000) {
    const container = document.getElementById("message-container");
    const message = document.createElement("div");
    message.textContent = msg;
    message.className = "message";
    container.appendChild(message);

    setTimeout(() => {
        message.classList.add("fade-out");
        setTimeout(() => container.removeChild(message), 500);
    }, duration);
}

function shakeRow() {
    const currentRow = document.getElementsByClassName("row")[guesses.length];
    currentRow.classList.add("shake");
    setTimeout(() => currentRow.classList.remove("shake"), 500);
}

function submitGuess() {
    if (currentGuess.length !== WORD_LENGTH) {
        showMessage("Pas assez de lettres");
        shakeRow();
        return;
    }

    const guessLower = currentGuess.toLowerCase();
    if (!VALID_GUESSES.includes(guessLower) && !TARGET_WORDS.includes(guessLower)) {
        showMessage("Ce mot n'est pas dans la liste");
        shakeRow();
        return;
    }

    flipTiles();
}

function flipTiles() {
    animating = true;
    const guess = currentGuess.toLowerCase();
    const currentRow = document.getElementsByClassName("row")[guesses.length];
    const tiles = currentRow.getElementsByClassName("tile");

    const targetLetters = targetWord.split("");
    const guessLetters = guess.split("");
    const result = new Array(WORD_LENGTH).fill("absent");

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

    // Animation
    for (let i = 0; i < WORD_LENGTH; i++) {
        setTimeout(() => {
            tiles[i].classList.add("flip");
            tiles[i].dataset.state = result[i];

            // Update keyboard
            const key = document.querySelector(`.key[data-key="${guess[i].toUpperCase()}"]`);
            if (key) {
                const currentState = key.dataset.state;
                if (result[i] === "correct") {
                    key.dataset.state = "correct";
                } else if (result[i] === "present" && currentState !== "correct") {
                    key.dataset.state = "present";
                } else if (result[i] === "absent" && currentState !== "correct" && currentState !== "present") {
                    key.dataset.state = "absent";
                }
            }

            setTimeout(() => tiles[i].classList.remove("flip"), 250);
        }, i * 250);
    }

    setTimeout(() => {
        guesses.push(guess);

        if (guess === targetWord) {
            handleWin();
        } else if (guesses.length === MAX_GUESSES) {
            handleLoss();
        } else {
            currentGuess = "";
            animating = false;
        }
    }, WORD_LENGTH * 250);
}

function handleWin() {
    showMessage("Magnifique !", 3000);
    gameOver = true;
    animating = false;
    updateStats(true);
    setTimeout(showStats, 1500);
}

function handleLoss() {
    showMessage(targetWord.toUpperCase(), 10000); // Show word for longer
    gameOver = true;
    animating = false;
    updateStats(false);
    setTimeout(showStats, 1500);
}

function loadStats() {
    try {
        const saved = localStorage.getItem("wordle-fr-stats");
        if (saved) {
            stats = JSON.parse(saved);
        }
    } catch (e) {
        console.error("Failed to load stats, resetting:", e);
        // Optional: clear bad data
        // localStorage.removeItem("wordle-fr-stats");
    }
}

function updateStats(won) {
    stats.gamesPlayed++;
    if (won) {
        stats.gamesWon++;
        stats.currentStreak++;
    } else {
        stats.currentStreak = 0;
    }
    localStorage.setItem("wordle-fr-stats", JSON.stringify(stats));
}

function loadSettings() {
    const isLightMode = localStorage.getItem("wordle-fr-light-mode") === "true";
    if (isLightMode) {
        document.body.classList.add("light-mode");
    }
}

function toggleTheme() {
    document.body.classList.toggle("light-mode");
    const isLightMode = document.body.classList.contains("light-mode");
    localStorage.setItem("wordle-fr-light-mode", isLightMode);
}

function showStats() {
    document.getElementById("games-played").textContent = stats.gamesPlayed;
    const winPct = stats.gamesPlayed > 0
        ? Math.round((stats.gamesWon / stats.gamesPlayed) * 100)
        : 0;
    document.getElementById("win-pct").textContent = winPct;
    document.getElementById("current-streak").textContent = stats.currentStreak;
    document.getElementById("stats-modal").classList.remove("hidden");
}
