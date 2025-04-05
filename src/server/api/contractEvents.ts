import { env } from "~/env.js";
import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";
import { z } from "zod";

export const contractEventsRouter = createTRPCRouter({
  getLogHandleResult: publicProcedure
    .input(
      z.object({
        offset: z.string().default("0"),
        limit: z.string().default("10"),
      }),
    )
    .query(async ({ input }) => {
      const { offset, limit } = input;
      
      try {
        
        const hostname = "bjng3k6eyfdftbqd64ldtrm7we.multibaas.com";
        
        // Clean the JWT token by removing spaces
        const rawJwt = env.CURVEGRID_JWT || "";
        const jwt = rawJwt.trim().replace(/\s*=\s*/, '=').replace(/^"(.*)"$/, '$1');
        
        if (!jwt) {
          console.error("CURVEGRID_JWT is not set or empty");
          throw new Error("API credentials are not configured");
        }

        // Use the exact query format provided
        const resp = await fetch(
          `https://${hostname}/api/v0/queries`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${jwt}`
            },
            body: JSON.stringify({
              events: [
                {
                  select: [
                    {
                      name: "specID",
                      type: "input",
                      alias: "",
                      inputIndex: 0
                    },
                    {
                      name: "isAccepted",
                      type: "input",
                      alias: "",
                      inputIndex: 1
                    },
                    {
                      name: "block_number",
                      type: "block_number",
                      alias: ""
                    },
                    {
                      name: "tx_hash",
                      type: "tx_hash",
                      alias: ""
                    },
                    {
                      name: "triggered_at",
                      type: "triggered_at",
                      alias: ""
                    }
                  ],
                  eventName: "LogHandleResult(bytes32,bool)"
                }
              ]
            })
          }
        );
      
        if (!resp.ok) {
          const errorText = await resp.text();
          console.error(`API request failed with status: ${resp.status}`);
          console.error(`Error response: ${errorText}`);
          
          if (resp.status === 401) {
            throw new Error("Authentication failed - JWT token is invalid or expired");
          } else if (resp.status === 404) {
            throw new Error("API endpoint not found - check the hostname");
          } else if (resp.status >= 500) {
            throw new Error("Server error - the API service may be experiencing issues");
          } else {
            throw new Error(`API request failed with status ${resp.status}: ${errorText.substring(0, 100)}`);
          }
        }
        
        const data = await resp.json();
        
        // Check if we have rows in the result (based on test results)
        if (data.result && data.result.rows && Array.isArray(data.result.rows)) {
          const rows = data.result.rows.filter((row: Record<string, any>) => Object.keys(row).length > 0);
          
          if (rows.length > 0) {
            // We found actual data, map and return it
            const events = rows.map((row: Record<string, any>) => {
              // Access fields with lowercase names based on the test results
              // Convert string representation of array to actual array if needed
              let specID = row.specid || row.specID; // Try both casing
              if (typeof specID === 'string' && specID.startsWith('[') && specID.endsWith(']')) {
                try {
                  // Parse string representation of array "[1, 2, 3]" to actual array
                  const arrayStr = specID.replace(/\[|\]/g, '').split(',').map(s => parseInt(s.trim(), 10));
                  specID = '0x' + Array.from(arrayStr)
                    .map((num: number) => num.toString(16).padStart(2, '0'))
                    .join('');
                } catch (e) {
                  console.error("Error parsing specID:", e);
                  // Keep original if parsing fails
                }
              } else if (Array.isArray(specID)) {
                specID = '0x' + Array.from(specID)
                  .map((num: number) => num.toString(16).padStart(2, '0'))
                  .join('');
              }
              
              // Convert timestamp string to Unix timestamp
              let timestamp = 0;
              if (row.triggered_at && typeof row.triggered_at === 'string') {
                timestamp = Math.floor(new Date(row.triggered_at).getTime() / 1000);
              }
              
              // Convert isAccepted value - could be "false" string or boolean false
              const isAccepted = 
                row.isaccepted === true || 
                row.isaccepted === "true" || 
                row.isaccepted === 1 ||
                row.isAccepted === true || 
                row.isAccepted === "true" || 
                row.isAccepted === 1;
              
              const event = {
                blockNumber: parseInt(row.block_number, 10) || 0,
                transactionHash: row.tx_hash || "",
                timestamp: timestamp,
                args: {
                  specID: specID,
                  isAccepted: isAccepted
                }
              };
              return event;
            });
            
            return events;
          }
        }
        
        // If we reach here, the API call was successful but no events were found
        return [];
        
      } catch (error) {
        console.error("Error fetching contract events:", error);
        throw error;
      }
    }),
}); 