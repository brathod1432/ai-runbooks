# Discussion Guidelines

GitHub Discussions is the community space for **awesome-ai-runbooks**. It is
where we ask questions, trade ideas, and celebrate the runbooks we ship. This
guide explains how to use it well so the space stays useful, welcoming, and
searchable. All activity here is governed by our
[Code of Conduct](../CODE_OF_CONDUCT.md).

## Categories

We organize discussions into four categories. Please post in the right one.

- **Q&A** — Ask how to use a runbook, adapt one to your agent platform, or
  interpret the standards. Questions have a formal *answer*, so mark the reply
  that solved your problem as the accepted answer. This helps the next person.
- **Ideas** — Float a concept before it is a formal request: a new runbook
  category, a tooling improvement, a change to the review process. Ideas are for
  gathering signal and refining a proposal.
- **Show and tell** — Share a runbook you adapted, a trajectory from a real
  agent run, metrics you collected, or an integration you built. Show the
  community what worked.
- **Announcements** — Read-only for maintainers: releases, roadmap updates, and
  governance changes.

## Etiquette

- **Be kind and assume good faith.** People arrive with different backgrounds and
  agent stacks. Critique ideas, never people.
- **Stay on topic** and keep one thread to one subject. Start a new discussion
  rather than hijacking an unrelated one.
- **Search first.** Someone may have already answered your question or proposed
  your idea. Add to the existing thread instead of duplicating it.
- **No secrets, ever.** Never paste credentials, tokens, private hostnames, or
  customer data. Redact logs and outputs before sharing. Security-sensitive
  reports belong in a private advisory — see [`SECURITY.md`](../SECURITY.md).
- **Give back.** If an answer helped you, upvote it and mark it accepted.

## How to ask a good question

The faster we understand your situation, the faster you get a useful answer.

1. **Write a specific title.** "Kafka lag runbook: which metric for partition
   skew?" beats "help with runbook".
2. **State your goal.** What outcome are you trying to reach?
3. **Show what you tried.** Include the runbook and section you followed, the
   command you ran, and the *actual* vs *expected* result.
4. **Include context.** Agent platform (Devin, Claude Code, Cursor, etc.),
   commit or tag, OS, and relevant tool versions.
5. **Make it reproducible.** Trim logs to the relevant lines and format code and
   output in fenced blocks.

## Issue or discussion?

Use this quick test:

- **Open a discussion** when the outcome is open-ended: a question, an idea to
  explore, or something to share. Discussions are conversations.
- **Open an issue** when there is a concrete, trackable unit of work: a bug in a
  runbook or tool, a specific new-runbook request, a documentation gap, or a
  feature with a clear definition of done. Issues are tasks.

A common path is to start in **Ideas**, refine the proposal with community
feedback, and then open a scoped issue once there is consensus. Maintainers may
convert a discussion to an issue (or vice versa) to keep work tracked in the
right place.

Thanks for helping build a high-quality, safety-first library of agent
runbooks. Good discussions today become great runbooks tomorrow.
