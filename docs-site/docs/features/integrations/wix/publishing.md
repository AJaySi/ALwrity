# Publishing Flow

End‑to‑end flow for publishing a blog post to Wix.

## Steps
1. Check connection (tokens + `memberId`)
2. Convert markdown → Ricos JSON
3. Import images to Wix Media Manager
4. Create blog post via Wix Blog API
5. Publish (or save draft)
6. Return URL

## From the Blog Writer
- Generate content in ALwrity
- Use “Publish to Wix” action
- The publisher will:
  - Verify connection
  - Convert content
  - Import images
  - Create & publish
  - Return published URL

## Notes
- Categories and tags are looked up/created automatically
- SEO metadata is posted with the blog (see SEO Metadata)
- Errors are reported with actionable messages


