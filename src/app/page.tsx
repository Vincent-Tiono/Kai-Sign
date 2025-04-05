// import { HydrateClient } from "~/trpc/server";
// import CardErc7730 from "./address-abi-form";
// import Image from "next/image";

// export default async function Home() {
//   return (
//     <HydrateClient>
//       <div className="container relative m-auto flex min-h-screen items-center justify-center p-4 overflow-hidden">
//         {/* Background grid pattern */}
//         <div className="fixed inset-0 z-0 bg-[#0d041b]" style={{
//           backgroundImage: `
//             linear-gradient(rgba(57, 27, 112, 0.7) 1px, transparent 1px),
//             linear-gradient(90deg, rgba(57, 27, 112, 0.7) 1px, transparent 1px)
//           `,
//           backgroundSize: '30px 30px'
//         }} />
        
//         {/* Floating ETH Icons - Top */}
//         <Image 
//           src="/assets/eth.svg" 
//           alt="ETH Icon" 
//           width={30} 
//           height={30} 
//           className="nft-icon animation-delay-1" 
//           style={{ top: '10%', left: '5%' }}
//         />
//         <Image 
//           src="/assets/eth.svg" 
//           alt="ETH Icon" 
//           width={24} 
//           height={24} 
//           className="nft-icon animation-delay-2" 
//           style={{ top: '15%', left: '25%' }}
//         />
//         <Image 
//           src="/assets/eth.svg" 
//           alt="ETH Icon" 
//           width={28} 
//           height={28} 
//           className="nft-icon animation-delay-3" 
//           style={{ top: '7%', left: '45%' }}
//         />
//         <Image 
//           src="/assets/eth.svg" 
//           alt="ETH Icon" 
//           width={20} 
//           height={20} 
//           className="nft-icon animation-delay-4" 
//           style={{ top: '20%', left: '65%' }}
//         />
//         <Image 
//           src="/assets/eth.svg" 
//           alt="ETH Icon" 
//           width={22} 
//           height={22} 
//           className="nft-icon animation-delay-5" 
//           style={{ top: '5%', left: '85%' }}
//         />
//         <Image 
//           src="/assets/eth.svg" 
//           alt="ETH Icon" 
//           width={26} 
//           height={26} 
//           className="nft-icon animation-delay-2" 
//           style={{ top: '12%', left: '15%' }}
//         />
//         <Image 
//           src="/assets/eth.svg" 
//           alt="ETH Icon" 
//           width={18} 
//           height={18} 
//           className="nft-icon animation-delay-3" 
//           style={{ top: '18%', left: '55%' }}
//         />
//         <Image 
//           src="/assets/eth.svg" 
//           alt="ETH Icon" 
//           width={32} 
//           height={32} 
//           className="nft-icon animation-delay-4" 
//           style={{ top: '8%', left: '75%' }}
//         />
        
//         {/* Cat Rockets - Bottom */}
//         <div className="absolute bottom-[5%] left-0 w-full">
//           <Image 
//             src="/assets/catrocket.png" 
//             alt="Cat Rocket" 
//             width={80} 
//             height={80} 
//             className="rocket-ship animation-delay-1" 
//           />
//           <Image 
//             src="/assets/catrocket.png" 
//             alt="Cat Rocket" 
//             width={70} 
//             height={70} 
//             className="rocket-ship animation-delay-6" 
//           />
//           <Image 
//             src="/assets/catrocket.png" 
//             alt="Cat Rocket" 
//             width={60} 
//             height={60} 
//             className="rocket-ship animation-delay-4" 
//           />
//         </div>
        
//         {/* NFT GIF - Left Side */}
//         <div className="absolute left-10 top-1/2 hidden -translate-y-1/2 transform lg:block">
//           <div className="relative h-72 w-64 overflow-hidden rounded-lg border border-[#664bda]/30 float-animation glow-animation">
//             <Image
//               src="/assets/nft_gif.gif"
//               alt="NFT Animation"
//               width={256}
//               height={288}
//               className="object-cover"
//             />
//             <div className="absolute inset-0 bg-gradient-to-t from-[#0d041b] to-transparent opacity-30"></div>
//           </div>
//         </div>
        
//         {/* To The Moon GIF - Right Side */}
//         <div className="absolute right-10 top-1/2 hidden -translate-y-1/2 transform lg:block">
//           <div className="relative h-72 w-64 overflow-hidden rounded-lg border border-[#664bda]/30 float-animation-reverse glow-animation">
//             <Image
//               src="/assets/to_the_moon_gif.gif"
//               alt="To The Moon Animation"
//               width={256}
//               height={288}
//               className="object-cover"
//             />
//             <div className="absolute inset-0 bg-gradient-to-t from-[#0d041b] to-transparent opacity-30"></div>
//             <div className="absolute bottom-2 left-0 right-0 text-center text-sm font-medium text-white text-glow">
//               To The Moon
//             </div>
//           </div>
//         </div>
        
//         {/* Content */}
//         <div className="relative z-10">
//           <CardErc7730 />
//         </div>
//       </div>
//     </HydrateClient>
//   );
// }



import { HydrateClient } from "~/trpc/server";
import CardErc7730 from "./address-abi-form";
import { ModeToggle } from "~/components/ui/theme-switcher";

export default async function Home() {
  return (
    <HydrateClient>
      <div className="container m-auto flex h-screen max-w-2xl items-center justify-center p-4">
        <div>
          <h1 className="mb-6 flex items-center justify-between text-2xl font-bold">
            <span>
              ERC7730 Json builder <span className="text-red-500">Alpha</span>
            </span>
            <ModeToggle />
          </h1>

          <CardErc7730 />
        </div>
      </div>
    </HydrateClient>
  );
}