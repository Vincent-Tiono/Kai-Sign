import { HydrateClient } from "~/trpc/server";
import { Button } from "~/components/ui/button";
import Link from "next/link";
import FileUploader from "./fileUploader";

export default function VerificationResultsPage() {
  return (
    <HydrateClient>
      <div className="container mx-auto max-w-4xl p-6">
        <h1 className="mb-4 text-3xl font-bold">ERC7730 JSON Verification</h1>
        
        <FileUploader />
        
        <div className="mb-8 rounded-lg bg-blue-50 p-6 text-blue-700 dark:bg-blue-900 dark:text-blue-100">
          <h2 className="mb-2 text-xl font-medium">What is ERC7730?</h2>
          <p>
            ERC7730 is a standard for smart contract clear signing, providing structured JSON specifications 
            that hardware wallets can use to display transaction details in a user-friendly way.
          </p>
        </div>
        
        <div className="mb-8 space-y-4">
          <h2 className="text-xl font-medium">Benefits of Using ERC7730</h2>
          <ul className="list-inside list-disc space-y-2">
            <li>Improved transaction transparency for end users</li>
            <li>Clearer display of contract interactions on hardware wallets</li>
            <li>Reduced risk of phishing and blind signing attacks</li>
            <li>Standardized format for describing smart contract operations</li>
          </ul>
        </div>
        
        <div className="flex justify-between">
          <Button variant="outline" asChild>
            <Link href="/">Back to Home</Link>
          </Button>
        </div>
      </div>
    </HydrateClient>
  );
} 