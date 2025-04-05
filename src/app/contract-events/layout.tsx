import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Smart Contract Events",
  description: "View events from smart contracts on the blockchain",
};

export default function ContractEventsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <main className="flex-1">{children}</main>
    </div>
  );
} 