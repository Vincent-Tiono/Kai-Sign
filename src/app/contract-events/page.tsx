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

export default function ContractEventsPage() {
  const [page, setPage] = useState(0);
  const [limit] = useState(10);
  const [events, setEvents] = useState<any[]>([]);
  const [rawResponse, setRawResponse] = useState<any>(null);
  
  const { data, isLoading, error } = api.contractEvents.getLogHandleResult.useQuery({
    offset: (page * limit).toString(),
    limit: limit.toString(),
  });

  useEffect(() => {
    if (data && !isLoading) {
      // Store the raw response for debugging
      setRawResponse(data);
      console.log("API Response:", JSON.stringify(data, null, 2));
      
      // Check various possible structures and set events accordingly
      if (Array.isArray(data)) {
        console.log("Data is an array");
        setEvents(data);
      } else if (data.result && Array.isArray(data.result)) {
        console.log("Data has result array");
        setEvents(data.result);
      } else if (data.result && data.result.rows && Array.isArray(data.result.rows) && data.result.rows.length > 0 && Object.keys(data.result.rows[0]).length > 0) {
        // Handle the specific response pattern from the queries endpoint
        console.log("Data has result.rows array with content");
        setEvents(data.result.rows);
      } else if (data.results && Array.isArray(data.results)) {
        console.log("Data has results array");
        setEvents(data.results);
      } else if (data.data && Array.isArray(data.data)) {
        console.log("Data has data array");
        setEvents(data.data);
      } else if (data.events && Array.isArray(data.events)) {
        console.log("Data has events array");
        setEvents(data.events);
      } else if (data.items && Array.isArray(data.items)) {
        console.log("Data has items array");
        setEvents(data.items);
      } else {
        // Deep check for nested arrays
        let foundEvents = false;
        Object.keys(data).forEach(key => {
          if (!foundEvents && data[key] && Array.isArray(data[key])) {
            console.log(`Found array in data.${key}`);
            setEvents(data[key]);
            foundEvents = true;
          } else if (!foundEvents && typeof data[key] === 'object' && data[key] !== null) {
            Object.keys(data[key]).forEach(nestedKey => {
              if (!foundEvents && data[key][nestedKey] && Array.isArray(data[key][nestedKey])) {
                console.log(`Found array in data.${key}.${nestedKey}`);
                setEvents(data[key][nestedKey]);
                foundEvents = true;
              }
            });
          }
        });
        
        if (!foundEvents) {
          console.error("Unexpected data structure:", data);
          setEvents([]);
        }
      }
    }
  }, [data, isLoading]);

  const handleNextPage = () => {
    setPage((prev) => prev + 1);
  };

  const handlePrevPage = () => {
    setPage((prev) => Math.max(0, prev - 1));
  };

  return (
    <div className="container mx-auto py-10">
      <h1 className="text-3xl font-bold mb-6">Smart Contract Events</h1>
      <Card>
        <CardHeader>
          <CardTitle>LogHandleResult Events</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, index) => (
                <Skeleton key={index} className="h-12 w-full" />
              ))}
            </div>
          ) : error ? (
            <div className="text-red-500 p-4 border border-red-300 rounded">
              <p>Error loading events: {error.message}</p>
            </div>
          ) : (
            <>
              {events.length > 0 ? (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Block Number</TableHead>
                        <TableHead>Transaction Hash</TableHead>
                        <TableHead>SpecID</TableHead>
                        <TableHead>Is Accepted</TableHead>
                        <TableHead>Timestamp</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {events.map((event, index) => (
                        <TableRow key={index}>
                          <TableCell>{event.blockNumber || 'N/A'}</TableCell>
                          <TableCell className="font-mono text-xs">
                            {event.transactionHash ? 
                              `${event.transactionHash.slice(0, 10)}...${event.transactionHash.slice(-8)}` : 
                              'N/A'}
                          </TableCell>
                          <TableCell className="font-mono text-xs">
                            {event.args && event.args.specID ? 
                              `${event.args.specID.slice(0, 10)}...${event.args.specID.slice(-8)}` : 
                              'N/A'}
                          </TableCell>
                          <TableCell>
                            {event.args && event.args.isAccepted !== undefined ? 
                              (event.args.isAccepted ? "Yes" : "No") : 
                              'N/A'}
                          </TableCell>
                          <TableCell>
                            {event.timestamp ? 
                              new Date(event.timestamp * 1000).toLocaleString() : 
                              'N/A'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <div className="text-center py-10 border rounded-md">
                  <p className="text-gray-500 mb-4">No LogHandleResult events found</p>
                  <p className="text-sm mb-6">The contract exists and is configured correctly, but no events of this type have been emitted yet.</p>
                  
                  <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-4 mx-auto max-w-2xl text-left">
                    <h3 className="text-blue-800 font-medium mb-2">Contract Information</h3>
                    <p className="text-sm mb-2"><span className="font-semibold">Contract:</span> KaiSign</p>
                    <p className="text-sm mb-2"><span className="font-semibold">Address:</span> 0x2d2f90786a365a2044324f6861697e9EF341F858</p>
                    <p className="text-sm mb-2"><span className="font-semibold">Event:</span> LogHandleResult(bytes32,bool)</p>
                    <p className="text-sm mb-2"><span className="font-semibold">Parameters:</span> specID (bytes32), isAccepted (bool)</p>
                  </div>
                  
                  {rawResponse && (
                    <div className="mt-4 p-4 bg-gray-100 rounded-md text-left overflow-auto max-h-96 mx-auto max-w-2xl">
                      <p className="font-semibold mb-2">Raw API Response:</p>
                      <pre className="text-xs">
                        {JSON.stringify(rawResponse, null, 2)}
                      </pre>
                    </div>
                  )}
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