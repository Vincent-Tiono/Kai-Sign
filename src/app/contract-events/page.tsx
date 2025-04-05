"use client";

import { useState, useEffect } from "react";
import { api } from "~/trpc/react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "~/components/ui/table";
import { Skeleton } from "~/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Pagination, PaginationContent, PaginationItem, PaginationNext, PaginationPrevious } from "~/components/ui/pagination";
import { Alert, AlertDescription, AlertTitle } from "~/components/ui/alert";
import { InfoIcon, AlertTriangle } from "lucide-react";

export default function ContractEventsPage() {
  const [page, setPage] = useState(0);
  const [limit] = useState(10);
  const [events, setEvents] = useState<any[]>([]);
  const [rawResponse, setRawResponse] = useState<any>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorDetails, setErrorDetails] = useState<string | null>(null);
  
  const { data, isLoading, error, refetch } = api.contractEvents.getLogHandleResult.useQuery({
    offset: (page * limit).toString(),
    limit: limit.toString(),
  }, {
    retry: false, // Don't automatically retry on error
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
  });

  // Handle error updates separately to avoid linter errors with onError
  useEffect(() => {
    if (error) {
      console.error("Query error:", error);
      setErrorDetails(error.message || "Unknown error occurred");
    }
  }, [error]);

  useEffect(() => {
    if (data && !isLoading) {
      // Store the raw response for debugging
      setRawResponse(data);
      
      // Clear any previous error
      setErrorDetails(null);
      
      // Check if there's a status message
      if (data.message && typeof data.message === 'string') {
        setStatusMessage(data.message);
      } else {
        setStatusMessage(null);
      }
      
      let eventData: any[] = [];
      
      // Check various possible structures and set events accordingly
      if (Array.isArray(data)) {
        eventData = data;
      } else if (data.result && Array.isArray(data.result)) {
        eventData = data.result;
      } else if (data.result && data.result.rows && Array.isArray(data.result.rows) && data.result.rows.length > 0 && Object.keys(data.result.rows[0]).length > 0) {
        // Handle the specific response pattern from the queries endpoint
        eventData = data.result.rows;
      } else if (data.results && Array.isArray(data.results)) {
        eventData = data.results;
      } else if (data.data && Array.isArray(data.data)) {
        eventData = data.data;
      } else if (data.events && Array.isArray(data.events)) {
        eventData = data.events;
      } else if (data.items && Array.isArray(data.items)) {
        eventData = data.items;
      } else {
        // Deep check for nested arrays
        let foundEvents = false;
        Object.keys(data).forEach(key => {
          if (!foundEvents && data[key] && Array.isArray(data[key])) {
            eventData = data[key];
            foundEvents = true;
          } else if (!foundEvents && typeof data[key] === 'object' && data[key] !== null) {
            Object.keys(data[key]).forEach(nestedKey => {
              if (!foundEvents && data[key][nestedKey] && Array.isArray(data[key][nestedKey])) {
                eventData = data[key][nestedKey];
                foundEvents = true;
              }
            });
          }
        });
        
        if (!foundEvents) {
          console.error("Unexpected data structure:", data);
          eventData = [];
        }
      }
      
      // Sort events by timestamp in descending order (newest first)
      eventData.sort((a, b) => {
        const timestampA = a.timestamp || 0;
        const timestampB = b.timestamp || 0;
        return timestampB - timestampA;
      });
      
      setEvents(eventData);
    }
  }, [data, isLoading]);

  const handleNextPage = () => {
    setPage((prev: number) => prev + 1);
  };

  const handlePrevPage = () => {
    setPage((prev: number) => Math.max(0, prev - 1));
  };

  const handleRetry = async () => {
    setErrorDetails(null);
    try {
      await refetch();
    } catch (err) {
      console.error("Refetch failed:", err);
      setErrorDetails(err instanceof Error ? err.message : "Retry failed");
    }
  };

  return (
    <div className="container mx-auto py-10">
      <h1 className="text-3xl font-bold mb-6">Validated ERC7730 metadata</h1>
      <Card>
        <CardHeader>
          <CardTitle>Past results (Query powered by Curvegrid)</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, index) => (
                <Skeleton key={index} className="h-12 w-full" />
              ))}
            </div>
          ) : error || errorDetails ? (
            <div className="text-red-500 p-4 border border-red-300 rounded">
              <div className="flex items-start mb-2">
                <AlertTriangle className="h-5 w-5 mr-2 mt-0.5" />
                <div>
                  <h3 className="font-bold">Error loading events</h3>
                  <p className="text-sm mt-1">{errorDetails || error?.message || "Unknown error"}</p>
                </div>
              </div>
              <button 
                onClick={handleRetry}
                className="mt-3 px-4 py-2 bg-red-100 text-red-800 rounded hover:bg-red-200 transition-colors"
              >
                Retry
              </button>
            </div>
          ) : (
            <>
              {statusMessage && (
                <Alert className="mb-4">
                  <InfoIcon className="h-4 w-4" />
                  <AlertTitle>API Status</AlertTitle>
                  <AlertDescription>{statusMessage}</AlertDescription>
                </Alert>
              )}
              
              {events.length > 0 ? (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Transaction Hash</TableHead>
                        <TableHead>Is Accepted</TableHead>
                        <TableHead>Timestamp</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {events.map((event, index) => (
                        event.args && event.args.isAccepted ? (
                          <TableRow key={index}>
                            <TableCell className="font-mono text-xs">
                              {event.transactionHash ? (
                                <a 
                                  href={`https://sepolia.etherscan.io/tx/${event.transactionHash}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-blue-600 hover:underline"
                                >
                                  {`${event.transactionHash.slice(0, 10)}...${event.transactionHash.slice(-8)}`}
                                </a>
                              ) : 'N/A'}
                            </TableCell>
                            <TableCell>
                              {event.args && event.args.isAccepted ? "Yes" : ""}
                            </TableCell>
                            <TableCell>
                              {event.timestamp ? 
                                new Date(event.timestamp * 1000).toLocaleString() : 
                                'N/A'}
                            </TableCell>
                          </TableRow>
                        ) : null
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Transaction Hash</TableHead>
                        <TableHead>Is Accepted</TableHead>
                        <TableHead>Timestamp</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <TableRow>
                        <TableCell>N/A</TableCell>
                        <TableCell>N/A</TableCell>
                        <TableCell>N/A</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </div>
              )}
              
              <Pagination className="mt-4">
                <PaginationContent>
                  <PaginationItem>
                    <PaginationPrevious onClick={handlePrevPage} disabled={page === 0} />
                  </PaginationItem>
                  <PaginationItem>
                    <span className="px-4">Page {page + 1}</span>
                  </PaginationItem>
                  <PaginationItem>
                    <PaginationNext onClick={handleNextPage} disabled={events.length < limit} />
                  </PaginationItem>
                </PaginationContent>
              </Pagination>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 