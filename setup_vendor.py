import os
import requests

def download_file(url, dest_path):
    if os.path.exists(dest_path):
        print(f"Skipping {os.path.basename(dest_path)}, already exists.")
        return

    print(f"Downloading {url} ...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        print(f"Saved to {dest_path}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def main():
    vendor_dir = os.path.join('static', 'vendor')
    if not os.path.exists(vendor_dir):
        os.makedirs(vendor_dir)
        print(f"Created directory: {vendor_dir}")

    files = [
        ("https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css", "bootstrap.min.css"),
        ("https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js", "bootstrap.min.js"),
        ("https://unpkg.com/vue@3/dist/vue.global.prod.js", "vue.global.prod.js"),
        ("https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js", "chart.umd.min.js")
    ]

    for url, filename in files:
        dest = os.path.join(vendor_dir, filename)
        download_file(url, dest)

    print("All vendor files ready.")

if __name__ == "__main__":
    main()
