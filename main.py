#!/usr/bin/env python3
import argparse
import textwrap

import config
import storage
import sources
import scoring


def cmd_fetch(args):
    storage.init_db()
    categories = list(config.CATEGORIES.keys()) if args.category == "all" else [args.category]

    total_new = 0
    for cat in categories:
        cfg = config.CATEGORIES[cat]
        print(f"\n=== Fetching jobs: {cfg['label']} ===")
        raw = []
        raw += sources.fetch_remotive(cat, cfg["remotive_category"])
        raw += sources.fetch_remoteok(cfg["remoteok_tags"])
        # arbeitnow: use the first must_include term as the search string
        if cfg["must_include_any"]:
            raw += sources.fetch_arbeitnow(cfg["must_include_any"][0])
        raw += sources.fetch_jobicy(cfg["remoteok_tags"][0] if cfg["remoteok_tags"] else "")
        if cat in config.WWR_FEEDS:
            raw += sources.fetch_wwr_rss(config.WWR_FEEDS[cat])
        for sub in config.REDDIT_SUBS.get(cat, []):
            raw += sources.fetch_reddit(sub)

        new_count = 0
        for item in raw:
            if not item.get("title") or not item.get("url"):
                continue
            if not scoring.matches_category(item["title"], cat):
                continue
            listing = {
                "id": storage.make_id(item["source"], item["url"]),
                "kind": item["kind"],
                "category": cat,
                "title": item["title"].strip(),
                "company": item.get("company", ""),
                "location": item.get("location", ""),
                "url": item["url"],
                "source": item["source"],
                "posted": item.get("posted", ""),
                "score": scoring.score_listing(item["title"], cat),
            }
            if storage.upsert_listing(listing):
                new_count += 1
        print(f"  -> {new_count} new job listings saved")
        total_new += new_count

        if not args.jobs_only:
            print(f"=== Fetching clients (Upwork): {cfg['label']} ===")
            client_new = 0
            for term in config.CLIENT_SEARCH_TERMS.get(cat, []):
                for item in sources.fetch_upwork_rss(term):
                    listing = {
                        "id": storage.make_id(item["source"], item["url"]),
                        "kind": "client",
                        "category": cat,
                        "title": item["title"].strip(),
                        "company": item.get("company", ""),
                        "location": item.get("location", ""),
                        "url": item["url"],
                        "source": item["source"],
                        "posted": item.get("posted", ""),
                        "score": scoring.score_listing(item["title"], cat),
                    }
                    if storage.upsert_listing(listing):
                        client_new += 1
            print(f"  -> {client_new} new client listings saved")
            total_new += client_new

    print(f"\nDone. {total_new} new listings added. Run 'python main.py list' to see them.")


def cmd_list(args):
    storage.init_db()
    rows = storage.list_listings(category=args.category, status=args.status, kind=args.kind, limit=args.limit)
    if not rows:
        print("No listings found. Try 'python main.py fetch --category all' first.")
        return
    for r in rows:
        tag = "[JOB]" if r["kind"] == "job" else "[CLIENT]"
        print(f"{r['id']}  {tag}  score={r['score']:<3} [{r['status']}]  {r['title']}")
        print(f"          {r['company'] or ''}  |  {r['category']}  |  via {r['source']}")
    print(f"\n{len(rows)} shown. Use 'python main.py show <id>' for details.")


def cmd_show(args):
    storage.init_db()
    r = storage.get_listing(args.id)
    if not r:
        print("Not found.")
        return
    print(textwrap.dedent(f"""
        ID:       {r['id']}
        Title:    {r['title']}
        Company:  {r['company']}
        Category: {r['category']}
        Kind:     {r['kind']}
        Location: {r['location']}
        Source:   {r['source']}
        Posted:   {r['posted']}
        Status:   {r['status']}
        Score:    {r['score']}
        URL:      {r['url']}
    """).strip())


def cmd_status(args):
    storage.init_db()
    ok = storage.set_status(args.id, args.new_status)
    print("Updated." if ok else "No listing found with that ID.")


def cmd_stats(args):
    storage.init_db()
    rows = storage.stats()
    if not rows:
        print("No data yet.")
        return
    from collections import defaultdict
    grid = defaultdict(dict)
    for r in rows:
        grid[r["category"]][r["status"]] = r["n"]
    for cat, statuses in grid.items():
        parts = ", ".join(f"{k}={v}" for k, v in statuses.items())
        print(f"{cat:20s} {parts}")


def build_parser():
    p = argparse.ArgumentParser(prog="jobscout", description="Find and track jobs + client gigs across your target categories.")
    sub = p.add_subparsers(dest="command", required=True)

    cats = list(config.CATEGORIES.keys()) + ["all"]

    f = sub.add_parser("fetch", help="Pull fresh listings from all sources")
    f.add_argument("--category", choices=cats, default="all")
    f.add_argument("--jobs-only", action="store_true", help="Skip client/Upwork search")
    f.set_defaults(func=cmd_fetch)

    l = sub.add_parser("list", help="List saved listings, ranked by score")
    l.add_argument("--category", choices=list(config.CATEGORIES.keys()))
    l.add_argument("--status", choices=["new", "saved", "applied", "rejected"])
    l.add_argument("--kind", choices=["job", "client"])
    l.add_argument("--limit", type=int, default=25)
    l.set_defaults(func=cmd_list)

    s = sub.add_parser("show", help="Show full details for one listing")
    s.add_argument("id")
    s.set_defaults(func=cmd_show)

    st = sub.add_parser("status", help="Update a listing's status")
    st.add_argument("id")
    st.add_argument("new_status", choices=["new", "saved", "applied", "rejected"])
    st.set_defaults(func=cmd_status)

    stat = sub.add_parser("stats", help="Show counts by category and status")
    stat.set_defaults(func=cmd_stats)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
