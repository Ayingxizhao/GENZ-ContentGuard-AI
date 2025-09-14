# Seed Keywords for Malicious Content Categorization

This directory contains comprehensive keyword lists for semi-supervised topic modeling to categorize malicious Gen Z social media content using BERTopic clustering.

## Overview

The `seed_keywords.py` file contains 1,014 carefully curated keywords across four main categories:

- **Hate/Discrimination**: 219 keywords
- **Harassment/Bullying**: 227 keywords  
- **Sexual Content**: 303 keywords
- **General Toxicity**: 265 keywords

## Category Descriptions

### 1. Hate/Discrimination
Terms targeting individuals based on identity characteristics including race, ethnicity, gender, sexual orientation, religion, disability, and other protected attributes.

**Key Patterns:**
- Identity-based slurs (karen, boomer, incel, simp)
- Political/ideological attacks (libtard, feminazi, sjw, woke)
- Gender discrimination (femoid, roastie, thot, e-girl)
- Race/ethnicity coded language (mayo, coon, spic, chink)
- Disability discrimination (retard, autist, cripple)
- Religious discrimination (christfag, muzzie, cultist)
- Coded language and euphemisms (google, skittles, 13/50, 14/88)

### 2. Harassment/Bullying
Personal attacks, threats, intimidation tactics, and behaviors designed to harm, frighten, or control others.

**Key Patterns:**
- Direct threats and intimidation tactics
- Personal attacks and cyberbullying
- Modern Gen Z harassment terminology

### 3. Sexual Content
Explicit sexual language, inappropriate sexual comments, sexual harassment, and sexually suggestive content.

**Key Patterns:**
- Explicit sexual language and terminology
- Gen Z sexual slang and euphemisms
- Sexual harassment and inappropriate content

### 4. General Toxicity
Aggressive language, insults, mean-spirited behavior, and general negative interactions that create hostile environments.

**Key Patterns:**
- Aggressive and confrontational language
- Gen Z toxicity slang and behaviors
- Social exclusion and drama patterns

## Keyword Selection Methodology

### Gen Z Language Patterns
Keywords were selected based on current Gen Z communication patterns including:
- **Modern slang**: rizz, mid, cheugy, no cap, periodt
- **Internet terminology**: ratio, cope, seethe, mald, cringe
- **Social media behaviors**: cancel, ghost, slide in dms, touch grass
- **Gaming culture**: L, W, noob, sweaty, tryhard

### Variations and Misspellings
Intentional misspellings and variations are included to capture attempts to bypass content moderation:
- **Letter substitutions**: k*ren, b**mer, f*ck
- **Number substitutions**: h4te, 5h1t, l0ser
- **Symbol substitutions**: @ss, d!ck, p*ssy
- **Spacing variations**: f u c k, k i l l y o u r s e l f

### Coded Language
Euphemisms and coded references used to disguise malicious intent:
- **Food items**: Google, Skittles, Mayo, Cracker
- **Numbers**: 13/50, 14/88, 1488, 88
- **Animals**: Coon, Spic, Chink, Wetback
- **Objects**: NPC, Normie, Based, Unbased

### Cultural Context
Terms reflect current online culture and harassment patterns:
- **Political discourse**: Karen, Boomer, NPC, Woke
- **Gaming toxicity**: Noob, Sweaty, Tryhard, Camping
- **Social media**: Cancel culture, Virtue signaling, Main character syndrome
- **Relationship dynamics**: Simp, Pick me, Thirst trap, Rizz

## Usage Instructions

### Basic Usage
```python
from data.seed_keywords import seed_categories, get_keywords_by_category

# Get all keywords
all_keywords = seed_categories

# Get keywords for specific category
hate_keywords = get_keywords_by_category("Hate/Discrimination")
harassment_keywords = get_keywords_by_category("Harassment/Bullying")
```

### BERTopic Integration
```python
from data.seed_keywords import seed_categories
from bertopic import BERTopic

# Initialize BERTopic with seed topics
topic_model = BERTopic()
topic_model.fit(documents)

# Use seed keywords to guide clustering
for category, keywords in seed_categories.items():
    # Use keywords as seed topics for semi-supervised learning
    pass
```

### Category Metadata
```python
from data.seed_keywords import get_category_metadata

metadata = get_category_metadata("Hate/Discrimination")
print(metadata["description"])
print(metadata["subcategories"])
print(metadata["patterns"])
```

## Ethical Considerations

### Content Warning
These keywords contain explicit language, slurs, and offensive terms. They are provided for research and content moderation purposes only.

### Responsible Use
- Use only for legitimate research and content moderation
- Do not use to generate harmful content
- Respect privacy and dignity of individuals
- Follow applicable laws and platform policies

### Bias and Limitations
- Keywords may reflect biases in online discourse
- Some terms may be context-dependent
- Regular updates needed to reflect evolving language
- Cultural and regional variations not fully captured

## Maintenance and Updates

### Regular Updates Required
Language evolves rapidly, especially Gen Z slang and online harassment tactics. Regular updates are recommended:
- Monthly review of new slang terms
- Quarterly assessment of coded language patterns
- Annual comprehensive review of all categories

### Version Control
Track changes to keyword lists to:
- Monitor evolving harassment patterns
- Identify new coded language
- Assess effectiveness of detection
- Maintain audit trail for research

### Community Input
Consider input from:
- Content moderators
- Online safety researchers
- Gen Z community members
- Platform safety teams

## Research Applications

### Topic Modeling
Use keywords to guide BERTopic clustering for:
- Semi-supervised topic discovery
- Content categorization
- Trend analysis
- Pattern recognition

### Content Moderation
Apply keywords for:
- Automated content filtering
- Flagging systems
- Risk assessment
- User safety measures

### Academic Research
Support research on:
- Online harassment patterns
- Gen Z communication styles
- Hate speech evolution
- Social media toxicity

## Technical Notes

### File Structure
```
data/
├── seed_keywords.py      # Main keyword dictionary and functions
└── README.md            # This documentation file
```

### Dependencies
- Python 3.7+
- No external dependencies required
- Compatible with BERTopic, scikit-learn, and other ML libraries

### Performance Considerations
- Keywords loaded in memory (1,014 terms total)
- Fast dictionary lookups
- Minimal computational overhead
- Suitable for real-time applications

## Contact and Support

For questions about these keyword lists or suggestions for improvements, please refer to the main project documentation or create an issue in the project repository.

---

**Last Updated**: December 2024  
**Version**: 1.0  
**Total Keywords**: 1,014 across 4 categories
