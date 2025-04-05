"use client";

import { useState } from "react";
import { Button } from "~/components/ui/button";
import { FileJson, Upload, CheckCircle, AlertCircle } from "lucide-react";
import { Card } from "~/components/ui/card";
import { useErc7730Store } from "~/store/erc7730Provider";
import { useToast } from "~/hooks/use-toast";

export default function FileUploader() {
  const [file, setFile] = useState<File | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState<"idle" | "success" | "error">("idle");
  const [jsonData, setJsonData] = useState<any>(null);
  const { setErc7730 } = useErc7730Store((state) => state);
  const { toast } = useToast();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      // Use a non-null assertion since we already checked length > 0
      const selectedFile = e.target.files[0]!;
      setFile(selectedFile);
      setVerificationStatus("idle");
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setIsVerifying(true);
    
    try {
      const fileContent = await file.text();
      const parsedData = JSON.parse(fileContent);
      
      // Basic validation - check if it has the expected ERC7730 structure
      const isValidFormat = 
        parsedData && 
        typeof parsedData === "object" &&
        "$schema" in parsedData &&
        "context" in parsedData &&
        "metadata" in parsedData;
      
      if (isValidFormat) {
        setVerificationStatus("success");
        setJsonData(parsedData);
        setErc7730(parsedData);
        toast({
          title: "File Verified Successfully",
          description: "The ERC7730 JSON file is valid.",
          variant: "default",
        });
      } else {
        setVerificationStatus("error");
        toast({
          title: "Invalid File Format",
          description: "The uploaded file does not appear to be a valid ERC7730 JSON specification.",
          variant: "destructive",
        });
      }
    } catch (error) {
      setVerificationStatus("error");
      toast({
        title: "Error Parsing JSON",
        description: "The file could not be parsed as valid JSON.",
        variant: "destructive",
      });
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <Card className="p-6 mb-8">
      <div className="flex flex-col gap-4">
        <h2 className="text-xl font-medium">Upload ERC7730 JSON File</h2>
        
        <div className="flex flex-col items-center justify-center gap-4 border-2 border-dashed rounded-lg p-6">
          <FileJson size={48} className="text-gray-400" />
          <p className="text-sm text-gray-500">
            {file ? `Selected: ${file.name}` : "Drag and drop your JSON file here or click to browse"}
          </p>
          
          <input
            type="file"
            id="jsonFileUpload"
            accept=".json"
            onChange={handleFileChange}
            className="hidden"
          />
          
          <Button
            asChild={!file}
            variant="outline"
            disabled={isVerifying}
          >
            {!file ? (
              <label htmlFor="jsonFileUpload" className="cursor-pointer">
                <Upload className="mr-2 h-4 w-4" />
                Browse Files
              </label>
            ) : (
              <label htmlFor="jsonFileUpload" className="cursor-pointer">
                <Upload className="mr-2 h-4 w-4" />
                Change File
              </label>
            )}
          </Button>
          
          {file && (
            <Button
              onClick={handleUpload}
              disabled={isVerifying}
              className="mt-2"
            >
              {isVerifying ? "Verifying..." : "Verify JSON"}
            </Button>
          )}
        </div>
        
        {verificationStatus === "success" && (
          <div className="flex items-center gap-2 text-green-600 mt-2">
            <CheckCircle className="h-5 w-5" />
            <span>File verified successfully!</span>
          </div>
        )}
        
        {verificationStatus === "error" && (
          <div className="flex items-center gap-2 text-red-600 mt-2">
            <AlertCircle className="h-5 w-5" />
            <span>Invalid JSON format. Please upload a valid ERC7730 specification.</span>
          </div>
        )}
      </div>
    </Card>
  );
} 