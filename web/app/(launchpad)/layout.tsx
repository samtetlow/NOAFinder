import { auth } from "@/lib/auth";
import { Sidebar } from "@/components/Sidebar";

export default async function LaunchpadLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await auth();
  return (
    <div className="flex min-h-screen bg-brand-mist">
      <Sidebar userEmail={session?.user?.email} />
      <main className="flex-1 min-w-0">{children}</main>
    </div>
  );
}
