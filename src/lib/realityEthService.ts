import { toast } from "~/hooks/use-toast";

// Function to get environment variable with a fallback
const getEnvVar = (key: string, fallback: string = ""): string => {
  const value = process.env[`NEXT_PUBLIC_${key}`] || fallback;
  return value;
};

// GraphQL endpoint for Reality.eth
const REALITY_ETH_GRAPH_URL = getEnvVar(
  "REALITY_ETH_GRAPH_URL",
  "https://gateway.thegraph.com/api/73380b22a17017c081123ec9c0e34677/subgraphs/id/F3XjWNiNFUTbZhNQjXuhP7oDug2NaPwMPZ5XCRx46h5U"
);

// Structure for the Reality.eth question data
interface RealityEthQuestion {
  id: string;
  currentScheduledFinalizationTimestamp?: string;
  timeout?: string;
  createdTimestamp: string;
  currentAnswer?: string;
  currentAnswerBond?: string;
  isPendingArbitration?: boolean;
}

/**
 * Get question data by ID from the Reality.eth Graph API
 * @param questionId The ID of the question to fetch
 * @returns Question data or null if not found
 */
export const getQuestionData = async (questionId: string): Promise<RealityEthQuestion | null> => {
  try {
    console.log("Fetching Reality.eth question data for ID:", questionId);
    
    // Get reality.eth contract address from env or use default
    const realityEthContract = getEnvVar(
      "REALITY_ETH_CONTRACT",
      "0xaf33DcB6E8c5c4D9dDF579f53031b514d19449CA"
    );
    
    // Construct the full ID in format contractAddress-questionId
    const fullQuestionId = questionId.includes("-") 
      ? questionId // Already in the correct format
      : `${realityEthContract.toLowerCase()}-${questionId}`;
    
    console.log("Using full question ID format:", fullQuestionId);
    
    // First try a schema introspection query to check if the API is working and what fields are available
    try {
      const introspectionQuery = `
        {
          __schema {
            types {
              name
              kind
              fields {
                name
                type {
                  name
                  kind
                }
              }
            }
          }
        }
      `;
      
      console.log("Sending introspection query to check API schema...");
      
      const introspectionResponse = await fetch(REALITY_ETH_GRAPH_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: introspectionQuery }),
      });
      
      const introspectionData = await introspectionResponse.json();
      console.log("Schema introspection response:", introspectionData);
      
      // Extract question type to see available fields
      if (introspectionData.data && introspectionData.data.__schema) {
        const questionType = introspectionData.data.__schema.types.find(
          (type: any) => type.name === 'Question'
        );
        
        if (questionType) {
          console.log("Question type fields:", questionType.fields?.map((f: any) => f.name));
        }
      }
    } catch (introspectionError) {
      console.warn("Introspection query failed:", introspectionError);
    }
    
    // Try multiple query formats

    // Format 1: Standard query
    const standardQuery = `
      {
        question(id: "${fullQuestionId}") {
          id
          currentAnswer
          currentAnswerBond
          currentScheduledFinalizationTimestamp
          isPendingArbitration
          timeout
          createdTimestamp
        }
      }
    `;

    // Format 2: Explicit "where" clause
    const whereQuery = `
      {
        question(where: {id: "${fullQuestionId}"}) {
          id
          currentAnswer
          currentAnswerBond
          currentScheduledFinalizationTimestamp
          isPendingArbitration
          timeout
          createdTimestamp
        }
      }
    `;

    // Format 3: Using questions (plural) query with filter
    const questionsQuery = `
      {
        questions(where: {id: "${fullQuestionId}"}, first: 1) {
          id
          currentAnswer
          currentAnswerBond
          currentScheduledFinalizationTimestamp
          isPendingArbitration
          timeout
          createdTimestamp
        }
      }
    `;

    // Try each query format
    for (const [queryName, query] of [
      ["Standard", standardQuery], 
      ["Where clause", whereQuery], 
      ["Questions filter", questionsQuery]
    ]) {
      try {
        console.log(`Trying ${queryName} query:`, query);
        
        const response = await fetch(REALITY_ETH_GRAPH_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query }),
        });

        const data = await response.json();
        console.log(`${queryName} query response:`, data);
        
        // Check for errors
        if (data.errors) {
          console.warn(`GraphQL Errors in ${queryName} query:`, JSON.stringify(data.errors));
          continue; // Try next query format
        }
        
        // Extract question data based on query format
        let questionData = null;
        
        if (queryName === "Questions filter") {
          // For questions query, get the first item
          if (data.data?.questions && data.data.questions.length > 0) {
            questionData = data.data.questions[0];
          }
        } else {
          // For direct question queries
          if (data.data?.question) {
            questionData = data.data.question;
          }
        }
        
        // If we found the question, return it
        if (questionData) {
          console.log(`Found question using ${queryName} query:`, questionData);
          
          // If createdTimestamp is missing but we have other timestamps, add a default
          if (!questionData.createdTimestamp && questionData.currentScheduledFinalizationTimestamp) {
            // Estimate createdTimestamp by subtracting 15 minutes (900 seconds) from finalization
            const finalizationTime = parseInt(questionData.currentScheduledFinalizationTimestamp);
            questionData.createdTimestamp = String(finalizationTime - 900);
            console.log("Added estimated createdTimestamp:", questionData.createdTimestamp);
          }
          
          return questionData;
        }
      } catch (queryError) {
        console.warn(`Error in ${queryName} query:`, queryError);
      }
    }
    
    // Try one more approach - search by hash prefix
    if (fullQuestionId.length >= 10) {
      try {
        const prefixQuery = `
          {
            questions(where: {id_contains: "${fullQuestionId.substring(0, 10)}"}, first: 10) {
              id
              currentAnswer
              currentAnswerBond
              currentScheduledFinalizationTimestamp
              isPendingArbitration
              timeout
              createdTimestamp
            }
          }
        `;
        
        console.log("Trying prefix search query:", prefixQuery);
        
        const prefixResponse = await fetch(REALITY_ETH_GRAPH_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query: prefixQuery }),
        });
        
        const prefixData = await prefixResponse.json();
        console.log("Prefix search response:", prefixData);
        
        if (prefixData.data?.questions && prefixData.data.questions.length > 0) {
          // Find the question with matching ID or closest match
          const exactMatch = prefixData.data.questions.find((q: any) => q.id === fullQuestionId);
          
          if (exactMatch) {
            console.log("Found exact match with prefix search:", exactMatch);
            return exactMatch;
          }
          
          // If no exact match, return the first result
          console.log("No exact match found, using first result:", prefixData.data.questions[0]);
          return prefixData.data.questions[0];
        }
      } catch (prefixError) {
        console.warn("Error in prefix search:", prefixError);
      }
    }
    
    // If all attempts fail, return null
    console.warn("All query attempts failed, returning null");
    return null;
  } catch (error) {
    console.error("Error fetching question data:", error);
    throw error;
  }
};

/**
 * Get all questions for a specific user address
 * @param userAddress The address of the user
 * @returns Array of questions or null if none found
 */
export const getQuestionsByUser = async (userAddress: string): Promise<RealityEthQuestion[] | null> => {
  try {
    console.log("Fetching Reality.eth questions for user:", userAddress);
    
    // GraphQL query to fetch questions for a specific user
    const query = `
      {
        questions(where: {user: "${userAddress}"}) {
          id
          currentAnswer
          currentAnswerBond
          currentScheduledFinalizationTimestamp
          isPendingArbitration
          timeout
          createdTimestamp
        }
      }
    `;

    // Make the GraphQL request
    const response = await fetch(REALITY_ETH_GRAPH_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error(`Network error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log("TheGraph API response for user questions:", data);
    
    if (data.errors) {
      console.error("GraphQL Errors:", JSON.stringify(data.errors));
      throw new Error(`GraphQL errors: ${data.errors[0].message}`);
    }

    if (!data.data || !data.data.questions || data.data.questions.length === 0) {
      console.warn("No questions found for user");
      return [];
    }

    return data.data.questions;
  } catch (error) {
    console.error("Error fetching user questions:", error);
    throw error;
  }
};

/**
 * Format a timestamp into a human-readable date string
 */
export const formatFinalizationTime = (timestamp?: string, timeout?: string, createdTimestamp?: string): string => {
  let finalizeTime: number;
  
  // If we have timeout and createdTimestamp, calculate finalization time
  if (timeout && createdTimestamp) {
    const timeoutSeconds = parseInt(timeout);
    const creationTime = parseInt(createdTimestamp);
    finalizeTime = (creationTime + timeoutSeconds) * 1000; // Convert to milliseconds
  } 
  // If we only have createdTimestamp, assume a default 15-minute timeout
  else if (createdTimestamp) {
    const creationTime = parseInt(createdTimestamp);
    // Use 15 minutes (900 seconds) as default timeout
    finalizeTime = (creationTime + 900) * 1000; // Convert to milliseconds
  }
  // If we have a timestamp (currentScheduledFinalizationTimestamp), use it
  else if (timestamp) {
    finalizeTime = parseInt(timestamp) * 1000; // Convert to milliseconds
  }
  // Fallback to current time + 15 minutes if all else fails
  else {
    finalizeTime = Date.now() + (15 * 60 * 1000); // Current time + 15 minutes
  }
  
  const date = new Date(finalizeTime);
  return date.toLocaleString();
};

/**
 * Check if a question is finalized based on its timestamps
 */
export const hasFinalizationTimePassed = async (questionId: string): Promise<boolean> => {
  try {
    console.log("Checking if finalization time has passed for question ID:", questionId);
    
    // Try to get the question data
    const questionData = await getQuestionData(questionId);
    
    if (!questionData) {
      console.warn("No question data available for hasFinalizationTimePassed check");
      
      // Use a default assumption - if no data available, assume we're still in the waiting period
      // This is safer than returning true and allowing premature finalization
      return false;
    }
    
    console.log("Got question data for finalization check:", questionData);
    
    // Debug log for all timestamps
    console.log("Timestamp debug values:");
    console.log("- currentScheduledFinalizationTimestamp:", questionData.currentScheduledFinalizationTimestamp ? 
      new Date(parseInt(questionData.currentScheduledFinalizationTimestamp) * 1000).toISOString() : "not set");
    console.log("- timeout:", questionData.timeout || "not set");
    console.log("- createdTimestamp:", questionData.createdTimestamp ? 
      new Date(parseInt(questionData.createdTimestamp) * 1000).toISOString() : "not set");
    
    let finalizationTime: number;
    
    // IMPORTANT: Reality.eth uses timestamps in seconds, not milliseconds
    // Calculate finalization time based on available data
    if (questionData.currentScheduledFinalizationTimestamp) {
      // Convert from seconds to milliseconds for JavaScript Date comparison
      finalizationTime = parseInt(questionData.currentScheduledFinalizationTimestamp) * 1000;
      console.log("Using currentScheduledFinalizationTimestamp:", new Date(finalizationTime).toISOString());
    }
    else if (questionData.timeout && questionData.createdTimestamp) {
      const timeoutSeconds = parseInt(questionData.timeout);
      const creationTime = parseInt(questionData.createdTimestamp);
      finalizationTime = (creationTime + timeoutSeconds) * 1000;
      console.log(`Using timeout (${timeoutSeconds}s) + createdTimestamp:`, new Date(finalizationTime).toISOString());
    }
    else if (questionData.createdTimestamp) {
      const creationTime = parseInt(questionData.createdTimestamp);
      finalizationTime = (creationTime + 900) * 1000; // Default 15 min timeout
      console.log("Using default timeout (900s) + createdTimestamp:", new Date(finalizationTime).toISOString());
    }
    else {
      console.warn("Insufficient data to calculate finalization time, defaulting to false");
      return false;
    }
    
    const currentTime = Date.now();
    const result = currentTime > finalizationTime;
    
    // More detailed logging
    console.log(`Finalization check result: ${result}`);
    console.log(`- Current time: ${new Date(currentTime).toISOString()} (${currentTime}ms)`);
    console.log(`- Finalization time: ${new Date(finalizationTime).toISOString()} (${finalizationTime}ms)`);
    console.log(`- Time difference: ${(currentTime - finalizationTime) / 1000} seconds`);
    
    return result;
  } catch (error) {
    console.error("Error checking finalization:", error);
    return false;
  }
};

/**
 * Get time remaining until finalization
 */
export const getTimeRemainingUntilFinalization = (timestamp?: string, timeout?: string, createdTimestamp?: string): string => {
  let finalizationTime: number;
  
  // Calculate finalization time based on available data
  if (timeout && createdTimestamp) {
    const timeoutSeconds = parseInt(timeout);
    const creationTime = parseInt(createdTimestamp);
    finalizationTime = (creationTime + timeoutSeconds) * 1000;
  }
  else if (createdTimestamp) {
    const creationTime = parseInt(createdTimestamp);
    finalizationTime = (creationTime + 900) * 1000; // Default 15 min timeout
  }
  else if (timestamp) {
    finalizationTime = parseInt(timestamp) * 1000;
  }
  else {
    finalizationTime = Date.now() + (15 * 60 * 1000);
  }
  
  const currentTime = Date.now();
  const timeRemaining = finalizationTime - currentTime;
  
  if (timeRemaining <= 0) {
    return "Finalization time has passed";
  }
  
  // Calculate days, hours, minutes, seconds
  const days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
  const hours = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);
  
  // Format based on remaining time
  if (days > 0) {
    return `${days}d ${hours}h ${minutes}m remaining`;
  } else if (hours > 0) {
    return `${hours}h ${minutes}m ${seconds}s remaining`;
  } else {
    return `${minutes}m ${seconds}s remaining`;
  }
};

/**
 * Get current answer for a question (1 = true/valid, 0 = false/invalid)
 */
export const getCurrentAnswer = async (questionId: string): Promise<string | null> => {
  const questionData = await getQuestionData(questionId);
  return questionData?.currentAnswer ?? null;
};
