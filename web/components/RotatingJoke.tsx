"use client";

import { useEffect, useState } from "react";

const JOKES = [
  // Self-deprecating one-liners
  "I'm not crying. I just opened the formatting requirements.",
  "What's a grant writer's favorite color? Beige.",
  "Don't trust anyone who says 'just one more revision.'",
  "My Gantt chart hates me back.",
  "What do you call a grant writer who's on time? Unemployed.",
  "I'd explain what I do, but you'd leave.",
  "I tried to put 'attended every status meeting' on my resume. The recruiter laughed.",
  "What do you call a startup founder applying to NIH? Optimistic.",
  "Three things are certain in life: death, taxes, and a reviewer asking about scalability.",

  // Setup + punchline
  "I asked my therapist if I should quit grant writing. She said let's set realistic milestones.",
  "I told my dentist I'm a grant writer. He just nodded and started drilling.",
  "My boss said the proposal needs more white space. I sent him thirty pages of margins.",
  "My five-year-old asked what I do. I told her I help scientists ask the government for money. She asked if I ever get it. I said sometimes. She said we should pray.",
  "I told someone at a party I work in federal contracts. They went to get another drink and never came back. It's now my icebreaker.",
  "Three reviewers walked into a panel. Two recommended not funding. The third wrote a haiku.",
  "How do you make a contracting officer laugh? Tell them your timeline.",
  "What's a contracting officer's spirit animal? A pause button.",
  "What's a federal contractor's favorite drink? Whatever the per diem allows.",
  "Why don't statisticians get hired into capture? Their confidence intervals are too honest.",
  "Why did the cybersecurity grant cross the road? It was the only path through the firewall.",

  // Observational
  "Inside every clarification is a third instruction.",
  "Federal procurement: where 'simplified' means forty-two pages.",
  "The grants.gov UI is intuitive — if you've been using it since 2003.",
  "Inside every RFP is an instruction that contradicts a previous instruction.",
  "Federal acronym soup: where one of the ingredients is also called 'soup.'",
  "The agency posted a Q&A document. Forty-seven questions. Every answer is 'see Section H.'",
  "I read the FOA. I read the SOW. They are not friends.",
  "I read a 200-page solicitation in one sitting. My optometrist sends his regards.",
  "A 'short response' from a federal agency is between fourteen days and the heat death of the universe.",
  "Apparently 'aggressive timeline' and 'feasible timeline' are different things. I am informed of this. Three years later.",

  // Lived experience
  "I once submitted a perfect proposal. The reviewer wrote 'felt rushed.'",
  "The reviewer wrote 'great work.' I got a 4 out of 10. I went home.",
  "My capture team identified three decision-makers. Two have retired. One was a typo.",
  "I had a great idea in the shower. By the time I sat down, it was a bullet point. By the time I opened Word, it was an acronym.",
  "I attended a 90-minute kickoff. Twenty minutes were the kickoff. Seventy were people clarifying which kickoff.",
  "My favorite part of the proposal is the cover letter. Everyone else's favorite part is the cover letter — because it's the only part they read.",
  "I worked through the weekend on a proposal. The agency canceled the FOA Monday morning.",
  "Three months of capture. Two hours of writing. One typo. Zero stars.",
  "Confidence is going into a Phase II review with a slide that says 'we still don't know how this works.'",
  "My SBIR Commercialization Plan says TBD. My investor pitch also says TBD. At least they match.",
  "I asked AI to write my technical narrative. It hallucinated. The reviewer said it 'felt fresh.'",
  "I wrote a perfect Specific Aims page. It took eight years and the loss of three relationships.",

  // Universal dad-energy jokes (palate cleansers)
  "I'm reading a book about anti-gravity. It's impossible to put down.",
  "I told my wife she was drawing her eyebrows too high. She looked surprised.",
  "Parallel lines have so much in common — it's a shame they'll never meet.",
  "Why did the scarecrow win an award? He was outstanding in his field.",
  "How do you organize a space party? You planet.",
  "Why don't scientists trust atoms? They make up everything.",
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
