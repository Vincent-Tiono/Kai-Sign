"use client";

import { useState } from "react";
import { Button } from "~/components/ui/button";
import { FileJson, Upload, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { Card } from "~/components/ui/card";
import { useErc7730Store } from "~/store/erc7730Provider";
import { useToast } from "~/hooks/use-toast";
import { uploadToIPFS } from "~/lib/ipfsService";
import { web3Service } from "~/lib/web3Service";

export default function FileUploader() {
  const [file, setFile] = useState<File | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState<"idle" | "success" | "error">("idle");
  const [jsonData, setJsonData] = useState<any>(null);
  const [ipfsHash, setIpfsHash] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isConnectingWallet, setIsConnectingWallet] = useState(false);
  const [walletConnected, setWalletConnected] = useState(false);
  const [isSendingTransaction, setIsSendingTransaction] = useState(false);
  const [transactionHash, setTransactionHash] = useState<string | null>(null);
  const [currentWalletAddress, setCurrentWalletAddress] = useState<string | null>(null);
  const [minBond, setMinBond] = useState<string | null>(null);
  const { setErc7730 } = useErc7730Store((state) => state);
  const { toast } = useToast();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      // Use a non-null assertion since we already checked length > 0
      const selectedFile = e.target.files[0]!;
      setFile(selectedFile);
      setVerificationStatus("idle");
      setIpfsHash(null);
      setTransactionHash(null);
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
          description: "The ERC7730 JSON file is valid. Uploading to IPFS...",
          variant: "default",
        });
        
        // Upload to IPFS
        await uploadToIpfs(parsedData);
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

  const uploadToIpfs = async (data: any) => {
    setIsUploading(true);
    
    try {
      // Upload to IPFS
      toast({
        title: "Uploading to IPFS",
        description: "Sending your file to IPFS storage. This may take a moment...",
        variant: "default",
      });
      
      const hash = await uploadToIPFS(data);
      setIpfsHash(hash);
      
      toast({
        title: "Uploaded to IPFS Successfully",
        description: `Your file is now stored on IPFS with hash: ${hash.substring(0, 8)}...${hash.substring(hash.length - 4)}`,
        variant: "default",
      });
      
      // Connect wallet after IPFS upload
      await connectWallet();
    } catch (error) {
      console.error("Error uploading to IPFS:", error);
      toast({
        title: "IPFS Upload Failed",
        description: "Failed to upload file to IPFS. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };
  
  const connectWallet = async () => {
    setIsConnectingWallet(true);
    
    try {
      // Connect to MetaMask
      const account = await web3Service.connect();
      setCurrentWalletAddress(account);
      setWalletConnected(true);
      
      // Get minimum bond amount
      const minBondAmount = await web3Service.getMinBond();
      setMinBond(minBondAmount.toString());
      
      toast({
        title: "Wallet Connected",
        description: `Connected to wallet: ${account.substring(0, 6)}...${account.substring(account.length - 4)}`,
        variant: "default",
      });
    } catch (error: any) {
      console.error("Error connecting wallet:", error);
      toast({
        title: "Wallet Connection Failed",
        description: error.message || "Failed to connect to wallet. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsConnectingWallet(false);
    }
  };
  
  const submitToBlockchain = async () => {
    if (!ipfsHash || !walletConnected) return;
    
    setIsSendingTransaction(true);
    
    try {
      // Get minimum bond amount again to make sure it's current
      const bondAmount = await web3Service.getMinBond();
      
      // Submit to blockchain
      const txHash = await web3Service.proposeSpec(ipfsHash, bondAmount);
      setTransactionHash(txHash);
      
      toast({
        title: "Transaction Submitted",
        description: `Successfully submitted transaction with hash: ${txHash.substring(0, 10)}...`,
        variant: "default",
      });
    } catch (error: any) {
      console.error("Error submitting to blockchain:", error);
      toast({
        title: "Transaction Failed",
        description: error.message || "Failed to submit transaction. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSendingTransaction(false);
    }
  };

  return (
    <Card className="p-6 mb-8 bg-gray-950 border-gray-800">
      <div className="flex flex-col gap-4">
        <h2 className="text-xl font-medium">Upload ERC7730 JSON File</h2>
        
        <div className="flex flex-col items-center justify-center gap-6 border-2 border-dashed border-gray-700 rounded-lg p-8">
          <FileJson size={52} className="text-gray-400" />
          <p className="text-sm text-gray-400 text-center">
            {file ? `Selected: ${file.name}` : "Drag and drop your JSON file here or click to browse"}
          </p>
          
          <input
            type="file"
            id="jsonFileUpload"
            accept=".json"
            onChange={handleFileChange}
            className="hidden"
          />
          
          {!file ? (
            <Button
              asChild
              variant="outline"
              size="lg"
              className="px-8 py-6 min-w-[220px] text-white bg-transparent border border-gray-700 hover:bg-gray-800 hover:border-gray-600 transition-colors"
            >
              <label htmlFor="jsonFileUpload" className="cursor-pointer flex items-center justify-center text-base">
                <Upload className="mr-2 h-5 w-5" />
                Browse Files
              </label>
            </Button>
          ) : (
            <div className="flex flex-col items-center gap-4 w-full max-w-md">
              <Button
                asChild
                variant="outline"
                size="lg"
                className="w-full px-8 py-6 text-white bg-transparent border border-gray-700 hover:bg-gray-800 hover:border-gray-600 transition-colors"
              >
                <label htmlFor="jsonFileUpload" className="cursor-pointer flex items-center justify-center text-base">
                  <Upload className="mr-2 h-5 w-5" />
                  Change File
                </label>
              </Button>
              
              {!ipfsHash ? (
                <Button
                  onClick={handleUpload}
                  disabled={isVerifying || isUploading}
                  size="lg"
                  className="w-full px-8 py-6 mt-2 text-base bg-white text-black hover:bg-gray-100"
                >
                  {isVerifying || isUploading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      {isVerifying ? "Verifying..." : "Uploading to IPFS..."}
                    </>
                  ) : (
                    "Verify JSON"
                  )}
                </Button>
              ) : !walletConnected ? (
                <Button
                  onClick={connectWallet}
                  disabled={isConnectingWallet}
                  size="lg"
                  className="w-full px-8 py-6 mt-2 text-base bg-blue-600 text-white hover:bg-blue-700"
                >
                  {isConnectingWallet ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Connecting Wallet...
                    </>
                  ) : (
                    "Connect Wallet"
                  )}
                </Button>
              ) : !transactionHash ? (
                <Button
                  onClick={submitToBlockchain}
                  disabled={isSendingTransaction}
                  size="lg"
                  className="w-full px-8 py-6 mt-2 text-base bg-green-600 text-white hover:bg-green-700"
                >
                  {isSendingTransaction ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Submitting Transaction...
                    </>
                  ) : (
                    `Submit with Bond (${minBond ? (Number(minBond) / 10**18).toFixed(5) : "..."} ETH)`
                  )}
                </Button>
              ) : (
                <div className="w-full p-4 bg-green-900/30 border border-green-700 rounded-lg text-center">
                  <p className="text-green-500 font-medium mb-1">Transaction Submitted!</p>
                  <a 
                    href={`https://sepolia.etherscan.io/tx/${transactionHash}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-400 hover:underline"
                  >
                    View on Etherscan
                  </a>
                </div>
              )}
            </div>
          )}
        </div>
        
        {verificationStatus === "success" && !ipfsHash && (
          <div className="flex items-center gap-2 text-green-500 mt-4">
            <CheckCircle className="h-5 w-5" />
            <span>File verified successfully!</span>
          </div>
        )}
        
        {ipfsHash && (
          <div className="flex flex-col gap-2 text-green-500 mt-4">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5" />
              <span>
                IPFS Hash: <span className="font-mono text-xs bg-gray-800 px-2 py-1 rounded">{ipfsHash}</span>
              </span>
            </div>
            <div className="text-sm text-gray-400">
              View on: 
              <a 
                href={`https://gateway.ipfs.io/ipfs/${ipfsHash}`}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-2 text-blue-400 hover:underline"
              >
                IPFS Gateway
              </a>
              <span className="mx-1">|</span>
              <a 
                href={`https://ipfs.io/ipfs/${ipfsHash}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 hover:underline"
              >
                IPFS.io
              </a>
              <span className="mx-1">|</span>
              <a 
                href={`https://w3s.link/ipfs/${ipfsHash}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 hover:underline"
              >
                web3.storage
              </a>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Note: IPFS content may take a few minutes to propagate across the network. If one gateway doesn't work, try another.
            </p>
          </div>
        )}
        
        {verificationStatus === "error" && (
          <div className="flex items-center gap-2 text-red-500 mt-4">
            <AlertCircle className="h-5 w-5" />
            <span>Invalid JSON format. Please upload a valid ERC7730 specification.</span>
          </div>
        )}
      </div>
    </Card>
  );
} 