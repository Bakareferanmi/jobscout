from dataclasses import dataclass, field
from typing import List

from profile import Profile


NEGATIVE_INTENT_TERMS = [
    "[for hire]",
    "for hire",
    "available for hire",
    "seeking work",
    "looking for work",
    "looking for a job",
    "open to work",
    "freelance developer available",
    "developer available",
    "i am a developer",
    "i'm a developer",
]


OPPORTUNITY_TYPES = {
    "JOB",
    "CLIENT",
    "STARTUP",
    "FREELANCE",
    "WEB3",
}


@dataclass
class Opportunity:
    title: str
    description: str = ""
    url: str = ""
    source: str = ""
    opportunity_type: str = "JOB"

    matched_skills: List[str] = field(default_factory=list)
    score: int = 0

    def display(self):
        print()
        print("━" * 60)
        print(f"🔥 {self.opportunity_type} OPPORTUNITY")
        print("━" * 60)
        print()
        print(f"Title:   {self.title}")
        print(f"Source:  {self.source}")
        print(f"Match:   {self.score}%")

        if self.matched_skills:
            print()
            print("Matched skills:")
            for skill in self.matched_skills:
                print(f"  ✓ {skill}")

        if self.url:
            print()
            print(f"URL: {self.url}")

        print()
        print("━" * 60)


def classify_opportunity(title: str, description: str = "") -> str:
    text = f"{title} {description}".lower()

    # First determine whether the author is offering their own services.
    # These are not opportunities for Bakare.
    if any(term in text for term in NEGATIVE_INTENT_TERMS):
        return "IGNORE"

    web3_terms = [
        "web3",
        "blockchain",
        "defi",
        "dao",
        "crypto",
        "smart contract",
        "dapp",
    ]

    client_terms = [
        "website",
        "web site",
        "landing page",
        "business website",
        "web application",
        "web app",
        "mobile app",
        "application development",
        "build a website",
        "build a web app",
        "build an app",
        "need a developer",
        "need a web developer",
        "need someone to build",
        "developer needed",
        "website needed",
        "website development",
        "web development",
    ]

    startup_terms = [
        "startup",
        "start-up",
        "mvp",
        "founder",
        "early stage",
        "product launch",
        "build a product",
    ]

    freelance_terms = [
        "freelance",
        "freelancer",
        "contract",
        "gig",
        "fixed price",
        "client project",
    ]

    if any(term in text for term in web3_terms):
        return "WEB3"

    if any(term in text for term in client_terms):
        return "CLIENT"

    if any(term in text for term in startup_terms):
        return "STARTUP"

    if any(term in text for term in freelance_terms):
        return "FREELANCE"

    return "JOB"


def calculate_match(
    title: str,
    description: str,
    profile: Profile,
) -> tuple[int, List[str]]:
    text = f"{title} {description}".lower()
    matched = []

    # Technical skill matches.
    for skill in profile.skills:
        if skill.lower() in text:
            matched.append(skill)

    score = min(len(matched) * 12, 48)

    # Target-role relevance.
    role_text = title.lower()

    for role in profile.target_roles:
        role_words = role.lower().split()

        if any(word in role_text for word in role_words):
            score += 15
            break

    # Service relevance.
    service_matches = 0

    service_keywords = {
        "business websites": [
            "website", "web site", "business website",
            "landing page",
        ],
        "web applications": [
            "web app", "web application", "web platform",
        ],
        "startup mvps": [
            "mvp", "startup", "prototype", "product",
        ],
        "landing pages": [
            "landing page",
        ],
        "ai integrations": [
            "ai", "artificial intelligence", "gemini",
            "chatbot", "ai agent",
        ],
        "mobile applications": [
            "mobile app", "android app", "ios app",
            "react native",
        ],
    }

    for service, keywords in service_keywords.items():
        if any(keyword in text for keyword in keywords):
            service_matches += 1

    # Commercial/service intent is a strong signal.
    score += min(service_matches * 18, 36)

    opportunity_type = classify_opportunity(title, description)

    if opportunity_type == "IGNORE":
        return 0, matched

    if opportunity_type == "CLIENT":
        score += 16
    elif opportunity_type == "STARTUP":
        score += 10
    elif opportunity_type == "FREELANCE":
        score += 8
    elif opportunity_type == "WEB3":
        score += 6

    return min(score, 100), matched


def analyze(
    title: str,
    description: str = "",
    url: str = "",
    source: str = "",
    profile: Profile | None = None,
) -> Opportunity:
    profile = profile or Profile.load()

    opportunity_type = classify_opportunity(title, description)

    score, matched_skills = calculate_match(
        title,
        description,
        profile,
    )

    return Opportunity(
        title=title,
        description=description,
        url=url,
        source=source,
        opportunity_type=opportunity_type,
        matched_skills=matched_skills,
        score=score,
    )


if __name__ == "__main__":
    profile = Profile.load()

    examples = [
        (
            "React Developer Needed",
            "Startup looking for a React and TypeScript developer to build an MVP.",
        ),
        (
            "Need a website for my business",
            "Looking for someone to build a modern business website.",
        ),
        (
            "Frontend Engineer",
            "Junior frontend developer needed. React and JavaScript experience required.",
        ),
        (
            "Web3 Frontend Developer",
            "Looking for a React developer to build a DeFi dashboard.",
        ),
    ]

    for title, description in examples:
        opportunity = analyze(
            title,
            description,
            profile=profile,
            source="Demo",
        )

        opportunity.display()
