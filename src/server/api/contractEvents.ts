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
        // First try to get events using the standard approach
        console.log(`Querying for LogHandleResult events with offset=${offset} and limit=${limit}`);
        
        const query = new URLSearchParams({
          offset,
          limit,
        }).toString();

        const hostname = "bjng3k6eyfdftbqd64ldtrm7we.multibaas.com";
        const jwt = env.CURVEGRID_JWT || "";
        
        // Log JWT token length for debugging (don't log the actual token for security)
        console.log(`JWT token length: ${jwt.length}`);
        
        if (!jwt) {
          console.error("CURVEGRID_JWT is not set or empty");
          throw new Error("API credentials are not configured");
        }
        
        // Try getting events using the queries endpoint
        const resp = await fetch(
          `https://${hostname}/api/v0/queries?${query}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${jwt}`,
            },
            body: JSON.stringify({
              events: [
                {
                  eventName: "LogHandleResult(bytes32,bool)",
                  select: [],
                },
              ],
            }),
          },
        );

        // If not successful, try a different endpoint
        if (!resp.ok) {
          const errorText = await resp.text();
          console.error(`First API request failed: ${resp.status} - ${errorText}`);
          
          // Try a different approach - get events directly
          console.log("Trying alternate method to get events...");
          
          // Try to find contract address from events endpoint
          const contractsResp = await fetch(
            `https://${hostname}/api/v0/contracts`,
            {
              headers: {
                Authorization: `Bearer ${jwt}`,
              },
            }
          );
          
          if (!contractsResp.ok) {
            throw new Error(`Contracts API request failed: ${contractsResp.status}`);
          }
          
          const contractsData = await contractsResp.json();
          console.log("Available contracts:", JSON.stringify(contractsData, null, 2));
          
          if (contractsData && contractsData.result && contractsData.result.length > 0) {
            // Use the first contract address as a fallback
            const address = contractsData.result[0].address;
            const chainID = contractsData.result[0].chain_id;
            
            console.log(`Using contract at ${address} on chain ${chainID}`);
            
            // Try to get events for this contract
            const eventsResp = await fetch(
              `https://${hostname}/api/v0/chains/${chainID}/addresses/${address}/events?${query}`,
              {
                headers: {
                  Authorization: `Bearer ${jwt}`,
                },
              }
            );
            
            if (!eventsResp.ok) {
              throw new Error(`Events API request failed: ${eventsResp.status}`);
            }
            
            const eventsData = await eventsResp.json();
            return eventsData;
          } else {
            throw new Error("No contracts found in the API");
          }
        }

        const data = await resp.json();
        return data;
      } catch (error) {
        console.error("Error fetching contract events:", error);
        throw error;
      }
    }),
}); 