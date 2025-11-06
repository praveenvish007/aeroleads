# autodialer.py
# Simple autodialer simulator for a VS Code assignment.
# • Generates 100 fake Indian toll‑free numbers
# • Calls them one‑by‑one with random outcomes
# • AI‑prompt: “make a call to +9118001234567”
# • Real‑time stats + CSV log
# • No Twilio, no OpenAI, no database, no external packages

import csv
import random
import re
import time
from datetime import datetime

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
FAKE_COUNT = 100                # default batch size
OUTPUT_CSV = "call_logs.csv"
AI_GREETINGS = [
    "Hello, this is an AI test call from the autodialer.",
    "Namaste! Autodialer AI checking the line – all good?",
    "Hi there! This is a simulated AI voice call.",
    "Greetings from the autodialer – just a quick test.",
    "Hello! AI autodialer speaking. Have a great day!"
]
STATUSES = ["queued", "ringing", "answered", "completed", "failed", "busy", "no-answer"]
DURATION_RANGE = {
    "answered": (15, 45),   # seconds when answered
    "completed": (10, 30),
    "no-answer": (20, 20),
    "busy": (3, 5),
    "ringing": (5, 10),
    "queued": (0, 0),
    "failed": (0, 0)
}

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def generate_fake_numbers(count: int) -> list[str]:
    """+91 1800 xxxx xxxx  (fake toll‑free)"""
    nums = []
    for _ in range(count):
        part1 = random.randint(1000, 9999)
        part2 = random.randint(1000, 9999)
        nums.append(f"+911800{part1}{part2}")
    return nums


def simulate_call(number: str) -> dict:
    """Return a dict with simulated call details."""
    status = random.choice(STATUSES)

    low, high = DURATION_RANGE[status]
    duration = random.randint(low, high) if low != high else low

    spoken = random.choice(AI_GREETINGS) if status == "answered" else "N/A"

    call = {
        "number": number,
        "status": status,
        "duration_sec": duration,
        "spoken": spoken,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # visual feedback
    print(f"Calling {number} → {status} ({duration}s)")
    if status == "answered":
        print(f"   AI said: {spoken[:50]}{'...' if len(spoken)>50 else ''}")
    time.sleep(random.uniform(0.5, 1.5))   # keep it snappy
    return call


def parse_ai_prompt(text: str) -> str | None:
    """Return phone number if prompt matches, else None."""
    m = re.search(r"make a call to\s*(\+91[1-9]\d{9,12})", text, re.I)
    return m.group(1) if m else None


def save_logs(logs: list[dict]):
    if not logs:
        return
    keys = logs[0].keys()
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(logs)
    print(f"\nSaved {len(logs)} records to {OUTPUT_CSV}")


def print_stats(logs: list[dict]):
    if not logs:
        print("No calls yet.")
        return
    total = len(logs)
    counts = {}
    for c in logs:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    print("\n=== CALL STATISTICS ===")
    for st, cnt in counts.items():
        pct = cnt / total * 100
        print(f"{st.capitalize():10}: {cnt:3} ({pct:5.1f}%)")
    print("=======================\n")


# ----------------------------------------------------------------------
# Main menu loop
# ----------------------------------------------------------------------
def main():
    all_logs: list[dict] = []

    print("Autodialer Simulator (pure Python – no external services)")
    while True:
        print("\n--- Menu ---")
        print("1. Generate & call 100 fake numbers")
        print("2. Load numbers from numbers.txt & call")
        print("3. AI prompt (e.g. 'make a call to +9118001234567')")
        print("4. Show current stats")
        print("5. Save logs & quit")
        choice = input("Choose (1‑5): ").strip()

        if choice == "1":
            numbers = generate_fake_numbers(FAKE_COUNT)
            print(f"\nStarting batch of {len(numbers)} calls …")
            for n in numbers:
                all_logs.append(simulate_call(n))

        elif choice == "2":
            try:
                with open("numbers.txt", "r", encoding="utf-8") as f:
                    numbers = [line.strip() for line in f if line.strip().startswith("+91")]
                if not numbers:
                    print("numbers.txt is empty or has no +91 numbers.")
                    continue
                print(f"Loaded {len(numbers)} numbers – calling …")
                for n in numbers:
                    all_logs.append(simulate_call(n))
            except FileNotFoundError:
                print("numbers.txt not found – create it with one number per line.")

        elif choice == "3":
            prompt = input("Enter prompt: ").strip()
            num = parse_ai_prompt(prompt)
            if num:
                print(f"AI request → {num}")
                all_logs.append(simulate_call(num))
            else:
                print("Invalid prompt. Example: make a call to +9118001234567")

        elif choice == "4":
            print_stats(all_logs)

        elif choice == "5":
            save_logs(all_logs)
            print("Goodbye!")
            break

        else:
            print("Invalid option – try again.")


if __name__ == "__main__":
    main()