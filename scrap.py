from bs4 import BeautifulSoup as beauty
import cloudscraper
import re

scraper = cloudscraper.create_scraper(delay=60, browser='chrome') 
base_url = "https://www.wakfu.com/fr/mmorpg/encyclopedie/montures?page="

num_page_start = 0
num_pages = 2

# Create empty arrays for storing data
image_numbers = []
names = []
item_levels = []
item_characteristics = []
item_rarity = []
item_type = []
item_ids = []

for page_num in range(1, num_pages + 1):
    # Construct the URL for the current page
    url = base_url + str(num_page_start + page_num)
    info = scraper.get(url).text
    soup = beauty(info, "html.parser")
    print(f"Scraping page {num_page_start + page_num}...")
    
    span_ak_linker = soup.find_all('span', class_='ak-linker')

    for span in span_ak_linker:
        img = span.find('img')
        if img and img.get('src'):
            image_url = img.get('src')
            # Use a regular expression to extract the numeric part
            match = re.search(r'/(\d+)\.w\d+h\d+\.png', image_url)
            if match:
                image_number = match.group(1)
                image_numbers.append(image_number)
            
        a = span.find('a')
        if a:
            name = a.get_text()
            href_value = a['href']
            
            # Check if the name is not empty
            if name.strip():
                names.append(name)
                # Use regular expressions to extract the number from the 'href'
                number_match = re.search(r'/(\d+)-', href_value)
                if number_match:
                    number = number_match.group(1)
                    item_ids.append(number)
                else:
                    item_ids.append('')  # Handle cases where the number is not found
                

            
    rows = soup.find_all('tr') 
    
    
    for row in rows:
        # Get the text of the td element with class 'item-level'
        td_item_level = row.find('td', class_='item-level')
        if td_item_level:
             # Use a regular expression to extract the number
            level_text = td_item_level.get_text()
            level_number = re.search(r'\d+', level_text)
            if level_number:
                item_levels.append(level_number.group())
        
        # Get the text of the td element with class 'item-caracteristics'
        td_item_caracteristics = row.find('td', class_='item-caracteristics')
        if td_item_caracteristics:
            item_caracteristics_text = td_item_caracteristics.get_text()
            # Remove extra spaces and trim leading/trailing whitespace
            cleaned_text = ' '.join(item_caracteristics_text.split())
            item_characteristics.append(cleaned_text)
            
         # Get the span element with the class 'ak-icon-small'
        td_item_rarity = row.find('span', class_='ak-icon-small')
        if td_item_rarity:
            # Get the class attribute
            class_attr = td_item_rarity.get('class')
            if class_attr:
                # Look for the 'ak-rarity-' class within the class attribute
                rarity_class = next((c for c in class_attr if c.startswith('ak-rarity-')), None)
                if rarity_class:
                    # Extract the rarity value from the class
                    rarity_value = rarity_class.split('-')[-1]
                    item_rarity.append(rarity_value)
                else:
                    item_rarity.append('')  # Handle cases where rarity class is not found
            else:
                item_rarity.append('')  # Handle cases where class attribute is not found
        
        # Get the title of the img within the td element with class 'item-type'
        td_item_type = row.find('td', class_='item-type')
        if td_item_type:
            img = td_item_type.find('img')
            if img and img.get('title'):
                img_title = img['title']
                item_type.append(img_title)
            else:
                item_type.append('')  # Handle cases where title is not found

armor_data = []



# Append the data from the individual arrays to the armor_data array
for i in range(len(image_numbers)):
    armor_data.append({
        'Image': image_numbers[i],
        'Name': names[i],
        'Item Level': item_levels[i],
        'Item Characteristics': item_characteristics[i],
        'Item Rarity': item_rarity[i],
        'Item Type': item_type[i],
        'Item ID': item_ids[i]
        
    })


# Create an SQL file and open it for writing
sql_file_name = "armor_data.sql"
with open(sql_file_name, "w") as sql_file:
    # Write SQL statements to the file
    for armor in armor_data:
        # Escape single quotes in the name
        name = armor['Name'].replace("'", "''")
        sql_statement = f"INSERT INTO mount (Image, Name, Level, Characteristics,Rarity ,Type ,ID_item) VALUES ('{armor['Image']}', '{name}', {armor['Item Level']}, '{armor['Item Characteristics']}', '{armor['Item Rarity']}', '{armor['Item Type']}', '{armor['Item ID']}');\n"
        sql_file.write(sql_statement)

print(f"SQL statements have been written to '{sql_file_name}'.")

