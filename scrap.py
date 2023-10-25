from bs4 import BeautifulSoup as beauty
import cloudscraper
import re

scraper = cloudscraper.create_scraper(delay=10, browser='chrome') 
base_url = "https://www.wakfu.com/fr/mmorpg/encyclopedie/armures?page="

num_pages = 1

# Create empty arrays for storing data
image_numbers = []
names = []
item_levels = []
item_characteristics = []

for page_num in range(1, num_pages + 1):
    # Construct the URL for the current page
    url = base_url + str(page_num)
    info = scraper.get(url).text
    soup = beauty(info, "html.parser")
    
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
            # Check if the name is not empty
            if name.strip():
                names.append(name)
            
    rows = soup.find_all('tr', class_='ak-bg-odd') + soup.find_all('tr', class_='ak-bg-even')
    
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

armor_data = []

# Append the data from the individual arrays to the armor_data array
for i in range(len(image_numbers)):
    armor_data.append({
        'Image': image_numbers[i],
        'Name': names[i],
        'Item Level': item_levels[i],
        'Item Characteristics': item_characteristics[i]
    })



# Create an SQL file and open it for writing
sql_file_name = "armor_data.sql"
with open(sql_file_name, "w") as sql_file:
    # Write SQL statements to the file
    for armor in armor_data:
        # Escape single quotes in the name
        name = armor['Name'].replace("'", "''")
        sql_statement = f"INSERT INTO armor (Image, Name, Level, Characteristics) VALUES ('{armor['Image']}', '{name}', {armor['Item Level']}, '{armor['Item Characteristics']}');\n"
        sql_file.write(sql_statement)

print(f"SQL statements have been written to '{sql_file_name}'.")

