import csv
import os
import time
import psutil
from datetime import datetime, timedelta
from extract_commit_history import extract_commit_history_from_url
from urllib.parse import urlparse

CSV_FILE = "github_java_repositories_paginated.csv"
NUM_REPOS = 1000
LOG_FILE = "run.log"

# Hardcoded username and scratch path for SLURM cluster
SCRATCH_OUTPUT_DIR = "/mnt/scratch2/users/40455692/closer_output"


def log_message(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_msg = f"{timestamp} {message}"
    print(full_msg)  # Print to SLURM stdout
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(full_msg + "\n")


def get_output_filename(git_url):
    os.makedirs(SCRATCH_OUTPUT_DIR, exist_ok=True)
    parsed_url = urlparse(git_url)
    repo_name = os.path.splitext(os.path.basename(parsed_url.path))[0]
    owner = parsed_url.path.strip('/').split('/')[0]
    return os.path.join(SCRATCH_OUTPUT_DIR, f"{owner}_{repo_name}.json")


def get_memory_usage_mb():
    return psutil.Process(os.getpid()).memory_info().rss / (1024 ** 2)


def process_repos(csv_path, limit=1000):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = list(csv.DictReader(csvfile))
        total = min(limit, len(reader))

        for i, row in enumerate(reader[:limit]):
            url = row.get("URL")
            if not url:
                log_message(f"⚠️ Skipping row {i+1}: URL missing")
                continue

            output_file = get_output_filename(url)
            if os.path.exists(output_file):
                log_message(f"⏩ Skipping ({i+1}/{total}): Already exists → {output_file}")
                continue

            log_message(f"🔄 Processing ({i+1}/{total}): {url}")
            start_time = time.time()

            try:
                extract_commit_history_from_url(
                    url,
                    output_path=output_file,  # <-- Pass the file path to save JSON
                    years_back=10
                )
                elapsed = time.time() - start_time
                mem_used = get_memory_usage_mb()
                remaining = (elapsed * (total - i - 1)) / 60  # in minutes
                log_message(f"✅ Finished in {elapsed:.2f}s | RAM: {mem_used:.1f}MB | ETA: {remaining:.1f} min")
            except Exception as e:
                log_message(f"❌ Error processing {url}: {e}")

if __name__ == "__main__":
    log_message("🚀 Starting repository processing job...")
    process_repos(CSV_FILE, NUM_REPOS)
    log_message("✅ Job completed.")
