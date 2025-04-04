import { HydrateClient } from "~/trpc/server";
import { Button } from "~/components/ui/button";
import Link from "next/link";

export default function VerificationResultsPage() {
  return (
    <HydrateClient>
      <div className="container mx-auto max-w-4xl p-6">
        <h1 className="mb-4 text-3xl font-bold">Verification Results</h1>
        
        <div className="mb-8 rounded-lg bg-green-50 p-6 text-green-700 dark:bg-green-900 dark:text-green-100">
          <h2 className="mb-2 text-xl font-medium">Success!</h2>
          <p>
            Your ERC7730 JSON specification has been validated successfully. It complies with the 
            required format and contains valid content for clear signing.
          </p>
        </div>
        
        <div className="mb-8 space-y-4">
          <h2 className="text-xl font-medium">Contract Details</h2>
          <div className="rounded border p-4">
            <p><strong>Contract Name:</strong> Example ERC20 Token</p>
            <p><strong>Address:</strong> 0x1234...5678</p>
            <p><strong>Network:</strong> Ethereum Mainnet</p>
            <p><strong>Verification Date:</strong> {new Date().toLocaleDateString()}</p>
          </div>
        </div>
        
        <div className="mb-8 space-y-4">
          <h2 className="text-xl font-medium">Recommendations</h2>
          <ul className="list-inside list-disc space-y-2">
            <li>Submit this specification to the ERC7730 registry</li>
            <li>Ensure hardware wallet compliance with Clear Signing standards</li>
            <li>Provide clear documentation for users interacting with your contract</li>
          </ul>
        </div>
        
        <div className="flex justify-between">
          <Button variant="outline" asChild>
            <Link href="/review">Back to Review</Link>
          </Button>
          <Button asChild>
            <Link href="/">Home</Link>
          </Button>
        </div>
      </div>
    </HydrateClient>
  );
} 