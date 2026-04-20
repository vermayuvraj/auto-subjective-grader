# SEO And Google Search Console Setup

This guide explains how to improve indexing and search visibility for `https://ai-grader.dev`.

## 1. What was already added in the codebase

The website now includes:

- sitewide metadata
- Open Graph and Twitter preview tags
- canonical URLs
- `robots.txt`
- `sitemap.xml`
- structured data (JSON-LD)
- route-specific metadata for Home, Evaluate, Team, and Documentation
- optional Google Search Console verification support through an environment variable

## 2. Add Google Search Console verification

Use the **HTML tag** method in Google Search Console.

### Steps

1. Open Google Search Console.
2. Add the property `https://ai-grader.dev`.
3. Choose **HTML tag** verification.
4. Copy the verification token only.

It will look similar to this:

```txt
google-site-verification=abc123xyz...
```

You only need the value after the equals sign.

Example:

```txt
abc123xyz...
```

### Where to put it

Add this environment variable in the web deployment:

```txt
GOOGLE_SITE_VERIFICATION=abc123xyz...
```

The app already reads this variable and outputs the verification meta tag automatically.

### Files involved

- `web/app/layout.tsx`
- `web/lib/seo.ts`
- `web/.env.example`

## 3. Submit the sitemap

After deployment, submit:

```txt
https://ai-grader.dev/sitemap.xml
```

inside Google Search Console.

## 4. Request indexing

Request indexing for these pages first:

- `https://ai-grader.dev/`
- `https://ai-grader.dev/evaluate`
- `https://ai-grader.dev/team`
- `https://ai-grader.dev/documentation.html`

## 5. Best target keywords

These are the strongest realistic keyword targets for this project.

### Primary keywords

- AI grader
- subjective answer sheet evaluation system
- automated subjective grading
- answer sheet evaluation tool
- AI answer sheet checker

### Secondary keywords

- rubric based grading system
- handwritten answer sheet OCR
- printed answer sheet OCR
- exam paper evaluation system
- student answer sheet grading
- formula and diagram grading

### Long-tail keywords

- AI tool for subjective answer sheet evaluation
- automated grading system for descriptive answers
- rubric based AI grading for exam papers
- handwritten answer sheet evaluation using OCR
- AI system for checking student answer sheets
- answer sheet grading with Gemini and SBERT

## 6. Which keywords should go on which page

### Home page

Target:

- AI grader
- subjective answer sheet evaluation system
- automated subjective grading

### Evaluate page

Target:

- answer sheet evaluation tool
- AI answer sheet checker
- rubric based grading system

### Documentation page

Target:

- subjective answer sheet evaluation documentation
- AI grading workflow
- OCR grading pipeline

### Team page

Target:

- Ai Grader team
- automated subjective grader project team

## 7. How to improve ranking over time

Code-side SEO helps indexing, but ranking also depends on authority and freshness.

Do these next:

1. Add the project to your GitHub README with the live domain.
2. Add the domain to your LinkedIn project section and team profiles.
3. Publish a short project summary on LinkedIn or Medium linking to the site.
4. Add one blog-style update or changelog page later.
5. Keep the documentation page detailed and useful.
6. Get backlinks from college pages, GitHub, portfolio sites, or research references.

## 8. Realistic expectation

The site will not become rank 1 just because metadata was added.

What this setup does:

- makes the site crawlable
- gives Google clear page meanings
- improves snippet quality
- improves social sharing previews
- gives Search Console a clean verification path

What still affects ranking:

- backlinks
- content quality
- page age
- user engagement
- how competitive the searched keyword is

## 9. Recommended first search phrases to test

Start by checking performance for:

- `ai grader subjective answer sheet`
- `automated subjective answer sheet evaluation system`
- `ai answer sheet checker for descriptive answers`
- `rubric based answer sheet grading`
- `handwritten answer sheet ai grading`

These are more realistic than trying to rank immediately for the very broad phrase `AI grader`.

