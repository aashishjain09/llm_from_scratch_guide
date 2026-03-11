import os, argparse, requests
from tqdm import tqdm
from typing import List

BASE_URL = "https://huggingface.co/datasets/monology/pile-uncopyrighted/resolve/main"
VAL_URL = f"{BASE_URL}/val.jsonl.zst"
TRAIN_URLS = [f"{BASE_URL}/train/{i:02d}.jsonl.zst" for i in range(64)]

def download_file(url: str, file_name: str) -> None:
    """
    Downloads a file from the given URL and saves it with the specified file name.
    Displays progress bar using tqdm.

    Args:
        url (str): The URL of the file to download.
        file_name (str): The local path where the file will be saved.
    """
    print(f"Downloading: {file_name}...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    with open(file_name, 'wb') as f:
        for chunk in tqdm(response.iter_content(block_size), total=total_size//block_size, desc="Downloading", leave=True):
            f.write(chunk)

def download_dataset(val_url: str, train_urls: List[str], val_dir: str, train_dir: str, max_train_files: int) -> None:
    """
    Manages downloading of the dataset, including both validation and training files.

    Args:
        val_url (str): URL for the validation dataset.
        train_urls (list): List of URLs for the training dataset files.
        val_dir (str): Directory where the validation file will be stored.
        train_dir (str): Directory where the training files will be stored.
        max_train_files (int): Maximum number of training files to download.
    """
    val_file_path = os.path.join(val_dir, "val.jsonl.zst")
    if not os.path.exists(val_file_path):
        print(f"Validation file not found. Downloading from {val_url}...")
        download_file(val_url, val_file_path)
    else:
        print("Validation data already present. Skipping download.")
    
    for idx, url in enumerate(train_urls[:max_train_files]):
        file_name = f"{idx:02d}.jsonl.zst"
        file_path = os.path.join(train_dir, file_name)
        if not os.path.exists(file_path):
            print(f"Training file {file_name} not found. Downloading...")
            download_file(url, file_path)
        else:
            print(f"Training file {file_name} already present. Skipping download.")

def main() -> None:
    """
    Main function to parse arguments and orchestrate the dataset download process.
    """
    parser = argparse.ArgumentParser(description="Download PILE dataset.")
    parser.add_argument('--train_max', type=int, default=1, help="Max number of training files to download.")
    parser.add_argument('--train_dir', default="data/train", help="Directory for storing training data.")
    parser.add_argument('--val_dir', default="data/val", help="Directory for storing validation data.")

    args = parser.parse_args()

    os.makedirs(args.train_dir, exist_ok=True)
    os.makedirs(args.val_dir, exist_ok=True)

    download_dataset(VAL_URL, TRAIN_URLS, args.val_dir, args.train_dir, args.train_max)

    print("Dataset downloaded successfully.")


if __name__ == "__main__":
    main()