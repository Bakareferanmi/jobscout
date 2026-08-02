"""
Category definitions for JobScout.
Edit KEYWORDS to tune what counts as a match for each category.
"""

CATEGORIES = {
    "frontend": {
        "label": "Frontend (Intern/Junior)",
        "must_include_any": ["frontend", "front-end", "front end", "react", "javascript", "html", "css", "web developer"],
        "level_include": ["junior", "intern", "entry", "graduate", "trainee", "associate", "jr."],
        "exclude": ["senior", "lead", "staff", "principal", "head of", "manager", "director", "10+ years", "8+ years"],
        "remotive_category": "software-dev",
        "remoteok_tags": ["frontend", "junior", "react"],
    },
    "data-analysis": {
        "label": "Data Analysis",
        "must_include_any": ["data analyst", "data analysis", "data science", "sql", "power bi", "tableau", "excel analyst"],
        "level_include": ["junior", "intern", "entry", "graduate", "trainee", "associate", "jr."],
        "exclude": ["senior", "lead", "staff", "principal", "head of", "director", "10+ years", "8+ years"],
        "remotive_category": "data",
        "remoteok_tags": ["data", "junior", "analyst"],
    },
    "digital-marketing": {
        "label": "Social Media / Digital Marketing",
        "must_include_any": ["digital marketing", "social media", "content marketing", "seo", "marketing assistant",
                              "community manager", "growth marketing", "brand", "content creator"],
        "level_include": [],  # marketing roles rarely gated by "junior" in title, so don't over-filter
        "exclude": ["senior", "director", "vp ", "head of", "10+ years"],
        "remotive_category": "marketing",
        "remoteok_tags": ["marketing", "social", "content"],
    },
    "electrical": {
        "label": "Electrical/Electronics Engineering (Entry-level)",
        "must_include_any": ["electrical engineer", "electronics engineer", "electrical technician",
                              "power systems", "embedded", "control systems", "instrumentation", "iot engineer"],
        "level_include": ["junior", "intern", "entry", "graduate", "trainee", "associate", "jr.", "grad"],
        "exclude": ["senior", "lead", "principal", "10+ years", "8+ years"],
        "remotive_category": "all-others",
        "remoteok_tags": ["engineer", "iot", "embedded"],
    },
    "it-support": {
        "label": "IT Support",
        "must_include_any": ["it support", "helpdesk", "help desk", "technical support", "desktop support",
                              "systems administrator", "it technician", "service desk"],
        "level_include": [],
        "exclude": ["senior", "lead", "manager", "director", "10+ years"],
        "remotive_category": "all-others",
        "remoteok_tags": ["support", "helpdesk", "it"],
    },
}

# Search terms used against Upwork's public RSS job-search feed for "clients" work.
CLIENT_SEARCH_TERMS = {
    "frontend": ["react developer", "frontend developer", "landing page developer"],
    "data-analysis": ["data analyst", "excel data entry analysis", "dashboard sql"],
    "digital-marketing": ["social media manager", "digital marketing", "content marketing"],
    "electrical": ["iot developer", "embedded systems", "electrical design"],
    "it-support": ["it support", "technical support specialist", "helpdesk"],
}

REDDIT_SUBS = {
    "frontend": ["forhire", "jobbit", "remotejs"],
    "data-analysis": ["forhire", "jobbit"],
    "digital-marketing": ["forhire", "socialmediajobs"],
    "electrical": ["forhire"],
    "it-support": ["forhire", "jobbit"],
}

WWR_FEEDS = {
    "frontend": "https://weworkremotely.com/categories/remote-programming-jobs.rss",
    "digital-marketing": "https://weworkremotely.com/categories/remote-marketing-jobs.rss",
    "it-support": "https://weworkremotely.com/categories/remote-customer-support-jobs.rss",
}

DB_PATH = "jobscout.db"
