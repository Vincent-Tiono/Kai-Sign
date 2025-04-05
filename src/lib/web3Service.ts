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
  }
];

// Fixed contract address on Sepolia - all lowercase for safety
const RAW_CONTRACT_ADDRESS = "0x328bffe9fc25cc02096a50da549b83b2c87b0101";

// Sepolia chain ID
const SEPOLIA_CHAIN_ID = 11155111;

export class Web3Service {
  private provider: ethers.BrowserProvider | null = null;
  private signer: ethers.Signer | null = null;
  private contract: ethers.Contract | null = null;
  
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
      
      // Get properly checksummed address
      try {
        const checksummedAddress = ethers.getAddress(RAW_CONTRACT_ADDRESS);
        console.log("Using checksummed contract address:", checksummedAddress);
        
        // Create contract instance with checksummed address
        this.contract = new ethers.Contract(
          checksummedAddress,
          CONTRACT_ABI,
          this.signer
        );
        
        // Test contract connection
        try {
          const minBond = await this.contract.minBond();
          console.log("Contract connection successful. Min bond:", minBond.toString());
        } catch (contractError) {
          console.error("Contract connection test failed:", contractError);
          // Continue anyway since the error might be with the minBond call, not the connection
        }
        
      } catch (checksumError) {
        console.error("Address checksum error:", checksumError);
        throw new Error(`Invalid contract address format: ${RAW_CONTRACT_ADDRESS}`);
      }
      
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
    try {
      if (!this.contract) {
        throw new Error("Not connected to MetaMask. Please connect first.");
      }
      
      // Use try-catch to get minBond
      try {
        // Call the minBond function on the contract
        const minBond = await this.contract.minBond();
        console.log("Min bond from contract:", minBond.toString());
        return minBond;
      } catch (error) {
        console.error("Error getting minBond from contract:", error);
        
        // Fallback to hardcoded value for demo purposes
        console.log("Using fallback min bond value");
        return BigInt("100000000000000");
      }
    } catch (error) {
      console.error("Error in getMinBond:", error);
      throw error;
    }
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
        // Create the spec first
        const createTx = await this.contract.createSpec(ipfsHash);
        console.log("Create transaction sent:", createTx.hash);
        await createTx.wait();
        console.log("Create transaction confirmed");
      } catch (createError) {
        console.error("Error in createSpec:", createError);
        console.log("Proceeding to proposeSpec anyway - spec might already exist");
      }
      
      // Then propose with a bond
      const proposeTx = await this.contract.proposeSpec(ipfsHash, { 
        value: bondAmount,
        gasLimit: 500000 // Add explicit gas limit
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
}

// Export a singleton instance
export const web3Service = new Web3Service(); 