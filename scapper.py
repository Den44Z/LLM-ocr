import requests
import time
import random
import os


def safe_pdf_downloader(urls, save_dir="downloaded_pdfs", delay_range=(5, 15), proxies=None):
    """
    Safely download multiple PDFs with anti-ban measures

    Args:
        urls (list): List of PDF URLs to download
        save_dir (str): Directory to save PDFs (default: 'downloaded_pdfs')
        delay_range (tuple): Min/max delay between requests in seconds (default: 5-15)
        proxies (dict): Optional proxies for request rotation
    """
    # Common desktop User-Agents (expand this list)
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.1",
        "Mozilla/5.0 (Windows NT 10.0; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.3"
    ]

    # Create save directory if not exists
    os.makedirs(save_dir, exist_ok=True)

    for i, url in enumerate(urls):
        try:
            # Generate random delay (except first request)
            if i > 0:
                delay = random.uniform(*delay_range)
                print(f"Waiting {delay:.1f} seconds before next request...")
                time.sleep(delay)

            # Get filename from URL
            filename = url.split("/")[-1]
            save_path = os.path.join(save_dir, filename)

            # Skip existing files
            if os.path.exists(save_path):
                print(f"Skipping existing file: {filename}")
                continue

            # Rotate headers and proxies
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }

            print(f"Downloading ({i + 1}/{len(urls)}): {filename}")

            # Stream download with timeout
            response = requests.get(
                url,
                headers=headers,
                proxies=proxies,
                stream=True,
                timeout=20
            )

            # Check for 4xx/5xx errors
            response.raise_for_status()

            # Save content
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive chunks
                        f.write(chunk)

            print(f"Successfully saved: {save_path}")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("Rate limited - consider increasing delays or using proxies")
                return  # Abort on rate limit
            print(f"HTTP Error {e.response.status_code} for {url}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {url}: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    # Example usage
    pdf_urls = [
        "https://www.resmigazete.gov.tr/eskiler/2025/01/20250121-27.pdf",
        # Add more URLs here
    ]

    safe_pdf_downloader(
        pdf_urls,
        save_dir="resmi_gazete_pdfs",
        delay_range=(10, 30),  # More conservative delays
        # proxies={"http": "http://10.10.1.10:3128"}  # Uncomment to use proxies
    )