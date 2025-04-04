"use client";

import { Download } from "lucide-react";
import { Button } from "~/components/ui/button";
import { useErc7730Store } from "~/store/erc7730Provider";
import { useToast } from "~/hooks/use-toast";

const DownloadJsonButton = () => {
  const erc7730 = useErc7730Store((s) => s.finalErc7730);
  const { toast } = useToast();

  const handleDownloadJson = () => {
    if (erc7730) {
      const jsonData = JSON.stringify(erc7730, null, 2);
      const blob = new Blob([jsonData], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement("a");
      a.href = url;
      a.download = "erc7730-specification.json";
      document.body.appendChild(a);
      a.click();
      
      URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast({
        title: "JSON downloaded!",
        description: "The complete ERC7730 JSON file has been saved to your downloads folder."
      });
    } else {
      toast({
        title: "No data to download",
        description: "Please validate at least one operation first.",
        variant: "destructive"
      });
    }
  };

  return (
    <Button 
      onClick={handleDownloadJson} 
      variant="outline"
      disabled={!erc7730}
    >
      <Download className="mr-2 h-4 w-4" />
      Download JSON
    </Button>
  );
};

export default DownloadJsonButton; 