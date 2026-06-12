"use client";

import { useEffect, useState } from "react";

const JOKES = [
  // Federal program officers
  "I asked the program officer for an extension. They gave me a fiscal year.",
  "How many program officers does it take to change a lightbulb? Depends on which fiscal year we’re in.",
  "My program officer left for industry. The new one asked what an SBIR was.",
  "What did the program officer say to the late proposal? Better late than 90 days from now.",
  "My program officer asked for a one-pager. I sent a 47-page narrative. She thanked me for the brevity.",
  "A program officer walks into a bar. The bartender asks what she wants. She says, ‘Whatever’s aligned with the funding priorities.’",

  // Proposals & boilerplate
  "My proposal said it needed more buzzwords. It came back synergized.",
  "My grant was rejected for being too clear. The reviewer said the boilerplate felt thin.",
  "I read the FOA three times. It still doesn’t match the SOW.",
  "I wrote a 25-page management plan for a 6-month project. The Gantt chart had its own Gantt chart.",
  "I tried to compress my technical narrative. It came back asking for more figures.",
  "My proposal got Highly Meritorious. So did 137 others. Only 12 were funded.",
  "Why did the proposal use Comic Sans? The reviewer asked the same question.",
  "What do you call a proposal with no win theme? A novella.",
  "Why did the grant writer get fired? She used active voice.",
  "Confidence is going into a Phase II review with the same slide deck you used in Phase I.",
  "My SBIR commercialization plan says: pivot. To what? I don’t know yet. That’s the pivot.",

  // Contracting & compliance
  "A federal contract walks into a bar. The bartender says: I’ll be with you in 30 to 90 days.",
  "I asked the contracting officer for clarification. She quoted FAR 52.212-4 and walked away.",
  "What did the OMB say to the cost proposal? You spelled ‘reasonable’ wrong.",
  "I forgot to register on SAM.gov. The error message felt personal.",
  "Why did the proposal cross the road? Because the SAM.gov registration expired on the other side.",
  "I tried to claim small business status. The certifications form had 14 questions about size.",
  "My SBIR Phase I budget had a typo. Now I’m a millionaire on paper and bankrupt in reality.",
  "What’s the smallest unit of government time? A ‘shortly.’",
  "What’s a contractor’s favorite holiday? End of fiscal year — also their least favorite.",
  "What’s the difference between a deadline and a suggestion? About 11:59 PM Eastern.",
  "I tried to explain TRL levels at Thanksgiving. My uncle thought I said ‘truffle.’",

  // Capture & BD
  "I told my capture manager I needed to do more BD. So I bought a dishwasher.",
  "Why did the BD pipeline get clogged? It was full of dead leads pretending to be qualified.",
  "The reviewer said my pitch deck was ‘visionary.’ Two weeks later: rejected.",
  "I asked Falcon to predict my win probability. It said ‘inconclusive but encouraging.’",
  "My capture plan said: identify decision-makers. I identified seven. None of them returned my email.",

  // Reviewers, panels & odds
  "Why don’t grant writers gamble? Every odds calculation includes ‘subject to availability of funds.’",
  "What’s the difference between Phase I and Phase II? A nervous breakdown and a year.",
  "What does NIH stand for? Never Indicate Hubris.",
  "I tried to align my deliverables with my milestones. Now neither of them speak to me.",
  "I tried to explain my work breakdown structure. They asked if I meant my mental state.",

  // Workplace & general
  "Why did the scarecrow win an award? He was outstanding in his field.",
  "Why don’t scientists trust atoms? They make up everything — unlike the indirect rate.",
  "Parallel lines have a lot in common. It’s a shame the appropriations committee will never let them meet.",
  "I optimized my CV for federal Form 365. Now LinkedIn thinks I’m dead.",
  "I emailed grants.gov support. They emailed back asking if I’d tried emailing grants.gov support.",
  "Why don’t biotech founders sleep? Their burn rate is faster than the FDA review cycle.",

  // Data, tooling, the existential
  "USASpending.gov walks into a bar. The bartender says: come back when your data has been indexed.",
  "I asked Wrike to summarize my workload. It returned a Gantt chart of my regrets.",
  "My burn rate exceeded my comprehension rate sometime last Tuesday.",
];

export function RotatingJoke() {
  // Pick a random starting index so two simultaneous viewers don’t see
  // the same joke at the same time.
  const [idx, setIdx] = useState(0);
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    setIdx(Math.floor(Math.random() * JOKES.length));
  }, []);

  useEffect(() => {
    const id = setInterval(() => {
      setVisible(false);
      // Fade out, swap, fade back in.
      setTimeout(() => {
        setIdx((i) => (i + 1) % JOKES.length);
        setVisible(true);
      }, 350);
    }, 9000);
    return () => clearInterval(id);
  }, []);

  return (
    <div
      className={
        "text-center text-brand/60 max-w-xl transition-opacity duration-300 " +
        (visible ? "opacity-100" : "opacity-0")
      }
    >
      <p className="text-sm italic leading-relaxed">“{JOKES[idx]}”</p>
    </div>
  );
}
