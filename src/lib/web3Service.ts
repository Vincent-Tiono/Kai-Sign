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
  },
  {
    "inputs": [{"internalType": "string", "name": "ipfs", "type": "string"}],
    "name": "getStatus",
    "outputs": [{"internalType": "enum KaiSign.Status", "name": "", "type": "uint8"}],
    "stateMutability": "view",
    "type": "function"
  }
];

// Contract address on Sepolia testnet
// Replace this with the actual deployed contract address
const CONTRACT_ADDRESS = "0xDc5f343AD5108FAd1D6aa766252B05b58A10C527";

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
      // Check if ethereum object is available (MetaMask or other injected provider)
      if (typeof window !== 'undefined' && window.ethereum) {
        // Request account access
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        
        // Create provider and signer
        this.provider = new ethers.BrowserProvider(window.ethereum);
        this.signer = await this.provider.getSigner();
        
        // Create contract instance
        this.contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, this.signer);
        
        // Return the connected account
        return accounts[0];
      } else {
        throw new Error("MetaMask or compatible wallet not found. Please install MetaMask.");
      }
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
      
      // Call the minBond function on the contract
      const minBond = await this.contract.minBond();
      return minBond;
    } catch (error) {
      console.error("Error getting minimum bond:", error);
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
      await this.checkNetwork();
      
      // Create the spec first
      const createTx = await this.contract.createSpec(ipfsHash);
      await createTx.wait();
      
      // Then propose with a bond
      const proposeTx = await this.contract.proposeSpec(ipfsHash, { value: bondAmount });
      const receipt = await proposeTx.wait();
      
      return receipt.hash;
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
    
    const network = await this.provider.getNetwork();
    const chainId = Number(network.chainId);
    
    if (chainId !== SEPOLIA_CHAIN_ID) {
      await this.switchToSepolia();
      return false;
    }
    
    return true;
  }
  
  /**
   * Request MetaMask to switch to the Sepolia network
   */
  async switchToSepolia(): Promise<void> {
    if (typeof window === 'undefined' || !window.ethereum) return;
    
    try {
      // Try to switch to Sepolia
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: '0x' + SEPOLIA_CHAIN_ID.toString(16) }],
      });
    } catch (error: any) {
      // If the chain hasn't been added, add it
      if (error.code === 4902) {
        await window.ethereum.request({
          method: 'wallet_addEthereumChain',
          params: [
            {
              chainId: '0x' + SEPOLIA_CHAIN_ID.toString(16),
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
      } else {
        throw error;
      }
    }
  }
}

// Export a singleton instance
export const web3Service = new Web3Service(); 