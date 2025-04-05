"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { Loader2, CheckCircle, XCircle, AlertTriangle, ArrowLeft, ExternalLink, RotateCcw, Clock } from "lucide-react";
import { useToast } from "~/hooks/use-toast";
import { web3Service } from "~/lib/web3Service";
import { getQuestionData, hasFinalizationTimePassed, getTimeRemainingUntilFinalization, formatFinalizationTime, getQuestionsByUser } from "~/lib/realityEthService";
import Link from "next/link";

export default function VerificationStatusPage() {
  const searchParams = useSearchParams();
  const ipfsHash = searchParams?.get("ipfsHash");
  const questionId = searchParams?.get("questionId");
  
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [finalizationTimestamp, setFinalizationTimestamp] = useState<string | null>(null);
  const [timeoutValue, setTimeoutValue] = useState<string | null>(null);
  const [createdTimestampValue, setCreatedTimestampValue] = useState<string | null>(null);
  const [timeRemaining, setTimeRemaining] = useState<string | null>(null);
  const [canFinalize, setCanFinalize] = useState(false);
  const [isProcessingResult, setIsProcessingResult] = useState(false);
  const [transactionHash, setTransactionHash] = useState<string | null>(null);
  const [specStatus, setSpecStatus] = useState<number>(-1);
  const { toast } = useToast();
  
  useEffect(() => {
    // Update time remaining every second if we have a timestamp or createdTimestamp
    if (finalizationTimestamp || createdTimestampValue) {
      // Initial update
      const updateTimeRemaining = () => {
        const remaining = getTimeRemainingUntilFinalization(
          finalizationTimestamp || undefined,
          timeoutValue || undefined,
          createdTimestampValue || undefined
        );
        setTimeRemaining(remaining);
        
        // Also check if finalization time has passed
        const now = Date.now();
        let finalizationTime: number;
        
        if (finalizationTimestamp) {
          finalizationTime = parseInt(finalizationTimestamp) * 1000;
          console.log("Using finalizationTimestamp for calculation:", new Date(finalizationTime).toISOString());
        } else if (timeoutValue && createdTimestampValue) {
          finalizationTime = (parseInt(createdTimestampValue) + parseInt(timeoutValue)) * 1000;
          console.log("Using timeout + createdTimestamp for calculation:", new Date(finalizationTime).toISOString());
        } else if (createdTimestampValue) {
          finalizationTime = (parseInt(createdTimestampValue) + 900) * 1000;
          console.log("Using default timeout + createdTimestamp for calculation:", new Date(finalizationTime).toISOString());
        } else {
          console.log("No timing data available for finalization check");
          return;
        }
        
        const newCanFinalize = now > finalizationTime;
        
        // Log detailed timing info when the value changes
        if (newCanFinalize !== canFinalize) {
          console.log("Finalization status changed to:", newCanFinalize);
          console.log("- Current time:", new Date(now).toISOString());
          console.log("- Finalization time:", new Date(finalizationTime).toISOString());
          console.log("- Time difference (ms):", now - finalizationTime);
        }
        
        setCanFinalize(newCanFinalize);
      };
      
      // Initial update
      updateTimeRemaining();
      
      const interval = setInterval(updateTimeRemaining, 1000); // Update every second
      
      return () => clearInterval(interval);
    }
  }, [finalizationTimestamp, timeoutValue, createdTimestampValue]);
  
  useEffect(() => {
    if (ipfsHash && questionId) {
      fetchData();
    }
  }, [ipfsHash, questionId]);
  
  const fetchData = async () => {
    if (!ipfsHash || !questionId) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Get question data from Reality.eth
      try {
        console.log("Trying to get question data for ID:", questionId);
        const questionData = await getQuestionData(questionId);
        
        if (!questionData) {
          console.warn("Question data is null in verification status page");
          
          // Use estimated values instead of throwing an error
          const defaultCreatedTimestamp = Math.floor(Date.now() / 1000 - 900).toString(); // 15 minutes ago
          setCreatedTimestampValue(defaultCreatedTimestamp);
          setTimeoutValue("900"); // 15 minute timeout as default
          
          // Calculate time with defaults
          const remaining = getTimeRemainingUntilFinalization(
            undefined,
            "900",
            defaultCreatedTimestamp
          );
          setTimeRemaining(remaining);
          
          // Direct calculation for finalization status
          const now = Date.now();
          const estimatedFinalizationTime = (parseInt(defaultCreatedTimestamp) + 900) * 1000;
          const directCanFinalize = now > estimatedFinalizationTime;
          
          console.log("Fallback calculation of canFinalize:", directCanFinalize);
          console.log("- Current time:", new Date(now).toISOString());
          console.log("- Estimated finalization time:", new Date(estimatedFinalizationTime).toISOString());
          console.log("- Time difference (seconds):", (now - estimatedFinalizationTime) / 1000);
          
          // We trust the direct calculation for fallback case
          setCanFinalize(directCanFinalize);
          
          // Also check using the service
          try {
            // This will likely return false since there's no question data
            const serviceCanFinalize = await hasFinalizationTimePassed(questionId);
            console.log("Service hasFinalizationTimePassed returned:", serviceCanFinalize);
            
            // If there's a mismatch, log it but still use our direct calculation
            if (serviceCanFinalize !== directCanFinalize) {
              console.warn("Mismatch between service and direct calculation in fallback");
            }
          } catch (finalizeError) {
            console.error("Error checking finalization with service:", finalizeError);
          }
          
          // Get spec status from contract
          try {
            const status = await web3Service.getSpecStatus(ipfsHash);
            setSpecStatus(status);
          } catch (statusError) {
            console.error("Error getting spec status:", statusError);
            // Don't set an error as the status might not be available yet
          }
          
          return;
        }
        
        console.log("Received question data in status page:", questionData);
        
        // Set state with available data, handling optional fields
        setFinalizationTimestamp(questionData.currentScheduledFinalizationTimestamp || null);
        setTimeoutValue(questionData.timeout || null);
        setCreatedTimestampValue(questionData.createdTimestamp || null);
        
        // Calculate time remaining based on available data
        const remaining = getTimeRemainingUntilFinalization(
          questionData.currentScheduledFinalizationTimestamp,
          questionData.timeout,
          questionData.createdTimestamp
        );
        setTimeRemaining(remaining);
        
        // Check if finalization time has passed
        const canFinalize = await hasFinalizationTimePassed(questionId);
        setCanFinalize(canFinalize);
        
        // Log why canFinalize is set the way it is for debugging
        console.log("Initial canFinalize value set to:", canFinalize);
        
        // Double check with direct calculation
        let calculatedFinalizationTime: number | null = null;
        if (questionData.currentScheduledFinalizationTimestamp) {
          calculatedFinalizationTime = parseInt(questionData.currentScheduledFinalizationTimestamp) * 1000;
        } else if (questionData.timeout && questionData.createdTimestamp) {
          calculatedFinalizationTime = (parseInt(questionData.createdTimestamp) + parseInt(questionData.timeout)) * 1000;
        } else if (questionData.createdTimestamp) {
          calculatedFinalizationTime = (parseInt(questionData.createdTimestamp) + 900) * 1000;
        }
        
        if (calculatedFinalizationTime) {
          const now = Date.now();
          const directlyCalculated = now > calculatedFinalizationTime;
          console.log("Direct calculation of canFinalize:", directlyCalculated);
          console.log("- Current time:", new Date(now).toISOString());
          console.log("- Calculated finalization time:", new Date(calculatedFinalizationTime).toISOString());
          console.log("- Time difference (seconds):", (now - calculatedFinalizationTime) / 1000);
          
          // If there's a mismatch, use the direct calculation as it's more reliable
          if (directlyCalculated !== canFinalize) {
            console.warn("Mismatch between hasFinalizationTimePassed and direct calculation, using direct calculation");
            setCanFinalize(directlyCalculated);
          }
        }
        
        // Get spec status from contract
        try {
          const status = await web3Service.getSpecStatus(ipfsHash);
          setSpecStatus(status);
        } catch (statusError) {
          console.error("Error getting spec status:", statusError);
          // Don't set an error as the status might not be available yet
        }
      } catch (questionError: any) {
        console.error("Error fetching question data:", questionError);
        
        // Handle question not found errors specifically
        if (questionError.message.includes("Question not found") || questionError.message.includes("No question data found")) {
          setError("This question hasn't been registered in Reality.eth yet. Please wait a few minutes for the transaction to be processed and try again.");
        } else {
          setError(questionError.message || "Failed to fetch verification data. Please try again.");
        }
      }
    } catch (err: any) {
      console.error("Error fetching verification data:", err);
      setError(err.message || "Failed to fetch verification data. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleResult = async () => {
    if (!ipfsHash || !canFinalize) {
      toast({
        title: "Action Required",
        description: "Please connect your wallet first.",
        variant: "destructive",
      });
      return;
    }
    
    setIsProcessingResult(true);
    
    try {
      // Call handleResult on the contract
      const txHash = await web3Service.handleResult(ipfsHash);
      setTransactionHash(txHash);
      
      toast({
        title: "Transaction Submitted",
        description: `Successfully submitted transaction to fetch the verification result.`,
        variant: "default",
      });
      
      // Wait a bit and then fetch the new status
      setTimeout(async () => {
        try {
          const newStatus = await web3Service.getSpecStatus(ipfsHash);
          setSpecStatus(newStatus);
        } catch (statusError) {
          console.error("Error getting updated spec status:", statusError);
        }
      }, 3000);
    } catch (error: any) {
      console.error("Error handling result:", error);
      toast({
        title: "Error Processing Result",
        description: error.message || "Failed to process verification result. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsProcessingResult(false);
    }
  };
  
  const refreshStatus = async () => {
    if (!ipfsHash) return;
    
    setIsLoading(true);
    
    try {
      // Check if finalization time has passed
      if (questionId) {
        const canFinalizeCheck = await hasFinalizationTimePassed(questionId);
        setCanFinalize(canFinalizeCheck);
      }
      
      // Get spec status if available
      const status = await web3Service.getSpecStatus(ipfsHash);
      setSpecStatus(status);
      
      toast({
        title: "Status Refreshed",
        description: "The verification status has been updated.",
        variant: "default",
      });
    } catch (err: any) {
      console.error("Error refreshing status:", err);
      toast({
        title: "Error Refreshing Status",
        description: err.message || "Failed to refresh status. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  const getStatusDisplay = () => {
    if (specStatus === null) {
      return (
        <div className="flex items-center p-3 bg-yellow-900/30 border border-yellow-700 rounded-lg">
          <AlertTriangle className="h-5 w-5 text-yellow-500 mr-2" />
          <span className="text-yellow-500">Status not yet available</span>
        </div>
      );
    }
    
    switch (specStatus) {
      case 0: // Submitted
        return (
          <div className="flex items-center p-3 bg-blue-900/30 border border-blue-700 rounded-lg">
            <AlertTriangle className="h-5 w-5 text-blue-500 mr-2" />
            <span className="text-blue-500">Submitted - Waiting for verification</span>
          </div>
        );
      case 1: // Accepted
        return (
          <div className="flex items-center p-3 bg-green-900/30 border border-green-700 rounded-lg">
            <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
            <span className="text-green-500">Accepted - Specification verified as valid</span>
          </div>
        );
      case 2: // Rejected
        return (
          <div className="flex items-center p-3 bg-red-900/30 border border-red-700 rounded-lg">
            <XCircle className="h-5 w-5 text-red-500 mr-2" />
            <span className="text-red-500">Rejected - Specification deemed invalid</span>
          </div>
        );
      default:
        return (
          <div className="flex items-center p-3 bg-gray-900/30 border border-gray-700 rounded-lg">
            <AlertTriangle className="h-5 w-5 text-gray-500 mr-2" />
            <span className="text-gray-500">Unknown status</span>
          </div>
        );
    }
  };
  
  if (isLoading) {
    return (
      <div className="container mx-auto max-w-2xl py-8 px-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">Loading Verification Status</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Loader2 className="h-12 w-12 animate-spin text-blue-500 mb-4" />
            <p className="text-gray-400">Fetching verification data...</p>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="container mx-auto max-w-2xl py-8 px-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">Error</CardTitle>
          </CardHeader>
          <CardContent className="py-6">
            <div className="p-4 bg-red-900/30 border border-red-700 rounded-lg mb-6">
              <p className="text-red-500">{error}</p>
            </div>
            <Link href="/verification-results">
              <Button variant="outline" className="flex items-center">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Upload
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto max-w-3xl p-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-2xl">Verification Status</CardTitle>
            <Button variant="outline" size="sm" onClick={refreshStatus} disabled={isProcessingResult}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent className="py-6">
          <div className="mb-6">
            <h3 className="text-lg font-medium mb-2">IPFS Hash</h3>
            <div className="flex items-center">
              <code className="font-mono text-sm bg-gray-800 px-3 py-2 rounded break-all">{ipfsHash}</code>
              <a 
                href={`https://ipfs.io/ipfs/${ipfsHash}`}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-2 text-blue-400 hover:text-blue-300"
              >
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
          </div>
          
          <div className="mb-6">
            <h3 className="text-lg font-medium mb-2">Question ID</h3>
            <div className="flex items-center">
              <code className="font-mono text-sm bg-gray-800 px-3 py-2 rounded break-all">{questionId}</code>
              <a 
                href={`https://reality.eth.limo/app/#!/question/0xaf33dcb6e8c5c4d9ddf579f53031b514d19449ca-${questionId}`}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-2 text-blue-400 hover:text-blue-300"
              >
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
          </div>
          
          <div className="mb-6">
            <h3 className="text-lg font-medium mb-2">Verification Status</h3>
            {getStatusDisplay()}
          </div>
          
          {finalizationTimestamp || createdTimestampValue ? (
            <div className="mb-6">
              <h3 className="text-lg font-medium mb-2">Verification Timing</h3>
              <div className="p-4 bg-gray-800 rounded-lg flex flex-col gap-3">
                <div className="flex items-center">
                  <Clock className="h-5 w-5 text-blue-400 mr-3" />
                  <div>
                    <p className="text-gray-300 font-medium">
                      Finalization Time: {formatFinalizationTime(
                        finalizationTimestamp || '',
                        timeoutValue || undefined,
                        createdTimestampValue || undefined
                      )}
                    </p>
                    {timeRemaining && (
                      <p className={`mt-1 text-sm font-bold ${timeRemaining.includes("passed") ? "text-green-500" : "text-amber-500"}`}>
                        {timeRemaining}
                      </p>
                    )}
                    
                    <div className="mt-2 text-xs text-gray-400">
                      {finalizationTimestamp && (
                        <p>Using scheduled finalization timestamp: {new Date(parseInt(finalizationTimestamp) * 1000).toLocaleString()}</p>
                      )}
                      {!finalizationTimestamp && timeoutValue && createdTimestampValue && (
                        <p>
                          Using creation time ({new Date(parseInt(createdTimestampValue) * 1000).toLocaleString()}) + 
                          timeout ({parseInt(timeoutValue) / 60} minutes)
                        </p>
                      )}
                      {!finalizationTimestamp && !timeoutValue && createdTimestampValue && (
                        <p>
                          Using creation time ({new Date(parseInt(createdTimestampValue) * 1000).toLocaleString()}) + 
                          default timeout (15 minutes)
                        </p>
                      )}
                    </div>
                  </div>
                </div>
                
                {canFinalize ? (
                  <div className="mt-1 p-3 bg-green-900/30 border border-green-600 rounded-lg">
                    <p className="text-green-400 font-medium flex items-center">
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Verification period has ended. You can now fetch the result.
                    </p>
                    {finalizationTimestamp && (
                      <p className="text-xs text-green-500/60 mt-1">
                        Finalization became available at: {new Date(parseInt(finalizationTimestamp) * 1000).toLocaleString()}
                      </p>
                    )}
                  </div>
                ) : (
                  <div className="mt-1 p-3 bg-amber-900/30 border border-amber-600 rounded-lg">
                    <p className="text-amber-400 font-medium flex items-center">
                      <Clock className="h-4 w-4 mr-2" />
                      Verification is still in the waiting period. Please check back later.
                    </p>
                    <p className="text-xs text-amber-500/60 mt-1">
                      Expected finalization time: {formatFinalizationTime(
                        finalizationTimestamp || '',
                        timeoutValue || '900',
                        createdTimestampValue || String(Math.floor(Date.now() / 1000 - 900))
                      )}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ) : null}
          
          <div className="flex justify-between mt-8">
            <Link href="/verification-results">
              <Button variant="outline" className="flex items-center">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Upload
              </Button>
            </Link>
            
            {canFinalize && specStatus !== 1 && specStatus !== 2 && (
              <Button 
                onClick={handleResult}
                disabled={isProcessingResult || !canFinalize}
                className="bg-green-600 hover:bg-green-700"
              >
                {isProcessingResult ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  "Fetch Verification Result"
                )}
              </Button>
            )}
          </div>
          
          {transactionHash && (
            <div className="mt-6 p-4 bg-green-900/30 border border-green-700 rounded-lg">
              <p className="text-green-500 font-medium mb-1">Transaction Submitted!</p>
              <div className="flex justify-between items-center">
                <code className="font-mono text-xs text-gray-400 truncate max-w-xs">{transactionHash}</code>
                <a 
                  href={`https://sepolia.etherscan.io/tx/${transactionHash}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-400 hover:underline ml-2 flex items-center"
                >
                  View on Etherscan
                  <ExternalLink className="h-3 w-3 ml-1" />
                </a>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 