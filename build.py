#!/usr/bin/env python3
"""Build static blog from posts.json — recreates the California Survey Company Surveyor's Blog."""

import json
import os
import html
from datetime import datetime
from pathlib import Path

OUTDIR = Path("/home/jp/Projects/poppasblog/site")
OUTDIR.mkdir(exist_ok=True)
(OUTDIR / "images").mkdir(exist_ok=True)

with open("/home/jp/Projects/poppasblog/posts.json") as f:
    posts = json.load(f)


def slug(title):
    return "".join(c if c.isalnum() else "-" for c in title.lower()).strip("-")


def format_date(iso):
    dt = datetime.fromisoformat(iso)
    return dt.strftime("%A, %d %B %Y %H:%M")


def format_date_short(iso):
    dt = datetime.fromisoformat(iso)
    return dt.strftime("%B %d, %Y")


def content_to_html(text):
    """Convert plain text content to HTML paragraphs, preserving poetry/verse structure."""
    # Split into paragraphs on double-newline or single-newline patterns
    lines = text.split("\n") if "\n" in text else [text]

    # Check if this looks like it has verse/poetry (short lines)
    short_lines = sum(1 for l in lines if 0 < len(l.strip()) < 80)
    total_lines = sum(1 for l in lines if l.strip())
    is_verse = total_lines > 4 and short_lines / max(total_lines, 1) > 0.6

    if is_verse:
        # Preserve line breaks for poetry
        result = []
        in_verse = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if in_verse:
                    result.append("</p>\n<p>")
                    in_verse = False
                continue
            if len(stripped) < 80:
                if not in_verse:
                    result.append("<p>")
                    in_verse = True
                else:
                    result.append("<br>")
                result.append(html.escape(stripped))
            else:
                if in_verse:
                    result.append("</p>")
                    in_verse = False
                result.append(f"<p>{html.escape(stripped)}</p>")
        if in_verse:
            result.append("</p>")
        return "\n".join(result)

    # Regular prose — split on sentence boundaries that look like paragraph breaks
    # The content was extracted with paragraphs joined by spaces
    # Try to split on double-space patterns that indicate paragraph breaks
    paragraphs = text.split("  ")
    if len(paragraphs) < 2:
        paragraphs = [text]

    # Filter and clean
    result = []
    for p in paragraphs:
        p = p.strip()
        if p:
            result.append(f"<p>{html.escape(p)}</p>")
    return "\n".join(result) if result else f"<p>{html.escape(text)}</p>"


def image_html(images):
    """Generate image tags for post images."""
    parts = []
    for img in images:
        img_path = Path("/home/jp/Projects/poppasblog/images") / img
        if img_path.exists() and img_path.stat().st_size > 0:
            parts.append(f'<div class="post-image"><img src="images/{html.escape(img)}" alt="" loading="lazy"></div>')
        # Skip images that weren't recovered
    return "\n".join(parts)


def post_html(post, is_full=False):
    s = slug(post["title"])
    comment_text = f'Comments ({post["commentCount"]})' if post["commentCount"] > 0 else "Add your comment"

    imgs = image_html(post.get("images", []))

    content = content_to_html(post["content"])

    if is_full:
        return f'''<article class="blog-post" id="{s}">
  <div class="post-header">
    <h2 class="post-title">{html.escape(post["title"])}</h2>
    <div class="post-meta">
      <span class="post-author">Written by {html.escape(post["author"])}</span>
      <span class="post-date">{format_date(post["date"])}</span>
    </div>
  </div>
  <div class="post-content">
    {imgs}
    {content}
  </div>
  <div class="post-footer">
    {f'<div class="post-updated">Last Updated on {format_date(post["lastUpdated"])}</div>' if post.get("lastUpdated") else ""}
    <div class="post-comments">{comment_text}</div>
  </div>
</article>'''
    else:
        # Summary for index — first 300 chars
        preview = post["content"][:300]
        if len(post["content"]) > 300:
            preview = preview.rsplit(" ", 1)[0] + "..."
        return f'''<article class="blog-post-summary">
  <h2 class="post-title"><a href="{s}.html">{html.escape(post["title"])}</a></h2>
  <div class="post-meta">
    <span class="post-author">Written by {html.escape(post["author"])}</span>
    <span class="post-date">{format_date_short(post["date"])}</span>
  </div>
  <p class="post-preview">{html.escape(preview)}</p>
  <a href="{s}.html" class="read-more">Read more...</a>
</article>'''


CSS = '''
:root {
  --green-dark: #3b5e2b;
  --green-mid: #5a8a3c;
  --green-light: #8cb86b;
  --green-pale: #e8f0e0;
  --blue-dark: #1a3a5c;
  --blue-bg: #d4e4f0;
  --blue-light: #e8f0f8;
  --text: #333;
  --text-light: #666;
  --white: #fff;
  --border: #c0d0b0;
  --shadow: rgba(0,0,0,0.1);
}

@media (prefers-color-scheme: dark) {
  :root {
    --green-dark: #8cb86b;
    --green-mid: #6a9a4c;
    --green-light: #3b5e2b;
    --green-pale: #1a2a14;
    --blue-dark: #a0c0e0;
    --blue-bg: #0e1e2e;
    --blue-light: #152535;
    --text: #d8d8d0;
    --text-light: #a0a098;
    --white: #1a2418;
    --border: #3a4a30;
    --shadow: rgba(0,0,0,0.3);
  }
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Georgia', 'Times New Roman', serif;
  background: var(--blue-bg);
  color: var(--text);
  line-height: 1.7;
  min-height: 100vh;
}

a { color: var(--green-dark); text-decoration: none; }
a:hover { text-decoration: underline; color: var(--green-mid); }

#wrapper {
  max-width: 1100px;
  margin: 0 auto;
  background: var(--white);
  box-shadow: 0 0 20px var(--shadow);
  min-height: 100vh;
}

/* Header */
#header {
  background: linear-gradient(135deg, var(--green-dark), var(--green-mid));
  padding: 24px 30px;
  border-bottom: 3px solid var(--green-light);
}

#header h1 {
  font-size: 1.8em;
  color: var(--white);
  font-weight: normal;
  letter-spacing: 0.02em;
}

#header h1 a { color: var(--white); }
#header h1 a:hover { text-decoration: none; opacity: 0.9; }

#header .subtitle {
  color: var(--green-pale);
  font-size: 0.85em;
  margin-top: 4px;
  font-style: italic;
}

/* Navigation */
#nav {
  background: var(--green-pale);
  border-bottom: 1px solid var(--border);
  padding: 0 30px;
  display: flex;
  flex-wrap: wrap;
  gap: 0;
}

#nav a {
  display: inline-block;
  padding: 10px 16px;
  color: var(--green-dark);
  font-size: 0.85em;
  font-family: 'Helvetica Neue', Arial, sans-serif;
  border-right: 1px solid var(--border);
}

#nav a:hover, #nav a.active {
  background: var(--green-dark);
  color: var(--white);
  text-decoration: none;
}

@media (prefers-color-scheme: dark) {
  #nav a:hover, #nav a.active {
    background: var(--green-mid);
  }
}

/* Breadcrumb */
.breadcrumb {
  padding: 8px 30px;
  font-size: 0.8em;
  color: var(--text-light);
  border-bottom: 1px solid var(--border);
  font-family: 'Helvetica Neue', Arial, sans-serif;
}

.breadcrumb a { color: var(--text-light); }

/* Content area */
#content {
  padding: 30px;
  display: flex;
  gap: 30px;
}

#main-col {
  flex: 1;
  min-width: 0;
}

.page-heading {
  font-size: 1.5em;
  color: var(--green-dark);
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--green-pale);
}

/* Timeline sidebar */
#timeline {
  width: 200px;
  flex-shrink: 0;
  position: sticky;
  top: 20px;
  align-self: flex-start;
  max-height: calc(100vh - 40px);
  overflow-y: auto;
  font-family: 'Helvetica Neue', Arial, sans-serif;
  font-size: 0.78em;
  padding-right: 8px;
}

#timeline::-webkit-scrollbar { width: 4px; }
#timeline::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

#timeline h3 {
  font-size: 0.85em;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-light);
  margin-bottom: 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}

.tl-year {
  margin-bottom: 12px;
}

.tl-year-label {
  font-weight: bold;
  color: var(--green-dark);
  font-size: 1.05em;
  margin-bottom: 4px;
  padding: 2px 0;
}

.tl-post {
  display: block;
  padding: 3px 0 3px 12px;
  border-left: 2px solid var(--border);
  color: var(--text-light);
  line-height: 1.3;
  transition: border-color 0.15s, color 0.15s;
}

.tl-post:hover {
  border-left-color: var(--green-mid);
  color: var(--green-dark);
  text-decoration: none;
}

.tl-post .tl-date {
  display: block;
  font-size: 0.85em;
  color: var(--text-light);
  opacity: 0.7;
}

/* Blog posts */
.blog-post, .blog-post-summary {
  margin-bottom: 32px;
  padding-bottom: 28px;
  border-bottom: 1px solid var(--border);
}

.blog-post:last-child, .blog-post-summary:last-child {
  border-bottom: none;
}

.post-title {
  font-size: 1.3em;
  color: var(--green-dark);
  margin-bottom: 6px;
  font-weight: normal;
}

.post-title a { color: var(--green-dark); }

.post-meta {
  font-size: 0.8em;
  color: var(--text-light);
  margin-bottom: 14px;
  font-family: 'Helvetica Neue', Arial, sans-serif;
}

.post-meta .post-author {
  margin-right: 16px;
}

.post-content {
  font-size: 0.95em;
  line-height: 1.8;
}

.post-content p {
  margin-bottom: 14px;
}

.post-content p:last-child {
  margin-bottom: 0;
}

.post-image {
  margin: 16px 0;
  text-align: center;
}

.post-image img {
  max-width: 100%;
  height: auto;
  border: 1px solid var(--border);
  border-radius: 2px;
}

.post-preview {
  font-size: 0.9em;
  color: var(--text);
  margin-bottom: 10px;
  line-height: 1.6;
}

.read-more {
  font-size: 0.85em;
  font-family: 'Helvetica Neue', Arial, sans-serif;
  color: var(--green-mid);
}

.post-footer {
  margin-top: 16px;
  font-size: 0.8em;
  color: var(--text-light);
  font-family: 'Helvetica Neue', Arial, sans-serif;
}

.post-updated {
  margin-bottom: 4px;
  font-style: italic;
}

.post-comments {
  color: var(--green-mid);
}

/* Back link */
.back-link {
  display: inline-block;
  margin-bottom: 20px;
  font-size: 0.85em;
  font-family: 'Helvetica Neue', Arial, sans-serif;
}

/* Pagination */
.pagination {
  text-align: center;
  padding: 20px 0;
  font-family: 'Helvetica Neue', Arial, sans-serif;
  font-size: 0.85em;
}

.pagination a, .pagination span {
  display: inline-block;
  padding: 6px 12px;
  margin: 0 2px;
  border: 1px solid var(--border);
  border-radius: 3px;
}

.pagination span.current {
  background: var(--green-dark);
  color: var(--white);
  border-color: var(--green-dark);
}

/* Footer */
#footer {
  background: var(--green-pale);
  border-top: 1px solid var(--border);
  padding: 16px 30px;
  text-align: center;
  font-size: 0.75em;
  color: var(--text-light);
  font-family: 'Helvetica Neue', Arial, sans-serif;
}

/* Year navigation */
.year-nav {
  margin-bottom: 24px;
  font-family: 'Helvetica Neue', Arial, sans-serif;
  font-size: 0.85em;
}

.year-nav a, .year-nav span {
  display: inline-block;
  padding: 4px 10px;
  margin-right: 4px;
  border: 1px solid var(--border);
  border-radius: 3px;
}

.year-nav span.current {
  background: var(--green-dark);
  color: var(--white);
  border-color: var(--green-dark);
}

/* Responsive */
@media (max-width: 800px) {
  #content { flex-direction: column; }
  #timeline {
    width: 100%;
    position: static;
    max-height: none;
    border-bottom: 1px solid var(--border);
    padding-bottom: 16px;
    margin-bottom: 16px;
  }
}

@media (max-width: 640px) {
  #header { padding: 18px 16px; }
  #header h1 { font-size: 1.4em; }
  #nav { padding: 0 8px; }
  #nav a { padding: 8px 10px; font-size: 0.8em; }
  #content { padding: 20px 16px; }
  .page-heading { font-size: 1.2em; }
  .post-title { font-size: 1.1em; }
}
'''

def build_timeline(posts):
    """Build the sidebar timeline HTML grouped by year."""
    grouped = {}
    for p in posts:
        dt = datetime.fromisoformat(p["date"])
        grouped.setdefault(dt.year, []).append(p)

    tl = '<h3>Timeline</h3>\n'
    for year in sorted(grouped.keys(), reverse=True):
        tl += f'<div class="tl-year">\n<div class="tl-year-label">{year}</div>\n'
        for p in grouped[year]:
            s = slug(p["title"])
            dt = datetime.fromisoformat(p["date"])
            month_day = dt.strftime("%b %d")
            title_short = p["title"] if len(p["title"]) <= 28 else p["title"][:26] + "..."
            tl += f'<a class="tl-post" href="#{s}"><span class="tl-date">{month_day}</span>{html.escape(title_short)}</a>\n'
        tl += '</div>\n'
    return tl


NAV_ITEMS = [
    ("Home", "index.html"),
    ("Projects", "#"),
    ("Services", "#"),
    ("The Community", "#"),
    ("Equipment &amp; Methodology", "#"),
    ("Links", "#"),
    ("Surveyor's Blog", "index.html"),
]


def page_template(title, content, active_nav="Surveyor's Blog", breadcrumb_extra="", timeline_html=""):
    nav_html = ""
    for name, href in NAV_ITEMS:
        cls = ' class="active"' if name == active_nav else ""
        nav_html += f'<a href="{href}"{cls}>{name}</a>\n'

    bc = '<a href="index.html">Home</a> &rsaquo; '
    if breadcrumb_extra:
        bc += f'<a href="index.html">Surveyor\'s Blog</a> &rsaquo; {breadcrumb_extra}'
    else:
        bc += "Surveyor's Blog"

    sidebar = f'<aside id="timeline">{timeline_html}</aside>' if timeline_html else ""

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} - California Survey Company</title>
  <meta name="description" content="California Survey Co. Land Surveying and the Art of Surveying">
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📐</text></svg>">
  <style>{CSS}</style>
</head>
<body>
  <div id="wrapper">
    <div id="header">
      <h1><a href="index.html">California Survey Company</a></h1>
      <div class="subtitle">Land Surveying and the Art of Surveying</div>
    </div>
    <div id="nav">
      {nav_html}
    </div>
    <div class="breadcrumb">{bc}</div>
    <div id="content">
      <div id="main-col">
        {content}
      </div>
      {sidebar}
    </div>
    <div id="footer">
      Copyright &copy; 2013 California Survey Company. All Rights Reserved.<br>
      Originally powered by Joomla! &mdash; Recreated with care.
    </div>
  </div>
</body>
</html>'''


# Copy images to site directory
import shutil
src_images = Path("/home/jp/Projects/poppasblog/images")
dst_images = OUTDIR / "images"
for img in src_images.iterdir():
    if img.is_file() and img.stat().st_size > 0:
        shutil.copy2(img, dst_images / img.name)

# Group posts by year
years = {}
for p in posts:
    y = datetime.fromisoformat(p["date"]).year
    years.setdefault(y, []).append(p)

sorted_years = sorted(years.keys(), reverse=True)

# Build timeline
timeline = build_timeline(posts)

# Build index page (all posts expanded)
index_content = '<h1 class="page-heading">Surveyor\'s Blog</h1>\n'

for p in posts:
    index_content += post_html(p, is_full=True) + "\n"

with open(OUTDIR / "index.html", "w") as f:
    f.write(page_template("Surveyor's Blog", index_content, timeline_html=timeline))

# Build individual post pages
for p in posts:
    s = slug(p["title"])
    content = f'<a href="index.html" class="back-link">&larr; Back to all posts</a>\n'
    content += post_html(p, is_full=True)

    # Find prev/next
    idx = posts.index(p)
    nav = '<div style="display:flex;justify-content:space-between;margin-top:24px;font-size:0.85em;font-family:Helvetica Neue,Arial,sans-serif;">'
    if idx < len(posts) - 1:
        older = posts[idx + 1]
        nav += f'<a href="{slug(older["title"])}.html">&larr; {html.escape(older["title"])}</a>'
    else:
        nav += '<span></span>'
    if idx > 0:
        newer = posts[idx - 1]
        nav += f'<a href="{slug(newer["title"])}.html">{html.escape(newer["title"])} &rarr;</a>'
    else:
        nav += '<span></span>'
    nav += '</div>'
    content += nav

    with open(OUTDIR / f"{s}.html", "w") as f:
        f.write(page_template(p["title"], content, breadcrumb_extra=html.escape(p["title"]), timeline_html=timeline))

# Build year pages
for y in sorted_years:
    year_content = f'<h1 class="page-heading">Surveyor\'s Blog &mdash; {y}</h1>\n'
    year_content += '<div class="year-nav">Filter by year: <a href="index.html">All</a> '
    for yy in sorted_years:
        if yy == y:
            year_content += f'<span class="current">{yy}</span> '
        else:
            year_content += f'<a href="year-{yy}.html">{yy}</a> '
    year_content += '</div>\n'

    for p in years[y]:
        year_content += post_html(p, is_full=True) + "\n"

    with open(OUTDIR / f"year-{y}.html", "w") as f:
        f.write(page_template(f"Surveyor's Blog - {y}", year_content, timeline_html=timeline))

print(f"Built {len(posts)} post pages + index + {len(sorted_years)} year pages")
print(f"Images copied: {len(list(dst_images.iterdir()))}")
print(f"Output: {OUTDIR}")
