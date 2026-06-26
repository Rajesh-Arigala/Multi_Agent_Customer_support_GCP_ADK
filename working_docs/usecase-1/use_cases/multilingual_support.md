# Multilingual Support

## Purpose
This document defines the language capability as a product USP.

## Supported Languages
```text
English
Kannada
Hindi
Telugu
Tamil
Malayalam
Marathi
Bengali
```

## Transliteration Requirement
The user may write an Indian language using English letters.

Examples:

```text
ela unnaru -> Telugu transliteration
enakku appointment venum -> Tamil transliteration
mujhe IVF ke baare mein info chahiye -> Hindi transliteration
nanage appointment beku -> Kannada transliteration
```

## Agent Behavior
```text
detect language
detect script
detect transliteration
reply in the same language/style
store preferred_language
store preferred_script
keep staff-facing notes in English
```

## Example
User:

```text
ivf gurinchi cheppandi
```

Expected response style:

```text
IVF gurinchi general information istanu. Idi medical diagnosis kaadu. Mee medical history, reports, test results batti our doctor correct guidance istaru.
```

## Roadmap
```text
V1: text only
V2: optional voice input and audio response
V3: video consultation booking
```
