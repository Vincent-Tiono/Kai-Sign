"use client";

import { useRouter } from "next/navigation";
import { useContext, useEffect } from "react";
import { Erc7730StoreContext, useErc7730Store } from "~/store/erc7730Provider";
import EditOperation from "./editOperation";
import useOperationStore from "~/store/useOperationStore";

const OperationsManagement = () => {
  const router = useRouter();
  const hasHydrated = useContext(Erc7730StoreContext)?.persist?.hasHydrated();

  const { getOperations } = useErc7730Store((s) => s);
  const operations = getOperations();
  const { selectedOperation } = useOperationStore();

  useEffect(() => {
    if (hasHydrated && operations === null) {
      router.push("/");
    }
  }, [operations, router, hasHydrated]);

  if (hasHydrated !== true) {
    return <div>Loading...</div>;
  }

  if (selectedOperation === null)
    return (
      <div className="flex h-screen w-full items-center justify-center text-xl">
        Select an operation to clear sign first
      </div>
    );

  return (
    <div className="w-full p-10">
      <EditOperation selectedOperation={selectedOperation} />
    </div>
  );
};

export default OperationsManagement;
