import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

export default function TrainingRecordsRedirect() {
  // Training Records is hosted out-of-band at ascend.grantengine.com
  // (samtetlow/trainingattestation). The sidebar entry already opens
  // that URL in a new tab; this server redirect catches anyone who
  // bookmarked the in-launchpad path before the move (or pastes the
  // URL directly) and bounces them to the live app.
  redirect("https://ascend.grantengine.com");
}
