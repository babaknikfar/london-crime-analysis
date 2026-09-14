# Crime in London: What 1.14 Million Police Records Tell Us About 2025

*A plain-English summary of an analysis of Metropolitan Police crime data.*

---

## The Big Picture

In 2025, the Metropolitan Police Service recorded **1,140,024 crime incidents** across Greater London. That's roughly **3,100 incidents per day** — a number that sounds alarming until you break it down by type, location, and season.

This report summarizes what the data shows, in language anyone can follow. No statistics background required.

## What Kinds of Crime Happen Most?

Not all crime is equal. Here's how the 1.14 million incidents split across the 14 categories the police use:

| Rank | Crime Type | Incidents | Share |
|---:|---|---:|---:|
| 1 | Violence and sexual offences | 270,115 | 23.7% |
| 2 | Anti-social behaviour | 234,967 | 20.6% |
| 3 | Other theft | 100,244 | 8.8% |
| 4 | Shoplifting | 86,774 | 7.6% |
| 5 | Theft from the person | 85,420 | 7.5% |
| 6 | Vehicle crime | 84,205 | 7.4% |
| 7 | Public order | 58,054 | 5.1% |
| 8 | Criminal damage and arson | 54,677 | 4.8% |
| 9 | Drugs | 53,885 | 4.7% |
| 10 | Burglary | 47,684 | 4.2% |
| 11 | Robbery | 31,332 | 2.7% |
| 12 | Bicycle theft | 13,826 | 1.2% |
| 13 | Other crime | 13,149 | 1.2% |
| 14 | Possession of weapons | 5,692 | 0.5% |

**Two categories make up nearly half of all recorded crime**: violence and sexual offences (23.7%) plus anti-social behaviour (20.6%).

It's worth noting that "violence and sexual offences" is a single, very broad category in the police data. It merges everything from minor assaults to serious crimes, so it's not as homogeneous as the name suggests.

## Where Does Crime Happen?

Crime in London is **highly concentrated**. The busiest single neighbourhood recorded **13,249 incidents** in 2025 — more than 11 times the median.

The top five hotspots:

1. **Westminster 013G** — 13,249 incidents
2. **Westminster 013B** — 9,896
3. **Westminster 018A** — 9,097
4. **Westminster 018C** — 6,062
5. **Hillingdon 031A** — 5,907

**Westminster dominates the list**, which makes sense: it's the heart of central London, with the highest foot traffic, nightlife, and tourist density. High footfall correlates strongly with both opportunistic crime (shoplifting, theft from the person) and reported incidents (more witnesses, more reports).

This is not a story about "dangerous neighbourhoods" — it's a story about **where people gather**.

## When Does Crime Happen?

Crime in London is **seasonal**. The data shows a clear pattern:

- **Summer** (June–August): 306,465 incidents — the peak
- **Spring** (March–May): 286,168
- **Autumn** (September–November): 285,872
- **Winter** (December–February): 261,519 — the quietest season

**July is the busiest month** (106,634 incidents). **February is the calmest** (83,660).

This 15% swing between peak and trough isn't random — it's statistically significant. Warmer weather, longer daylight hours, and more people outdoors all correlate with more reported incidents.

## The Anonymization Story

Here's a detail most people never notice: **20.6% of records are missing their unique identifier**. That's 234,967 incidents.

These aren't errors. They're **deliberately anonymized** records — cases where the police have withheld the identifier to protect victims, typically for sensitive crimes like domestic abuse or sexual offences.

Our analysis found something striking: **every anonymized record is an anti-social behaviour incident**. That's 100% overlap — every single redacted record belongs to that one category. This isn't random; it reflects how anti-social behaviour incidents are reported and processed differently from other crimes.

The lesson: **the "missing" data isn't missing — it's withheld on purpose**, and knowing that changes how you interpret it.

## What We Didn't Expect to Find

Three surprises from the analysis:

1. **The "Crime ID" field isn't unique.** We found 4,513 cases where two different incidents shared the same ID. This means the ID can't be used reliably as a unique key — an important discovery for anyone building on this data.

2. **The Metropolitan Police reports crimes outside London.** About 0.5% of incidents occurred in surrounding counties like West Sussex. The Met's jurisdiction extends beyond London's administrative borders.

3. **"Supermarket" is the most common location.** Not a specific street — the generic placeholder "Supermarket" appears 47,486 times. When the police anonymize a location, they often replace it with a category rather than a specific place.

## What This Analysis Doesn't Tell You

Data is powerful, but it has limits. This analysis **cannot** tell you:

- Whether crime is rising or falling (we only have one year of data)
- How crime compares to previous years
- Whether reported crime reflects actual crime (many crimes go unreported)
- Anything about crimes that were never reported to the police

The numbers show **recorded crime**, not total crime. That distinction matters.

## The Bottom Line

London in 2025 saw over a million recorded crimes — concentrated in central boroughs, peaking in summer, and dominated by two categories that make up nearly half of all incidents. The data is detailed enough to spot patterns, but messy enough to require careful, honest handling.

Every finding in this report comes from a documented, tested pipeline that treats data quality as a first-class concern. The full methodology, code, and raw analysis are available in the project repository.

---

*Built with Python, pandas, and a healthy respect for messy real-world data.*