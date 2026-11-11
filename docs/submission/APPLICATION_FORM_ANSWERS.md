# Portal Application — Field-by-Field Answers

For **https://ai4elections.risenetworks.org/application**.
Five steps. No character limits are set on the form, but keep every long answer
under about 1,000 characters so the server-side validator never truncates it.

Answer the fields in the order below. Fields marked `[YOU]` are personal facts
only you can supply; everything else is copy-paste ready.

> Reminder: this form is the **application**, not the prototype submission. The
> working prototype is entered in step 3 (`prototype_link`). The prototype is due
> 13 December 2026.

---

## Step 1 — Personal Information

| Portal field | Answer |
| --- | --- |
| First Name | `[YOU — first name]` |
| Last Name | `[YOU — last name]` |
| Email Address | `[YOU — reachable email]` |
| Phone Number | `[YOU — e.g. +234 80X XXX XXXX]` |
| Country of Residence | **Nigeria** |
| State of Residence | `[YOU — e.g. Federal Capital Territory]` |
| City | `[YOU — e.g. Abuja]` |
| What best describe your application? | **Team** |

`application_type` is the only option that unlocks the team block in step 4, so
choose **Team**.

## Step 1 — Your Background

| Portal field | Answer |
| --- | --- |
| Tell us about your experience * | see answer 1 |
| Primary Area of Expertise * | `Cybersecurity, AI Security, and Secure Software Development` |
| Years of Experience * | `4` |
| Current Role / Occupation * | `Cybersecurity Practitioner and Software Developer` |
| Organisation / Institution * | `Jigawa Digital Network (JDN)` |
| Highest level of Education * | `Bachelor's degree in Cybersecurity` |
| Academic / Professional Field * | `Cybersecurity and Software Development` |

**1. Tell us about your experience**

> I am a cybersecurity professional and software developer with a strong interest in AI security, cloud security, and the application of emerging technologies to real-world challenges.
>
> I have practical experience designing and developing security-focused applications, including SentinelShare, a blockchain-based secure file-sharing system with intelligent threat detection. I have also worked on cloud security projects using AWS and Microsoft Azure, alongside web application development and cybersecurity research.
>
> My technical experience includes Python, JavaScript, React, FastAPI, PostgreSQL, Linux, AWS, Azure, and machine-learning concepts.
>
> Beyond technical development, I am passionate about cybersecurity awareness, digital resilience, and using technology to address challenges within my community.
>
> I am particularly interested in applying AI to strengthen cybersecurity, detect emerging threats, and support safer digital systems. Through AI4Elections, I hope to contribute my technical skills, collaborate with other innovators, and develop practical solutions that strengthen electoral cybersecurity and public trust.

---

## Step 2 — Your Skills

| Portal field | Answer |
| --- | --- |
| Skills (Use (,) after each skill) * | see answer 2 |
| Tell us about your relevant experience * | see answer 3 |

**2. Skills** (comma after each skill, as the field asks)

> Cybersecurity, Software Development, Python Programming, JavaScript, React.js, FastAPI, Machine Learning, Artificial Intelligence, Cloud Security, Blockchain Technology, Linux, Network Security, Database Management, Threat Detection, Secure Application Development, Technical Research, Problem Solving, Team Collaboration

**3. Tell us about your relevant experience**

> I have practical experience in cybersecurity, software development, cloud technologies and the development of security-focused applications. One of my major projects is SentinelShare, a blockchain-based secure file-sharing system integrated with intelligent threat detection using machine learning. I have also worked on cloud security projects using AWS and Microsoft Azure, including cloud resource configuration, security hardening and access management.
>
> I also work with a three-person team on Votex AI, a defensive electoral incident platform built for this challenge. It covers secure intake, explainable phishing analysis, cross-report correlation, privacy-preserving national aggregates and a hash-chain audit trail, and it is validated with 40 backend tests plus browser tests for keyboard-only reporting and four locales.
>
> Additionally, I have experience developing web applications, implementing authentication systems, working with databases, and exploring AI applications in cybersecurity. I have also been involved in cybersecurity awareness and digital innovation initiatives.
>
> These experiences have strengthened my ability to identify security challenges, develop practical technical solutions and work with emerging technologies. I am particularly interested in applying these skills to electoral cybersecurity, threat intelligence and digital resilience.

---

## Step 2 — Your Interest

| Portal field | Answer |
| --- | --- |
| Which challenge track interests you most? * | `Track 4 — Electoral Cybersecurity & Resilience` |
| Why are you interested in this challenge area? * | see answer 4 |

**4. Why are you interested in this challenge area?**

> My interest in this area is practical. I want to apply my cybersecurity and software development experience to a public-interest problem where the impact is direct, and electoral cybersecurity is one of the clearest examples.
>
> Election-related organisations and authorised stakeholders face growing cybersecurity threats, including phishing attacks, malicious links, impersonation, social engineering and suspicious digital communications. However, identifying, analysing and prioritising these incidents quickly can be challenging, especially when reports come from different sources.
>
> Votex AI aims to address this gap by providing an AI-assisted platform that helps authorised stakeholders analyse reported incidents, identify potential threats, assess their risk levels and receive actionable defensive recommendations. The goal is to improve electoral cybersecurity incident response, protect sensitive electoral information and strengthen trust in Nigeria's electoral processes through responsible AI and human oversight.

---

## Step 3 — Your Idea

Answer **Yes, I have an idea**. Six text areas then appear, followed by idea
stage and prototype questions.

| Portal field | Answer |
| --- | --- |
| Do you already have a solution idea? * | **Yes, I have an idea** |
| If Yes, what problem are you trying to solve? * | see answer 5 |
| Who is affected by this problem? * | see answer 6 |
| Describe your proposed solution * | see answer 7 |
| How would AI or technology contribute to the solution? * | see answer 8 |
| Who would benefit from the solution? * | see answer 9 |
| What makes your approach different or useful? * | see answer 10 |
| What stage is your idea currently at? * | **Working prototype** |
| Do you already have a prototype? | **Yes** |
| If yes, prototype/project link | `https://github.com/Ibrahim-15217/votex-ai` |

**5. What problem are you trying to solve?**

> During an election period, phishing, malicious links, impersonation and social engineering target the people and organisations that run and observe the process. Reports of those incidents arrive through different channels and formats, so each one is handled in isolation. One coordinated campaign can look like dozens of unrelated complaints, analysts lose time re-triaging the same indicators, and evidence is hard to authenticate afterwards.
>
> The risk is not only technical. National-level visibility can expose the small organisation or individual whose report revealed a pattern, which discourages reporting. Most existing tools are either awareness material or dashboards with no structured intake, no explanation behind their risk scoring and no audit trail. Votex AI closes that gap by turning scattered reports into explainable, correlated and auditable incident intelligence, with a human in control at every step.

**6. Who is affected by this problem?**

> The problem affects electoral institutions and their staff, election officials, authorised election observers, civil society organisations, political stakeholders, journalists and citizens who depend on reliable electoral information. These groups may encounter phishing attacks, impersonation, malicious links and other cyber threats that could compromise sensitive information, disrupt operations or undermine public confidence in the electoral process.

**7. Describe your proposed solution**

> Votex AI is an AI-assisted electoral cybersecurity incident triage and resilience platform that helps authorised stakeholders identify, analyse and respond to potential cyber threats targeting the electoral environment.
>
> Reporters submit suspicious URLs, phishing messages, impersonation attempts and other incident reports through a plain-language intake, with evidence validated and hashed for integrity. A hybrid analyser combines URL and domain rules, text signals and a TF-IDF + Logistic Regression model to extract indicators, classify the report and assign an explainable risk level, showing the reasons and model version beside the score.
>
> The platform includes an incident management dashboard, threat intelligence views, correlation that links separate reports from the same organisation into one campaign, audit logs backed by a tamper-evident hash chain, and a human-review mechanism that lets analysts verify, override and manage AI-generated assessments. National aggregates suppress any cell with fewer than five contributors.
>
> Votex AI uses synthetic, anonymised and authorised public data only. It strengthens electoral cybersecurity and incident response without interfering with live electoral infrastructure or replacing human judgement.

**8. How would AI or technology contribute to the solution?**

> AI does the triage, not the decision. The analyser scores each report and explains itself: URL and domain rules catch look-alike portals, text signals catch urgency and credential requests, and a TF-IDF + Logistic Regression model adds a learned signal. Each component and weight is published, so an analyst can see why a report scored 72 instead of trusting a black box. The score is advisory — a human decides, can override, and every action is audited. Analysis runs fully offline: the system never visits a submitted link and never scans a third-party system.

**9. Who would benefit from the solution?**

> Electoral staff and observers get a fast, low-friction way to report. Analysts get one queue with explainable triage and linked cases instead of scattered inboxes. Coordinators get aggregate visibility that suppresses any cell below k = 5, so national trends never expose a single reporter. Voters benefit indirectly from earlier detection of fake portals. Civil-society and electoral bodies get an auditable, reproducible design they can pilot under written authorisation.

**10. What makes your approach different or useful?**

> Votex AI goes beyond conventional security monitoring by combining explainable AI triage with cross-report correlation, privacy-preserving aggregate reporting and a tamper-evident audit trail. Rather than producing a black-box score, it shows which indicators and weights drove each risk level, so an analyst can verify or override the assessment. Separate reports that share indicators are linked into one campaign, and national views suppress any cell below k = 5 so a pattern never exposes the organisation that reported it. The workflow is reproducible from synthetic data, works on low-bandwidth devices, and keeps human experts in control of every security decision.

---

## Step 4 — Applying as an existing team

This block appears because step 1 says **Team**. It is not marked required, but
fill it: it is how the judges identify the team.

| Portal field | Answer |
| --- | --- |
| Team Name | `Cyber Defenders` |
| Team Lead | `[YOU — full name]` |
| Team size | `3` |
| Team Description | see answer 11 |
| Names and Role of Team Members ( use (,) after each name and role) | see answer 12 |

**11. Team Description**

> Cyber Defenders is a three-person, multidisciplinary team building defensive technology for Nigerian elections. We combine cybersecurity and incident-response thinking, backend engineering and applied machine learning, and inclusive frontend design. Together we built Votex AI end to end: secure intake, explainable phishing analysis, tenant-scoped correlation, privacy-preserving national aggregates and a tamper-evident audit trail. We work evidence-first — every claim is backed by a test, screenshot or reproducible command — and we are committed to nonpartisan, human-supervised, NDPA-aligned use of AI.

**12. Names and Role of Team Members**

> `[MEMBER 1 NAME] - Team lead, product, problem framing and demo, [MEMBER 2 NAME] - Cybersecurity, backend, auth, privacy and audit, [MEMBER 3 NAME] - Engineering, AI, frontend and accessibility`

Use the real names and keep the comma-after-each-item format. Team size must
match the number of names: **3**.

### Accessibility & Participation needs

| Portal field | Answer |
| --- | --- |
| Do you have any accessibility or participation requirements you would like us to consider? | **No** (choose **Yes** and describe if anyone on the team needs support) |
| If yes, please tell us what support you may require | leave blank unless you chose Yes |

---

## Step 5 — Declarations

Read the text on the page, then tick:

- [ ] **I have read and understand the responsible participation requirements.**
- [ ] **I confirm that the information provided in this application is accurate to the best of my knowledge.**
- [ ] **I agree to the processing of my information for the purposes described in the Privacy Notice.**
- [ ] **I agree to the Applicant Declaration.**
- [ ] *(optional)* **I would like to opt in to the #AI4Elections Community of Practice and national registry.** — recommended: tick it, it is consent-based and you can withdraw.

All four required boxes must be ticked before **Submit Application** works.

---

## Before you press Submit

1. Every `[YOU]` and `[MEMBER …]` placeholder is replaced.
2. Team size says **3** and the member list has exactly three names.
3. `prototype_link` is `https://github.com/Ibrahim-15217/votex-ai` and it opens
   in a private browser window (the repo is public).
4. No confidential programme material, `.env` file, database or real voter data
   is linked anywhere in the application.
5. Screenshot the **Application Submitted** panel (or save the confirmation
   email) the moment it appears. That screenshot is your receipt.
6. Deadline: **12 November 2026, 11:59pm WAT**. Submit with time to spare —
   the portal does no draft saving, so keep this page open until it confirms.

## What the application does not ask for

These belong in the **13 December prototype submission**, not here:

- the three-minute demo video;
- the problem statement, methodology, model card, data sheet and threat model;
- the test evidence and screenshots.

Have them ready in the repository and in `docs/submission/` when the prototype
form opens.
