"""
Web Emoji Scraper for SS6 Super Student Game
Uses MCP browser tools to scrape real emoji images from the web
"""

import os
import asyncio
import urllib.request
import urllib.parse
from pathlib import Path

# Emoji associations as defined in the instructions
EMOJI_ASSOCIATIONS = {
    'A': ['Apple', 'Ant'],
    'B': ['Ball', 'Banana'],
    'C': ['Cat', 'Car'],
    'D': ['Dog', 'Duck'],
    'E': ['Elephant', 'Egg'],
    'F': ['Fish', 'Flower'],
    'G': ['Giraffe', 'Grapes'],
    'H': ['House', 'Hat'],
    'I': ['Ice Cream', 'Iguana'],
    'J': ['Jar', 'Juice'],
    'K': ['Kite', 'Key'],
    'L': ['Lion', 'Leaf'],
    'M': ['Mouse', 'Moon'],
    'N': ['Nest', 'Nose'],
    'O': ['Orange', 'Owl'],
    'P': ['Penguin', 'Pizza'],
    'Q': ['Queen', 'Question Mark'],
    'R': ['Rainbow', 'Rabbit'],
    'S': ['Sun', 'Snake'],
    'T': ['Tree', 'Tiger'],
    'U': ['Umbrella', 'Unicorn'],
    'V': ['Violin', 'Volcano'],
    'W': ['Whale', 'Watermelon'],
    'X': ['X-ray', 'Xylophone'],
    'Y': ['Yarn', 'Yacht'],
    'Z': ['Zebra', 'Zipper']
}

def scrape_emoji_from_openmoji():
    """
    Scrape emoji images from OpenMoji - a free emoji library.
    This is a fallback method that uses direct URLs.
    """
    print("Scraping emojis from OpenMoji (open source emoji library)...")
    
    # OpenMoji base URL for PNG files
    base_url = "https://raw.githubusercontent.com/hfg-gmuend/openmoji/master/color/72x72/"
    
    # Common emoji Unicode mappings
    emoji_mappings = {
        'Apple': '1F34E.png',
        'Ant': '1F41C.png',
        'Ball': '26BD.png',  # Soccer ball
        'Banana': '1F34C.png',
        'Cat': '1F431.png',
        'Car': '1F697.png',
        'Dog': '1F436.png',
        'Duck': '1F986.png',
        'Elephant': '1F418.png',
        'Egg': '1F95A.png',
        'Fish': '1F41F.png',
        'Flower': '1F33C.png',
        'Giraffe': '1F992.png',
        'Grapes': '1F347.png',
        'House': '1F3E0.png',
        'Hat': '1F3A9.png',
        'Ice Cream': '1F366.png',
        'Iguana': '1F98E.png',
        'Jar': '1FAD9.png',
        'Juice': '1F9C3.png',
        'Kite': '1FA81.png',
        'Key': '1F5DD.png',
        'Lion': '1F981.png',
        'Leaf': '1F343.png',
        'Mouse': '1F42D.png',
        'Moon': '1F31D.png',
        'Nest': '1FAB9.png',
        'Nose': '1F443.png',
        'Orange': '1F34A.png',
        'Owl': '1F989.png',
        'Penguin': '1F427.png',
        'Pizza': '1F355.png',
        'Queen': '1F478.png',
        'Question Mark': '2753.png',
        'Rainbow': '1F308.png',
        'Rabbit': '1F430.png',
        'Sun': '2600.png',
        'Snake': '1F40D.png',
        'Tree': '1F333.png',
        'Tiger': '1F42F.png',
        'Umbrella': '2602.png',
        'Unicorn': '1F984.png',
        'Violin': '1F3BB.png',
        'Volcano': '1F30B.png',
        'Whale': '1F433.png',
        'Watermelon': '1F349.png',
        'X-ray': '1FA78.png',
        'Xylophone': '1FA98.png',
        'Yarn': '1F9F6.png',
        'Yacht': '26F5.png',
        'Zebra': '1F993.png',
        'Zipper': '1F910.png'  # Using zipper-mouth face as proxy
    }
    
    assets_dir = Path("assets/emojis")
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    downloaded_count = 0
    failed_count = 0
    
    for letter, emojis in EMOJI_ASSOCIATIONS.items():
        for i, emoji_name in enumerate(emojis, 1):
            if emoji_name in emoji_mappings:
                unicode_file = emoji_mappings[emoji_name]
                url = base_url + unicode_file
                
                # Create filename matching our naming convention
                filename = f"{letter}_{emoji_name.lower().replace(' ', '_')}_{i}.png"
                filepath = assets_dir / filename
                
                try:
                    print(f"Downloading {emoji_name} for letter {letter}...")
                    urllib.request.urlretrieve(url, str(filepath))
                    downloaded_count += 1
                    print(f"✅ Downloaded: {filename}")
                    
                except Exception as e:
                    print(f"❌ Failed to download {emoji_name}: {e}")
                    failed_count += 1
            else:
                print(f"⚠️  No emoji mapping found for: {emoji_name}")
                failed_count += 1
    
    print(f"\nDownload complete: {downloaded_count} successful, {failed_count} failed")
    return downloaded_count > 0

def backup_existing_emojis():
    """Backup existing placeholder emojis before replacing them."""
    assets_dir = Path("assets/emojis")
    backup_dir = Path("assets/emojis_backup")
    
    if assets_dir.exists() and any(assets_dir.iterdir()):
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        print("Backing up existing emoji files...")
        for file in assets_dir.glob("*.png"):
            backup_file = backup_dir / file.name
            backup_file.write_bytes(file.read_bytes())
        
        print(f"✅ Backed up {len(list(assets_dir.glob('*.png')))} emoji files to {backup_dir}")

def main():
    """Main function to scrape and download emoji images."""
    print("🎨 SS6 Web Emoji Scraper")
    print("=" * 40)
    
    # Backup existing emojis
    backup_existing_emojis()
    
    # Try to scrape from OpenMoji
    success = scrape_emoji_from_openmoji()
    
    if success:
        print("\n🎉 Successfully downloaded emoji images!")
        print("Real emoji images are now available for the alphabet level.")
    else:
        print("\n❌ Failed to download emoji images.")
        print("Falling back to placeholder emojis.")

if __name__ == "__main__":
    main()