# Entry-Level Job Application Assistant

[中文](README.md)

An Agent skill that turns a resume, career goals, and a clear authorization scope into verified job opportunities and official applications. It supports search, draft preparation, authorized submission, and recovery after interruptions. It is not a standalone bot or a hiring guarantee.

[Download the customer bundle](downloads/entry-level-job-application-with-guide.zip) for the skill plus a Chinese guide. Install the skill and tell your Agent what you need. The optional `guide.html` explains setup and helps compose prompts; it does not search or apply, and you can skip it. Older skill-only ZIPs do not include the guide. Marketplace delivery files must be replaced separately.

## Get the skill or support the author

- **Free:** [skill source](skills/entry-level-job-application) · [complete bundle with Chinese guide](downloads/entry-level-job-application-with-guide.zip)
- **Support the author:** [purchase through SkillPay](https://render.alipay.com/p/yuyan/180020010001298808/product.html?caprMode=sync&merchantId=2088822673721480&productId=P0806000212843919). One-time price: CNY 19.9; the product page controls the current price.

Both channels provide the same skill. The Chinese guide and configuration examples are also publicly available for free. Purchasing supports the author and provides the packaged files through the platform; there are no paid-only features. Bring a compatible Agent; model costs are separate. Human application services and hiring guarantees are not included.

## After delivery or installation

When the Agent loads this skill after delivery, it explains capabilities, the minimum information needed, three ready-to-use prompts, and the optional guide. Specific tasks get a brief introduction instead; continuing a task does not repeat it. The instructions are self-contained even when no HTML attachment is delivered.

If your Agent only downloads the files, say: “After delivery, load entry-level-job-application and explain how I can start, including a guide link I can actually access.” This is a skill instruction, not a platform installation hook. Replace the marketplace delivery file separately and verify what customers receive.

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
