"use client";

import { FileJson } from "lucide-react";
import { Button } from "~/components/ui/button";
import * as React from "react";

import { ResponsiveDialog } from "~/components/ui/responsiveDialog";
import { useErc7730Store } from "~/store/erc7730Provider";
import { useToast } from "~/hooks/use-toast";

export function ReviewJson() {
  const [open, setOpen] = React.useState(false);
  const erc7730 = useErc7730Store((s) => s.finalErc7730);
  const { toast } = useToast();

  const handleCopyToClipboard = () => {
    void navigator.clipboard.writeText(JSON.stringify(erc7730, null, 2));
    toast({
      title: "JSON copied to clipboard!",
    });
  };

  return (
    <ResponsiveDialog
      dialogTrigger={<Button variant="outline">Submit</Button>}
      dialogTitle="Submit your JSON"
      open={open}
      setOpen={setOpen}
    >
      <div className="space-y-4 p-4 md:p-0">
        <p className="text-sm text-gray-600">
          Before submitting, please review your JSON. If everything looks good,
          copy it to your clipboard and create a pull request in the following
          repository:
          <a
            href="https://github.com/LedgerHQ/clear-signing-erc7730-registry"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-500 underline"
          >
            LedgerHQ Clear Signing ERC7730 Registry
          </a>
          .
        </p>
        <pre className="max-h-64 overflow-auto rounded border bg-gray-100 p-4 text-sm dark:text-black">
          {JSON.stringify(erc7730, null, 2)}
        </pre>
        <Button onClick={handleCopyToClipboard}>Copy JSON to Clipboard</Button>
      </div>
    </ResponsiveDialog>
  );
}

export default ReviewJson;
