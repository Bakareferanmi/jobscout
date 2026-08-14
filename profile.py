from dataclasses import dataclass, asdict
from pathlib import Path
import json


PROFILE_FILE = Path("profile.json")


@dataclass
class Profile:
    name: str = "Bakare Feranmi"
    title: str = "Frontend Software Engineer"
    level: str = "Junior / Intern"

    email: str = "bakareferanmi96@gmail.com"
    portfolio: str = "https://BeepeeLabs.vercel.app"
    github: str = "https://github.com/Bakareferanmi"

    skills: tuple = (
        "React",
        "JavaScript",
        "TypeScript",
        "Next.js",
        "Tailwind CSS",
        "Node.js",
        "React Native",
        "AI/API Integration",
    )

    services: tuple = (
        "Business websites",
        "Web applications",
        "Startup MVPs",
        "Landing pages",
        "AI integrations",
        "Mobile applications",
    )

    target_roles: tuple = (
        "Frontend Software Engineer",
        "Junior Software Engineer",
        "React Developer",
        "Frontend Developer",
    )

    target_opportunities: tuple = (
        "Junior roles",
        "Internships",
        "Startup collaborations",
        "Freelance projects",
        "Web3 projects",
    )

    remote: bool = True

    def to_dict(self):
        return asdict(self)

    def save(self):
        PROFILE_FILE.write_text(
            json.dumps(self.to_dict(), indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls):
        if not PROFILE_FILE.exists():
            profile = cls()
            profile.save()
            return profile

        data = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))

        # JSON stores tuples as lists. Convert them back.
        for field in ("skills", "services", "target_roles", "target_opportunities"):
            if field in data:
                data[field] = tuple(data[field])

        return cls(**data)

    def display(self):
        print()
        print("=" * 60)
        print("                     JOBSCOUT")
        print("                  YOUR PROFILE")
        print("=" * 60)
        print()
        print(f"Name:       {self.name}")
        print(f"Title:      {self.title}")
        print(f"Level:      {self.level}")
        print(f"Email:      {self.email}")
        print(f"Portfolio:  {self.portfolio}")
        print(f"GitHub:     {self.github}")
        print(f"Remote:     {'Yes' if self.remote else 'No'}")
        print()

        print("SKILLS")
        for skill in self.skills:
            print(f"  • {skill}")

        print()
        print("SERVICES")
        for service in self.services:
            print(f"  • {service}")

        print()
        print("TARGET ROLES")
        for role in self.target_roles:
            print(f"  • {role}")

        print()
        print("TARGET OPPORTUNITIES")
        for opportunity in self.target_opportunities:
            print(f"  • {opportunity}")

        print()
        print("=" * 60)


if __name__ == "__main__":
    Profile.load().display()
