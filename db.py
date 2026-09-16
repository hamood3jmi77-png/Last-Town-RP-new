import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "mtrp.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS content (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS social_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    url TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS timeline_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS team_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    image TEXT DEFAULT '',
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS roster_creators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    platform TEXT DEFAULT '',
    image TEXT DEFAULT '',
    url TEXT DEFAULT '',
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    department TEXT DEFAULT '',
    location TEXT DEFAULT '',
    job_type TEXT DEFAULT '',
    description TEXT DEFAULT '',
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS faqs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT DEFAULT 'Event',
    image TEXT DEFAULT '',
    event_date TEXT DEFAULT '',
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS streams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_name TEXT NOT NULL,
    platform TEXT DEFAULT 'Kick',
    url TEXT DEFAULT '',
    thumbnail TEXT DEFAULT '',
    is_live INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS leaderboard_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rank INTEGER DEFAULT 0,
    player_name TEXT NOT NULL,
    playtime TEXT DEFAULT '',
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    image TEXT DEFAULT '',
    join_url TEXT DEFAULT '',
    sort_order INTEGER DEFAULT 0
);
"""

DEFAULT_CONTENT = {
    "site.name_line1": "MYSTERY TOWN",
    "site.name_line2": "STUDIOS",
    "site.meta_title": "Mystery Town - MT Studios | MTRP | البلدة الغامضة | #1 GTA V RP in MENA",
    "site.meta_description": "Mystery Town Studios (MT / MTRP / البلدة الغامضة) — the #1 GTA V FiveM roleplay community in MENA.",
    "site.favicon": "/static/favicon.png",

    "nav.home": "Home",
    "nav.roster": "Roster",
    "nav.team": "Team",
    "nav.live": "Live",
    "nav.careers": "Careers",
    "nav.faq": "FAQ",
    "nav.leaderboard": "Leaderboard",
    "nav.store_label": "Store",
    "nav.store_url": "#",
    "nav.signin_label": "Sign In",

    "home.eyebrow": "The #1 GTA RP in the Middle East",
    "home.hero_title_line1": "MYSTERY",
    "home.hero_title_line2": "TOWN",
    "home.hero_desc": "The most immersive GTA V roleplay experience. Join 300,000+ players in a world of adventure, drama, and unforgettable stories.",
    "home.hero_btn_primary": "Join Now",
    "home.hero_btn_primary_url": "#",
    "home.hero_btn_secondary": "Learn More",
    "home.hero_btn_secondary_url": "#",
    "home.hero_bg_image": "/static/images/hero-bg.webp",

    "home.servers_title": "Choose Your Adventure",
    "home.servers_subtitle": "Pick a server and start your journey in the Mystery Town universe.",

    "home.pulse_title": "Community Pulse",
    "home.pulse_discord_value": "0",
    "home.pulse_discord_label": "Discord Members",
    "home.pulse_followers_value": "300K+",
    "home.pulse_followers_label": "Followers",
    "home.pulse_views_value": "20M+",
    "home.pulse_views_label": "Monthly Views",
    "home.pulse_hours_value": "5M+",
    "home.pulse_hours_label": "Watch Hours",

    "home.events_title": "MT Events",
    "home.events_subtitle": "The biggest moments in Mystery Town history",
    "home.events_empty": "No events found",

    "home.stats_players_value": "300K+",
    "home.stats_players_label": "Registered Players",
    "home.stats_creators_value": "100+",
    "home.stats_creators_label": "Creator Partners",
    "home.stats_impressions_value": "20M+",
    "home.stats_impressions_label": "Monthly Impressions",
    "home.stats_team_value": "50+",
    "home.stats_team_label": "Team Members",

    "home.journey_title": "THE JOURNEY",

    "home.gallery_title": "Experience the Living World",
    "home.gallery_subtitle": "Immerse yourself in the stunning visuals and epic moments from the Mystery Town world. Every image tells a story of adventure, drama, and unforgettable experiences.",

    "home.social_cta_title": "Want to See More?",
    "home.social_cta_subtitle": "Follow us on social media for more epic moments and behind-the-scenes content.",
    "home.social_cta_button": "X / Twitter",
    "home.social_cta_url": "https://x.com/",

    "shared.back_to_home": "Back to Home",

    "faq.title": "Got Questions?",
    "faq.subtitle": "Can't find what you're looking for? Reach out on Twitter/X for more help.",

    "team.title": "The People Behind Mystery Town",
    "team.subtitle": "Meet the dedicated team that builds, manages, and supports the Mystery Town experience.",
    "team.empty": "More team members coming soon — stay tuned for announcements!",

    "careers.title": "Join Our Team",
    "careers.subtitle": "Help us build something meaningful. We're looking for talented people to join Mystery Town Studios.",
    "careers.open_positions_label": "Open Positions",
    "careers.roles_suffix": "roles",
    "careers.empty_title": "No Open Positions",
    "careers.empty_desc": "We don't have any open positions right now. Follow us on social media for announcements.",

    "auth.title": "Sign In",
    "auth.subtitle": "Welcome back to Mystery Town",
    "auth.discord_btn": "Discord",
    "auth.steam_btn": "Steam",
    "auth.divider": "OR",
    "auth.email_label": "Email",
    "auth.email_placeholder": "your@email.com",
    "auth.password_label": "Password",
    "auth.password_placeholder": "Min 6 characters",
    "auth.forgot_password": "Forgot your password?",
    "auth.submit": "Sign In",
    "auth.signup_prompt": "Need an account? Create one",

    "leaderboard.title": "Leaderboard",
    "leaderboard.subtitle": "Top 50 players ranked by total playtime on MT Whitelist RP",
    "leaderboard.server_tab": "MT Whitelist RP",
    "leaderboard.note": "Leaderboard data is sourced from the game server and refreshed automatically.",
    "leaderboard.empty": "No players ranked yet — be the first on the board!",

    "live.title": "All Live Streams",
    "live.subtitle": "Watch Mystery Town community streamers live on Kick.com",
    "live.empty_title": "No Streams Live",
    "live.empty_desc": "Check back later to catch our community streamers in action.",

    "roster.title": "CREATOR ROSTER",
    "roster.subtitle": "Meet the talented content creators who bring Mystery Town to life.",
    "roster.filter_label": "ALL CREATORS",
    "roster.empty": "No creators found",
    "roster.empty2": "More creators coming soon — stay tuned for announcements!",

    "footer.based_in": "Based in Saudi Arabia",
    "footer.serving": "Serving a Global Community Worldwide",
    "footer.cr_no": "CR No. 7023685857",
    "footer.vat_id": "SA VAT ID: 314311978600003",
    "footer.email": "support@mtrp.gg",
    "footer.copyright": "© 2026 MT Studios. All rights reserved.",
}

DEFAULT_TIMELINE = [
    ("2019", "Mystery Town is Born", "MT RP was founded as a GTA V roleplay community, setting the foundation for what would become one of the largest RP platforms in the Middle East."),
    ("2020", "Community Growth", "The community rapidly expanded to tens of thousands of registered players, with advanced systems for economy, gangs, and law enforcement."),
    ("2021-2022", "Streamer Partnerships", "MT RP partnered with over 100 content creators across Twitch, Kick, YouTube, and social media, generating millions of monthly impressions."),
    ("2023", "Major Platform Update", "A significant platform overhaul brought new mechanics, improved performance, and attracted a wave of new players and streamers to the community."),
    ("2024", "300K+ Players", "Mystery Town reached over 300,000 registered players, solidifying its position as the leading GTA RP platform in the Arab region."),
    ("2026 - Today", "Expanding in UGC & Going Global", "MT Studios is expanding across UGC platforms like GTA and RDR, focusing on building a global roleplay community and becoming a worldwide leader in interactive entertainment."),
]

DEFAULT_SOCIAL_LINKS = [
    ("youtube", "https://youtube.com/"),
    ("tiktok", "https://tiktok.com/"),
    ("instagram", "https://instagram.com/"),
    ("x", "https://x.com/"),
    ("discord", "https://discord.gg/mtrp"),
]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(admin_username="admin", admin_password="admin123"):
    conn = get_db()
    conn.executescript(SCHEMA)

    cur = conn.execute("SELECT COUNT(*) AS c FROM admin_users")
    if cur.fetchone()["c"] == 0:
        conn.execute(
            "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
            (admin_username, generate_password_hash(admin_password)),
        )

    for key, value in DEFAULT_CONTENT.items():
        conn.execute(
            "INSERT OR IGNORE INTO content (key, value) VALUES (?, ?)", (key, value)
        )

    cur = conn.execute("SELECT COUNT(*) AS c FROM timeline_items")
    if cur.fetchone()["c"] == 0:
        for i, (year, title, desc) in enumerate(DEFAULT_TIMELINE):
            conn.execute(
                "INSERT INTO timeline_items (year, title, description, sort_order) VALUES (?, ?, ?, ?)",
                (year, title, desc, i),
            )

    cur = conn.execute("SELECT COUNT(*) AS c FROM social_links")
    if cur.fetchone()["c"] == 0:
        for i, (platform, url) in enumerate(DEFAULT_SOCIAL_LINKS):
            conn.execute(
                "INSERT INTO social_links (platform, url, sort_order) VALUES (?, ?, ?)",
                (platform, url, i),
            )

    conn.commit()
    conn.close()

def get_content_dict():
    conn = get_db()
    rows = conn.execute("SELECT key, value FROM content").fetchall()
    conn.close()
    return {row["key"]: row["value"] for row in rows}

if __name__ == "__main__":
    init_db()
    print("Database initialized at", DB_PATH)
