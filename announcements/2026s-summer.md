<!--
Working draft of the OCPC Summer 2026 Codeforces announcement.
This file lives OUTSIDE docs/, so Jekyll does not publish it — but the repo is
public, so the draft is visible on GitHub. The body below the "=== ANNOUNCEMENT
SOURCE ===" divider is Codeforces markup, ready to paste once the placeholders
(⟨…⟩) are filled.
-->

# OCPC Summer 2026 — Codeforces announcement (working draft)

Single combined announcement for the two onsite editions (**Hong Kong**, August;
**Iași**, September). They are both core-organized, share the same contest set,
and have the same fee/discount/registration structure, so one season post is
simpler and easier to get onto the Codeforces front page.

## To fill in before posting

- [ ] **Exact dates** — Hong Kong (August) and Iași (September).
- [ ] **Registration form** link — or change the Registration section to "opening soon, watch Discord".
- [ ] **Deadlines** — early-bird date, plus remote / onsite registration cutoffs (depend on dates).
- [ ] **Online participants** — finish the "clarify for online teams that …" thought (which edition's schedule / timezone do online teams follow?).
- [ ] **Per-site schedule** — confirm contest count / days off per site (Iași likely 7 contests + 2 days off; Hong Kong TBD), if we want to state it.
- [ ] **Problem-author list** (being collected) — fill the Problem authors section in the style of past announcements.
- [ ] **Post date** — the `[user:…,2026-06-20]` tags use today's date; bump to the actual posting date so ranks render correctly.
- [ ] **Decide:** also remove "ETH Zürich" from the archived seasons (`_data/2026w/team.yml`, `_data/2025s/team.yml`), or leave the archive frozen?
- [ ] **Deploy ocpc.camp first** — Codeforces rehosts images at post time, so the cropped Order Capital logo / dropped affiliation only appear if the site is redeployed before posting.

## Conventions used here

- Sponsors are shown **per site**: Jane Street appears in **both** (Hong Kong Platinum, Iași Gold); Pinely and Order Capital are Iași Gold. ICPC sits in the top header as the Foundation partner; each site shows its own host-university partner (CityU / UAIC).
- Each site's logos sit on **one line directly under its title**, no "supported by" / "partnership" labels; below them a single italic link to that site's `sponsors.html` (rather than listing sponsor names), which also conveys "these are that site's sponsors". Sponsors are sized a touch larger than the host-university mark.
- Order Capital renders a little taller (`54px` vs `40px`) to balance visual weight against the wider Jane Street / Pinely marks.
- **Contact / sponsors / visa links:** the root `contact.html` and `sponsors.html` only redirect in the multi-site setup, so the post links the **per-site** pages (HK / Iași). **Visa** is handled once in Registration, linking the portal `info.html` (applies to both sites).
- We do **not** name the organizers explicitly ("organized by us …"), and avoid emphasising a "single shared form" — the registration link just gets dropped in when ready.
- Discord invite: `yEWjcPs5qZ` (same as the site).

---

=== ANNOUNCEMENT SOURCE (paste into Codeforces) ===

Hi everyone!

<center><a href="https://ocpc.camp"><img src="https://ocpc.camp/images/ocpc_light.svg" height="80px"></a>
<a href="https://icpc.foundation/"><img src="https://ocpc.camp/images/ICPC.svg" height="80px"></a></center>

The [OCPC](https://ocpc.camp/) (Osijek Competitive Programming Camp), an [award-winning](https://www.linkedin.com/feed/update/urn:li:activity:7368330111089131522/) camp for university students preparing for ICPC and other coding competitions, is back this **Summer 2026** — this time with **two onsite editions**:

- **Hong Kong** — **August 2026**, hosted at the City University of Hong Kong.
- **Iași, Romania** — **September 2026**, hosted at Alexandru Ioan Cuza University of Iași.

Both editions are organized by us together with local hosts at each site, and use the **same contest set** — so you take part in **one** of them. As a rough guide, the **Iași** edition is most convenient for teams based in Europe, and **Hong Kong** for teams in APAC and East Asia — but you are welcome at whichever you prefer. The camp is inspired by the competitive programming camps we attended during our active ICPC years: a series of ICPC-style contests (5 hours, 9–12 problems each), with analysis sessions and days off in between.

### Hong Kong — August 2026

<center>
<a href="https://www.janestreet.com/join-jane-street/open-roles/?type=students-and-new-grads&location=all-locations"><img src="https://ocpc.camp/images/Jane%20Street.svg" height="55px" style="margin:0 18px;vertical-align:middle;"></a>
<a href="https://www.cityu.edu.hk/"><img src="https://ocpc.camp/images/cityu.svg" height="40px" style="margin:0 18px;vertical-align:middle;"></a>
</center>
<center><i><a href="https://ocpc.camp/2026s/hk/sponsors.html">Sponsors and partners of the Hong Kong camp</a></i></center>

- **Venue:** City University of Hong Kong, Kowloon Tong, Hong Kong.
- **Onsite hosts:** Minming Li and [user:SGColin,2026-06-20] (City University of Hong Kong).
- **Local teams:** **in-person participation is free** for teams representing Hong Kong universities.
- **Exact dates:** ⟨TBA⟩. Expected start time **10:00 HKT**.

### Iași, Romania — September 2026

<center>
<a href="https://www.janestreet.com/join-jane-street/open-roles/?type=students-and-new-grads&location=all-locations"><img src="https://ocpc.camp/images/Jane%20Street.svg" height="40px" style="margin:0 16px;vertical-align:middle;"></a>
<a href="https://pinely.com/"><img src="https://ocpc.camp/images/Pinely.svg" height="40px" style="margin:0 16px;vertical-align:middle;"></a>
<a href="https://ordercapital.com/"><img src="https://ocpc.camp/images/order-capital.svg" height="54px" style="margin:0 16px;vertical-align:middle;"></a>
<a href="https://www.uaic.ro/en/"><img src="https://ocpc.camp/images/uaic.png" height="36px" style="margin:0 16px;vertical-align:middle;"></a>
</center>
<center><i><a href="https://ocpc.camp/2026s/iasi/sponsors.html">Sponsors and partners of the Iași camp</a></i></center>

- **Venue:** Faculty of Computer Science, Alexandru Ioan Cuza University of Iași.
- **Onsite host:** [user:juve45,2026-06-20] (Alexandru Ioniță, UAIC Iași).
- **Exact dates:** ⟨TBA⟩. Expected start time **10:00 EEST**.

### Details

The participation fee for both online and onsite participants is **198€ per team** (the same at both sites). As in previous editions, it does _not_ include regular meals, travel or accommodation.

We support and empathize with those affected by the ongoing war in Ukraine, therefore we offer **free participation** for affected individuals and teams affiliated with Ukrainian institutions.

Additionally, we offer the following discounts:

- **Early bird discount:** reduced fee of **147€ per team** if you register before ⟨early-bird deadline⟩.
- **Hardship discount:** fee reduction to **49€ per team**, on request, if the default fee makes it a financial burden for you. We do not require any proof or documentation and trust your self-assessment. Nevertheless, we ask you to be mindful when using it, as we rely on participation fees as the baseline for running the camp.

For remote participants, the listed start time is still the preferred one, but we will make accommodations for virtual participation at a later time, when necessary.

Most of our contests are originally developed for the camp. A small number of contests may be based on previous contests that have not been released to the general public. If you have seen some problems of a contest before, you can't participate on that day, and we will privately contact participants who might be affected.

After the camp, we will have a silence period during which camp materials will not be released to the public. We ask participants not to discuss the problems in public unless they obtained an explicit permission from contest authors.

If you would like to get a feel of the contests, you can find links to some of the previously published camp contests **[here](https://ocpc.camp/archive.html)**.

If you have any questions, please join our **[Discord server](https://discord.gg/yEWjcPs5qZ)**, or reach out via the contact page for [Hong Kong](https://ocpc.camp/2026s/hk/contact.html) or [Iași](https://ocpc.camp/2026s/iasi/contact.html).

### Registration

The registration form will be posted here ⟨link — coming soon⟩; you pick your location (Hong Kong or Iași) in it.

We ask you to register before ⟨remote deadline⟩ if you want to participate remotely and before ⟨onsite deadline⟩ if you want to participate onsite. If you require a visa (for Romania or Hong Kong), please register **as soon as possible**, as it can take a few weeks depending on your location — see [Visa & invitation letters](https://ocpc.camp/2026s/info.html).

Also, if your university or organization has a lively ICPC community that may be interested in attending, and you have contacts of people in charge (e.g. coaches), we would highly appreciate if you could share some details in a direct message to me. Thanks!

### Problem authors

We'd like to thank and praise the authors of the contests in the camp:

⟨problemsetter list — to be filled, in the style of previous announcements⟩

You can find more details about contest rules and technical setup on the [website](https://ocpc.camp/contest-info.html).

### Special thanks

Finally, we say special thanks to

- our sponsors — for [Hong Kong](https://ocpc.camp/2026s/hk/sponsors.html) and [Iași](https://ocpc.camp/2026s/iasi/sponsors.html) — who make the camp possible;
- the ICPC Foundation for their help and support;
- Codeforces for support and guidance;
- [eolymp](https://eolymp.com) for providing an online judge for the contests;
- City University of Hong Kong and Alexandru Ioan Cuza University of Iași for hosting the two editions;
- the University of Osijek, which provided a physical location for the camp in its earlier editions;
- [user:BigBag,2026-06-20] for consistently making very useful combined scoreboards at https://acmallukrainian.ho.ua/camps/.
