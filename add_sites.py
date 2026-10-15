import json
from pathlib import Path

p = Path("sites.json")
sites = json.loads(p.read_text())

new = [
("Instagram","instagram.com"),("Facebook","facebook.com"),
("TikTok","tiktok.com"),("LinkedIn","linkedin.com"),
("YouTube","youtube.com"),("Threads","threads.net"),
("Bluesky","bsky.app"),("Mastodon","mastodon.social"),
("Telegram","telegram.org"),("Discord","discord.com"),
("WhatsApp","whatsapp.com"),("Medium","medium.com"),
("Substack","substack.com"),("Quora","quora.com"),
("Stack Overflow","stackoverflow.com"),("GitLab","gitlab.com"),
("Bitbucket","bitbucket.org"),("CodePen","codepen.io"),
("Hugging Face","huggingface.co"),("Kaggle","kaggle.com"),
("LeetCode","leetcode.com"),("HackerRank","hackerrank.com"),
("Steam","steampowered.com"),("Epic Games","epicgames.com"),
("Roblox","roblox.com"),("Minecraft","minecraft.net"),
("PlayStation","playstation.com"),("Xbox","xbox.com"),
("Kick","kick.com"),("Battle.net","battle.net"),
("Riot Games","riotgames.com"),("EA","ea.com"),
("Ubisoft","ubisoft.com"),("Netflix","netflix.com"),
("Disney+","disneyplus.com"),("Hulu","hulu.com"),
("Max","max.com"),("Prime Video","primevideo.com"),
("Deezer","deezer.com"),("Bandcamp","bandcamp.com"),
("Last.fm","last.fm"),("Vimeo","vimeo.com"),
("Dailymotion","dailymotion.com"),("Giphy","giphy.com"),
("Tenor","tenor.com"),("Amazon","amazon.com"),
("eBay","ebay.com"),("Etsy","etsy.com"),
("AliExpress","aliexpress.com"),("Alibaba","alibaba.com"),
("Temu","temu.com"),("Shein","shein.com"),
("Walmart","walmart.com"),("PayPal","paypal.com"),
("Wise","wise.com"),("Fiverr","fiverr.com"),
("Upwork","upwork.com"),("Canva","canva.com"),
("Figma","figma.com"),("Notion","notion.so"),
("Trello","trello.com"),("Dropbox","dropbox.com"),
("Box","box.com"),("Proton","proton.me"),
("Yahoo","yahoo.com"),("Outlook","outlook.com"),
("Pornhub","pornhub.com"),("XNXX","xnxx.com"),
("XVideos","xvideos.com"),("XHamster","xhamster.com"),
("RedTube","redtube.com"),("YouPorn","youporn.com"),
("Patreon","patreon.com"),("Buy Me a Coffee","buymeacoffee.com"),
("Kickstarter","kickstarter.com"),("Indiegogo","indiegogo.com"),
("Booking.com","booking.com"),("Airbnb","airbnb.com"),
("Tripadvisor","tripadvisor.com"),("Duolingo","duolingo.com"),
("Coursera","coursera.org"),("Udemy","udemy.com")
]

existing = {s.get("domain", "").lower() for s in sites}
added = 0

for name, domain in new:
    if domain.lower() not in existing:
        sites.append({
            "name": name,
            "domain": domain,
            "method": "manual"
        })
        existing.add(domain.lower())
        added += 1

p.write_text(json.dumps(sites, indent=2) + "\n")
json.loads(p.read_text())

print("SUCCESS! Added", added, "new sites.")
print("Total catalog entries:", len(sites))
print("Note: Catalog entries do not guarantee account detection.")
