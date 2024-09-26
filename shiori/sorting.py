import re

data = """
4 Hitohito Tadano    Players  0   Rarity Secret Rare   Maturation 3   Lvl 2513 Raid Id 1823070  Time Left  48 Mins
5 Shiro    Players  0   Rarity Secret Rare   Maturation 3   Lvl 2513 Raid Id 2274085  Time Left  48 Mins
6 Souya KawataAngry    Players  0   Rarity Secret Rare   Maturation 2   Lvl 1851 Raid Id 2523107  Time Left  48 Mins
12 Touka Kirishima    Players  0   Rarity Secret Rare   Maturation 2   Lvl 1851 Raid Id 3718201  Time Left  48 Mins
14 Kofuku    Players  0   Rarity Secret Rare   Maturation 1   Lvl 2513 Raid Id 4495261  Time Left  48 Mins
16 Katsuki Bakugo    Players  0   Rarity Secret Rare   Maturation 3   Lvl 1851 Raid Id 5514532  Time Left  48 Mins
17 Suika    Players  0   Rarity Secret Rare   Maturation 2   Lvl 973 Raid Id 6310843  Time Left  48 Mins
22 Izuku Midoriya    Players  0   Rarity Secret Rare   Maturation 2   Lvl 973 Raid Id 8253688  Time Left  48 Mins
24 Nezuko Kamado    Players  0   Rarity Secret Rare   Maturation 2   Lvl 2513 Raid Id 9146643  Time Left  48 Mins
29 Sylphiette    Players  0   Rarity Secret Rare   Maturation 2   Lvl 2513 Raid Id 1589500  Time Left  48 Mins
"""

# Split the data into lines and process each line
for line in data.strip().split('\n'):
    # Use regex to find the relevant parts
    match = re.match(r'(\d+)\s+(.+?)\s+Players\s+(\d+)\s+Rarity\s+(Secret Rare)\s+Maturation\s+(\d+)\s+Lvl\s+(\d+)\s+Raid Id\s+(\d+)\s+Time Left\s+(\d+\s+Mins)', line)

    if not match:
        print(f"Skipping line due to unexpected format: {line}")
        continue

    # Extracted values
    raid_number = match.group(1)
    name = match.group(2)
    players = match.group(3)
    rarity = match.group(4)
    maturation = match.group(5)
    level = match.group(6)
    raid_id = match.group(7)
    time_left = match.group(8)

    # Print the formatted output
    print(f"Raid Number: {raid_number}")
    print(f"Name: {name}")
    print(f"Players: {players}")
    print(f"Rarity: {rarity}")
    print(f"Maturation: {maturation}")
    print(f"Level: {level}")
    print(f"Raid Id: {raid_id}")
    print(f"Time Left: {time_left}")
    print(f"=rd join {raid_id}")  # Command to join the raid
    print('-' * 40)  # Separator line for better readability
