import gzip
import json
import os
import re
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "jananivasudevan4_data.json.gz"
OUTPUT_FOLDER = "HackerRank-Solutions"

# ============================================================
# CREATE FOLDERS
# ============================================================

base = Path(OUTPUT_FOLDER)

folders = {
    "python": base / "Python",
    "sql": base / "SQL",
    "problem_solving": base / "Problem_Solving",
    "other": base / "Other"
}

for folder in folders.values():
    folder.mkdir(parents=True, exist_ok=True)

# ============================================================
# LOAD HACKERRANK DATA
# ============================================================

print("Reading HackerRank data...")

with gzip.open(INPUT_FILE, "rt", encoding="utf-8") as file:
    data = json.load(file)

print("Data loaded successfully.")

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_filename(name):
    """Convert problem name into a safe filename."""

    name = str(name)

    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', '_', name)

    return name[:150]


def find_submissions(obj, results=None):
    """
    Recursively search the JSON data for objects that look
    like HackerRank submissions.
    """

    if results is None:
        results = []

    if isinstance(obj, dict):

        # Check whether this object resembles a submission
        keys = {str(k).lower() for k in obj.keys()}

        submission_indicators = {
            "code",
            "source_code",
            "language",
            "challenge",
            "problem",
            "status"
        }

        if len(keys.intersection(submission_indicators)) >= 2:
            results.append(obj)

        for value in obj.values():
            find_submissions(value, results)

    elif isinstance(obj, list):

        for item in obj:
            find_submissions(item, results)

    return results


# ============================================================
# FIND SUBMISSIONS
# ============================================================

print("Searching for submissions...")

submissions = find_submissions(data)

print(f"Possible submissions found: {len(submissions)}")

# ============================================================
# PROCESS SUBMISSIONS
# ============================================================

saved = 0

for index, submission in enumerate(submissions, start=1):

    # --------------------------------------------------------
    # Find code
    # --------------------------------------------------------

    code = (
        submission.get("code")
        or submission.get("source_code")
        or submission.get("sourceCode")
        or submission.get("answer")
    )

    if not code:
        continue

    # --------------------------------------------------------
    # Find problem name
    # --------------------------------------------------------

    challenge = (
        submission.get("challenge")
        or submission.get("problem")
        or submission.get("challenge_name")
        or submission.get("name")
        or f"submission_{index}"
    )

    # If challenge is a dictionary
    if isinstance(challenge, dict):

        challenge = (
            challenge.get("name")
            or challenge.get("title")
            or challenge.get("slug")
            or f"submission_{index}"
        )

    # --------------------------------------------------------
    # Find language
    # --------------------------------------------------------

    language = (
        submission.get("language")
        or submission.get("language_name")
        or submission.get("lang")
        or "Unknown"
    )

    language = str(language).lower()

    # --------------------------------------------------------
    # Select folder and extension
    # --------------------------------------------------------

    if "python" in language:

        folder = folders["python"]
        extension = ".py"

    elif "sql" in language:

        folder = folders["sql"]
        extension = ".sql"

    elif any(
        x in language
        for x in [
            "java",
            "cpp",
            "c++",
            "c",
            "javascript",
            "ruby",
            "go"
        ]
    ):

        folder = folders["problem_solving"]

        extension_map = {
            "java": ".java",
            "cpp": ".cpp",
            "c++": ".cpp",
            "c": ".c",
            "javascript": ".js",
            "ruby": ".rb",
            "go": ".go"
        }

        extension = extension_map.get(language, ".txt")

    else:

        folder = folders["other"]
        extension = ".txt"

    # --------------------------------------------------------
    # Filename
    # --------------------------------------------------------

    filename = clean_filename(challenge)

    filepath = folder / f"{filename}{extension}"

    # Avoid overwriting duplicate problems
    counter = 2

    while filepath.exists():

        filepath = folder / f"{filename}_{counter}{extension}"

        counter += 1

    # --------------------------------------------------------
    # Save code
    # --------------------------------------------------------

    with open(filepath, "w", encoding="utf-8") as output:

        output.write(code)

    saved += 1

    print(f"[{saved}] {filepath}")

# ============================================================
# CREATE README
# ============================================================

readme = base / "README.md"

with open(readme, "w", encoding="utf-8") as file:

    file.write("""# HackerRank Solutions

This repository contains my HackerRank coding solutions.

## Structure

- `Python/` - Python solutions
- `SQL/` - SQL solutions
- `Problem_Solving/` - Other programming languages
- `Other/` - Uncategorized submissions

Solutions are organized based on the programming language used.

## HackerRank

My HackerRank profile:

https://www.hackerrank.com/
""")

# ============================================================
# FINISHED
# ============================================================

print("\n======================================")
print("DONE")
print("======================================")
print(f"Submissions saved: {saved}")
print(f"Output folder: {base.resolve()}")

if saved == 0:
    print(
        "\nNo submission code was detected in the exported JSON."
        "\nThe HackerRank export may contain account/data information "
        "but not the actual source code."
    )