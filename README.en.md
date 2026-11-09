# Entry-Level Job Application Assistant

[中文](README.md)

An Agent skill that turns a resume, career goals, and a clear authorization scope into verified job opportunities and official applications. It supports search, draft preparation, authorized submission, and recovery after interruptions. It is not a standalone bot or a hiring guarantee.

Try the [interactive Chinese tutorial](docs/starter-kit/README.md): download the repository and open `docs/starter-kit/guide.html` in a browser. No frontend build step is required.

## Get started

Copy the complete [skills/entry-level-job-application](skills/entry-level-job-application) folder into your Agent's skill directory, including its references, scripts, assets, and metadata. See the [client guide](skills/entry-level-job-application/references/clients.md) for documented host-specific paths and invocation syntax. The operational skill and detailed references are currently in Chinese.

Tell the assistant where your resume is, what work you want, and what it may do:

> Use entry-level-job-application. Read my resume at [absolute path to my private resume] and find entry-level data analyst roles in Shanghai or Hangzhou. Compare verified opportunities and prepare drafts only. Do not register, upload, or submit. Ask together for any missing facts that affect the current step.

For automatic applications, explicitly authorize the scope of filling, uploading, and submitting. Necessary account registration follows its own authorization. Confirmed facts and standing permissions are reused; you do not fill out internal JSON or an environment questionnaire.

| Mode | Scope |
|---|---|
| Search and compare | Verify and rank opportunities; no registration, uploads, or submission |
| Prepare | Organize materials and draft within the authorized scope |
| Apply and submit | Submit within standing authorization, verify the receipt, and continue |

## How it works

- Verify specific roles through employer websites or employer-linked recruitment systems. Keep evidence for personal facts and job details.
- Check eligibility before scoring fit. Use intervals for unknown preferences; a score is not a hiring probability.
- Save submission state before clicking and reconcile with the official record afterward. An uncertain result does not trigger another submission.
- Hand off personal verification and unsupported steps with a concrete next action. CAPTCHA failures share a three-attempt ceiling; stricter site and tool restrictions take precedence.

Reuse capable existing tools. Automatically initialize missing Playwright MCP capability only when needed and authorized; add Windows-MCP only for necessary native Windows interaction. No persistent background service is created.

Optional Python standard-library helpers, `check_application.py` and `application_state.py`, check prepared application data and maintain an atomic private ledger. Simple searches do not need them. Without a usable Python runtime, use reliable private records instead of installing an environment just for the helpers. See [execution and recovery](skills/entry-level-job-application/references/execution.md) and the [evidence format](skills/entry-level-job-application/references/evidence.md).

## Local validation

From the repository root, using a verified local Python interpreter:

```text
python -m unittest discover -s tests -v
python tools/demo.py
```

On Windows, use the interpreter's actual path if needed to avoid Store aliases. The demo uses fictional data and does not log in or submit applications.

See [test coverage](TESTING.md) and the [offline demo guide](docs/demo.md). Documented configuration branches exist for Codex, Claude Code, DeepSeek Harness, and ZCode; they do not establish universal compatibility. Current evidence is local and simulated: live ATS submissions, every client integration, and marketplace purchase/delivery have not been verified.

Keep resumes, credentials, screenshots, and application records outside this public repository. Buying the skill does not grant permission to access personal data or submit applications.
