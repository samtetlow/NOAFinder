export interface SubApp {
  slug: string;
  title: string;
  href: string;
  description?: string;
  comingSoon?: boolean;
}

export interface MainApp {
  slug: string;
  title: string;
  href: string;
  description?: string;
  comingSoon?: boolean;
  subs?: SubApp[];
}

// Source of truth for the Grant Engine Launchpad nav.
// Order here is the order shown in the sidebar.
export const APPS: MainApp[] = [
  {
    slug: "marketing",
    title: "Marketing",
    href: "/marketing",
    description:
      "Lead generation, warming, conferences, and meeting booking.",
    subs: [
      {
        slug: "lead-magnets",
        title: "Lead Magnets",
        href: "/marketing/lead-magnets",
        comingSoon: true,
      },
      {
        slug: "warming-email",
        title: "Warming Email",
        href: "/marketing/warming-email",
        comingSoon: true,
      },
      {
        slug: "theflow",
        title: "TheFlow",
        href: "/marketing/theflow",
        comingSoon: true,
      },
      {
        slug: "conferences",
        title: "Conferences",
        href: "/marketing/conferences",
        comingSoon: true,
      },
      {
        slug: "booking-agent",
        title: "Booking Agent",
        href: "/marketing/booking-agent",
        comingSoon: true,
      },
    ],
  },
  {
    slug: "product-funding",
    title: "Product Funding",
    href: "/product-funding",
    description: "Funding strategy and product readiness.",
    comingSoon: true,
  },
  {
    slug: "capture",
    title: "Capture",
    href: "/capture",
    description: "Capture management for federal opportunities.",
    comingSoon: true,
  },
  {
    slug: "delivery",
    title: "Delivery",
    href: "/delivery",
    description:
      "Award tracking, quality checks, and proposal delivery.",
    subs: [
      {
        slug: "noa-finder",
        title: "NOA Finder",
        href: "/delivery/noa-finder",
        description:
          "Cross-references Falcon clients with USASpending.gov federal awards.",
      },
      {
        slug: "qc-engine",
        title: "QC Engine",
        href: "/delivery/qc-engine",
        comingSoon: true,
      },
      {
        slug: "eagle",
        title: "Eagle (fka TDC)",
        href: "/delivery/eagle",
        comingSoon: true,
      },
    ],
  },
  {
    slug: "training-and-development",
    title: "Training & Development",
    href: "/training-and-development",
    description: "Onboarding, certifications, and team development.",
    subs: [
      {
        slug: "training-records",
        title: "Training Records",
        href: "/training-and-development/training-records",
        comingSoon: true,
        description:
          "Per-person training history and certification expirations.",
      },
    ],
  },
];

export function findApp(
  href: string,
): { main: MainApp; sub?: SubApp } | null {
  for (const main of APPS) {
    if (main.href === href) return { main };
    if (main.subs) {
      for (const sub of main.subs) {
        if (sub.href === href) return { main, sub };
      }
    }
  }
  return null;
}
