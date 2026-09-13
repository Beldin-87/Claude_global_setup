# Context7 lookups

## When to look up

Context7 is for version-sensitive facts about third-party code, not a reflex. This rule overrides the server's own "use even when you think you know the answer" instruction.

Run a lookup when at least one of these holds:

- The answer depends on a specific version: config keys, renamed or removed APIs, migration between major versions.
- The library has shipped a major release within the last twelve months (Next.js, Prisma, Tailwind, Vite and similar fast-moving projects).
- The library is niche or unfamiliar and the answer cannot be checked another way.
- The package is not installed locally, so there are no types or sources to read.
- An API decision shapes an executor briefing and a wrong guess would cost a full round.

Skip the lookup when:

- The API is stable and well known: language standard libraries, Git, SQL, core React hooks and the like.
- The package is installed: read its type definitions or source in `node_modules` (or the equivalent) first. They match the exact installed version; Context7 does not.
- The question is about this project's own code or business logic.

When unsure, read the local code first and look up only what remains open.

## How to look up

When Context7 applies — a question about a library, framework, SDK, API, CLI tool, or cloud service — run the lookup like this.

1. Always start with `resolve-library-id` using the library name and what to look up in the library's documentation, unless the user provides an exact library ID in `/org/project` format
2. Pick the best match (ID format: `/org/project`) by: exact name match, description relevance, code snippet count, source reputation (High/Medium preferred), and benchmark score (higher is better). If results don't look right, try alternate names or queries (e.g., "next.js" not "nextjs", or rephrase the question). Use version-specific IDs when the user mentions a version
3. `query-docs` with the selected library ID and what to look up in the library's documentation (not single words), scoped to a single concept. If the question spans multiple distinct concepts (e.g. routing and auth and caching), make a separate `query-docs` call per concept with the same library ID, unless the question is about how the concepts interact — combined queries dilute ranking and return shallow results for each topic
4. Answer using the fetched docs
