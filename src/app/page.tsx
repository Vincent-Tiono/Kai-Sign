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
              ERC7730 Json Builder <span className="text-red-500">By 開Sign</span>
            </span>
            <ModeToggle />
          </h1>

          <CardErc7730 />
        </div>
      </div>
    </HydrateClient>
  );
}
