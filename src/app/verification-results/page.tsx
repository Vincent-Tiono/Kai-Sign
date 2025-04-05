import { HydrateClient } from "~/trpc/server";
import { Button } from "~/components/ui/button";
import Link from "next/link";
import FileUploader from "./fileUploader";

export default function VerificationResultsPage() {
  return (
    <HydrateClient>
      <div className="container mx-auto max-w-4xl p-6 text-white">
        <h1 className="mb-8 text-4xl font-bold">ERC7730 JSON Verification</h1>
        
        <FileUploader />
        
        <div className="mb-12 rounded-lg bg-blue-950 p-8 text-white">
          <h2 className="mb-4 text-2xl font-medium">What is ERC7730?</h2>
          <p className="text-gray-300">
            ERC7730 is a standard for smart contract clear signing, providing structured JSON specifications 
            that hardware wallets can use to display transaction details in a user-friendly way.
          </p>
        </div>
        
        <div className="mb-12 space-y-6">
          <h2 className="text-2xl font-medium">Benefits of Using ERC7730</h2>
          <ul className="list-inside list-disc space-y-4 text-gray-300">
            <li>Improved transaction transparency for end users</li>
            <li>Clearer display of contract interactions on hardware wallets</li>
            <li>Reduced risk of phishing and blind signing attacks</li>
            <li>Standardized format for describing smart contract operations</li>
          </ul>
        </div>
        
        <div className="flex justify-start">
          <Button 
            variant="outline" 
            asChild
            className="px-8 py-6 text-base border border-gray-700 hover:bg-gray-800 hover:border-gray-600"
          >
            <Link href="/">Back to Home</Link>
          </Button>
        </div>
      </div>
    </HydrateClient>
  );
} 