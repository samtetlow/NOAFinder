"use client";

import { useEffect, useState } from "react";

const JOKES = [
  "I asked the program officer for an extension. They gave me a fiscal year.",
  "Why did the scarecrow win an award? He was outstanding in his field.",
  "My proposal said it needed more buzzwords. It came back synergized.",
  "How many program officers does it take to change a lightbulb? Depends on which fiscal year we’re in.",
  "USASpending.gov walks into a bar. The bartender says: come back when your data has been indexed.",
  "What’s the difference between a deadline and a suggestion? About 11:59 PM Eastern.",
  "I told my capture manager I needed to do more BD. So I bought a dishwasher.",
  "Why don’t scientists trust atoms? They make up everything — unlike the indirect rate.",
  "My grant was rejected for being too clear. The reviewer said the boilerplate felt thin.",
  "I read the FOA three times. It still doesn’t match the SOW.",
  "Parallel lines have a lot in common. It’s a shame the appropriations committee will never let them meet.",
  "Why did the proposal cross the road? Because the SAM.gov registration expired on the other side.",
  "A federal contract walks into a bar. The bartender says: I’ll be with you in 30 to 90 days.",
  "Confidence is going into a Phase II review with the same slide deck you used in Phase I.",
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
