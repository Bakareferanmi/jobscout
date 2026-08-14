from dataclasses import dataclass, field
from typing import List

from profile import Profile


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

    web3_terms = [
        "web3",
        "blockchain",
        "defi",
        "dao",
        "crypto",
        "smart contract",
        "dapp",
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
        "project",
        "fixed price",
    ]

    client_terms = [
        "website",
        "web site",
        "landing page",
        "business website",
        "build a website",
        "need a developer",
        "need a web developer",
        "need someone to build",
    ]

    if any(term in text for term in web3_terms):
        return "WEB3"

    if any(term in text for term in startup_terms):
        return "STARTUP"

    if any(term in text for term in client_terms):
        return "CLIENT"

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

    for skill in profile.skills:
        skill_lower = skill.lower()

        # Match both the full skill and common spacing variations.
        if skill_lower in text:
            matched.append(skill)

    score = 0

    # Skills are the strongest signal.
    score += min(len(matched) * 12, 60)

    # Role relevance.
    role_text = title.lower()

    for role in profile.target_roles:
        role_words = role.lower().split()

        if any(word in role_text for word in role_words):
            score += 15
            break

    # Service relevance.
    for service in profile.services:
        if service.lower() in text:
            score += 10
            break

    # Opportunity-type relevance.
    opportunity_type = classify_opportunity(title, description)

    if opportunity_type in {
        "CLIENT",
        "STARTUP",
        "FREELANCE",
        "WEB3",
    }:
        score += 10

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
