"""Generate a synthetic, labelled electoral-phishing dataset for Votex AI.

Design rules
------------
- Synthetic only: every message is generated from templates. No real message,
  person, voter record or private communication is used.
- Reserved domains and IP ranges only for suspicious links: ``.example``,
  ``.test`` and RFC 5737 documentation addresses. This prevents accidental
  traffic to a real host if a demo link is clicked.
- Benign links point to public institutional home pages used purely as
  illustrative context. They are not scraped or tested.
- Both classes share electoral vocabulary so a classifier must learn security
  signals instead of simply detecting the word "election".
- Balanced classes (700/700) and a fixed seed keep experiments reproducible.

Run from the repository root:

    python ai-engine/training/generate_data.py

Outputs:
    ai-engine/datasets/electoral_phishing_synthetic.csv
    ai-engine/datasets/manifest.json
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

SEED = 20261109
ROWS_PER_CLASS = 700
HAUSA_SHARE = 0.15

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "datasets"
CSV_PATH = OUTPUT_DIR / "electoral_phishing_synthetic.csv"
MANIFEST_PATH = OUTPUT_DIR / "manifest.json"

STATES = [
    "Abia",
    "Adamawa",
    "Akwa Ibom",
    "Anambra",
    "Bauchi",
    "Bayelsa",
    "Benue",
    "Borno",
    "Cross River",
    "Delta",
    "Ebonyi",
    "Edo",
    "Ekiti",
    "Enugu",
    "FCT",
    "Gombe",
    "Imo",
    "Jigawa",
    "Kaduna",
    "Kano",
    "Katsina",
    "Kebbi",
    "Kogi",
    "Kwara",
    "Lagos",
    "Nasarawa",
    "Niger",
    "Ogun",
    "Ondo",
    "Osun",
    "Oyo",
    "Plateau",
    "Rivers",
    "Sokoto",
    "Taraba",
    "Yobe",
    "Zamfara",
]

ROLES = [
    "Presiding Officer",
    "Electoral Officer",
    "Ward Collation Officer",
    "Registration Officer",
    "ICT Officer",
    "Observer",
    "Party Agent",
    "Media Officer",
]

OFFICES = [
    "Demo Electoral Commission",
    "State Electoral Office",
    "Local Government Electoral Office",
    "National Situation Room",
    "Observer Coordination Desk",
]

SALUTATIONS_EN = [
    "Dear {role},",
    "Hello {role},",
    "Attention: {role}",
    "Dear colleague,",
    "Good day {role},",
]

SALUTATIONS_HA = [
    "Gaisuwa {role},",
    "Sannu {role},",
    "Kula: {role}",
    "Ya ku abokin aiki,",
]

CHANNELS = ["email", "sms", "whatsapp", "web_form"]

OFFICIAL_URLS = [
    "https://inec.gov.ng/",
    "https://inec.gov.ng/news/",
    "https://inec.gov.ng/contact/",
    "https://cert.gov.ng/advisories/",
    "https://cert.gov.ng/report/",
    "https://nccc.gov.ng/",
]

SUSPICIOUS_URLS = [
    "http://inec-verify.example/portal",
    "https://inec-portal.example/login",
    "http://pvc-confirm.example/",
    "https://ng-electionresults.example/",
    "http://inec-support.example/verify",
    "https://voter-accreditation.example/",
    "http://inecstaff.example/",
    "https://election-update.example/result",
    "http://192.0.2.10/verify",
    "https://198.51.100.23/portal",
    "https://203.0.113.45/inec/login",
    "https://short.example/inec",
    "https://inec-secure.example/payment",
]

PHISHING_TEMPLATES: dict[str, list[str]] = {
    "fake_portal": [
        "Your voter accreditation status is pending. Confirm your details within 24 hours at {url} to avoid removal from the supplementary register in {state}.",
        "The {office} has opened a new verification window for {state}. Validate your polling unit and voter record at {url} before {deadline}.",
        "Final notice: your PVC record could not be matched. Re-enter your voter identification number and date of birth at {url}.",
        "A new electoral portal has been deployed for {state}. Log in with your voter credentials at {url} to download your confirmation slip.",
        "Your registration was flagged during duplicate checks. Resolve the issue at {url} before the display exercise closes.",
    ],
    "credential_harvest": [
        "To receive the updated ward results template, sign in with your official email and password at {url}.",
        "The situation room is migrating accounts. Confirm your username, password and one-time code at {url} to keep access.",
        "Your account session expired. Re-authenticate at {url} and upload a photo of your staff identity card.",
        "ICT support needs your login details to restore access to the collation dashboard. Submit them securely at {url}.",
        "Complete the mandatory security update by entering your credentials at {url}. Accounts not updated by {deadline} will be suspended.",
    ],
    "payment_fraud": [
        "Your PVC is ready for collection. Pay a Naira {amount} logistics fee at {url} and bring the receipt to {office}.",
        "Accreditation for {state} observers requires a Naira {amount} processing fee. Pay at {url} to receive your tag before {deadline}.",
        "Your election duty allowance of Naira {amount} is on hold. Confirm your bank details and pay a release fee at {url}.",
        "Only paid registrations will be included in the final training list. Send Naira {amount} via {url} to secure your place.",
        "Pay the Naira {amount} verification charge at {url} to activate your result portal account for {state}.",
    ],
    "impersonation": [
        "This is a message from the {office} ICT desk. We need your password to verify the {state} collation system before {deadline}.",
        "The National Chairman has approved a special result review for {state}. Send your official account details to {url} for clearance.",
        "I am the {role} supervisor for {state}. Reply with the login for the ward dashboard so I can approve the uploaded results.",
        "You have been selected for a sensitive assignment. Confirm your identity and password at {url} to receive the briefing.",
        "Security unit directive: share your portal PIN with the officer at {url} for the audit scheduled on {deadline}.",
    ],
    "fake_result": [
        "Provisional results for {state} have been released early. View them at {url} before the official announcement.",
        "Breaking: final collation figures for your local government are available at {url}. Download and forward immediately.",
        "The result server is live. Check your polling unit score at {url} and circulate the screenshot.",
        "Leaked collation sheets for {state} are available. Verify them at {url} before they are taken down.",
        "Your polling unit result has been altered. See the corrected figure at {url} and confirm before {deadline}.",
    ],
    "malware_attachment": [
        "The updated collation template is attached. Enable macros and open it before {deadline} to submit {state} figures.",
        "Download the election duty roster at {url}. The file is password-protected; use the password INEC2027.",
        "Attached is the biometric verification utility for your laptop. Install it immediately or your device will be locked.",
        "Please open the attached results workbook and allow editing so the macro can sync your ward data.",
        "A security patch for the result portal is available at {url}. Run the executable as administrator.",
    ],
    "fake_accreditation": [
        "Observer accreditation for {state} closes today. Submit your details and payment reference at {url}.",
        "Your media accreditation badge is ready. Confirm your name, phone number and organisation at {url}.",
        "The {office} has extended special accreditation to your team. Register every member at {url} before {deadline}.",
        "Party agent accreditation has been moved online. Upload your passport photograph and identity number at {url}.",
        "You are invited to the official training in {state}. Confirm attendance and download your materials at {url}.",
    ],
}

BENIGN_TEMPLATES: dict[str, list[str]] = {
    "official_notice": [
        "The {office} will hold a routine coordination meeting for {state} on {deadline}. Attendance is free and no payment is required.",
        "Official notice: the display of the voters register will take place at ward offices in {state}. Verify details only at {official_url} or your local office.",
        "The commission has published the election timetable for {state}. Read the official notice at {official_url}.",
        "Staff rosters for the {state} exercise are available on the internal notice board. Contact your supervisor with any question.",
        "A public holiday has been declared for the election date. Normal office hours resume the following Monday.",
    ],
    "training_invitation": [
        "You are invited to a free training session for {role}s in {state} on {deadline}. Register through your supervisor or at {official_url}.",
        "The {office} will run a refresher on result collation procedures. No fee is required; bring your staff identification card.",
        "Training materials for presiding officers are available at {official_url}. Download the PDF and review it before the session.",
        "A virtual briefing for observers will hold on {deadline}. Joining details will be sent through official channels.",
        "Attendance at the ward training will be recorded by the supervisor. Please arrive 30 minutes early.",
    ],
    "security_advisory": [
        "Security reminder: the ICT team will never ask for your password or one-time code. Report suspicious messages to {official_url}.",
        "Phishing awareness: check the domain before signing in. Official communications use the published government domain, not short links.",
        "Advisory: do not enable macros in unexpected attachments. Report the email to the security desk and delete it.",
        "If you receive a message asking for payment to confirm your registration, do not pay. Verify it with your supervisor.",
        "Use your own account and never share credentials. The audit log records every login for accountability.",
    ],
    "public_awareness": [
        "Public awareness: collect your PVC at the ward office where you registered. Collection is free.",
        "Voters can check their polling unit at the official portal {official_url} or at the local government office.",
        "The commission reminds the public that election results are announced only through official channels.",
        "Report vote buying or intimidation to the official hotline. Your identity will be protected.",
        "Accreditation and voting are free. Do not pay any agent or official for assistance.",
    ],
    "observer_coordination": [
        "Observer deployment list for {state} is attached to the official coordination email. Confirm your availability with your team lead.",
        "The observers' briefing will start at 8:00am at the {office}. Bring your accreditation badge and a valid ID.",
        "Please submit your observation checklist through the official portal {official_url} after the exercise.",
        "A debrief for observers in {state} will hold on {deadline}. Share issues through your coordinator.",
        "Travel arrangements for accredited observers will be communicated by the coordination desk.",
    ],
    "result_verification_guidance": [
        "Polling unit results are displayed at the polling unit and uploaded to the official portal {official_url}. Compare the two before sharing.",
        "Only results announced by the returning officer are official. Ignore screenshots from unverified sources.",
        "If a result sheet appears altered, report it to the {office} with the polling unit code. Do not circulate it.",
        "Agents may request a copy of the result sheet at the polling unit. Follow the official procedure.",
        "The collation centre will publish updates at {official_url}. Verify any figure against the signed sheet.",
    ],
    "media_release": [
        "The {office} has issued a press release on preparations for {state}. Read the statement at {official_url}.",
        "A media briefing will hold on {deadline} at the {office}. Accreditation is free for approved outlets.",
        "The commission denies reports of a portal shutdown. Official updates are published at {official_url}.",
        "Journalists should verify claims with the press office before publication.",
        "The commission has published frequently asked questions about the accreditation process at {official_url}.",
    ],
}

PHISHING_TEMPLATES_HA: dict[str, list[str]] = {
    "fake_portal": [
        "Hattara: bayanan rajistar ku na zabe ba su cika ba. Tabbatar da su cikin sa'o'i 24 a {url} don kada a cire ku daga rajista a {state}.",
        "Ofishin {office} ya bude sabon lokaci na tabbatarwa a {state}. Duba rajistar ku a {url} kafin {deadline}.",
    ],
    "credential_harvest": [
        "Don samun sabon tsarin tattara sakamako, shiga da imel da kalmar sirri ta hukuma a {url}.",
        "Sashen ICT na bukatar kalmar sirrin ku don dawo da damar shiga dashboard. Aika su a {url}.",
    ],
    "payment_fraud": [
        "Katin zabe na ku ya shirya. Biya Naira {amount} a {url} don karbar shi a {office}.",
        "Ana bukatar Naira {amount} don tabbatar da ayyukan sa ido a {state}. Biya a {url} kafin {deadline}.",
    ],
    "impersonation": [
        "Wannan sako ne daga sashen ICT na {office}. Muna bukatar kalmar sirrin ku don tabbatar da tsarin {state}.",
        "Shugaban gudanarwa ya amince da bitar sakamako na {state}. Aika bayanan asusun ku a {url}.",
    ],
    "fake_result": [
        "An fitar da sakamakon farko na {state}. Duba su a {url} kafin sanarwar hukuma.",
        "Sakamakon gidan zabe na ku ya canza. Duba sabon adadi a {url} kafin {deadline}.",
    ],
    "malware_attachment": [
        "Sabon fom na tattara sakamako yana makale. Kunna macro kuma bude shi kafin {deadline}.",
        "Sauke kayan aikin tabbatar da zabe a {url}. Kunna fayil din nan take.",
    ],
    "fake_accreditation": [
        "Rajistar masu sa ido na {state} yana rufewa yau. Aika bayanan ku a {url}.",
        "An mika rajistar wakilan jam'iyya kan layi. Aika hoto da lambar shaida a {url}.",
    ],
}

BENIGN_TEMPLATES_HA: dict[str, list[str]] = {
    "official_notice": [
        "Sanarwa: ofishin {office} zai yi taron daidaitawa na {state} a {deadline}. Halarta kyauta ne kuma ba a bukatar biya.",
        "Za a nuna rajistar masu zabe a ofisoshin gunduma a {state}. Tabbatar da bayanai a {official_url} kawai.",
    ],
    "training_invitation": [
        "Ana gayyatar ku zuwa horo kyauta na {role}s a {state} a {deadline}. Yi rajista ta ofishin ku.",
        "Kayan horo na jami'an gudanarwa suna nan a {official_url}. Sauke su kafin zaman.",
    ],
    "security_advisory": [
        "Tunatarwa: sashen ICT ba zai taba tambayar kalmar sirrin ku ba. A kai rahoton sako mai shakka zuwa {official_url}.",
        "Kada ku kunna macro a fayil da ba ku tsammani. A kai rahoton imel ga sashen tsaro.",
    ],
    "public_awareness": [
        "Sanarwa ga jama'a: karbi katin zabe a ofishin da kuka yi rajista. Karba kyauta ce.",
        "Ana iya duba gidan zabe a {official_url} ko a ofishin karamar hukuma.",
    ],
    "observer_coordination": [
        "Jerin tura masu sa ido na {state} yana cikin imel na hukuma. Tabbatar da kasancewarku ga shugaban kungiya.",
        "Za a gudanar da taron masu sa ido a {office} da karfe 8:00 na safe. Ku kawo takardar izini.",
    ],
    "result_verification_guidance": [
        "Ana nuna sakamakon gidan zabe a gidan zabe kuma a {official_url}. Kwatanta su kafin yadawa.",
        "Sakamakon da jami'in dawo da sakamako ya sanar ne kawai ake karba. Yi watsi da hotunan da ba a tabbatar ba.",
    ],
    "media_release": [
        "Ofishin {office} ya fitar da sanarwa kan shirye-shiryen {state}. Karanta a {official_url}.",
        "Taron manema labarai zai gudana a {deadline} a {office}. Rajista kyauta ce ga kafofin da aka amince.",
    ],
}

PHISHING_CATEGORIES = list(PHISHING_TEMPLATES.keys())
BENIGN_CATEGORIES = list(BENIGN_TEMPLATES.keys())


def pick_url(rng: random.Random, label: int) -> str:
    return rng.choice(SUSPICIOUS_URLS if label == 1 else OFFICIAL_URLS)


def build_row(rng: random.Random, label: int, row_number: int) -> dict[str, str | int]:
    language = "ha" if rng.random() < HAUSA_SHARE else "en"
    templates = (
        (PHISHING_TEMPLATES_HA if label == 1 else BENIGN_TEMPLATES_HA)
        if language == "ha"
        else (PHISHING_TEMPLATES if label == 1 else BENIGN_TEMPLATES)
    )
    categories = list(templates.keys())
    category = rng.choice(categories)
    template = rng.choice(templates[category])

    salutation_pool = SALUTATIONS_HA if language == "ha" else SALUTATIONS_EN
    values = {
        "role": rng.choice(ROLES),
        "state": rng.choice(STATES),
        "office": rng.choice(OFFICES),
        "deadline": f"{rng.randint(1, 28)} {rng.choice(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])} 2027",
        "amount": f"{rng.choice([1_500, 2_000, 2_500, 3_000, 5_000, 7_500, 10_000]):,}",
        "url": pick_url(rng, label),
        "official_url": rng.choice(OFFICIAL_URLS),
    }

    salutation = rng.choice(salutation_pool).format(**values)
    body = template.format(**values)
    text = f"{salutation} {body}"

    channel = rng.choice(CHANNELS)
    if channel == "sms" and len(text) > 240:
        text = f"{text[:237].rsplit(' ', 1)[0]}..."

    created = datetime(2026, 6, 1, tzinfo=timezone.utc) + timedelta(
        seconds=rng.randint(0, 158 * 24 * 60 * 60)
    )

    return {
        "id": f"syn-{row_number:05d}",
        "text": text,
        "url": values["url"],
        "label": label,
        "category": category,
        "language": language,
        "channel": channel,
        "state": values["state"],
        "created_at": created.isoformat().replace("+00:00", "Z"),
    }


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    rng = random.Random(SEED)
    rows: list[dict[str, str | int]] = []
    seen_texts: set[str] = set()

    for label in (1, 0):
        generated = 0
        attempts = 0
        while generated < ROWS_PER_CLASS:
            attempts += 1
            if attempts > ROWS_PER_CLASS * 40:
                raise RuntimeError("Template space exhausted; add more variants.")
            candidate = build_row(rng, label, len(rows) + 1)
            if candidate["text"] in seen_texts:
                continue
            seen_texts.add(str(candidate["text"]))
            rows.append(candidate)
            generated += 1

    rng.shuffle(rows)
    for index, row in enumerate(rows, start=1):
        row["id"] = f"syn-{index:05d}"

    # Guard rails: catch template mistakes before the dataset reaches training.
    for row in rows:
        text = str(row["text"])
        assert text and "{" not in text and "}" not in text, text
        assert str(row["url"]).startswith("http"), row
        assert int(row["label"]) in (0, 1)
        if int(row["label"]) == 1:
            assert ".example" in str(row["url"]) or "192.0.2." in str(row["url"]) or str(
                row["url"]
            ).startswith(("https://198.51.100.", "https://203.0.113.")), row

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id",
        "text",
        "url",
        "label",
        "category",
        "language",
        "channel",
        "state",
        "created_at",
    ]
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    label_counts = Counter(int(row["label"]) for row in rows)
    language_counts = Counter(str(row["language"]) for row in rows)
    category_counts = Counter(f"{row['label']}:{row['category']}" for row in rows)
    channel_counts = Counter(str(row["channel"]) for row in rows)

    manifest = {
        "dataset": "electoral_phishing_synthetic",
        "version": "0.1.0",
        "description": (
            "Template-generated electoral phishing and benign communications. "
            "Synthetic only; no real messages, people or voter records."
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "ai-engine/training/generate_data.py",
        "seed": SEED,
        "rows": len(rows),
        "labels": {
            "phishing": label_counts[1],
            "benign": label_counts[0],
        },
        "languages": dict(sorted(language_counts.items())),
        "categories": dict(sorted(category_counts.items())),
        "channels": dict(sorted(channel_counts.items())),
        "files": [
            {
                "path": CSV_PATH.name,
                "bytes": CSV_PATH.stat().st_size,
                "sha256": sha256_of(CSV_PATH),
            }
        ],
        "suspicious_link_policy": (
            "Suspicious URLs use reserved .example domains and RFC 5737 documentation "
            "addresses only. Benign URLs reference public institutional home pages as "
            "illustrative context and are never contacted by the generator."
        ),
        "known_limitations": [
            "Template-generated text is less varied than real reports.",
            "Hausa coverage is limited and requires native-speaker review.",
            "Label noise is deliberately low; real reports are noisier.",
            "The dataset tests triage logic, not actor attribution.",
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("Votex AI synthetic dataset generated")
    print(f"  rows:      {len(rows)}")
    print(f"  phishing:  {label_counts[1]}  benign: {label_counts[0]}")
    print(f"  languages: {dict(language_counts)}")
    print(f"  csv:       {CSV_PATH}")
    print(f"  sha256:    {manifest['files'][0]['sha256']}")
    print(f"  manifest:  {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
