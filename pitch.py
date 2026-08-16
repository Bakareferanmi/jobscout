from textwrap import dedent


NAME = "Bakare Feranmi"
EMAIL = "bakareferanmi96@gmail.com"
PORTFOLIO = "BeepeeLabs.vercel.app"


def generate(listing):
    title = listing["title"] or ""
    company = listing["company"] or ""
    opportunity_type = (listing["opportunity_type"] or "JOB").upper()

    if opportunity_type == "CLIENT":
        subject = f"Frontend developer for: {title}"

        message = dedent(f"""\
        Hi,

        I came across your request for "{title}".

        I'm a frontend-focused software engineer specializing in React,
        Next.js and modern web applications. I can help turn your idea
        or prototype into a polished, responsive and production-ready
        website.

        You can see some of my work here:
        {PORTFOLIO}

        If you're still looking for someone to handle the project,
        I'd be happy to discuss the details and what you need built.

        Best,
        {NAME}
        {EMAIL}
        """)

    elif opportunity_type == "STARTUP":
        subject = f"Frontend development for {company or 'your startup'}"

        message = dedent(f"""\
        Hi,

        I came across {company or "your startup"} and noticed the
        opportunity around "{title}".

        I'm a frontend-focused software engineer working with React,
        Next.js and modern web applications. I also have experience
        thinking about products from both the technical and growth side.

        I'd be interested in contributing to what you're building.

        Portfolio:
        {PORTFOLIO}

        If you're open to it, I'd love to connect and learn more about
        what you're building and where I could add value.

        Best,
        {NAME}
        {EMAIL}
        """)

    elif opportunity_type == "WEB3":
        subject = f"Frontend developer interested in {title}"

        message = dedent(f"""\
        Hi,

        I came across your opening for "{title}" and wanted to reach out.

        I'm a frontend-focused software engineer specializing in React,
        modern JavaScript/TypeScript and web applications. I'm
        particularly interested in opportunities where I can contribute
        to building polished user-facing products.

        Portfolio:
        {PORTFOLIO}

        I'd be happy to share more about my work and discuss how I could
        contribute to the team.

        Best,
        {NAME}
        {EMAIL}
        """)

    elif opportunity_type == "FREELANCE":
        subject = "Interested in your freelance project"

        message = dedent(f"""\
        Hi,

        I came across "{title}" and I'm interested in helping with the
        project.

        I'm a frontend-focused software engineer specializing in React,
        Next.js and modern web development. I can help build responsive,
        polished websites and web applications from an idea, design or
        existing project.

        Portfolio:
        {PORTFOLIO}

        If the project is still available, I'd be happy to discuss the
        requirements and provide a suitable approach.

        Best,
        {NAME}
        {EMAIL}
        """)

    else:
        subject = f"Application: {title}"

        message = dedent(f"""\
        Hi,

        I came across the "{title}" opportunity and I'm interested in
        learning more about the role.

        I'm a frontend-focused software engineer specializing in React,
        Next.js and modern web applications. I'm particularly interested
        in opportunities where I can contribute to building high-quality
        user-facing products.

        Portfolio:
        {PORTFOLIO}

        I'd be happy to share more about my experience and discuss how
        I could contribute.

        Best,
        {NAME}
        {EMAIL}
        """)

    return subject.strip(), message.strip()
