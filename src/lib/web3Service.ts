import { ethers } from "ethers";

// Declare the window.ethereum for TypeScript
declare global {
  interface Window {
    ethereum?: {
      isMetaMask?: boolean;
      request: (request: { method: string; params?: Array<any> }) => Promise<any>;
    };
  }
}

// Type for contract methods to handle TS errors
type ContractWithMethods = ethers.Contract & {
  minBond: () => Promise<bigint>;
  createSpec: (ipfsHash: string) => Promise<any>;
  proposeSpec: (ipfsHash: string, options: { value: bigint }) => Promise<any>;
  handleResult: (ipfsHash: string) => Promise<any>;
  getQuestionId: (ipfsHash: string) => Promise<string>;
  getStatus: (ipfsHash: string) => Promise<number>;
  isAccepted: (ipfsHash: string) => Promise<boolean>;
};

// ABI for the KaiSign contract (based on the contract functions we need)
const CONTRACT_ABI = [
  {
    "inputs": [],
    "name": "minBond",
    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [{"internalType": "string", "name": "ipfs", "type": "string"}],
    "name": "createSpec",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [{"internalType": "string", "name": "ipfs", "type": "string"}],
    "name": "proposeSpec",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [{"internalType": "string", "name": "ipfs", "type": "string"}],
    "name": "handleResult",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [{"internalType": "string", "name": "ipfs", "type": "string"}],
    "name": "getQuestionId",
    "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [{"internalType": "string", "name": "ipfs", "type": "string"}],
    "name": "getStatus",
    "outputs": [{"internalType": "enum KaiSign.Status", "name": "", "type": "uint8"}],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [{"internalType": "string", "name": "ipfs", "type": "string"}],
    "name": "isAccepted",
    "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
    "stateMutability": "view",
    "type": "function"
  }
];

// Fixed contract address on Sepolia - all lowercase for safety
const RAW_CONTRACT_ADDRESS = "0x2d2f90786a365a2044324f6861697e9EF341F858";
// Sepolia chain ID
const SEPOLIA_CHAIN_ID = 11155111;

export class Web3Service {
  private provider: ethers.BrowserProvider | null = null;
  private signer: ethers.Signer | null = null;
  private contract: ContractWithMethods | null = null;
  
  /**
   * Connect to MetaMask and set up the provider, signer, and contract
   */
  async connect(): Promise<string> {
    try {
      // Check if ethereum object is available
      if (typeof window === 'undefined' || !window.ethereum) {
        throw new Error("MetaMask not found. Please install MetaMask extension.");
      }
      
      // Request account access
      const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
      if (!accounts || accounts.length === 0) {
        throw new Error("No accounts found. Please unlock MetaMask.");
      }
      
      console.log("Connected accounts:", accounts);
      
      // Create provider and signer
      this.provider = new ethers.BrowserProvider(window.ethereum);
      this.signer = await this.provider.getSigner();
      console.log("Signer address:", await this.signer.getAddress());
      
      // Get checksummed address
      const checksummedAddress = ethers.getAddress(RAW_CONTRACT_ADDRESS);
      console.log("Using contract address:", checksummedAddress);
      
      // Create contract instance with checksummed address
      this.contract = new ethers.Contract(
        checksummedAddress,
        CONTRACT_ABI,
        this.signer
      ) as unknown as ContractWithMethods;
      
      return accounts[0];
    } catch (error) {
      console.error("Failed to connect to MetaMask:", error);
      throw error;
    }
  }
  
  /**
   * Get the minimum bond amount required from the contract
   */
  async getMinBond(): Promise<bigint> {
    // Always use the hardcoded value
    const fixedBond = BigInt("100000000000000"); // 0.0001 ETH
    console.log("Using fixed bond amount:", fixedBond.toString());
    return fixedBond;
  }
  
  /**
   * Submit an IPFS hash to the contract with a bond
   */
  async proposeSpec(ipfsHash: string, bondAmount: bigint): Promise<string> {
    try {
      if (!this.contract || !this.signer) {
        throw new Error("Not connected to MetaMask. Please connect first.");
      }
      
      // Make sure we're on the Sepolia network
      const isCorrectNetwork = await this.checkNetwork();
      if (!isCorrectNetwork) {
        throw new Error("Please switch to the Sepolia network to continue.");
      }
      
      console.log("Creating spec with IPFS hash:", ipfsHash);
      console.log("Bond amount:", bondAmount.toString());
      
      try {
        // Create the spec first - we know contract is not null here
        const createTx = await this.contract.createSpec(ipfsHash);
        console.log("Create transaction sent:", createTx.hash);
        await createTx.wait();
        console.log("Create transaction confirmed");
      } catch (createError) {
        console.error("Error in createSpec:", createError);
        console.log("Proceeding to proposeSpec anyway - spec might already exist");
      }
      
      // Then propose with a bond - we know contract is not null here
      const proposeTx = await this.contract.proposeSpec(ipfsHash, { 
        value: bondAmount,
      });
      
      console.log("Propose transaction sent:", proposeTx.hash);
      const receipt = await proposeTx.wait();
      console.log("Propose transaction confirmed:", receipt);
      
      return proposeTx.hash;
    } catch (error) {
      console.error("Error proposing spec:", error);
      throw error;
    }
  }
  
  /**
   * Check if we're on the correct network, and if not, prompt to switch
   */
  async checkNetwork(): Promise<boolean> {
    if (!this.provider) return false;
    
    try {
      const network = await this.provider.getNetwork();
      const chainId = Number(network.chainId);
      console.log("Current network chainId:", chainId);
      
      if (chainId !== SEPOLIA_CHAIN_ID) {
        console.log("Wrong network. Switching to Sepolia...");
        await this.switchToSepolia();
        return false;
      }
      
      return true;
    } catch (error) {
      console.error("Error checking network:", error);
      return false;
    }
  }
  
  /**
   * Request MetaMask to switch to the Sepolia network
   */
  async switchToSepolia(): Promise<void> {
    if (typeof window === 'undefined' || !window.ethereum) return;
    
    const sepoliaChainIdHex = '0x' + SEPOLIA_CHAIN_ID.toString(16);
    console.log("Switching to Sepolia with chainId:", sepoliaChainIdHex);
    
    try {
      // Try to switch to Sepolia
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: sepoliaChainIdHex }],
      });
      console.log("Network switched successfully");
    } catch (error: any) {
      console.error("Error switching network:", error);
      
      // If the chain hasn't been added, add it
      if (error.code === 4902) {
        console.log("Sepolia not found in wallet. Adding network...");
        await window.ethereum.request({
          method: 'wallet_addEthereumChain',
          params: [
            {
              chainId: sepoliaChainIdHex,
              chainName: 'Sepolia Testnet',
              nativeCurrency: {
                name: 'Sepolia ETH',
                symbol: 'ETH',
                decimals: 18,
              },
              rpcUrls: ['https://rpc.sepolia.org'],
              blockExplorerUrls: ['https://sepolia.etherscan.io'],
            },
          ],
        });
        console.log("Sepolia network added");
      } else {
        throw error;
      }
    }
  }

  /**
   * Get the questionId from the contract for a given IPFS hash
   */
  async getQuestionId(ipfsHash: string): Promise<string> {
    try {
      if (!this.contract || !this.signer) {
        throw new Error("Not connected to MetaMask. Please connect first.");
      }
      
      // We know contract is not null here
      const questionId = await this.contract.getQuestionId(ipfsHash);
      console.log("Question ID for IPFS hash:", ipfsHash, "is", questionId);
      return questionId;
    } catch (error) {
      console.error("Error getting questionId:", error);
      throw error;
    }
  }

  /**
   * Get the current status of a specification from the contract
   * Returns: 0 = Submitted, 1 = Accepted, 2 = Rejected
   */
  async getSpecStatus(ipfsHash: string): Promise<number> {
    try {
      if (!this.contract || !this.signer) {
        throw new Error("Not connected to MetaMask. Please connect first.");
      }
      
      // We know contract is not null here
      const status = await this.contract.getStatus(ipfsHash);
      console.log("Status for IPFS hash:", ipfsHash, "is", status);
      return Number(status);
    } catch (error) {
      console.error("Error getting spec status:", error);
      throw error;
    }
  }

  /**
   * Check if a specification is accepted
   */
  async isSpecAccepted(ipfsHash: string): Promise<boolean> {
    try {
      if (!this.contract || !this.signer) {
        throw new Error("Not connected to MetaMask. Please connect first.");
      }
      
      // We know contract is not null here
      const isAccepted = await this.contract.isAccepted(ipfsHash);
      console.log("Acceptance status for IPFS hash:", ipfsHash, "is", isAccepted);
      return isAccepted;
    } catch (error) {
      console.error("Error checking if spec is accepted:", error);
      throw error;
    }
  }

  /**
   * Handle the result of a Reality.eth question by calling the contract's handleResult function
   */
  async handleResult(ipfsHash: string): Promise<string> {
    try {
      if (!this.contract || !this.signer) {
        throw new Error("Not connected to MetaMask. Please connect first.");
      }
      
      // Make sure we're on the Sepolia network
      const isCorrectNetwork = await this.checkNetwork();
      if (!isCorrectNetwork) {
        throw new Error("Please switch to the Sepolia network to continue.");
      }
      
      console.log("Handling result for IPFS hash:", ipfsHash);
      
      // We know contract is not null here
      const tx = await this.contract.handleResult(ipfsHash);
      console.log("Handle result transaction sent:", tx.hash);
      
      // Wait for transaction to be confirmed
      const receipt = await tx.wait();
      console.log("Handle result transaction confirmed:", receipt);
      
      return tx.hash;
    } catch (error) {
      console.error("Error handling result:", error);
      throw error;
    }
  }
}

// Export a singleton instance
export const web3Service = new Web3Service(); 