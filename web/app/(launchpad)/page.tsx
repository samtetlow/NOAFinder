import { RotatingJoke } from "@/components/RotatingJoke";

export const dynamic = "force-dynamic";

export default function LaunchpadHome() {
  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <RotatingJoke />
    </div>
  );
}
