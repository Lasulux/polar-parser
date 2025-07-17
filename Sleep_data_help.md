# Documentation to Help Understand the Sleep Data on Polar Watches

In the `.zip` files, there are five types of JSON files that contain sleep-related information:

- **Nightly recovery**
- **Nightly recovery blob**
- **Sleep result**
- **Sleep score**
- **Sleep wake**

Most of these contain information that is not explained anywhere publicly by Polar. However, there are some descriptions available for a couple of fields in these files. We could guess what the others are if we really want to use more data, but that is not too reliable...

---

## Nightly Recovery

This file contains nightly info, mostly about Polar-defined terms. There is not much help available online about what means what exactly, and the values to those fields are coded too. There are some additional unexplained values such as:

- `ansRate`
- `meanNightlyRecoveryRri`
- `meanNightlyRecoveryRmssd`
- `meanNightlyRecoveryRespirationInterval`
- `meanBaselineRri`
- `sdBaselineRri`
- `meanBaselineRmssd`
- `sdBaselineRmssd`
- `meanBaselineRespirationInterval`
- `sdBaselineRespirationInterval`

---

## Nightly Recovery Blob

This file contains raw, nightly sample information about `hrvData` (heart rate variability, probably), and `breathingRateData` with sampling times (start time and period).

- **hrvData**: 5-minute average samples of heart rate variability. Unit of samples is milliseconds (ms).
- **breathingRateData**: 5-minute average samples of breathing rate. Unit of samples is breaths per minute (bpm).

---

## Sleep Result

This file contains information about sleep cycles: how long the person was in each sleep stage (e.g., wake, REM, light, deep). It has summarized info about interruptions too (how many times, for how long did someone wake up?). Mostly unexplained online.

- `ansStatus`: ANS stands for autonomic nervous system. ANS charge is formed by measuring heart rate, heart rate variability, and breathing rate during roughly the first four hours of your sleep. It is formed by comparing your last night to your usual levels from the past 28 days. The scale is from -10.0 to +10.0. Around zero is your usual level.
- `ansRate`: ANS charge status:  
  - much below usual (1)  
  - below usual (2)  
  - usual (3)  
  - above usual (4)  
  - much above usual (5)

---

## Sleep Score

This file has different scores. Some are actually explained online, although only briefly and not very scientifically. Below are some that I found explanations for by Polar:

- **`sleepScore`**: Sleep score summarizes the amount and quality of your sleep into a single number on a scale of 1–100. It tells you how well you slept compared to the indicators of a good night's sleep based on current sleep science. It consists of six components: sleep time, long interruptions, continuity, actual sleep, REM sleep, and deep sleep.
- **`continuityScore`**: Continuity is an estimate of how continuous the sleep was on a scale of 1.0–5.0, where 5.0 reflects uninterrupted sleep. The lower the value, the more fragmented the sleep was.
- **`groupDurationScore`**: Sleep score consists of six components that are grouped under three themes. The score for the sleep duration theme looks at your sleep time compared to your ‘preferred sleep time’ setting and age-related duration recommendations. Group duration score ranges from 1.0 to 100.0 and is interpreted as textual feedback: poor, moderate, or good amount.
- **`groupSolidityScore`**: Sleep score consists of six components that are grouped under three themes. The score for the sleep solidity theme is the average of the component scores of long interruptions, continuity, and actual sleep. Group solidity score ranges from 1.0 to 100.0 and is interpreted as textual feedback: poor, moderate, or good solidity.
- **`groupRefreshScore`**: Sleep score consists of six components that are grouped under three themes. The score for the regeneration theme is the average of the scores of REM sleep and deep sleep. Group regeneration score ranges from 1.0 to 100.0 and is interpreted as textual feedback: poor, moderate, or good regeneration.

---

## Sleep Wake

This contains sleep/wake state times during the night and day. It shows at how many milliseconds during the day the watch switched to a new state. We can exactly follow when a person was awake or asleep using this.